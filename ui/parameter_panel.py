"""
Modern parameter panel for ball detection configuration - CustomTkinter
"""
import customtkinter as ctk
from tkinter import ttk

class ParameterPanel:
    def __init__(self, parent):
        self.parent = parent
        self.panel = None
        
        # Callbacks
        self.on_crop_requested = None
        self.on_corners_requested = None
        self.on_generate_grid = None
        self.on_analyze_colors = None
        self.on_start_configuration = None
        self.on_next_row = None
        self.on_previous_row = None
        self.on_finish_all_rows = None
        self.on_single_row_results = None
        
        # Parameters
        self.grid_spacing = 30
        self.color_tolerance = 40
        self.num_tubes = 5
        self.balls_per_tube = 4
        self.num_rows = 1
        
        self.setup_panel()
    
    def setup_panel(self):
        """Setup modern parameter panel UI"""
        # Main panel frame - Using scrollable frame to fit all content
        self.panel = ctk.CTkScrollableFrame(self.parent, corner_radius=15, width=350)
        self.panel.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        # Configure grid
        self.panel.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(self.panel, text="⚙️ Paramètres de Détection", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 15), sticky="ew")
        
        # Track current row for grid layout
        self.current_row = 1
        
        # Step 0: Rows configuration
        self.setup_rows_section()
        
        # Multi-row progress
        self.progress_label = ctk.CTkLabel(self.panel, text="", 
                                         font=ctk.CTkFont(size=14, weight="bold"))
        self.progress_label.grid(row=self.current_row, column=0, pady=10, sticky="ew")
        self.current_row += 1
        
        # Step 1: Crop
        self.setup_crop_section()
        
        # Step 2: Corners
        self.setup_corner_section()
        
        # Step 3: Grid
        self.setup_grid_section()
        
        # Step 4: Analysis
        self.setup_analysis_section()
        
        # Navigation (for multi-row)
        self.setup_navigation_section()
        
        # Status
        self.setup_status_section()
    
    def setup_rows_section(self):
        """Setup modern rows configuration section"""
        frame = ctk.CTkFrame(self.panel, corner_radius=10)
        frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=5)
        self.current_row += 1
        
        # Configure frame grid
        frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        section_title = ctk.CTkLabel(frame, text="🔧 Configuration", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        section_title.grid(row=0, column=0, pady=(15, 10), sticky="ew")
        
        # Number of rows
        rows_frame = ctk.CTkFrame(frame)
        rows_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        rows_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(rows_frame, text="Nombre de rangées:", 
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.rows_var = ctk.IntVar(value=self.num_rows)
        rows_spinbox = ctk.CTkOptionMenu(rows_frame, values=["1", "2", "3", "4", "5"],
                                       command=self.on_rows_change_menu,
                                       variable=self.rows_var)
        rows_spinbox.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        rows_spinbox.set(str(self.num_rows))
        
        # Start button
        self.start_button = ctk.CTkButton(frame, text="🚀 Démarrer Configuration", 
                                        command=self.request_start_configuration,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        height=35,
                                        state="disabled")
        self.start_button.grid(row=2, column=0, pady=15, padx=15, sticky="ew")
    
    def setup_navigation_section(self):
        """Setup modern navigation section for multi-row"""
        self.nav_frame = ctk.CTkFrame(self.panel, corner_radius=10)
        self.nav_frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=10)
        self.nav_frame.grid_remove()  # Hidden by default
        self.current_row += 1
        
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=1)
        self.nav_frame.grid_columnconfigure(2, weight=1)
        
        # Section title
        ctk.CTkLabel(self.nav_frame, text="🧭 Navigation", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=3, pady=(15, 10))
        
        # Navigation buttons frame
        nav_buttons = ctk.CTkFrame(self.nav_frame)
        nav_buttons.grid(row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=(5, 15))
        nav_buttons.grid_columnconfigure(0, weight=1)
        nav_buttons.grid_columnconfigure(1, weight=1)
        nav_buttons.grid_columnconfigure(2, weight=1)
        
        self.prev_button = ctk.CTkButton(nav_buttons, text="← Précédent", 
                                       command=self.request_previous_row,
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       fg_color=("orange", "darkorange"))
        self.prev_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.next_button = ctk.CTkButton(nav_buttons, text="Suivant →", 
                                       command=self.request_next_row,
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       fg_color=("green", "darkgreen"))
        self.next_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        self.finish_button = ctk.CTkButton(nav_buttons, text="🏁 Terminer", 
                                         command=self.request_finish_all_rows,
                                         font=ctk.CTkFont(size=12, weight="bold"),
                                         fg_color=("purple", "darkmagenta"))
        self.finish_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        self.finish_button.grid_remove()  # Hidden initially
        
        # Single row results button
        self.single_results_button = ctk.CTkButton(nav_buttons, text="🎯 Voir Résultats", 
                                                 command=self.request_single_row_results,
                                                 font=ctk.CTkFont(size=12, weight="bold"),
                                                 fg_color=("green", "darkgreen"))
        self.single_results_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        self.single_results_button.grid_remove()  # Hidden initially
    
    def setup_crop_section(self):
        """Setup modern crop section"""
        frame = ctk.CTkFrame(self.panel, corner_radius=10)
        frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=5)
        self.current_row += 1
        
        frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ctk.CTkLabel(frame, text="✂️ 1. Recadrage", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        self.crop_button = ctk.CTkButton(frame, text="📐 Recadrer l'image", 
                                       command=self.request_crop,
                                       font=ctk.CTkFont(size=13, weight="bold"),
                                       height=32,
                                       state="disabled")
        self.crop_button.grid(row=1, column=0, pady=(5, 15), padx=15, sticky="ew")
    
    def setup_corner_section(self):
        """Setup modern corner section"""
        frame = ctk.CTkFrame(self.panel, corner_radius=10)
        frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=5)
        self.current_row += 1
        
        frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ctk.CTkLabel(frame, text="🎯 2. Sélection des Coins", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        self.corners_button = ctk.CTkButton(frame, text="🔘 Sélectionner 4 coins", 
                                          command=self.request_corners,
                                          font=ctk.CTkFont(size=13, weight="bold"),
                                          height=32,
                                          state="disabled")
        self.corners_button.grid(row=1, column=0, pady=5, padx=15, sticky="ew")
        
        self.corners_status = ctk.CTkLabel(frame, text="Coins: 0/4", 
                                         font=ctk.CTkFont(size=12))
        self.corners_status.grid(row=2, column=0, pady=(5, 15))
    
    def setup_grid_section(self):
        """Setup modern grid section"""
        frame = ctk.CTkFrame(self.panel, corner_radius=10)
        frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=5)
        self.current_row += 1
        
        frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ctk.CTkLabel(frame, text="📐 3. Génération de Grille", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        # Tube parameters
        params_frame = ctk.CTkFrame(frame)
        params_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        params_frame.grid_columnconfigure(0, weight=1)
        params_frame.grid_columnconfigure(1, weight=1)
        
        # Tubes
        tubes_frame = ctk.CTkFrame(params_frame)
        tubes_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        tubes_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tubes_frame, text="Nb éprouvettes:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=5, pady=5)
        
        self.tubes_var = ctk.IntVar(value=self.num_tubes)
        tubes_spinbox = ctk.CTkOptionMenu(tubes_frame, values=[str(i) for i in range(2, 11)],
                                        command=self.on_tubes_change_menu,
                                        variable=self.tubes_var)
        tubes_spinbox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        tubes_spinbox.set(str(self.num_tubes))
        
        # Balls
        balls_frame = ctk.CTkFrame(params_frame)
        balls_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        balls_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(balls_frame, text="Balles/éprouvette:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=5, pady=5)
        
        self.balls_var = ctk.IntVar(value=self.balls_per_tube)
        balls_spinbox = ctk.CTkOptionMenu(balls_frame, values=[str(i) for i in range(2, 9)],
                                        command=self.on_balls_change_menu,
                                        variable=self.balls_var)
        balls_spinbox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        balls_spinbox.set(str(self.balls_per_tube))
        
        # Expected total
        self.expected_label = ctk.CTkLabel(frame, text=f"📊 Total attendu: {self.num_tubes * self.balls_per_tube}",
                                         font=ctk.CTkFont(size=12, weight="bold"))
        self.expected_label.grid(row=2, column=0, pady=5)
        
        self.generate_button = ctk.CTkButton(frame, text="⚡ Générer grille", 
                                           command=self.request_generate_grid,
                                           font=ctk.CTkFont(size=13, weight="bold"),
                                           height=32,
                                           state="disabled")
        self.generate_button.grid(row=3, column=0, pady=5, padx=15, sticky="ew")
        
        self.grid_status = ctk.CTkLabel(frame, text="Grille: Non générée", 
                                      font=ctk.CTkFont(size=11))
        self.grid_status.grid(row=4, column=0, pady=(5, 15))
    
    def setup_analysis_section(self):
        """Setup modern analysis section"""
        frame = ctk.CTkFrame(self.panel, corner_radius=10)
        frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=5)
        self.current_row += 1
        
        frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        ctk.CTkLabel(frame, text="🔍 4. Analyse des Couleurs", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        # Tolerance control
        ctk.CTkLabel(frame, text="Tolérance de couleur:", 
                    font=ctk.CTkFont(size=12)).grid(row=1, column=0, pady=(5, 0))
        
        self.tolerance_var = ctk.IntVar(value=self.color_tolerance)
        tolerance_slider = ctk.CTkSlider(frame, from_=20, to=80, number_of_steps=12,
                                       variable=self.tolerance_var, command=self.on_tolerance_change)
        tolerance_slider.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        tolerance_slider.set(self.color_tolerance)
        
        # Tolerance value display
        self.tolerance_label = ctk.CTkLabel(frame, text=f"Valeur: {self.color_tolerance}", 
                                          font=ctk.CTkFont(size=11))
        self.tolerance_label.grid(row=3, column=0, pady=(0, 10))
        
        self.analyze_button = ctk.CTkButton(frame, text="🎨 Analyser couleurs", 
                                          command=self.request_analyze_colors,
                                          font=ctk.CTkFont(size=13, weight="bold"),
                                          height=32,
                                          fg_color=("purple", "darkmagenta"),
                                          state="disabled")
        self.analyze_button.grid(row=4, column=0, pady=(5, 15), padx=15, sticky="ew")
    
    def setup_status_section(self):
        """Setup modern status section"""
        frame = ctk.CTkFrame(self.panel, corner_radius=10)
        frame.grid(row=self.current_row, column=0, sticky="ew", padx=20, pady=5)
        self.current_row += 1
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(frame, text="📝 État du Processus", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        # Status textbox - Reduced height to fit better
        self.status_text = ctk.CTkTextbox(frame, height=80, corner_radius=8,
                                        font=ctk.CTkFont(size=10))
        self.status_text.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        # Clear button
        clear_btn = ctk.CTkButton(frame, text="🗑️ Effacer tout", 
                                command=self.clear_all,
                                font=ctk.CTkFont(size=12, weight="bold"),
                                fg_color=("red", "darkred"),
                                height=28)
        clear_btn.grid(row=2, column=0, pady=15, padx=15, sticky="ew")
    
    def set_callbacks(self, crop_callback, corners_callback, grid_callback, analyze_callback, 
                     start_config_callback=None, next_row_callback=None, 
                     prev_row_callback=None, finish_callback=None, single_results_callback=None):
        """Set callback functions"""
        self.on_crop_requested = crop_callback
        self.on_corners_requested = corners_callback
        self.on_generate_grid = grid_callback
        self.on_analyze_colors = analyze_callback
        self.on_start_configuration = start_config_callback
        self.on_next_row = next_row_callback
        self.on_previous_row = prev_row_callback
        self.on_finish_all_rows = finish_callback
        self.on_single_row_results = single_results_callback
    
    def enable_crop_button(self, enabled=True):
        state = "normal" if enabled else "disabled"
        self.crop_button.configure(state=state)
    
    def enable_corners_button(self, enabled=True):
        state = "normal" if enabled else "disabled"
        self.corners_button.configure(state=state)
    
    def enable_generate_button(self, enabled=True):
        state = "normal" if enabled else "disabled"
        self.generate_button.configure(state=state)
    
    def enable_analyze_button(self, enabled=True):
        state = "normal" if enabled else "disabled"
        self.analyze_button.configure(state=state)
    
    def update_corners_status(self, count):
        self.corners_status.configure(text=f"Coins: {count}/4")
        if count == 4:
            self.enable_generate_button(True)
        else:
            self.enable_generate_button(False)
            self.enable_analyze_button(False)
    
    def update_grid_status(self, grid_count):
        if grid_count > 0:
            self.grid_status.configure(text=f"Grille: {grid_count} cercles")
            self.enable_analyze_button(True)
        else:
            self.grid_status.configure(text="Grille: Erreur")
            self.enable_analyze_button(False)
    
    def add_status_message(self, message):
        current_text = self.status_text.get("0.0", "end")
        self.status_text.delete("0.0", "end")
        self.status_text.insert("0.0", current_text + message + "\n")
    
    def clear_status(self):
        self.status_text.delete("0.0", "end")
    
    def request_crop(self):
        if self.on_crop_requested:
            self.on_crop_requested()
    
    def request_corners(self):
        if self.on_corners_requested:
            self.on_corners_requested()
    
    def request_generate_grid(self):
        if self.on_generate_grid:
            self.on_generate_grid()
    
    def request_analyze_colors(self):
        if self.on_analyze_colors:
            self.on_analyze_colors()
    
    def on_spacing_change(self, value):
        self.grid_spacing = int(value)
    
    def on_tolerance_change(self, value):
        self.color_tolerance = int(float(value))
        # Update tolerance display
        if hasattr(self, 'tolerance_label'):
            self.tolerance_label.configure(text=f"Valeur: {self.color_tolerance}")
    
    def on_tubes_change_menu(self, value):
        """Handle tubes change from option menu"""
        self.num_tubes = int(value)
        self.update_expected_total()
        # Callback to parent to save changes
        if hasattr(self, '_on_tube_params_changed') and self._on_tube_params_changed:
            self._on_tube_params_changed()
    
    def on_balls_change_menu(self, value):
        """Handle balls change from option menu"""
        self.balls_per_tube = int(value)
        self.update_expected_total()
        # Callback to parent to save changes
        if hasattr(self, '_on_tube_params_changed') and self._on_tube_params_changed:
            self._on_tube_params_changed()
    
    def on_tubes_change(self):
        self.num_tubes = self.tubes_var.get()
        self.update_expected_total()
        # Callback to parent to save changes
        if hasattr(self, '_on_tube_params_changed') and self._on_tube_params_changed:
            self._on_tube_params_changed()
    
    def on_balls_change(self):
        self.balls_per_tube = self.balls_var.get()
        self.update_expected_total()
        # Callback to parent to save changes
        if hasattr(self, '_on_tube_params_changed') and self._on_tube_params_changed:
            self._on_tube_params_changed()
    
    def set_tube_params_change_callback(self, callback):
        """Set callback for tube parameter changes"""
        self._on_tube_params_changed = callback
    
    def update_expected_total(self):
        total = self.num_tubes * self.balls_per_tube
        self.expected_label.config(text=f"Total attendu: {total}")
    
    def clear_all(self):
        self.update_corners_status(0)
        self.update_grid_status(0)
        self.clear_status()
        self.enable_corners_button(False)
        self.enable_generate_button(False)
        self.enable_analyze_button(False)
        self.add_status_message("Interface réinitialisée")
    
    def get_grid_spacing(self):
        return self.grid_spacing
    
    def get_color_tolerance(self):
        return self.color_tolerance
    
    def get_tube_parameters(self):
        return self.num_tubes, self.balls_per_tube
    
    def get_num_rows(self):
        return self.num_rows
    
    def on_rows_change(self):
        self.num_rows = self.rows_var.get()
        # Always enable start button when rows are configured
        self.start_button.configure(state="normal")
    
    def on_rows_change_menu(self, value):
        """Handle rows change from option menu"""
        self.num_rows = int(value)
        self.rows_var.set(self.num_rows)
        # Always enable start button when rows are configured
        self.start_button.configure(state="normal")
    
    def request_start_configuration(self):
        if self.on_start_configuration:
            self.on_start_configuration()
    
    def request_next_row(self):
        if self.on_next_row:
            self.on_next_row()
    
    def request_previous_row(self):
        if self.on_previous_row:
            self.on_previous_row()
    
    def request_finish_all_rows(self):
        if self.on_finish_all_rows:
            self.on_finish_all_rows()
    
    def request_single_row_results(self):
        if self.on_single_row_results:
            self.on_single_row_results()
    
    def enable_start_button(self, enabled=True):
        state = "normal" if enabled else "disabled"
        self.start_button.configure(state=state)
    
    def show_navigation(self, show=True):
        if show:
            self.nav_frame.grid()
        else:
            self.nav_frame.grid_remove()
    
    def update_navigation_buttons(self, is_first_row=True, is_last_row=True, can_finish=False, is_single_row=False):
        # Previous button
        if is_first_row:
            self.prev_button.configure(state="disabled")
        else:
            self.prev_button.configure(state="normal")
        
        # Handle single row case differently
        if is_single_row and is_last_row and can_finish:
            # Hide all navigation buttons except single results
            self.next_button.grid_remove()
            self.finish_button.grid_remove()
            self.single_results_button.grid()
            self.single_results_button.configure(state="normal")
        elif is_last_row:
            # Multi-row case: Hide next, show finish
            self.next_button.grid_remove()
            self.single_results_button.grid_remove()
            if can_finish:
                self.finish_button.grid()
                self.finish_button.configure(state="normal")
            else:
                self.finish_button.grid_remove()
        else:
            # Not last row: Hide finish buttons, show next
            self.finish_button.grid_remove()
            self.single_results_button.grid_remove()
            self.next_button.grid()
            self.next_button.configure(state="normal")
    
    def update_progress(self, current_row=1, total_rows=1):
        if total_rows > 1:
            self.progress_label.configure(text=f"🔄 Rangée {current_row}/{total_rows}")
        else:
            self.progress_label.configure(text=f"🔄 Rangée {current_row}/1")
    
    def enable_multi_row_mode(self, enabled=True):
        """Enable or disable multi-row specific controls"""
        if enabled:
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")
            self.show_navigation(False)