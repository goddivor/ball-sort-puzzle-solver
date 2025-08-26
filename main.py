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
from multi_row_manager import MultiRowManager
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
        self.multi_row_manager = MultiRowManager()
        
        # State
        self.current_grid = []
        self.photo = None
        self.is_multi_row_mode = False
        
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
            self.analyze_colors,
            self.start_multi_row_configuration,
            self.go_to_next_row,
            self.go_to_previous_row,
            self.finish_all_rows
        )
        
        # Set callback for tube parameter changes
        self.parameter_panel.set_tube_params_change_callback(self.on_tube_params_changed)
        
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
                self.parameter_panel.enable_start_button(True)
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
                # Save images to multi-row manager if in multi-row mode
                if self.is_multi_row_mode:
                    self.multi_row_manager.set_current_row_images(
                        cropped.copy(),
                        self.image_processor.processed_image.copy() if self.image_processor.processed_image else None
                    )
                
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
            
            # Save colors to multi-row manager if in multi-row mode
            if self.is_multi_row_mode:
                self.multi_row_manager.set_current_row_colors(color_groups)
                # Create and save matrices
                grid_matrix = self.create_grid_matrix()
                color_matrix = self.create_color_matrix(color_groups)
                self.multi_row_manager.set_current_row_matrices(grid_matrix, color_matrix)
            
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
    
    def start_multi_row_configuration(self):
        """Start multi-row configuration process"""
        num_rows = self.parameter_panel.get_num_rows()
        self.multi_row_manager.set_num_rows(num_rows)
        self.is_multi_row_mode = num_rows > 1
        
        if self.is_multi_row_mode:
            self.parameter_panel.show_navigation(True)
            self.update_multi_row_ui()
            self.parameter_panel.add_status_message(f"Mode multi-rangées: {num_rows} rangées")
        
        # Enable crop button for first row
        self.parameter_panel.enable_crop_button(True)
    
    def go_to_next_row(self):
        """Move to next row"""
        if not self.is_multi_row_mode:
            return
        
        # Save current row data
        self.save_current_row_data()
        
        if self.multi_row_manager.go_to_next_row():
            self.update_multi_row_ui()
            self.load_current_row_data()
            
            current_row = self.multi_row_manager.get_current_row_number()
            self.parameter_panel.add_status_message(f"Passage à la rangée {current_row}")
    
    def go_to_previous_row(self):
        """Move to previous row"""
        if not self.is_multi_row_mode:
            return
        
        # Save current row data
        self.save_current_row_data()
        
        if self.multi_row_manager.go_to_previous_row():
            self.update_multi_row_ui()
            self.load_current_row_data()
            
            current_row = self.multi_row_manager.get_current_row_number()
            self.parameter_panel.add_status_message(f"Retour à la rangée {current_row}")
    
    def finish_all_rows(self):
        """Finish all rows and show aggregated results"""
        if not self.is_multi_row_mode:
            return
        
        # Save current row data
        self.save_current_row_data()
        
        # Show aggregated results
        self.display_aggregated_results()
        self.parameter_panel.add_status_message("Configuration multi-rangées terminée")
    
    def save_current_row_data(self):
        """Save current row configuration"""
        if not self.is_multi_row_mode:
            return
        
        # Save current state to multi-row manager
        corners = self.grid_generator.get_corner_points()
        if len(corners) == 4:
            self.multi_row_manager.set_current_row_corners(corners)
        
        # Get the actual current values from the UI spinboxes
        num_tubes = self.parameter_panel.tubes_var.get()
        balls_per_tube = self.parameter_panel.balls_var.get()
        self.multi_row_manager.set_current_row_tube_params(num_tubes, balls_per_tube)
        
        if self.current_grid:
            self.multi_row_manager.set_current_row_grid(self.current_grid)
    
    def load_current_row_data(self):
        """Load data for current row"""
        if not self.is_multi_row_mode:
            return
        
        row_data = self.multi_row_manager.get_current_row_data()
        if not row_data:
            return
        
        # Reset UI state for new row
        self.current_grid = []
        self.grid_generator.clear_corner_points()
        
        # Load saved images if available
        if row_data['cropped_image']:
            self.image_processor.processed_image = row_data['cropped_image']
            self.display_current_image()
            self.parameter_panel.enable_corners_button(True)
        
        # Load saved corners if available
        if len(row_data['corners']) == 4:
            self.grid_generator.set_corner_points(row_data['corners'])
            self.parameter_panel.update_corners_status(4)
            self.parameter_panel.enable_generate_button(True)
        else:
            self.parameter_panel.update_corners_status(0)
        
        # Load tube parameters
        self.parameter_panel.tubes_var.set(row_data['num_tubes'])
        self.parameter_panel.balls_var.set(row_data['balls_per_tube'])
        self.parameter_panel.update_expected_total()
        
        # Load grid if available
        if row_data['grid']:
            self.current_grid = row_data['grid']
            self.display_grid_visualization()
            self.parameter_panel.update_grid_status(len(self.current_grid))
            self.parameter_panel.enable_analyze_button(True)
        
        # Load colors if available
        if row_data['colors']:
            self.display_analysis_results(row_data['colors'])
        else:
            self.clear_results()
    
    def update_multi_row_ui(self):
        """Update UI for multi-row mode"""
        if not self.is_multi_row_mode:
            return
        
        current_row = self.multi_row_manager.get_current_row_number()
        total_rows = self.multi_row_manager.num_rows
        
        self.parameter_panel.update_progress(current_row, total_rows)
        
        is_first = self.multi_row_manager.is_first_row()
        is_last = self.multi_row_manager.is_last_row()
        can_finish = self.multi_row_manager.can_finish_all_rows()
        
        self.parameter_panel.update_navigation_buttons(is_first, is_last, can_finish)
    
    def display_aggregated_results(self):
        """Display aggregated results from all rows"""
        results = self.multi_row_manager.get_aggregated_results()
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.results_frame, text="Résultats Globaux", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Summary
        summary_frame = tk.Frame(self.results_frame)
        summary_frame.pack(fill=tk.X, pady=5)
        
        summary_text = f"Rangées analysées: {results['completed_rows']}/{results['total_rows']}\n"
        summary_text += f"Total éprouvettes: {results['total_tubes']}\n"
        summary_text += f"Total balles détectées: {results['total_balls']}"
        
        tk.Label(summary_frame, text=summary_text, 
                font=("Arial", 12), justify=tk.LEFT).pack()
        
        # Colors by row
        if results['colors_by_row']:
            colors_frame = tk.Frame(self.results_frame)
            colors_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(colors_frame, text="Couleurs par rangée:", 
                    font=("Arial", 12, "bold")).pack(anchor=tk.W)
            
            for color_key, balls in results['colors_by_row'].items():
                color_frame = tk.Frame(colors_frame)
                color_frame.pack(fill=tk.X, pady=2)
                
                # Extract color info
                row_info, color = color_key.split('_', 1)
                color_rgb = eval(color) if color.startswith('(') else (128, 128, 128)
                
                # Color sample
                canvas = tk.Canvas(color_frame, width=25, height=25)
                color_hex = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
                canvas.create_rectangle(0, 0, 25, 25, fill=color_hex, outline="black")
                canvas.pack(side=tk.LEFT, padx=(0, 10))
                
                # Label
                tk.Label(color_frame, text=f"{row_info}: {len(balls)} balles").pack(side=tk.LEFT)
    
    def create_grid_matrix(self):
        """Create matrix representation of grid"""
        if not self.current_grid:
            return []
        
        # Get tube parameters
        num_tubes, balls_per_tube = self.parameter_panel.get_tube_parameters()
        
        # Create matrix
        matrix = []
        for tube_idx in range(num_tubes):
            tube_column = []
            for ball_idx in range(balls_per_tube):
                # Find matching grid point
                grid_point = None
                for circle in self.current_grid:
                    if circle.get('tube_idx') == tube_idx and circle.get('ball_idx') == ball_idx:
                        grid_point = {
                            'x': circle['x'],
                            'y': circle['y'],
                            'radius': circle['radius']
                        }
                        break
                tube_column.append(grid_point)
            matrix.append(tube_column)
        
        return matrix
    
    def create_color_matrix(self, color_groups):
        """Create matrix representation of colors"""
        if not self.current_grid or not color_groups:
            return []
        
        # Get tube parameters
        num_tubes, balls_per_tube = self.parameter_panel.get_tube_parameters()
        
        # Create matrix
        matrix = []
        for tube_idx in range(num_tubes):
            tube_column = []
            for ball_idx in range(balls_per_tube):
                # Find color for this position
                found_color = None
                for color, balls in color_groups.items():
                    for ball in balls:
                        # Find corresponding grid position
                        for circle in self.current_grid:
                            if (abs(circle['x'] - ball['x']) < 10 and 
                                abs(circle['y'] - ball['y']) < 10 and
                                circle.get('tube_idx') == tube_idx and
                                circle.get('ball_idx') == ball_idx):
                                found_color = color
                                break
                        if found_color:
                            break
                    if found_color:
                        break
                tube_column.append(found_color)
            matrix.append(tube_column)
        
        return matrix
    
    def show_final_results_window(self):
        """Show final results in separate window"""
        results = self.multi_row_manager.get_aggregated_results()
        
        # Create new window
        results_window = tk.Toplevel(self.root)
        results_window.title("Résultats Finaux - Ball Sort Puzzle")
        results_window.geometry("800x600")
        results_window.grab_set()
        
        # Main frame with scrollbar
        main_frame = tk.Frame(results_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title = tk.Label(scrollable_frame, text="Résultats Finaux", 
                        font=("Arial", 20, "bold"), fg="#2196F3")
        title.pack(pady=(0, 20))
        
        # Summary stats
        summary_frame = tk.LabelFrame(scrollable_frame, text="Résumé", font=("Arial", 14, "bold"))
        summary_frame.pack(fill=tk.X, pady=10)
        
        stats_text = f"""Rangées analysées: {results['completed_rows']}/{results['total_rows']}
Total éprouvettes: {results['total_tubes']}
Total balles détectées: {results['total_balls']}"""
        
        tk.Label(summary_frame, text=stats_text, font=("Arial", 12), 
                justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Color details by row
        if results['colors_by_row']:
            colors_frame = tk.LabelFrame(scrollable_frame, text="Détail des Couleurs", 
                                       font=("Arial", 14, "bold"))
            colors_frame.pack(fill=tk.X, pady=10)
            
            # Group by row
            rows_colors = {}
            for color_key, balls in results['colors_by_row'].items():
                row_info, color = color_key.split('_', 1)
                if row_info not in rows_colors:
                    rows_colors[row_info] = []
                rows_colors[row_info].append((color, len(balls)))
            
            for row_info, colors in rows_colors.items():
                row_frame = tk.Frame(colors_frame)
                row_frame.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(row_frame, text=f"{row_info}:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
                
                colors_grid = tk.Frame(row_frame)
                colors_grid.pack(fill=tk.X, padx=20)
                
                for i, (color, count) in enumerate(colors):
                    color_item = tk.Frame(colors_grid)
                    color_item.pack(fill=tk.X, pady=2)
                    
                    # Color sample
                    try:
                        color_rgb = eval(color) if color.startswith('(') else (128, 128, 128)
                        canvas_color = tk.Canvas(color_item, width=30, height=30)
                        color_hex = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
                        canvas_color.create_rectangle(0, 0, 30, 30, fill=color_hex, outline="black")
                        canvas_color.pack(side=tk.LEFT, padx=(0, 10))
                        
                        tk.Label(color_item, text=f"Couleur {i+1}: {count} balles").pack(side=tk.LEFT)
                    except:
                        tk.Label(color_item, text=f"Couleur {i+1}: {count} balles").pack()
        
        # Close button
        close_frame = tk.Frame(scrollable_frame)
        close_frame.pack(pady=20)
        
        tk.Button(close_frame, text="Fermer", command=results_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 12)).pack()
        
        # Pack scrollbar elements
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def on_tube_params_changed(self):
        """Called when tube parameters change in UI"""
        if self.is_multi_row_mode:
            # Save the current parameters immediately
            num_tubes = self.parameter_panel.tubes_var.get()
            balls_per_tube = self.parameter_panel.balls_var.get()
            self.multi_row_manager.set_current_row_tube_params(num_tubes, balls_per_tube)
    
    def display_aggregated_results(self):
        """Display aggregated results from all rows"""
        # Show in separate window instead of main UI
        self.show_final_results_window()
    
    def run(self):
        """Run app"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = BallSortSolver()
        app.run()
    except Exception as e:
        print(f"Erreur: {e}")