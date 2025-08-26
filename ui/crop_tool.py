"""
Interactive cropping tool for image processing
"""
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw

class CropTool:
    def __init__(self, parent, on_crop_complete=None):
        self.parent = parent
        self.on_crop_complete = on_crop_complete
        
        self.crop_window = None
        self.canvas = None
        self.image = None
        self.photo = None
        self.scale_factor = 1.0
        
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None
        self.is_dragging = False
        self.is_resizing = False
        self.resize_handle = None
    
    def open_crop_dialog(self, image):
        """Open crop dialog with given image"""
        if self.crop_window and self.crop_window.winfo_exists():
            self.crop_window.destroy()
        
        self.image = image
        self.crop_window = ctk.CTkToplevel(self.parent)
        self.crop_window.title("Recadrer l'image")
        self.crop_window.geometry("800x600")
        self.crop_window.grab_set()
        
        self.setup_crop_ui()
    
    def setup_crop_ui(self):
        """Setup crop tool UI"""
        # Instructions
        instructions = ctk.CTkLabel(
            self.crop_window,
            text="Glissez pour créer un rectangle de recadrage. Déplacez et redimensionnez selon vos besoins.",
            font=ctk.CTkFont(size=12)
        )
        instructions.pack(pady=10)
        
        # Canvas frame
        canvas_frame = ctk.CTkFrame(self.crop_window)
        canvas_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Canvas with scrollbars
        self.canvas = ctk.CTkCanvas(canvas_frame)
        
        h_scroll = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=self.canvas.xview)
        v_scroll = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Load and display image
        self.load_image_to_canvas()
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.crop_window)
        buttons_frame.pack(pady=10)
        
        ctk.CTkButton(buttons_frame, text="✅ OK", command=self.apply_crop,
                     fg_color="#4CAF50", hover_color="#45a049",
                     font=ctk.CTkFont(size=12, weight="bold"), height=32).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="❌ Annuler", command=self.cancel_crop,
                     fg_color="#f44336", hover_color="#da190b",
                     font=ctk.CTkFont(size=12, weight="bold"), height=32).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="🔄 Reset", command=self.reset_selection,
                     fg_color="#FF9800", hover_color="#f57c00",
                     font=ctk.CTkFont(size=12, weight="bold"), height=32).pack(side="left", padx=5)
    
    def load_image_to_canvas(self):
        """Load image to canvas"""
        if not self.image:
            return
        
        # Calculate display size
        max_canvas_width = 700
        max_canvas_height = 400
        
        img_width, img_height = self.image.size
        scale_x = max_canvas_width / img_width
        scale_y = max_canvas_height / img_height
        self.scale_factor = min(scale_x, scale_y, 1.0)
        
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        display_image = self.image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Configure canvas scroll region
        self.canvas.configure(scrollregion=(0, 0, display_width, display_height))
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
    
    def on_mouse_press(self, event):
        """Handle mouse press"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.rect_id:
            # Check if clicking on existing rectangle or its handles
            if self.is_point_in_rect(canvas_x, canvas_y):
                self.is_dragging = True
                self.drag_start_x = canvas_x
                self.drag_start_y = canvas_y
                return
        
        # Start new selection
        self.start_x = canvas_x
        self.start_y = canvas_y
        self.end_x = canvas_x
        self.end_y = canvas_y
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y,
            outline="red", width=2, dash=(5, 5)
        )
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.is_dragging and self.rect_id:
            # Move existing rectangle
            dx = canvas_x - self.drag_start_x
            dy = canvas_y - self.drag_start_y
            
            self.start_x += dx
            self.start_y += dy
            self.end_x += dx
            self.end_y += dy
            
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.end_x, self.end_y)
            
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
        elif self.rect_id:
            # Resize rectangle
            self.end_x = canvas_x
            self.end_y = canvas_y
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.end_x, self.end_y)
    
    def on_mouse_release(self, event):
        """Handle mouse release"""
        self.is_dragging = False
        self.is_resizing = False
    
    def is_point_in_rect(self, x, y):
        """Check if point is inside rectangle"""
        if not (self.start_x and self.start_y and self.end_x and self.end_y):
            return False
        
        left = min(self.start_x, self.end_x)
        right = max(self.start_x, self.end_x)
        top = min(self.start_y, self.end_y)
        bottom = max(self.start_y, self.end_y)
        
        return left <= x <= right and top <= y <= bottom
    
    def apply_crop(self):
        """Apply the crop"""
        if not self.rect_id or not self.image:
            return
        
        # Convert canvas coordinates to image coordinates
        left = min(self.start_x, self.end_x) / self.scale_factor
        top = min(self.start_y, self.end_y) / self.scale_factor
        right = max(self.start_x, self.end_x) / self.scale_factor
        bottom = max(self.start_y, self.end_y) / self.scale_factor
        
        # Ensure coordinates are within image bounds
        img_width, img_height = self.image.size
        left = max(0, min(left, img_width))
        top = max(0, min(top, img_height))
        right = max(left + 1, min(right, img_width))
        bottom = max(top + 1, min(bottom, img_height))
        
        if self.on_crop_complete:
            self.on_crop_complete(int(left), int(top), int(right), int(bottom))
        
        self.close_dialog()
    
    def cancel_crop(self):
        """Cancel crop operation"""
        self.close_dialog()
    
    def reset_selection(self):
        """Reset current selection"""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
    
    def close_dialog(self):
        """Close crop dialog"""
        if self.crop_window:
            self.crop_window.destroy()
            self.crop_window = None