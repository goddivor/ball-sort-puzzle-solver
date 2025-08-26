"""
Ball Sort Puzzle Solver - CustomTkinter Modern Preview
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys
import os

# Configure CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class ModernPreview:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎯 Ball Sort Puzzle Solver - Modern Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        self.photo = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup modern UI"""
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=3)  # Image area
        self.root.grid_columnconfigure(1, weight=1)  # Parameters panel
        self.root.grid_rowconfigure(0, weight=1)
        
        # Left: Image area
        self.setup_image_area()
        
        # Right: Parameters
        self.setup_parameter_panel()
    
    def setup_image_area(self):
        """Setup modern image area"""
        container = ctk.CTkFrame(self.root, corner_radius=15)
        container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Configure grid
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)  # Image frame gets most space
        
        # Title
        title = ctk.CTkLabel(container, text="🎯 Ball Sort Puzzle Solver", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        
        # Upload button
        upload_btn = ctk.CTkButton(container, 
                                 text="📁 Charger Image", 
                                 command=self.upload_image,
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 height=45,
                                 corner_radius=10)
        upload_btn.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        
        # Image display frame
        self.image_frame = ctk.CTkFrame(container, corner_radius=10)
        self.image_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configure image frame
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)
        
        # Default image placeholder
        placeholder = ctk.CTkLabel(self.image_frame, 
                                 text="📷 Aucune image chargée\n\nCliquez sur 'Charger Image' pour commencer", 
                                 font=ctk.CTkFont(size=16),
                                 text_color=("gray60", "gray40"))
        placeholder.grid(row=0, column=0, sticky="nsew")
        
        # Results frame
        self.results_frame = ctk.CTkScrollableFrame(container, height=150, corner_radius=10)
        self.results_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Demo results
        ctk.CTkLabel(self.results_frame, text="📊 Résultats d'analyse apparaîtront ici", 
                    font=ctk.CTkFont(size=12)).pack(pady=10)
    
    def setup_parameter_panel(self):
        """Setup modern parameter panel"""
        panel = ctk.CTkFrame(self.root, corner_radius=15, width=350)
        panel.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        panel.grid_propagate(False)
        
        # Configure grid
        panel.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(panel, text="⚙️ Paramètres de Détection", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 15), sticky="ew")
        
        # Configuration Section
        config_frame = ctk.CTkFrame(panel, corner_radius=10)
        config_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        config_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(config_frame, text="🔧 Configuration", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        # Number of rows
        rows_frame = ctk.CTkFrame(config_frame)
        rows_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        rows_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(rows_frame, text="Nombre de rangées:", 
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        rows_menu = ctk.CTkOptionMenu(rows_frame, values=["1", "2", "3", "4", "5"])
        rows_menu.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        rows_menu.set("1")
        
        # Start button
        start_btn = ctk.CTkButton(config_frame, text="🚀 Démarrer Configuration", 
                                font=ctk.CTkFont(size=14, weight="bold"),
                                height=35)
        start_btn.grid(row=2, column=0, pady=15, padx=15, sticky="ew")
        
        # Progress indicator
        progress = ctk.CTkLabel(panel, text="🔄 Rangée 1/1", 
                              font=ctk.CTkFont(size=14, weight="bold"))
        progress.grid(row=2, column=0, pady=10)
        
        # Crop Section
        crop_frame = ctk.CTkFrame(panel, corner_radius=10)
        crop_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        crop_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(crop_frame, text="✂️ 1. Recadrage", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        crop_btn = ctk.CTkButton(crop_frame, text="📐 Recadrer l'image", 
                               font=ctk.CTkFont(size=13, weight="bold"),
                               height=32)
        crop_btn.grid(row=1, column=0, pady=(5, 15), padx=15, sticky="ew")
        
        # Corners Section
        corners_frame = ctk.CTkFrame(panel, corner_radius=10)
        corners_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        corners_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(corners_frame, text="🎯 2. Sélection des Coins", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        corners_btn = ctk.CTkButton(corners_frame, text="🔘 Sélectionner 4 coins", 
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  height=32)
        corners_btn.grid(row=1, column=0, pady=(5, 15), padx=15, sticky="ew")
        
        # Grid Section
        grid_frame = ctk.CTkFrame(panel, corner_radius=10)
        grid_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(grid_frame, text="📐 3. Génération de Grille", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        grid_btn = ctk.CTkButton(grid_frame, text="⚡ Générer grille", 
                               font=ctk.CTkFont(size=13, weight="bold"),
                               height=32)
        grid_btn.grid(row=1, column=0, pady=(5, 15), padx=15, sticky="ew")
        
        # Analysis Section
        analysis_frame = ctk.CTkFrame(panel, corner_radius=10)
        analysis_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(analysis_frame, text="🔍 4. Analyse des Couleurs", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        # Tolerance slider
        ctk.CTkLabel(analysis_frame, text="Tolérance:", 
                    font=ctk.CTkFont(size=12)).grid(row=1, column=0, pady=5)
        
        tolerance_slider = ctk.CTkSlider(analysis_frame, from_=20, to=80, number_of_steps=12)
        tolerance_slider.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        tolerance_slider.set(40)
        
        analyze_btn = ctk.CTkButton(analysis_frame, text="🎨 Analyser couleurs", 
                                  font=ctk.CTkFont(size=13, weight="bold"),
                                  height=32)
        analyze_btn.grid(row=3, column=0, pady=(10, 15), padx=15, sticky="ew")
        
        # Results Button
        results_btn = ctk.CTkButton(panel, text="🏆 Voir Résultats", 
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  height=40,
                                  fg_color=("green", "darkgreen"))
        results_btn.grid(row=7, column=0, pady=20, padx=20, sticky="ew")
        
        # Status Section
        status_frame = ctk.CTkFrame(panel, corner_radius=10)
        status_frame.grid(row=8, column=0, sticky="ew", padx=20, pady=(10, 20))
        status_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(status_frame, text="📝 État du Processus", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(15, 10))
        
        status_text = ctk.CTkTextbox(status_frame, height=100, corner_radius=8)
        status_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        status_text.insert("0.0", "🚀 Interface modernisée avec CustomTkinter\\n✨ Design sombre professionnel\\n⚡ Prêt pour la détection de balles\\n🎯 Tous les outils disponibles")
        status_text.configure(state="disabled")
    
    def upload_image(self):
        """Demo upload image"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                # Load and display image
                image = Image.open(file_path)
                image.thumbnail((600, 400))  # Resize for display
                self.photo = ImageTk.PhotoImage(image)
                
                # Clear previous image
                for widget in self.image_frame.winfo_children():
                    widget.destroy()
                
                # Display new image
                label = ctk.CTkLabel(self.image_frame, image=self.photo, text="")
                label.grid(row=0, column=0, sticky="nsew")
                
                # Update results
                for widget in self.results_frame.winfo_children():
                    widget.destroy()
                
                ctk.CTkLabel(self.results_frame, text="✅ Image chargée avec succès!", 
                           font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
                ctk.CTkLabel(self.results_frame, text="🎯 Prêt pour la configuration", 
                           font=ctk.CTkFont(size=12)).pack(pady=2)
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")
    
    def run(self):
        """Run the modern preview"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ModernPreview()
        app.run()
    except Exception as e:
        print(f"Erreur: {e}")