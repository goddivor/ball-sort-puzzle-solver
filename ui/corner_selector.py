"""
Corner selection tool for grid calibration
"""
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw

class CornerSelector:
    def __init__(self, parent, on_corners_complete=None):
        self.parent = parent
        self.on_corners_complete = on_corners_complete
        
        self.selector_window = None
        self.canvas = None
        self.image = None
        self.photo = None
        self.scale_factor = 1.0
        self.circle_radius = 15
        
        self.corner_points = []
        self.point_ids = []
        self.selected_point = None
    
    def open_corner_dialog(self, image):
        """Open corner selection dialog"""
        if self.selector_window and self.selector_window.winfo_exists():
            self.selector_window.destroy()
        
        self.image = image
        self.corner_points = []
        self.point_ids = []
        
        self.selector_window = ctk.CTkToplevel(self.parent)
        self.selector_window.title("Sélection des coins")
        self.selector_window.geometry("900x700")
        self.selector_window.grab_set()
        
        self.setup_selector_ui()
    
    def setup_selector_ui(self):
        """Setup corner selector UI"""
        # Top frame with instructions and controls
        top_frame = ctk.CTkFrame(self.selector_window)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        instructions = ctk.CTkLabel(
            top_frame,
            text="Cliquez sur les 4 coins des balles : Haut-Gauche, Haut-Droite, Bas-Gauche, Bas-Droite",
            font=ctk.CTkFont(size=12)
        )
        instructions.pack(pady=5)
        
        # Circle size control
        control_frame = ctk.CTkFrame(top_frame)
        control_frame.pack(pady=5)
        
        ctk.CTkLabel(control_frame, text="Taille du cercle:").pack(side="left")
        
        radius_scale = ctk.CTkSlider(
            control_frame, from_=5, to=50, number_of_steps=45,
            command=self.on_radius_change
        )
        radius_scale.pack(side="left", padx=10)
        radius_scale.set(self.circle_radius)
        
        self.radius_label = ctk.CTkLabel(control_frame, text=f"{self.circle_radius}px")
        self.radius_label.pack(side="left")
        
        # Canvas frame
        canvas_frame = ctk.CTkFrame(self.selector_window)
        canvas_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        self.canvas = ctk.CTkCanvas(canvas_frame)
        
        h_scroll = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=self.canvas.xview)
        v_scroll = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Load image
        self.load_image_to_canvas()
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Status frame
        status_frame = ctk.CTkFrame(self.selector_window)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Points sélectionnés: 0/4",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack()
        
        # Points list
        list_frame = ctk.CTkFrame(self.selector_window)
        list_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(list_frame, text="Points sélectionnés:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        
        self.points_textbox = ctk.CTkTextbox(list_frame, height=100)
        self.points_textbox.pack(fill="x", pady=5)
        
        # Buttons for point management
        point_buttons_frame = ctk.CTkFrame(list_frame)
        point_buttons_frame.pack(fill="x")
        
        ctk.CTkButton(point_buttons_frame, text="🗑️ Effacer tout", 
                     command=self.clear_all_points,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     fg_color="#FF6B6B", hover_color="#FF5252").pack(side="left", padx=5)
        
        # Bottom buttons
        buttons_frame = ctk.CTkFrame(self.selector_window)
        buttons_frame.pack(pady=10)
        
        self.ok_button = ctk.CTkButton(buttons_frame, text="✅ OK", command=self.apply_corners,
                                      fg_color="#4CAF50", hover_color="#45a049",
                                      font=ctk.CTkFont(size=12, weight="bold"), height=35, state="disabled")
        self.ok_button.pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="❌ Annuler", command=self.cancel_selection,
                     fg_color="#f44336", hover_color="#da190b",
                     font=ctk.CTkFont(size=12, weight="bold"), height=35).pack(side="left", padx=5)
    
    def load_image_to_canvas(self):
        """Load image to canvas"""
        if not self.image:
            return
        
        # Calculate display size
        max_canvas_width = 800
        max_canvas_height = 500
        
        img_width, img_height = self.image.size
        scale_x = max_canvas_width / img_width
        scale_y = max_canvas_height / img_height
        self.scale_factor = min(scale_x, scale_y, 1.0)
        
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        display_image = self.image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(display_image)
        
        self.canvas.configure(scrollregion=(0, 0, display_width, display_height))
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
    
    def on_radius_change(self, value):
        """Handle radius change"""
        self.circle_radius = int(value)
        self.radius_label.configure(text=f"{self.circle_radius}px")
        
        # Update visual circles
        self.update_visual_circles()
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        if len(self.corner_points) >= 4:
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to original image coordinates
        orig_x = int(canvas_x / self.scale_factor)
        orig_y = int(canvas_y / self.scale_factor)
        
        # Add point
        self.corner_points.append({'x': orig_x, 'y': orig_y})
        
        # Draw visual circle on canvas
        display_radius = int(self.circle_radius * self.scale_factor)
        circle_id = self.canvas.create_oval(
            canvas_x - display_radius, canvas_y - display_radius,
            canvas_x + display_radius, canvas_y + display_radius,
            outline="red", width=2, fill="", dash=(3, 3)
        )
        
        # Draw center point
        center_id = self.canvas.create_oval(
            canvas_x - 3, canvas_y - 3,
            canvas_x + 3, canvas_y + 3,
            fill="red", outline="red"
        )
        
        self.point_ids.append((circle_id, center_id))
        
        self.update_status()
        self.update_points_list()
    
    def update_visual_circles(self):
        """Update visual representation of circles"""
        # Remove old circles
        for circle_id, center_id in self.point_ids:
            self.canvas.delete(circle_id)
            self.canvas.delete(center_id)
        
        self.point_ids = []
        
        # Redraw circles with new radius
        for point in self.corner_points:
            canvas_x = point['x'] * self.scale_factor
            canvas_y = point['y'] * self.scale_factor
            display_radius = int(self.circle_radius * self.scale_factor)
            
            circle_id = self.canvas.create_oval(
                canvas_x - display_radius, canvas_y - display_radius,
                canvas_x + display_radius, canvas_y + display_radius,
                outline="red", width=2, fill="", dash=(3, 3)
            )
            
            center_id = self.canvas.create_oval(
                canvas_x - 3, canvas_y - 3,
                canvas_x + 3, canvas_y + 3,
                fill="red", outline="red"
            )
            
            self.point_ids.append((circle_id, center_id))
    
    def update_status(self):
        """Update status display"""
        count = len(self.corner_points)
        self.status_label.configure(text=f"Points sélectionnés: {count}/4")
        
        if count == 4:
            self.ok_button.configure(state="normal")
        else:
            self.ok_button.configure(state="disabled")
    
    def update_points_list(self):
        """Update points textbox"""
        self.points_textbox.configure(state="normal")
        self.points_textbox.delete("0.0", "end")
        
        labels = ["Haut-Gauche", "Haut-Droite", "Bas-Gauche", "Bas-Droite"]
        
        for i, point in enumerate(self.corner_points):
            label = labels[i] if i < len(labels) else f"Point {i+1}"
            self.points_textbox.insert("end", f"{label}: ({point['x']}, {point['y']})\n")
        
        self.points_textbox.configure(state="disabled")
    
    def delete_last_point(self):
        """Delete last added point"""
        if not self.corner_points:
            return
        
        # Remove last point
        self.corner_points.pop()
        
        # Remove last visual elements
        if self.point_ids:
            circle_id, center_id = self.point_ids.pop()
            self.canvas.delete(circle_id)
            self.canvas.delete(center_id)
        
        self.update_status()
        self.update_points_list()
    
    def clear_all_points(self):
        """Clear all points"""
        self.corner_points = []
        
        # Clear visual elements
        for circle_id, center_id in self.point_ids:
            self.canvas.delete(circle_id)
            self.canvas.delete(center_id)
        
        self.point_ids = []
        
        self.update_status()
        self.update_points_list()
    
    def apply_corners(self):
        """Apply corner selection"""
        if len(self.corner_points) != 4:
            return
        
        # Add radius information to points
        points_with_radius = []
        for point in self.corner_points:
            points_with_radius.append({
                'x': point['x'],
                'y': point['y'],
                'radius': self.circle_radius
            })
        
        if self.on_corners_complete:
            self.on_corners_complete(points_with_radius, self.circle_radius)
        
        self.close_dialog()
    
    def cancel_selection(self):
        """Cancel corner selection"""
        self.close_dialog()
    
    def close_dialog(self):
        """Close corner selector dialog"""
        if self.selector_window:
            self.selector_window.destroy()
            self.selector_window = None