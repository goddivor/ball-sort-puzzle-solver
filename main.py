"""
Ball Sort Puzzle Solver - Working Version
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

# Import modules
from image_processor import ImageProcessor
from grid_generator import GridGenerator  
from color_analyzer import ColorAnalyzer
from parameter_panel import ParameterPanel
from crop_tool import CropTool
from corner_selector import CornerSelector

class BallSortSolver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ball Sort Puzzle Solver - Working Version")
        self.root.geometry("1200x800")
        
        # Core components
        self.image_processor = ImageProcessor()
        self.grid_generator = GridGenerator()
        self.color_analyzer = ColorAnalyzer()
        
        # State
        self.current_grid = []
        self.photo = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left: Image area
        self.setup_image_area(main_container)
        
        # Right: Parameters
        self.parameter_panel = ParameterPanel(main_container)
        self.parameter_panel.set_callbacks(
            self.open_crop_tool,
            self.open_corner_selector,
            self.generate_grid,
            self.analyze_colors
        )
        
        # Tools
        self.crop_tool = CropTool(self.root, self.on_crop_complete)
        self.corner_selector = CornerSelector(self.root, self.on_corners_complete)
    
    def setup_image_area(self, parent):
        """Setup image area"""
        container = tk.Frame(parent, bg="#f8f8f8")
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(container, text="Ball Sort Puzzle Solver", 
                        font=("Arial", 18, "bold"), bg="#f8f8f8")
        title.pack(pady=10)
        
        # Upload
        upload_btn = tk.Button(container, text="Charger Image", 
                              command=self.upload_image,
                              font=("Arial", 12), bg="#4CAF50", fg="white",
                              padx=20, pady=10)
        upload_btn.pack(pady=10)
        
        # Image frame
        self.image_frame = tk.Frame(container, bg="white", relief=tk.SUNKEN, bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Results
        self.results_frame = tk.Frame(container)
        self.results_frame.pack(fill=tk.X, pady=10)
    
    def upload_image(self):
        """Upload image"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                self.image_processor.load_image(file_path)
                self.display_current_image()
                self.parameter_panel.enable_crop_button(True)
                self.parameter_panel.add_status_message("Image chargée")
                self.clear_results()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
    
    def display_current_image(self):
        """Display image"""
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        display_img, _ = self.image_processor.resize_for_display()
        
        if display_img:
            self.photo = ImageTk.PhotoImage(display_img)
            label = tk.Label(self.image_frame, image=self.photo, bg="white")
            label.pack(expand=True)
        else:
            label = tk.Label(self.image_frame, text="Aucune image", 
                           font=("Arial", 14), bg="white", fg="gray")
            label.pack(expand=True)
    
    def open_crop_tool(self):
        """Open crop tool"""
        if not self.image_processor.original_image:
            messagebox.showerror("Erreur", "Charger une image d'abord")
            return
        self.crop_tool.open_crop_dialog(self.image_processor.original_image)
    
    def on_crop_complete(self, x1, y1, x2, y2):
        """Crop complete"""
        try:
            cropped = self.image_processor.crop_image(x1, y1, x2, y2)
            if cropped:
                self.display_current_image()
                self.parameter_panel.enable_corners_button(True)
                self.parameter_panel.add_status_message(f"Recadré: {cropped.size}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def open_corner_selector(self):
        """Open corner selector"""
        if not self.image_processor.processed_image:
            messagebox.showerror("Erreur", "Recadrer d'abord")
            return
        self.corner_selector.open_corner_dialog(self.image_processor.processed_image)
    
    def on_corners_complete(self, corner_points, radius):
        """Corners complete"""
        try:
            points = [{'x': p['x'], 'y': p['y']} for p in corner_points]
            self.grid_generator.set_corner_points(points)
            self.grid_generator.set_ball_radius(radius)
            self.parameter_panel.update_corners_status(len(corner_points))
            self.parameter_panel.add_status_message(f"4 coins, rayon: {radius}px")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def generate_grid(self):
        """Generate grid"""
        try:
            # Get tube parameters
            num_tubes, balls_per_tube = self.parameter_panel.get_tube_parameters()
            spacing = self.parameter_panel.get_grid_spacing()
            
            # Configure grid generator
            self.grid_generator.set_tube_parameters(num_tubes, balls_per_tube)
            self.grid_generator.set_grid_spacing(spacing)
            
            # Generate grid
            self.current_grid = self.grid_generator.generate_grid()
            
            if self.current_grid:
                expected_total = self.grid_generator.get_expected_ball_count()
                actual_count = len(self.current_grid)
                
                self.display_grid_visualization()
                self.parameter_panel.update_grid_status(actual_count)
                
                status_msg = f"Grille générée: {actual_count} cercles"
                if actual_count == expected_total:
                    status_msg += " ✓"
                else:
                    status_msg += f" (attendu: {expected_total})"
                
                self.parameter_panel.add_status_message(status_msg)
            else:
                messagebox.showerror("Erreur", "Échec génération grille")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def display_grid_visualization(self):
        """Show grid"""
        if not self.current_grid:
            return
        
        grid_image = self.image_processor.draw_circles_on_image(self.current_grid)
        original = self.image_processor.processed_image
        self.image_processor.processed_image = grid_image
        self.display_current_image()
        self.image_processor.processed_image = original
    
    def analyze_colors(self):
        """Analyze colors"""
        try:
            if not self.current_grid:
                messagebox.showerror("Erreur", "Générer grille d'abord")
                return
            
            tolerance = self.parameter_panel.get_color_tolerance()
            self.color_analyzer.set_tolerance(tolerance)
            
            detected = self.color_analyzer.analyze_grid_circles(
                self.image_processor.processed_image, self.current_grid
            )
            
            color_groups = self.color_analyzer.group_balls_by_color(detected)
            self.display_analysis_results(color_groups)
            self.parameter_panel.add_status_message(f"Analysé: {len(detected)} balles")
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def display_analysis_results(self, color_groups):
        """Display results"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not color_groups:
            tk.Label(self.results_frame, text="Aucune balle détectée").pack()
            return
        
        tk.Label(self.results_frame, text="Résultats:", 
                font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        total = 0
        for i, (color, balls) in enumerate(color_groups.items()):
            count = len(balls)
            total += count
            
            frame = tk.Frame(self.results_frame)
            frame.pack(fill=tk.X, pady=2)
            
            canvas = tk.Canvas(frame, width=25, height=25)
            color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            canvas.create_rectangle(0, 0, 25, 25, fill=color_hex, outline="black")
            canvas.pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(frame, text=f"Couleur {i+1}: {count} balles").pack(side=tk.LEFT)
        
        # Total and comparison with expected
        total_frame = tk.Frame(self.results_frame)
        total_frame.pack(pady=(10, 0))
        
        expected_total = self.grid_generator.get_expected_ball_count()
        total_text = f"TOTAL: {total} balles"
        
        if expected_total > 0:
            if total == expected_total:
                total_text += " ✓"
                color = "#4CAF50"
            else:
                total_text += f" (attendu: {expected_total})"
                color = "#FF9800"
        else:
            color = "#2196F3"
        
        tk.Label(total_frame, text=total_text,
                font=("Arial", 12, "bold"), fg=color).pack()
        
        # Tube analysis
        if hasattr(self, 'current_grid') and self.current_grid:
            num_tubes, balls_per_tube = self.parameter_panel.get_tube_parameters()
            tube_analysis = self.analyze_by_tubes(color_groups, num_tubes)
            
            if tube_analysis:
                tube_frame = tk.Frame(self.results_frame)
                tube_frame.pack(pady=5)
                
                tk.Label(tube_frame, text="Répartition par éprouvette:",
                        font=("Arial", 10, "bold")).pack()
                
                for tube_idx, tube_colors in tube_analysis.items():
                    tube_text = f"Éprouvette {tube_idx + 1}: {len(tube_colors)} couleurs"
                    tk.Label(tube_frame, text=tube_text, font=("Arial", 9)).pack()
    
    def analyze_by_tubes(self, color_groups, num_tubes):
        """Analyze color distribution by tubes"""
        if not self.current_grid:
            return None
        
        tube_analysis = {i: set() for i in range(num_tubes)}
        
        # Group balls by tubes based on grid positions
        for color, balls in color_groups.items():
            for ball in balls:
                # Find corresponding grid position
                for grid_circle in self.current_grid:
                    if (abs(grid_circle['x'] - ball['x']) < 10 and 
                        abs(grid_circle['y'] - ball['y']) < 10):
                        tube_idx = grid_circle.get('tube_idx', 0)
                        if tube_idx < num_tubes:
                            tube_analysis[tube_idx].add(color)
                        break
        
        return tube_analysis
    
    def clear_results(self):
        """Clear results"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def run(self):
        """Run app"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = BallSortSolver()
        app.run()
    except Exception as e:
        print(f"Erreur: {e}")