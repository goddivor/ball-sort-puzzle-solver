"""
Multi-Row Layout Dialog for Ball Sort Puzzle Solver
Allows user to configure the layout and empty tubes for multi-row puzzles
"""
import customtkinter as ctk
from tkinter import messagebox, Canvas
import math

class MultiRowLayoutDialog:
    """Dialog for configuring multi-row puzzle layout"""
    
    def __init__(self, parent, callback, multi_row_data):
        self.parent = parent
        self.callback = callback
        self.multi_row_data = multi_row_data
        self.dialog = None
        
        # Extract row information
        self.rows_info = self._analyze_multi_row_data()
        self.empty_tubes_count = 2  # Default
        self.layout_grid = {}  # {row_number: {'x': grid_x, 'y': grid_y}}
        
        # Layout configuration
        self.grid_cols = 2  # Default 2x2 grid
        self.grid_rows = 2
        self._initialize_default_layout()
    
    def _analyze_multi_row_data(self):
        """Analyze multi-row data to extract info about each row"""
        rows_info = []
        
        if 'colors_by_row' in self.multi_row_data:
            # Group by row
            rows_data = {}
            for color_key, balls in self.multi_row_data['colors_by_row'].items():
                row_info, color_str = color_key.split('_', 1)
                if row_info not in rows_data:
                    rows_data[row_info] = {'colors': {}, 'total_balls': 0}
                
                try:
                    if isinstance(color_str, str) and color_str.startswith('('):
                        color = eval(color_str)
                    elif isinstance(color_str, tuple):
                        color = color_str
                    else:
                        color = (128, 128, 128)
                except:
                    color = (128, 128, 128)
                
                rows_data[row_info]['colors'][color] = balls
                rows_data[row_info]['total_balls'] += len(balls)
            
            # Convert to list format
            for row_name, data in rows_data.items():
                # Estimate tubes count (this might need adjustment based on your tube parameter logic)
                estimated_tubes = max(1, len(data['colors']))  # Rough estimate
                
                rows_info.append({
                    'name': row_name,
                    'tubes_count': estimated_tubes,
                    'total_balls': data['total_balls'],
                    'colors': data['colors']
                })
        
        return rows_info
    
    def _initialize_default_layout(self):
        """Initialize default 2x2 layout"""
        positions = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Grid positions (x, y)
        
        for i, row_info in enumerate(self.rows_info):
            if i < len(positions):
                self.layout_grid[i] = {
                    'x': positions[i][0], 
                    'y': positions[i][1],
                    'row_info': row_info
                }
    
    def show_dialog(self):
        """Show the multi-row layout configuration dialog"""
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the dialog window"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Configuration Multi-Rangées")
        self.dialog.geometry("900x700")
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        self.dialog.minsize(800, 600)
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="🎮 Configuration Multi-Rangées", 
                           font=ctk.CTkFont(size=20, weight="bold"), text_color="#2196F3")
        title.pack(pady=(10, 20))
        
        # Create left and right sections
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left: Row information
        self._create_row_info_section(content_frame)
        
        # Right: Layout configuration
        self._create_layout_section(content_frame)
        
        # Empty tubes configuration
        self._create_empty_tubes_section(main_frame)
        
        # Buttons
        self._create_buttons_section(main_frame)
    
    def _create_row_info_section(self, parent):
        """Create section showing information about each row"""
        left_frame = ctk.CTkFrame(parent)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_frame, text="📊 Informations des Rangées",
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        # Scrollable frame for rows
        rows_scroll = ctk.CTkScrollableFrame(left_frame, height=300)
        rows_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        for i, row_info in enumerate(self.rows_info):
            row_frame = ctk.CTkFrame(rows_scroll, corner_radius=8)
            row_frame.pack(fill="x", pady=5, padx=5)
            
            # Row header
            header_frame = ctk.CTkFrame(row_frame)
            header_frame.pack(fill="x", padx=10, pady=10)
            
            row_name = ctk.CTkLabel(header_frame, text=f"📋 {row_info['name']}",
                                  font=ctk.CTkFont(size=12, weight="bold"))
            row_name.pack(side="left")
            
            stats_text = f"{row_info['tubes_count']} tubes • {row_info['total_balls']} balles"
            stats_label = ctk.CTkLabel(header_frame, text=stats_text,
                                     font=ctk.CTkFont(size=10), text_color="gray60")
            stats_label.pack(side="right")
            
            # Colors preview
            if row_info['colors']:
                colors_frame = ctk.CTkFrame(row_frame)
                colors_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                ctk.CTkLabel(colors_frame, text="Couleurs:",
                           font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=5, pady=5)
                
                # Show first few colors
                color_display_frame = ctk.CTkFrame(colors_frame)
                color_display_frame.pack(fill="x", padx=5, pady=(0, 5))
                
                for j, (color, balls) in enumerate(list(row_info['colors'].items())[:4]):
                    color_sample = ctk.CTkCanvas(color_display_frame, width=20, height=20)
                    color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                    color_sample.create_rectangle(0, 0, 20, 20, fill=color_hex, outline="black")
                    color_sample.pack(side="left", padx=2, pady=2)
                
                if len(row_info['colors']) > 4:
                    ctk.CTkLabel(color_display_frame, text=f"... +{len(row_info['colors']) - 4}",
                               font=ctk.CTkFont(size=9)).pack(side="left", padx=5)
    
    def _create_layout_section(self, parent):
        """Create section for layout configuration"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(right_frame, text="📐 Disposition des Rangées",
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        # Layout canvas
        self.layout_canvas = Canvas(right_frame, width=300, height=300, bg='white',
                                   relief='sunken', bd=2)
        self.layout_canvas.pack(padx=10, pady=10)
        
        # Bind click events for layout modification
        self.layout_canvas.bind("<Button-1>", self._on_layout_click)
        
        # Layout controls
        controls_frame = ctk.CTkFrame(right_frame)
        controls_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(controls_frame, text="Configuration de la grille:",
                   font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(10, 5))
        
        # Grid size controls
        grid_frame = ctk.CTkFrame(controls_frame)
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(grid_frame, text="Colonnes:").pack(side="left")
        self.cols_var = ctk.IntVar(value=self.grid_cols)
        cols_spinbox = self._create_spinbox(grid_frame, self.cols_var, 1, 4, self._update_layout)
        cols_spinbox.pack(side="left", padx=(5, 15))
        
        ctk.CTkLabel(grid_frame, text="Lignes:").pack(side="left")
        self.rows_var = ctk.IntVar(value=self.grid_rows)
        rows_spinbox = self._create_spinbox(grid_frame, self.rows_var, 1, 4, self._update_layout)
        rows_spinbox.pack(side="left", padx=(5, 0))
        
        # Draw initial layout
        self._draw_layout()
    
    def _create_spinbox(self, parent, variable, min_val, max_val, callback):
        """Create a custom spinbox"""
        frame = ctk.CTkFrame(parent)
        
        minus_btn = ctk.CTkButton(frame, text="-", width=25, height=25,
                                 command=lambda: self._spinbox_change(variable, -1, min_val, max_val, callback))
        minus_btn.pack(side="left")
        
        label = ctk.CTkLabel(frame, text=str(variable.get()), width=30)
        label.pack(side="left", padx=5)
        
        plus_btn = ctk.CTkButton(frame, text="+", width=25, height=25,
                                command=lambda: self._spinbox_change(variable, 1, min_val, max_val, callback))
        plus_btn.pack(side="left")
        
        # Store label reference for updates
        frame.label = label
        return frame
    
    def _spinbox_change(self, variable, change, min_val, max_val, callback):
        """Handle spinbox value change"""
        current = variable.get()
        new_value = max(min_val, min(max_val, current + change))
        variable.set(new_value)
        
        # Update display
        for child in variable.master.winfo_children():
            if hasattr(child, 'label'):
                child.label.configure(text=str(new_value))
                break
        
        callback()
    
    def _update_layout(self):
        """Update layout when grid size changes"""
        self.grid_cols = self.cols_var.get()
        self.grid_rows = self.rows_var.get()
        self._redistribute_rows()
        self._draw_layout()
    
    def _redistribute_rows(self):
        """Redistribute rows in new grid"""
        positions = []
        for y in range(self.grid_rows):
            for x in range(self.grid_cols):
                positions.append((x, y))
        
        # Reassign positions
        for i, (row_idx, row_data) in enumerate(self.layout_grid.items()):
            if i < len(positions):
                self.layout_grid[row_idx]['x'] = positions[i][0]
                self.layout_grid[row_idx]['y'] = positions[i][1]
    
    def _draw_layout(self):
        """Draw the layout on canvas"""
        self.layout_canvas.delete("all")
        
        # Calculate cell dimensions
        canvas_width = self.layout_canvas.winfo_width() or 300
        canvas_height = self.layout_canvas.winfo_height() or 300
        
        cell_width = (canvas_width - 40) // self.grid_cols
        cell_height = (canvas_height - 40) // self.grid_rows
        
        # Draw grid
        for x in range(self.grid_cols + 1):
            x_pos = 20 + x * cell_width
            self.layout_canvas.create_line(x_pos, 20, x_pos, canvas_height - 20, fill="gray", width=1)
        
        for y in range(self.grid_rows + 1):
            y_pos = 20 + y * cell_height
            self.layout_canvas.create_line(20, y_pos, canvas_width - 20, y_pos, fill="gray", width=1)
        
        # Draw row positions
        for row_idx, row_data in self.layout_grid.items():
            x = row_data['x']
            y = row_data['y']
            
            if x < self.grid_cols and y < self.grid_rows:
                # Calculate cell position
                cell_x = 20 + x * cell_width
                cell_y = 20 + y * cell_height
                
                # Draw row rectangle
                self.layout_canvas.create_rectangle(
                    cell_x + 5, cell_y + 5, cell_x + cell_width - 5, cell_y + cell_height - 5,
                    fill="#e3f2fd", outline="#2196F3", width=2
                )
                
                # Draw row info
                row_info = row_data['row_info']
                text_x = cell_x + cell_width // 2
                text_y = cell_y + cell_height // 2
                
                self.layout_canvas.create_text(text_x, text_y - 10, text=row_info['name'],
                                             font=('Arial', 10, 'bold'), fill='black')
                self.layout_canvas.create_text(text_x, text_y + 10, 
                                             text=f"{row_info['tubes_count']} tubes",
                                             font=('Arial', 8), fill='gray')
    
    def _on_layout_click(self, event):
        """Handle click on layout canvas to move rows"""
        # Calculate which cell was clicked
        canvas_width = self.layout_canvas.winfo_width()
        canvas_height = self.layout_canvas.winfo_height()
        
        cell_width = (canvas_width - 40) // self.grid_cols
        cell_height = (canvas_height - 40) // self.grid_rows
        
        clicked_x = max(0, min(self.grid_cols - 1, (event.x - 20) // cell_width))
        clicked_y = max(0, min(self.grid_rows - 1, (event.y - 20) // cell_height))
        
        # For now, simple rotation through positions (could be made more sophisticated)
        self._rotate_rows_at_position(clicked_x, clicked_y)
        self._draw_layout()
    
    def _rotate_rows_at_position(self, clicked_x, clicked_y):
        """Rotate rows at clicked position"""
        # Find if any row is at this position
        row_at_position = None
        for row_idx, row_data in self.layout_grid.items():
            if row_data['x'] == clicked_x and row_data['y'] == clicked_y:
                row_at_position = row_idx
                break
        
        if row_at_position is not None:
            # Move this row to next available position
            all_positions = [(x, y) for x in range(self.grid_cols) for y in range(self.grid_rows)]
            used_positions = [(data['x'], data['y']) for data in self.layout_grid.values()]
            
            # Find next position in cycle
            current_pos = (clicked_x, clicked_y)
            current_index = all_positions.index(current_pos)
            next_index = (current_index + 1) % len(all_positions)
            next_pos = all_positions[next_index]
            
            # If next position is occupied, swap
            occupant = None
            for row_idx, row_data in self.layout_grid.items():
                if row_data['x'] == next_pos[0] and row_data['y'] == next_pos[1]:
                    occupant = row_idx
                    break
            
            if occupant:
                # Swap positions
                self.layout_grid[occupant]['x'] = current_pos[0]
                self.layout_grid[occupant]['y'] = current_pos[1]
            
            self.layout_grid[row_at_position]['x'] = next_pos[0]
            self.layout_grid[row_at_position]['y'] = next_pos[1]
    
    def _create_empty_tubes_section(self, parent):
        """Create section for empty tubes configuration"""
        empty_frame = ctk.CTkFrame(parent, corner_radius=10)
        empty_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(empty_frame, text="🧪 Éprouvettes Vides (Rangée Séparée)",
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        explanation = """Les éprouvettes vides seront regroupées dans une rangée séparée.
Elles servent d'espace de travail pour résoudre le puzzle."""
        
        ctk.CTkLabel(empty_frame, text=explanation, font=ctk.CTkFont(size=11),
                   text_color="gray60", wraplength=600).pack(padx=20, pady=(0, 10))
        
        # Empty tubes input
        input_frame = ctk.CTkFrame(empty_frame)
        input_frame.pack(padx=20, pady=(0, 15))
        
        ctk.CTkLabel(input_frame, text="Nombre d'éprouvettes vides:",
                   font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 10), pady=15)
        
        self.empty_tubes_var = ctk.IntVar(value=self.empty_tubes_count)
        empty_spinbox = self._create_spinbox(input_frame, self.empty_tubes_var, 0, 10, 
                                           lambda: setattr(self, 'empty_tubes_count', self.empty_tubes_var.get()))
        empty_spinbox.pack(side="left", padx=(0, 15), pady=15)
    
    def _create_buttons_section(self, parent):
        """Create buttons section"""
        buttons_frame = ctk.CTkFrame(parent, corner_radius=10)
        buttons_frame.pack(fill="x")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(buttons_frame, text="❌ Annuler",
                                  command=self._cancel,
                                  fg_color="#f44336", hover_color="#da190b",
                                  font=ctk.CTkFont(size=12, weight="bold"),
                                  height=40, width=120)
        cancel_btn.pack(side="left", padx=15, pady=15)
        
        # Generate button
        generate_btn = ctk.CTkButton(buttons_frame, text="🎮 Générer Modèle Multi-Rangées",
                                   command=self._generate,
                                   fg_color="#4CAF50", hover_color="#45a049",
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   height=40, width=200)
        generate_btn.pack(side="right", padx=15, pady=15)
    
    def _cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()
    
    def _generate(self):
        """Generate the multi-row model"""
        if self.empty_tubes_count < 1:
            messagebox.showwarning("Attention", 
                                 "Au moins 1 éprouvette vide est recommandée.")
        
        # Prepare result data
        result = {
            'rows_info': self.rows_info,
            'layout_grid': self.layout_grid,
            'empty_tubes_count': self.empty_tubes_count,
            'grid_dimensions': (self.grid_cols, self.grid_rows)
        }
        
        self.dialog.destroy()
        
        # Call the callback with results
        if self.callback:
            self.callback(result)