"""
Game Generator Dialog for Ball Sort Puzzle Solver
Dialog to collect additional information needed for game modeling
"""
import customtkinter as ctk
from tkinter import messagebox

class GameGeneratorDialog:
    """Dialog to collect information for game model generation"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.dialog = None
        self.result = None
        
        # Variables
        self.empty_tubes_var = None
        self.confirm_generation = False
    
    def show_dialog(self, detected_tubes, total_balls, balls_per_tube):
        """
        Show the dialog to collect game generation parameters
        
        Args:
            detected_tubes: Number of tubes detected with balls
            total_balls: Total number of balls detected
            balls_per_tube: Balls per tube capacity
        """
        self.detected_tubes = detected_tubes
        self.total_balls = total_balls
        self.balls_per_tube = balls_per_tube
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the dialog window"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Génération du Modèle de Jeu")
        self.dialog.geometry("500x500")
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        
        # Main container - don't expand to leave room for buttons
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        
        # Title
        title = ctk.CTkLabel(main_frame, 
                           text="🎮 Génération du Modèle de Jeu", 
                           font=ctk.CTkFont(size=20, weight="bold"),
                           text_color="#2196F3")
        title.pack(pady=(10, 20))
        
        # Information section
        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(info_frame, 
                    text="📊 Informations détectées",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        # Detected info
        info_text = f"""• Éprouvettes avec balles: {self.detected_tubes}
• Total balles détectées: {self.total_balls}
• Capacité par éprouvette: {self.balls_per_tube} balles"""
        
        ctk.CTkLabel(info_frame, 
                    text=info_text,
                    font=ctk.CTkFont(size=12),
                    justify="left").pack(padx=20, pady=(0, 15))
        
        # Empty tubes section
        empty_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        empty_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(empty_frame,
                    text="🧪 Configuration des éprouvettes vides",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        # Explanation
        explanation = """Les éprouvettes vides sont cruciales pour résoudre le puzzle.
Elles servent d'espace temporaire pour déplacer les balles."""
        
        ctk.CTkLabel(empty_frame,
                    text=explanation,
                    font=ctk.CTkFont(size=11),
                    text_color="gray60",
                    wraplength=400).pack(padx=20, pady=(0, 10))
        
        # Input section
        input_frame = ctk.CTkFrame(empty_frame, corner_radius=8)
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Empty tubes input
        tubes_frame = ctk.CTkFrame(input_frame)
        tubes_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(tubes_frame,
                    text="Nombre d'éprouvettes vides:",
                    font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        
        self.empty_tubes_var = ctk.IntVar(value=2)  # Default to 2 empty tubes
        
        empty_tubes_spinbox = ctk.CTkFrame(tubes_frame)
        empty_tubes_spinbox.pack(side="right", padx=(10, 0))
        
        # Create custom spinbox
        minus_btn = ctk.CTkButton(empty_tubes_spinbox, 
                                 text="-", 
                                 width=30, 
                                 height=30,
                                 command=self._decrease_empty_tubes)
        minus_btn.pack(side="left")
        
        self.empty_tubes_label = ctk.CTkLabel(empty_tubes_spinbox,
                                            text=str(self.empty_tubes_var.get()),
                                            width=50,
                                            font=ctk.CTkFont(size=14, weight="bold"))
        self.empty_tubes_label.pack(side="left", padx=10)
        
        plus_btn = ctk.CTkButton(empty_tubes_spinbox,
                               text="+",
                               width=30,
                               height=30,
                               command=self._increase_empty_tubes)
        plus_btn.pack(side="left")
        
        # Summary section
        summary_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(summary_frame,
                    text="📋 Résumé de la génération",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        self.summary_label = ctk.CTkLabel(summary_frame,
                                        text=self._get_summary_text(),
                                        font=ctk.CTkFont(size=12),
                                        justify="left")
        self.summary_label.pack(padx=20, pady=(0, 15))
        
        # Buttons section - separate from main content
        buttons_container = ctk.CTkFrame(self.dialog, fg_color="transparent")
        buttons_container.pack(side="bottom", fill="x", padx=20, pady=(0, 20))
        
        # Buttons frame
        button_frame = ctk.CTkFrame(buttons_container, corner_radius=10)
        button_frame.pack(fill="x")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame,
                                  text="❌ Annuler",
                                  command=self._cancel,
                                  fg_color="#f44336",
                                  hover_color="#da190b",
                                  font=ctk.CTkFont(size=12, weight="bold"),
                                  height=40,
                                  width=120)
        cancel_btn.pack(side="left", padx=15, pady=15)
        
        # Generate button
        generate_btn = ctk.CTkButton(button_frame,
                                   text="🎮 Générer le Modèle",
                                   command=self._generate,
                                   fg_color="#4CAF50",
                                   hover_color="#45a049",
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   height=40,
                                   width=160)
        generate_btn.pack(side="right", padx=15, pady=15)
    
    def _decrease_empty_tubes(self):
        """Decrease empty tubes count"""
        current = self.empty_tubes_var.get()
        if current > 0:
            self.empty_tubes_var.set(current - 1)
            self._update_display()
    
    def _increase_empty_tubes(self):
        """Increase empty tubes count"""
        current = self.empty_tubes_var.get()
        if current < 10:  # Reasonable maximum
            self.empty_tubes_var.set(current + 1)
            self._update_display()
    
    def _update_display(self):
        """Update the display with current values"""
        self.empty_tubes_label.configure(text=str(self.empty_tubes_var.get()))
        self.summary_label.configure(text=self._get_summary_text())
    
    def _get_summary_text(self):
        """Get summary text for current configuration"""
        empty_tubes = self.empty_tubes_var.get()
        total_tubes = self.detected_tubes + empty_tubes
        
        summary = f"""• Éprouvettes avec balles: {self.detected_tubes}
• Éprouvettes vides: {empty_tubes}
• Total éprouvettes: {total_tubes}
• Total balles: {self.total_balls}"""
        
        return summary
    
    def _cancel(self):
        """Cancel the dialog"""
        self.confirm_generation = False
        self.dialog.destroy()
    
    def _generate(self):
        """Confirm generation and close dialog"""
        empty_tubes = self.empty_tubes_var.get()
        
        if empty_tubes < 1:
            messagebox.showwarning("Attention", 
                                 "Au moins 1 éprouvette vide est recommandée pour résoudre le puzzle.")
        
        self.result = {
            'empty_tubes_count': empty_tubes,
            'detected_tubes': self.detected_tubes,
            'total_tubes': self.detected_tubes + empty_tubes,
            'total_balls': self.total_balls,
            'balls_per_tube': self.balls_per_tube
        }
        
        self.confirm_generation = True
        self.dialog.destroy()
        
        # Call the callback with results
        if self.callback:
            self.callback(self.result)