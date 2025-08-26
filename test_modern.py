"""
Test the modernized interface
"""
import customtkinter as ctk
import sys
import os

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

try:
    from parameter_panel import ParameterPanel
    print("✅ ParameterPanel imported successfully")
except ImportError as e:
    print(f"❌ Error importing ParameterPanel: {e}")
    sys.exit(1)

class TestApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎯 Test Modern Interface")
        self.root.geometry("1200x800")
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Left area (placeholder)
        left_frame = ctk.CTkFrame(self.root, corner_radius=15)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        ctk.CTkLabel(left_frame, text="🖼️ Image Area", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(expand=True)
        
        # Right: Parameter panel
        try:
            self.parameter_panel = ParameterPanel(self.root)
            print("✅ ParameterPanel created successfully")
            
            # Set dummy callbacks
            self.parameter_panel.set_callbacks(
                lambda: print("Crop requested"),
                lambda: print("Corners requested"),  
                lambda: print("Grid requested"),
                lambda: print("Analyze requested"),
                lambda: print("Start config"),
                lambda: print("Next row"),
                lambda: print("Previous row"),
                lambda: print("Finish all"),
                lambda: print("Single results")
            )
            print("✅ Callbacks set successfully")
            
        except Exception as e:
            print(f"❌ Error creating ParameterPanel: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def run(self):
        print("🚀 Starting modern interface...")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = TestApp()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()