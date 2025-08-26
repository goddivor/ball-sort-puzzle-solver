"""
Simplified parameter panel for ball detection configuration
"""
import tkinter as tk
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
        
        # Parameters
        self.grid_spacing = 30
        self.color_tolerance = 40
        self.num_tubes = 5
        self.balls_per_tube = 4
        
        self.setup_panel()
    
    def setup_panel(self):
        """Setup parameter panel UI"""
        # Main panel frame
        self.panel = tk.Frame(self.parent, bg="#f0f0f0", width=280)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.panel.pack_propagate(False)
        
        # Title
        title = tk.Label(self.panel, text="Paramètres de Détection", 
                        font=("Arial", 14, "bold"), bg="#f0f0f0")
        title.pack(pady=10)
        
        # Step 1: Crop
        self.setup_crop_section()
        
        # Step 2: Corners
        self.setup_corner_section()
        
        # Step 3: Grid
        self.setup_grid_section()
        
        # Step 4: Analysis
        self.setup_analysis_section()
        
        # Status
        self.setup_status_section()
    
    def setup_crop_section(self):
        """Setup crop section"""
        frame = tk.LabelFrame(self.panel, text="1. Recadrage", bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.crop_button = tk.Button(frame, text="Recadrer l'image", 
                                    command=self.request_crop,
                                    bg="#2196F3", fg="white")
        self.crop_button.pack(pady=5)
        self.crop_button.config(state=tk.DISABLED)
    
    def setup_corner_section(self):
        """Setup corner section"""
        frame = tk.LabelFrame(self.panel, text="2. Coins", bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.corners_button = tk.Button(frame, text="Sélectionner coins", 
                                       command=self.request_corners,
                                       bg="#FF9800", fg="white")
        self.corners_button.pack(pady=5)
        self.corners_button.config(state=tk.DISABLED)
        
        self.corners_status = tk.Label(frame, text="Coins: 0/4", bg="#f0f0f0")
        self.corners_status.pack()
    
    def setup_grid_section(self):
        """Setup grid section"""
        frame = tk.LabelFrame(self.panel, text="3. Grille", bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tube parameters
        tubes_frame = tk.Frame(frame, bg="#f0f0f0")
        tubes_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(tubes_frame, text="Nb éprouvettes:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.tubes_var = tk.IntVar(value=self.num_tubes)
        tubes_spinbox = tk.Spinbox(tubes_frame, from_=2, to=10, width=5,
                                  textvariable=self.tubes_var, command=self.on_tubes_change)
        tubes_spinbox.pack(side=tk.RIGHT)
        
        balls_frame = tk.Frame(frame, bg="#f0f0f0")
        balls_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(balls_frame, text="Balles/éprouvette:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.balls_var = tk.IntVar(value=self.balls_per_tube)
        balls_spinbox = tk.Spinbox(balls_frame, from_=2, to=8, width=5,
                                  textvariable=self.balls_var, command=self.on_balls_change)
        balls_spinbox.pack(side=tk.RIGHT)
        
        # Expected total
        self.expected_label = tk.Label(frame, text=f"Total attendu: {self.num_tubes * self.balls_per_tube}",
                                      bg="#f0f0f0", font=("Arial", 9, "italic"))
        self.expected_label.pack(pady=2)
        
        self.generate_button = tk.Button(frame, text="Générer grille", 
                                        command=self.request_generate_grid,
                                        bg="#4CAF50", fg="white")
        self.generate_button.pack(pady=5)
        self.generate_button.config(state=tk.DISABLED)
        
        self.grid_status = tk.Label(frame, text="Grille: Non générée", bg="#f0f0f0")
        self.grid_status.pack()
    
    def setup_analysis_section(self):
        """Setup analysis section"""
        frame = tk.LabelFrame(self.panel, text="4. Analyse", bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame, text="Tolérance:", bg="#f0f0f0").pack()
        self.tolerance_var = tk.IntVar(value=self.color_tolerance)
        tolerance_scale = tk.Scale(frame, from_=20, to=80, orient=tk.HORIZONTAL,
                                  variable=self.tolerance_var, command=self.on_tolerance_change,
                                  bg="#f0f0f0")
        tolerance_scale.pack(fill=tk.X)
        
        self.analyze_button = tk.Button(frame, text="Analyser couleurs", 
                                       command=self.request_analyze_colors,
                                       bg="#9C27B0", fg="white")
        self.analyze_button.pack(pady=5)
        self.analyze_button.config(state=tk.DISABLED)
    
    def setup_status_section(self):
        """Setup status section"""
        frame = tk.LabelFrame(self.panel, text="État", bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = tk.Text(frame, height=6, width=30, font=("Arial", 9),
                                  state=tk.DISABLED, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(frame, text="Effacer tout", command=self.clear_all,
                 bg="#f44336", fg="white").pack()
    
    def set_callbacks(self, crop_callback, corners_callback, grid_callback, analyze_callback):
        """Set callback functions"""
        self.on_crop_requested = crop_callback
        self.on_corners_requested = corners_callback
        self.on_generate_grid = grid_callback
        self.on_analyze_colors = analyze_callback
    
    def enable_crop_button(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.crop_button.config(state=state)
    
    def enable_corners_button(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.corners_button.config(state=state)
    
    def enable_generate_button(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.generate_button.config(state=state)
    
    def enable_analyze_button(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.analyze_button.config(state=state)
    
    def update_corners_status(self, count):
        self.corners_status.config(text=f"Coins: {count}/4")
        if count == 4:
            self.enable_generate_button(True)
        else:
            self.enable_generate_button(False)
            self.enable_analyze_button(False)
    
    def update_grid_status(self, grid_count):
        if grid_count > 0:
            self.grid_status.config(text=f"Grille: {grid_count} cercles")
            self.enable_analyze_button(True)
        else:
            self.grid_status.config(text="Grille: Erreur")
            self.enable_analyze_button(False)
    
    def add_status_message(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def clear_status(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
    
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
        self.color_tolerance = int(value)
    
    def on_tubes_change(self):
        self.num_tubes = self.tubes_var.get()
        self.update_expected_total()
    
    def on_balls_change(self):
        self.balls_per_tube = self.balls_var.get()
        self.update_expected_total()
    
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