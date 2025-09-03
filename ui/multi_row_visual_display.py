"""
Multi-Row Visual Display for Ball Sort Puzzle Solver
Creates a graphical representation of multi-row game states with proper layout
"""
import customtkinter as ctk
from tkinter import Canvas
import math

class MultiRowVisualDisplay:
    """Visual representation of multi-row game state"""
    
    def __init__(self, parent, layout_data, multi_row_data):
        self.parent = parent
        self.layout_data = layout_data
        self.multi_row_data = multi_row_data
        self.window = None
        
        # Display constants
        self.TUBE_WIDTH = 45
        self.TUBE_HEIGHT = 150
        self.BALL_RADIUS = 15
        self.TUBE_SPACING = 55
        self.ROW_SECTION_MARGIN = 30
        self.SECTION_BORDER = 10
        
    def show_visual_display(self):
        """Create and show the multi-row visual game display"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("🎮 Modèle Multi-Rangées - Ball Sort Puzzle")
        
        # Calculate window size based on layout
        grid_cols, grid_rows = self.layout_data['grid_dimensions']
        max_tubes_per_row = max([row_info['tubes_count'] for row_info in self.layout_data['rows_info']])
        
        # Add space for empty tubes section
        section_width = max(400, (max_tubes_per_row * self.TUBE_SPACING) + 100)
        section_height = self.TUBE_HEIGHT + 120
        
        window_width = max(1000, (grid_cols * section_width) + 100)
        window_height = max(700, (grid_rows * section_height) + 200 + section_height)  # +section_height for empty tubes
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.grab_set()
        
        # Main scrollable frame
        main_scrollable = ctk.CTkScrollableFrame(self.window)
        main_scrollable.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title = ctk.CTkLabel(main_scrollable, text="🎮 Modèle Multi-Rangées", 
                           font=ctk.CTkFont(size=24, weight="bold"), text_color="#2196F3")
        title.pack(pady=(10, 20))
        
        # Info section
        self._create_info_section(main_scrollable)
        
        # Canvas for drawing the game (larger for scrolling)
        canvas_width = max(1200, window_width - 60)
        canvas_height = max(800, window_height)
        
        self.canvas = Canvas(main_scrollable, width=canvas_width, height=canvas_height,
                           bg='#f5f5f5', relief='sunken', bd=2)
        self.canvas.pack(pady=20)
        
        # Draw the multi-row game state
        self._draw_multi_row_game()
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_scrollable)
        button_frame.pack(pady=10)
        
        # Solve button
        solve_btn = ctk.CTkButton(button_frame, text="🧩 Résoudre le Puzzle Multi-Rangées", 
                                command=self._solve_multi_row_puzzle,
                                fg_color="#4CAF50", hover_color="#45a049",
                                font=ctk.CTkFont(size=14, weight="bold"), 
                                height=40, width=250)
        solve_btn.pack(side="left", padx=(0, 20))
        
        # Close button
        close_btn = ctk.CTkButton(button_frame, text="❌ Fermer", 
                                command=self.window.destroy,
                                fg_color="#f44336", hover_color="#da190b",
                                font=ctk.CTkFont(size=12, weight="bold"), 
                                height=40, width=120)
        close_btn.pack(side="left")
    
    def _create_info_section(self, parent):
        """Create information section"""
        info_frame = ctk.CTkFrame(parent, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 10))
        
        total_rows = len(self.layout_data['rows_info'])
        total_tubes = sum(row['tubes_count'] for row in self.layout_data['rows_info'])
        total_balls = sum(row['total_balls'] for row in self.layout_data['rows_info'])
        empty_tubes = self.layout_data['empty_tubes_count']
        
        info_text = f"Rangées: {total_rows} | Éprouvettes avec balles: {total_tubes} | "
        info_text += f"Éprouvettes vides: {empty_tubes} | Total balles: {total_balls}"
        
        ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=12)).pack(pady=15)
    
    def _draw_multi_row_game(self):
        """Draw the complete multi-row game state"""
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        
        grid_cols, grid_rows = self.layout_data['grid_dimensions']
        
        # Calculate section dimensions
        section_width = canvas_width // grid_cols
        section_height = (canvas_height - 200) // grid_rows  # Reserve space for empty tubes
        
        # Draw each row section
        for row_idx, row_data in self.layout_data['layout_grid'].items():
            x_grid = row_data['x']
            y_grid = row_data['y']
            row_info = row_data['row_info']
            
            # Calculate section position
            section_x = x_grid * section_width + self.ROW_SECTION_MARGIN
            section_y = y_grid * section_height + self.ROW_SECTION_MARGIN
            
            self._draw_row_section(section_x, section_y, section_width - (2 * self.ROW_SECTION_MARGIN),
                                 section_height - (2 * self.ROW_SECTION_MARGIN), row_info)
        
        # Draw empty tubes section at bottom
        empty_section_y = grid_rows * section_height + 50
        self._draw_empty_tubes_section(50, empty_section_y, canvas_width - 100, 150)
    
    def _draw_row_section(self, x, y, width, height, row_info):
        """Draw a single row section with its tubes"""
        # Determine section type and color
        section_type = row_info.get('type', 'data')
        if section_type == 'empty':
            border_color = '#FF9800'
            fill_color = '#fff3e0'
            title_color = '#FF9800'
        else:
            border_color = '#2196F3'
            fill_color = 'white'
            title_color = '#2196F3'
        
        # Draw section border
        self.canvas.create_rectangle(x, y, x + width, y + height,
                                   outline=border_color, width=3, fill=fill_color)
        
        # Section title
        title_y = y - 25
        self.canvas.create_text(x + width//2, title_y, text=f"📋 {row_info['name']}",
                              font=('Arial', 12, 'bold'), fill=title_color, anchor='center')
        
        # Calculate tube positions within section
        tubes_count = row_info['tubes_count']
        if tubes_count == 0:
            return
        
        # Distribute tubes evenly in section
        usable_width = width - (2 * self.SECTION_BORDER)
        tube_spacing = min(self.TUBE_SPACING, usable_width // tubes_count)
        start_x = x + self.SECTION_BORDER + (usable_width - (tubes_count - 1) * tube_spacing) // 2
        
        # Draw tubes for this row
        section_type = row_info.get('type', 'data')
        
        for tube_idx in range(tubes_count):
            tube_x = start_x + tube_idx * tube_spacing
            tube_y = y + self.SECTION_BORDER + 30
            
            if section_type == 'empty':
                # Draw empty tube
                self._draw_empty_tube(tube_x, tube_y, tube_idx + 1)
            else:
                # Get colors for this tube from matrices if available
                tube_colors = []
                if 'color_matrix' in row_info and row_info['color_matrix']:
                    color_matrix = row_info['color_matrix']
                    if tube_idx < len(color_matrix):
                        tube_column = color_matrix[tube_idx]
                        for ball_idx, color in enumerate(tube_column):
                            if color is not None:
                                tube_colors.append({
                                    'color': color,
                                    'level_index': ball_idx
                                })
                else:
                    # Fallback to old method
                    colors_list = list(row_info['colors'].items())
                    if tube_idx < len(colors_list):
                        color, balls = colors_list[tube_idx]
                        for ball_idx in range(min(4, len(balls))):
                            tube_colors.append({
                                'color': color,
                                'level_index': ball_idx
                            })
                
                self._draw_tube_in_section(tube_x, tube_y, tube_colors, tube_idx + 1)
    
    def _draw_tube_in_section(self, x, y, balls, tube_number):
        """Draw a single tube within a row section"""
        # Tube container
        tube_top = y
        tube_bottom = tube_top + self.TUBE_HEIGHT
        tube_left = x - (self.TUBE_WIDTH // 2)
        tube_right = x + (self.TUBE_WIDTH // 2)
        
        # Draw tube outline
        self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom,
                                   outline='black', width=2, fill='#f8f8f8')
        
        # Draw tube bottom (rounded)
        self.canvas.create_arc(tube_left, tube_bottom - 15, tube_right, tube_bottom + 15,
                              start=0, extent=180, outline='black', width=2, fill='#f8f8f8')
        
        # Tube label
        self.canvas.create_text(x, tube_top - 15, text=f"T{tube_number}",
                              font=('Arial', 8, 'bold'), fill='black', anchor='center')
        
        # Draw balls
        if balls:
            self._draw_balls_in_section_tube(x, tube_top, tube_bottom, balls)
    
    def _draw_balls_in_section_tube(self, tube_x, tube_top, tube_bottom, balls):
        """Draw balls inside a tube within a section"""
        if not balls:
            return
        
        # Calculate ball positions (from bottom up)
        usable_height = tube_bottom - tube_top - 30
        ball_spacing = min(self.BALL_RADIUS * 2.2, usable_height / 4)  # Max 4 balls
        
        # Start from bottom
        start_y = tube_bottom - 20 - self.BALL_RADIUS
        
        # Reverse balls to show correct order (bottom to top)
        reversed_balls = list(reversed(balls))
        
        for i, ball_data in enumerate(reversed_balls):
            ball_y = start_y - (i * ball_spacing)
            ball_x = tube_x
            
            # Get ball color
            color_rgb = ball_data['color']
            color_hex = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
            
            # Draw ball shadow
            shadow_offset = 1
            self.canvas.create_oval(ball_x - self.BALL_RADIUS + shadow_offset, 
                                  ball_y - self.BALL_RADIUS + shadow_offset,
                                  ball_x + self.BALL_RADIUS + shadow_offset, 
                                  ball_y + self.BALL_RADIUS + shadow_offset,
                                  fill='#cccccc', outline='')
            
            # Draw main ball
            self.canvas.create_oval(ball_x - self.BALL_RADIUS, ball_y - self.BALL_RADIUS,
                                  ball_x + self.BALL_RADIUS, ball_y + self.BALL_RADIUS,
                                  fill=color_hex, outline='black', width=1)
    
    def _draw_empty_tubes_section(self, x, y, width, height):
        """Draw the empty tubes section or include it in the main grid"""
        # Check if empty tubes are already included in the main grid layout
        empty_tubes_in_grid = False
        for row_data in self.layout_data['layout_grid'].values():
            if row_data.get('type') == 'empty':
                empty_tubes_in_grid = True
                break
        
        if empty_tubes_in_grid:
            # Show informational message that empty tubes are included in the grid
            self.canvas.create_text(x + width//2, y + height//2, 
                                  text="🧪 Les éprouvettes vides sont intégrées dans la grille ci-dessus",
                                  font=('Arial', 14, 'bold'), fill='#FF9800', anchor='center')
            return
        
        # Draw section border for standalone empty tubes
        self.canvas.create_rectangle(x, y, x + width, y + height,
                                   outline='#FF9800', width=3, fill='#fff3e0')
        
        # Section title
        title_y = y - 25
        self.canvas.create_text(x + width//2, title_y, text="🧪 Éprouvettes Vides (Espace de Travail)",
                              font=('Arial', 14, 'bold'), fill='#FF9800', anchor='center')
        
        # Draw empty tubes
        empty_count = self.layout_data['empty_tubes_count']
        if empty_count == 0:
            # Show message if no empty tubes
            self.canvas.create_text(x + width//2, y + height//2, 
                                  text="Aucune éprouvette vide configurée",
                                  font=('Arial', 11), fill='gray', anchor='center')
            return
        
        # Calculate tube positions
        usable_width = width - 60
        tube_spacing = min(self.TUBE_SPACING, usable_width // empty_count) if empty_count > 0 else self.TUBE_SPACING
        start_x = x + 30 + (usable_width - (empty_count - 1) * tube_spacing) // 2
        
        for i in range(empty_count):
            tube_x = start_x + i * tube_spacing
            tube_y = y + 30
            
            # Draw empty tube
            self._draw_empty_tube(tube_x, tube_y, i + 1)
    
    def _draw_empty_tube(self, x, y, tube_number):
        """Draw a single empty tube"""
        # Tube container
        tube_top = y
        tube_bottom = tube_top + self.TUBE_HEIGHT
        tube_left = x - (self.TUBE_WIDTH // 2)
        tube_right = x + (self.TUBE_WIDTH // 2)
        
        # Draw tube outline (dashed for empty)
        self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom,
                                   outline='gray', width=2, fill='white', dash=(5, 3))
        
        # Draw tube bottom (rounded)
        self.canvas.create_arc(tube_left, tube_bottom - 15, tube_right, tube_bottom + 15,
                              start=0, extent=180, outline='gray', width=2, fill='white', dash=(5, 3))
        
        # Tube label
        self.canvas.create_text(x, tube_top - 15, text=f"E{tube_number}",
                              font=('Arial', 8, 'bold'), fill='gray', anchor='center')
        
        # Empty indicator
        self.canvas.create_text(x, y + self.TUBE_HEIGHT//2, text="VIDE",
                              font=('Arial', 10, 'bold'), fill='lightgray', anchor='center')
    
    def _solve_multi_row_puzzle(self):
        """Launch the multi-row puzzle solver"""
        try:
            from models.puzzle_solver import MultiRowPuzzleSolver
            from ui.solution_display import MultiRowSolutionDisplay
            
            # Create solver instance with multi-row data
            solver = MultiRowPuzzleSolver(self.layout_data, self.multi_row_data)
            
            # Show solving progress dialog
            progress_window = ctk.CTkToplevel(self.window)
            progress_window.title("🧩 Résolution Multi-Rangées en cours...")
            progress_window.geometry("450x250")
            progress_window.grab_set()
            
            # Progress elements
            progress_label = ctk.CTkLabel(progress_window, text="🔄 Analyse du puzzle multi-rangées...", 
                                        font=ctk.CTkFont(size=14))
            progress_label.pack(pady=20)
            
            status_label = ctk.CTkLabel(progress_window, text="Initialisation de l'algorithme...", 
                                      font=ctk.CTkFont(size=11))
            status_label.pack(pady=10)
            
            progress_bar = ctk.CTkProgressBar(progress_window, width=350)
            progress_bar.pack(pady=20)
            progress_bar.set(0)
            
            # Start solving process
            self.window.after(100, lambda: self._perform_multi_row_solving(solver, progress_window, progress_bar, status_label))
            
        except ImportError:
            # Solver not implemented yet - show placeholder
            self._show_multi_row_solver_placeholder()
    
    def _perform_multi_row_solving(self, solver, progress_window, progress_bar, status_label):
        """Perform the multi-row solving process"""
        try:
            # Initialize progress tracking
            self.solving_progress = 0
            self.solving_statuses = [
                "🔍 Analyse de la structure multi-rangées...",
                "📊 Calcul des états possibles...", 
                "🧮 Application de l'algorithme de résolution...",
                "⚡ Optimisation de la solution...",
                "✨ Finalisation des étapes..."
            ]
            
            # Start progress animation
            self._update_multi_row_progress(solver, progress_window, progress_bar, status_label)
                
        except Exception as e:
            if progress_window.winfo_exists():
                progress_window.destroy()
            self._show_error_message(f"Erreur lors de la résolution multi-rangées: {str(e)}")
    
    def _update_multi_row_progress(self, solver, progress_window, progress_bar, status_label):
        """Update multi-row solving progress animation"""
        try:
            if not progress_window.winfo_exists():
                return
                
            if self.solving_progress < len(self.solving_statuses):
                # Update progress bar and status
                progress_value = (self.solving_progress + 1) / len(self.solving_statuses)
                progress_bar.set(progress_value)
                status_label.configure(text=self.solving_statuses[self.solving_progress])
                
                # Move to next step
                self.solving_progress += 1
                
                # Schedule next update
                self.window.after(800, lambda: self._update_multi_row_progress(solver, progress_window, progress_bar, status_label))
            else:
                # Progress complete
                self.window.after(500, lambda: self._complete_multi_row_solving(solver, progress_window))
                
        except Exception as e:
            if progress_window.winfo_exists():
                progress_window.destroy()
            self._show_error_message(f"Erreur lors de la mise à jour: {str(e)}")
    
    def _complete_multi_row_solving(self, solver, progress_window):
        """Complete the multi-row solving process"""
        try:
            if not progress_window.winfo_exists():
                return
                
            # Get actual solution from multi-row solver
            solution = solver.solve()
            
            progress_window.destroy()
            
            if solution and len(solution) > 0:
                # Show multi-row solution display
                from ui.solution_display import MultiRowSolutionDisplay
                solution_display = MultiRowSolutionDisplay(self.window, solution, self.layout_data, self.multi_row_data)
                solution_display.show_solution()
            else:
                # Show result message
                self._show_multi_row_solution_result(solution)
                
        except Exception as e:
            if progress_window.winfo_exists():
                progress_window.destroy()
            self._show_error_message(f"Erreur lors de la résolution: {str(e)}")
    
    def _show_multi_row_solution_result(self, solution):
        """Show result when multi-row puzzle is solved or no solution exists"""
        result_window = ctk.CTkToplevel(self.window)
        result_window.title("Résultat de la résolution multi-rangées")
        result_window.geometry("550x350")
        result_window.grab_set()
        
        frame = ctk.CTkFrame(result_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        if solution is not None and len(solution) == 0:
            # Puzzle already solved
            ctk.CTkLabel(frame, text="🎉 Puzzle multi-rangées déjà résolu !", 
                        font=ctk.CTkFont(size=18, weight="bold"), 
                        text_color="#4CAF50").pack(pady=20)
            
            message = """Le puzzle multi-rangées est déjà dans un état résolu !
            
✅ Toutes les rangées sont correctement organisées
✅ Les balles de même couleur sont groupées
✅ Aucun mouvement supplémentaire requis"""
            
        else:
            # No solution found
            ctk.CTkLabel(frame, text="❌ Aucune solution trouvée", 
                        font=ctk.CTkFont(size=18, weight="bold"), 
                        text_color="#f44336").pack(pady=20)
            
            message = """Aucune solution n'a pu être trouvée pour ce puzzle multi-rangées.

Causes possibles :
• Configuration impossible à résoudre
• Pas assez d'éprouvettes vides pour les mouvements
• Erreurs dans la détection des couleurs entre rangées
• Complexité trop élevée pour l'algorithme actuel
• Données inconsistantes entre les rangées"""
        
        ctk.CTkLabel(frame, text=message, 
                    font=ctk.CTkFont(size=12), 
                    justify="left").pack(pady=15)
        
        ctk.CTkButton(frame, text="OK", 
                     command=result_window.destroy,
                     fg_color="#2196F3").pack(pady=20)
    
    def _show_multi_row_solver_placeholder(self):
        """Show placeholder message for multi-row solver"""
        placeholder_window = ctk.CTkToplevel(self.window)
        placeholder_window.title("🚧 Solveur Multi-Rangées en développement")
        placeholder_window.geometry("550x350")
        placeholder_window.grab_set()
        
        frame = ctk.CTkFrame(placeholder_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="🚧 Solveur Multi-Rangées", 
                    font=ctk.CTkFont(size=20, weight="bold"), text_color="#FF9800").pack(pady=15)
        
        info_text = """Le système de résolution pour puzzles multi-rangées est en développement.
        
Fonctionnalités avancées prévues :
• 🧮 Algorithme optimisé pour structures complexes
• 🗂️ Gestion intelligente des rangées multiples
• 📊 Analyse de la complexité par section
• 🎯 Solution coordonnée entre rangées
• ⏱️ Optimisation du temps de résolution
• 📈 Statistiques détaillées par rangée
• 🔄 Stratégies de parallélisation
• 💡 Suggestions d'amélioration du layout"""
        
        ctk.CTkLabel(frame, text=info_text, font=ctk.CTkFont(size=11), justify="left").pack(pady=15)
        
        ctk.CTkButton(frame, text="✅ Compris", command=placeholder_window.destroy,
                     fg_color="#2196F3", height=35).pack(pady=15)
    
    def _show_no_solution_message(self):
        """Show message when no solution is found"""
        msg_window = ctk.CTkToplevel(self.window)
        msg_window.title("Aucune solution")
        msg_window.geometry("450x220")
        msg_window.grab_set()
        
        frame = ctk.CTkFrame(msg_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="❌ Aucune solution trouvée", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color="#f44336").pack(pady=20)
        
        ctk.CTkLabel(frame, text="Aucune solution n'a été trouvée pour ce puzzle multi-rangées.", 
                    font=ctk.CTkFont(size=12)).pack(pady=10)
        
        ctk.CTkButton(frame, text="OK", command=msg_window.destroy).pack(pady=20)
    
    def _show_error_message(self, error_msg):
        """Show error message"""
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Erreur")
        error_window.geometry("450x250")
        error_window.grab_set()
        
        frame = ctk.CTkFrame(error_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="❌ Erreur", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color="#f44336").pack(pady=15)
        
        ctk.CTkLabel(frame, text=error_msg, 
                    font=ctk.CTkFont(size=12), 
                    wraplength=350).pack(pady=10)
        
        ctk.CTkButton(frame, text="OK", command=error_window.destroy).pack(pady=20)