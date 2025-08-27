"""
Visual Game Display for Ball Sort Puzzle Solver
Creates a graphical representation of the game state with tubes and colored balls
"""
import customtkinter as ctk
from tkinter import Canvas
import math

class GameVisualDisplay:
    """Visual representation of the game state"""
    
    def __init__(self, parent, game_state):
        self.parent = parent
        self.game_state = game_state
        self.window = None
        
        # Display constants
        self.TUBE_WIDTH = 60
        self.TUBE_HEIGHT = 200
        self.BALL_RADIUS = 20
        self.TUBE_SPACING = 80
        self.TOP_MARGIN = 80
        self.BOTTOM_MARGIN = 100
        self.SIDE_MARGIN = 50
        
    def show_visual_display(self):
        """Create and show the visual game display"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("🎮 Modèle Visuel du Jeu - Ball Sort Puzzle")
        
        # Calculate window size based on number of tubes
        game_dict = self.game_state.to_dict()
        num_tubes = len(game_dict['tubes'])
        
        window_width = max(800, (num_tubes * self.TUBE_SPACING) + (2 * self.SIDE_MARGIN))
        window_height = self.TUBE_HEIGHT + self.TOP_MARGIN + self.BOTTOM_MARGIN + 150
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.grab_set()
        
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="🎮 Modèle Visuel du Jeu", 
                           font=ctk.CTkFont(size=24, weight="bold"), text_color="#2196F3")
        title.pack(pady=(10, 20))
        
        # Game info
        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_text = f"Total éprouvettes: {game_dict['total_tubes']} | "
        info_text += f"Éprouvettes avec balles: {game_dict['tubes_with_balls']} | "
        info_text += f"Éprouvettes vides: {game_dict['empty_tubes']} | "
        info_text += f"Total balles: {game_dict['total_balls']}"
        
        ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=12)).pack(pady=15)
        
        # Canvas for drawing the game
        canvas_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        canvas_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create canvas
        canvas_width = window_width - 80
        canvas_height = self.TUBE_HEIGHT + 100
        
        self.canvas = Canvas(canvas_frame, 
                           width=canvas_width, 
                           height=canvas_height,
                           bg='white',
                           relief='sunken',
                           bd=2)
        self.canvas.pack(padx=20, pady=20)
        
        # Draw the game
        self._draw_game_state(game_dict)
        
        # Close button
        close_frame = ctk.CTkFrame(main_frame)
        close_frame.pack()
        
        ctk.CTkButton(close_frame, text="❌ Fermer", command=self.window.destroy,
                     fg_color="#f44336", hover_color="#da190b",
                     font=ctk.CTkFont(size=12, weight="bold"), height=35).pack(pady=10)
    
    def _draw_game_state(self, game_dict):
        """Draw the complete game state on canvas"""
        tubes = game_dict['tubes']
        
        # Calculate starting position to center tubes
        total_width = len(tubes) * self.TUBE_SPACING
        start_x = max(self.SIDE_MARGIN, (self.canvas.winfo_reqwidth() - total_width) // 2)
        
        for i, tube_data in enumerate(tubes):
            tube_x = start_x + (i * self.TUBE_SPACING)
            self._draw_tube(tube_x, tube_data)
    
    def _draw_tube(self, x, tube_data):
        """Draw a single tube with its balls"""
        # Tube container (test tube shape)
        tube_top = self.TOP_MARGIN
        tube_bottom = tube_top + self.TUBE_HEIGHT
        tube_left = x - (self.TUBE_WIDTH // 2)
        tube_right = x + (self.TUBE_WIDTH // 2)
        
        # Draw tube outline
        self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom,
                                   outline='black', width=3, fill='#f8f8f8')
        
        # Draw tube bottom (rounded)
        self.canvas.create_arc(tube_left, tube_bottom - 20, tube_right, tube_bottom + 20,
                              start=0, extent=180, outline='black', width=3, fill='#f8f8f8')
        
        # Tube label
        tube_title = f"Tube {tube_data['index'] + 1}"
        if tube_data['is_empty']:
            tube_title += "\n(Vide)"
            label_color = "#999999"
        elif tube_data['is_complete']:
            tube_title += "\n✅ Complète"
            label_color = "#4CAF50"
        elif tube_data['is_pure']:
            tube_title += "\n🔸 Pure"
            label_color = "#2196F3"
        else:
            label_color = "#333333"
        
        self.canvas.create_text(x, tube_top - 30, text=tube_title, 
                              font=('Arial', 10, 'bold'), fill=label_color, anchor='center')
        
        # Draw balls in tube
        if tube_data['balls']:
            self._draw_balls_in_tube(x, tube_top, tube_bottom, tube_data['balls'], tube_data['capacity'])
    
    def _draw_balls_in_tube(self, tube_x, tube_top, tube_bottom, balls, capacity):
        """Draw balls inside a tube"""
        # Calculate ball positions
        usable_height = (tube_bottom - tube_top) - 40  # Leave some margin
        ball_spacing = min(self.BALL_RADIUS * 2.2, usable_height / max(1, capacity))
        
        # Start from bottom of tube
        start_y = tube_bottom - 30 - self.BALL_RADIUS
        
        # Reverse the balls list to show correct order (bottom to top)
        reversed_balls = list(reversed(balls))
        
        for i, ball_data in enumerate(reversed_balls):
            # Calculate ball position (from bottom up)
            ball_y = start_y - (i * ball_spacing)
            ball_x = tube_x
            
            # Get ball color
            color_rgb = ball_data['color']
            color_hex = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
            
            # Draw ball shadow for depth
            shadow_offset = 2
            self.canvas.create_oval(ball_x - self.BALL_RADIUS + shadow_offset, 
                                  ball_y - self.BALL_RADIUS + shadow_offset,
                                  ball_x + self.BALL_RADIUS + shadow_offset, 
                                  ball_y + self.BALL_RADIUS + shadow_offset,
                                  fill='#cccccc', outline='')
            
            # Draw main ball (solid color, no highlight)
            self.canvas.create_oval(ball_x - self.BALL_RADIUS, ball_y - self.BALL_RADIUS,
                                  ball_x + self.BALL_RADIUS, ball_y + self.BALL_RADIUS,
                                  fill=color_hex, outline='black', width=2)
            
            # Ball level indicator (small text) - show visual level (bottom = 1, top = max)
            visual_level = len(balls) - i  # Since we reversed the list, adjust the level display
            level_text = f"N{visual_level}"
            self.canvas.create_text(ball_x + self.BALL_RADIUS + 15, ball_y,
                                  text=level_text, font=('Arial', 8), fill='#666666')
    
    def _get_text_color_for_background(self, bg_color_rgb):
        """Get appropriate text color (black or white) for a background color"""
        r, g, b = bg_color_rgb
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return 'white' if luminance < 0.5 else 'black'