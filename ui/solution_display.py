"""
Solution Display for Ball Sort Puzzle Solver
Shows step-by-step solution visualization
"""
import customtkinter as ctk
from tkinter import Canvas
import time
from typing import List, Optional
from models.puzzle_solver import Move

class SolutionDisplay:
    """Visual step-by-step solution display"""
    
    def __init__(self, parent, solution: List[Move], initial_game_state):
        self.parent = parent
        self.solution = solution
        self.initial_game_state = initial_game_state
        self.window = None
        self.current_step = 0
        self.is_playing = False
        self.play_speed = 1000  # milliseconds between steps
        
        # Visual constants
        self.TUBE_WIDTH = 50
        self.TUBE_HEIGHT = 160
        self.BALL_RADIUS = 18
        self.TUBE_SPACING = 70
        self.TOP_MARGIN = 100
        self.BOTTOM_MARGIN = 150
        self.SIDE_MARGIN = 50
        
        # Animation variables
        self.animation_job = None
        self.current_game_state = None
    
    def show_solution(self):
        """Display the solution window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("🎯 Solution Étape par Étape - Ball Sort Puzzle")
        
        # Calculate window size
        game_dict = self.initial_game_state.to_dict()
        num_tubes = len(game_dict['tubes'])
        
        window_width = max(900, (num_tubes * self.TUBE_SPACING) + (2 * self.SIDE_MARGIN))
        window_height = self.TUBE_HEIGHT + self.TOP_MARGIN + self.BOTTOM_MARGIN + 200
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.grab_set()
        
        # Initialize current state
        self.current_game_state = self._copy_game_state(self.initial_game_state)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title and info
        self._create_header(main_frame)
        
        # Canvas for visualization
        self._create_canvas(main_frame, window_width - 60, self.TUBE_HEIGHT + 120)
        
        # Controls
        self._create_controls(main_frame)
        
        # Draw initial state
        self._draw_current_state()
    
    def _create_header(self, parent):
        """Create header with title and solution info"""
        header_frame = ctk.CTkFrame(parent, corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Title
        title = ctk.CTkLabel(header_frame, text="🎯 Solution Étape par Étape", 
                           font=ctk.CTkFont(size=20, weight="bold"), text_color="#2196F3")
        title.pack(pady=(15, 5))
        
        # Solution info
        if self.solution:
            info_text = f"Solution trouvée en {len(self.solution)} étapes"
            color = "#4CAF50"
        else:
            info_text = "Aucune solution trouvée"
            color = "#f44336"
        
        info_label = ctk.CTkLabel(header_frame, text=info_text, 
                                font=ctk.CTkFont(size=14), text_color=color)
        info_label.pack(pady=(0, 15))
    
    def _create_canvas(self, parent, width, height):
        """Create canvas for game visualization"""
        canvas_frame = ctk.CTkFrame(parent, corner_radius=10)
        canvas_frame.pack(fill="x", pady=(0, 15))
        
        self.canvas = Canvas(canvas_frame, width=width, height=height,
                           bg='white', relief='sunken', bd=2)
        self.canvas.pack(padx=20, pady=20)
    
    def _create_controls(self, parent):
        """Create control panel"""
        control_frame = ctk.CTkFrame(parent, corner_radius=10)
        control_frame.pack(fill="x", pady=(0, 15))
        
        # Step info
        self.step_info_label = ctk.CTkLabel(control_frame, 
                                          text=f"Étape: 0 / {len(self.solution)}", 
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.step_info_label.pack(pady=(15, 10))
        
        # Current move description
        self.move_description_label = ctk.CTkLabel(control_frame, 
                                                 text="État initial - Prêt à commencer", 
                                                 font=ctk.CTkFont(size=12),
                                                 text_color="#666666")
        self.move_description_label.pack(pady=(0, 15))
        
        # Control buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 15))
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        nav_frame.pack(side="left", padx=(0, 20))
        
        self.prev_btn = ctk.CTkButton(nav_frame, text="⏮️ Précédent", 
                                    command=self._previous_step,
                                    width=120, height=35)
        self.prev_btn.pack(side="left", padx=(0, 10))
        
        self.next_btn = ctk.CTkButton(nav_frame, text="Suivant ⏭️", 
                                    command=self._next_step,
                                    width=120, height=35)
        self.next_btn.pack(side="left")
        
        # Playback controls
        play_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        play_frame.pack(side="left", padx=(0, 20))
        
        self.play_btn = ctk.CTkButton(play_frame, text="▶️ Jouer", 
                                    command=self._toggle_play,
                                    fg_color="#4CAF50", hover_color="#45a049",
                                    width=120, height=35)
        self.play_btn.pack(side="left", padx=(0, 10))
        
        self.reset_btn = ctk.CTkButton(play_frame, text="🔄 Reset", 
                                     command=self._reset_solution,
                                     fg_color="#FF9800", hover_color="#f57c00",
                                     width=120, height=35)
        self.reset_btn.pack(side="left")
        
        # Speed control
        speed_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        speed_frame.pack(side="left")
        
        ctk.CTkLabel(speed_frame, text="Vitesse:", font=ctk.CTkFont(size=12)).pack()
        
        self.speed_slider = ctk.CTkSlider(speed_frame, from_=0.2, to=3.0, 
                                        number_of_steps=14,
                                        command=self._update_speed)
        self.speed_slider.set(1.0)
        self.speed_slider.pack()
        
        # Close button
        ctk.CTkButton(control_frame, text="❌ Fermer", 
                     command=self.window.destroy,
                     fg_color="#f44336", hover_color="#da190b",
                     height=35).pack(pady=(0, 15))
        
        # Update button states
        self._update_button_states()
    
    def _draw_current_state(self):
        """Draw the current game state"""
        self.canvas.delete("all")
        
        if not self.current_game_state:
            return
        
        game_dict = self.current_game_state.to_dict()
        tubes = game_dict['tubes']
        
        # Calculate starting position
        total_width = len(tubes) * self.TUBE_SPACING
        start_x = max(self.SIDE_MARGIN, (self.canvas.winfo_reqwidth() - total_width) // 2)
        
        # Draw each tube
        for i, tube_data in enumerate(tubes):
            tube_x = start_x + (i * self.TUBE_SPACING)
            self._draw_tube(tube_x, tube_data, i)
        
        # Highlight move if showing a step
        if self.current_step > 0 and self.current_step <= len(self.solution):
            move = self.solution[self.current_step - 1]
            self._highlight_move(move)
    
    def _draw_tube(self, x, tube_data, tube_index):
        """Draw a single tube with balls"""
        # Tube outline
        tube_top = self.TOP_MARGIN
        tube_bottom = tube_top + self.TUBE_HEIGHT
        tube_left = x - (self.TUBE_WIDTH // 2)
        tube_right = x + (self.TUBE_WIDTH // 2)
        
        self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom,
                                   outline='black', width=2, fill='#f8f8f8')
        
        # Tube bottom
        self.canvas.create_arc(tube_left, tube_bottom - 15, tube_right, tube_bottom + 15,
                              start=0, extent=180, outline='black', width=2, fill='#f8f8f8')
        
        # Tube label
        self.canvas.create_text(x, tube_top - 25, text=f"Tube {tube_index + 1}",
                              font=('Arial', 10, 'bold'), fill='black')
        
        # Draw balls
        if tube_data['balls']:
            self._draw_balls_in_tube(x, tube_top, tube_bottom, tube_data['balls'])
    
    def _draw_balls_in_tube(self, tube_x, tube_top, tube_bottom, balls):
        """Draw balls inside a tube"""
        usable_height = tube_bottom - tube_top - 40
        ball_spacing = min(self.BALL_RADIUS * 2.2, usable_height / 4)
        
        start_y = tube_bottom - 25 - self.BALL_RADIUS
        
        # Reverse balls for correct visual order
        reversed_balls = list(reversed(balls))
        
        for i, ball_data in enumerate(reversed_balls):
            ball_y = start_y - (i * ball_spacing)
            ball_x = tube_x
            
            color_rgb = ball_data['color']
            color_hex = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
            
            # Shadow
            self.canvas.create_oval(ball_x - self.BALL_RADIUS + 2, 
                                  ball_y - self.BALL_RADIUS + 2,
                                  ball_x + self.BALL_RADIUS + 2, 
                                  ball_y + self.BALL_RADIUS + 2,
                                  fill='#cccccc', outline='')
            
            # Ball
            self.canvas.create_oval(ball_x - self.BALL_RADIUS, ball_y - self.BALL_RADIUS,
                                  ball_x + self.BALL_RADIUS, ball_y + self.BALL_RADIUS,
                                  fill=color_hex, outline='black', width=2)
    
    def _highlight_move(self, move: Move):
        """Highlight the tubes involved in current move"""
        try:
            game_dict = self.current_game_state.to_dict()
            tubes = game_dict['tubes']
            
            # Calculate tube positions
            total_width = len(tubes) * self.TUBE_SPACING
            start_x = max(self.SIDE_MARGIN, (self.canvas.winfo_reqwidth() - total_width) // 2)
            
            # Highlight source tube (from)
            from_tube_x = start_x + (move.from_tube * self.TUBE_SPACING)
            self._draw_tube_highlight(from_tube_x, "#FF5722", "Source")
            
            # Highlight destination tube (to)
            to_tube_x = start_x + (move.to_tube * self.TUBE_SPACING)
            self._draw_tube_highlight(to_tube_x, "#4CAF50", "Destination")
            
        except Exception as e:
            print(f"Error highlighting move: {e}")
    
    def _draw_tube_highlight(self, tube_x, color, label):
        """Draw highlight around a tube"""
        tube_top = self.TOP_MARGIN - 10
        tube_bottom = tube_top + self.TUBE_HEIGHT + 20
        tube_left = tube_x - (self.TUBE_WIDTH // 2) - 5
        tube_right = tube_x + (self.TUBE_WIDTH // 2) + 5
        
        # Draw highlight rectangle
        self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom,
                                   outline=color, width=3, fill='', dash=(5, 5),
                                   tags="highlight")
        
        # Add label
        self.canvas.create_text(tube_x, tube_top - 15, text=label,
                              font=('Arial', 9, 'bold'), fill=color, 
                              anchor='center', tags="highlight")
    
    def _previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._apply_step_backwards()
            self._update_display()
    
    def _next_step(self):
        """Go to next step"""
        if self.current_step < len(self.solution):
            self._apply_step_forward()
            self.current_step += 1
            self._update_display()
    
    def _apply_step_forward(self):
        """Apply current step forward"""
        if self.current_step < len(self.solution):
            move = self.solution[self.current_step]
            print(f"DEBUG: Applying forward step {self.current_step}: {move.description}")
            # Apply move to current_game_state
            self._apply_move_to_game_state(move.from_tube, move.to_tube)
    
    def _apply_step_backwards(self):
        """Apply current step backward"""
        if self.current_step > 0:
            move = self.solution[self.current_step - 1]
            print(f"DEBUG: Applying backward step {self.current_step}: reverse of {move.description}")
            # Reverse the move on current_game_state
            self._reverse_move_on_game_state(move.from_tube, move.to_tube, move.balls_count)
    
    def _apply_move_to_game_state(self, from_tube_idx, to_tube_idx):
        """Apply a move to the current game state (with multiple balls support)"""
        try:
            # Get the move info for ball count
            move = None
            if hasattr(self, 'current_step') and self.current_step > 0 and self.current_step <= len(self.solution):
                move = self.solution[self.current_step - 1]
            
            # Work directly with game state objects
            from_tube = self.current_game_state.get_tube(from_tube_idx)
            to_tube = self.current_game_state.get_tube(to_tube_idx)
            
            if from_tube and to_tube and len(from_tube.balls) > 0:
                # Get consecutive balls of same color from top
                balls_to_move = self._get_consecutive_top_balls_from_tube(from_tube)
                
                # Limit by available space in destination
                available_space = to_tube.get_available_space()
                balls_to_move = balls_to_move[:available_space]
                
                # Move all balls
                balls_moved = []
                for _ in range(len(balls_to_move)):
                    if from_tube.balls:
                        ball = from_tube.balls.pop()  # Remove from top
                        ball.tube_index = to_tube_idx
                        ball.level_index = len(to_tube.balls)
                        to_tube.balls.append(ball)  # Add to destination
                        balls_moved.append(ball)
                
                print(f"DEBUG: Moved {len(balls_moved)} balls from tube {from_tube_idx} to tube {to_tube_idx}")
                print(f"DEBUG: From tube now has {len(from_tube.balls)} balls")
                print(f"DEBUG: To tube now has {len(to_tube.balls)} balls")
                
        except Exception as e:
            print(f"Error applying move: {e}")
    
    def _get_consecutive_top_balls_from_tube(self, tube):
        """Get consecutive balls of same color from the top of a tube object"""
        if not tube.balls:
            return []
        
        # Get top ball color
        top_ball = tube.balls[-1]
        top_color = top_ball.color
        
        consecutive_balls = []
        
        # Go from top to bottom, collecting same-colored balls
        for i in range(len(tube.balls) - 1, -1, -1):
            ball_color = tube.balls[i].color
            if ball_color == top_color:
                consecutive_balls.append(tube.balls[i])
            else:
                break
        
        return consecutive_balls
    
    def _reverse_move_on_game_state(self, original_from_tube_idx, original_to_tube_idx, balls_count):
        """Reverse a move on the current game state"""
        try:
            # Reverse move: move balls back from destination to source
            dest_tube = self.current_game_state.get_tube(original_to_tube_idx)
            source_tube = self.current_game_state.get_tube(original_from_tube_idx)
            
            if dest_tube and source_tube and len(dest_tube.balls) > 0:
                # Move the specified number of balls back
                balls_moved = []
                for _ in range(min(balls_count, len(dest_tube.balls))):
                    ball = dest_tube.balls.pop()  # Remove from destination
                    ball.tube_index = original_from_tube_idx
                    ball.level_index = len(source_tube.balls)
                    source_tube.balls.append(ball)  # Add back to source
                    balls_moved.append(ball)
                
                print(f"DEBUG: Reversed {len(balls_moved)} balls from tube {original_to_tube_idx} back to tube {original_from_tube_idx}")
                
        except Exception as e:
            print(f"Error reversing move: {e}")
    
    def _toggle_play(self):
        """Toggle automatic playback"""
        if self.is_playing:
            self._stop_play()
        else:
            self._start_play()
    
    def _start_play(self):
        """Start automatic playback"""
        self.is_playing = True
        self.play_btn.configure(text="⏸️ Pause")
        self._auto_play()
    
    def _stop_play(self):
        """Stop automatic playback"""
        self.is_playing = False
        self.play_btn.configure(text="▶️ Jouer")
        if self.animation_job:
            self.window.after_cancel(self.animation_job)
    
    def _auto_play(self):
        """Automatic playback loop"""
        if self.is_playing and self.current_step < len(self.solution):
            self._next_step()
            self.animation_job = self.window.after(self.play_speed, self._auto_play)
        else:
            self._stop_play()
    
    def _reset_solution(self):
        """Reset to initial state"""
        self._stop_play()
        self.current_step = 0
        self.current_game_state = self._copy_game_state(self.initial_game_state)
        self._update_display()
    
    def _update_speed(self, value):
        """Update playback speed"""
        # Convert slider value to milliseconds (inverted)
        self.play_speed = int(2000 / float(value))
    
    def _update_display(self):
        """Update all display elements"""
        self._draw_current_state()
        self._update_step_info()
        self._update_button_states()
    
    def _update_step_info(self):
        """Update step information display"""
        self.step_info_label.configure(text=f"Étape: {self.current_step} / {len(self.solution)}")
        
        if self.current_step == 0:
            self.move_description_label.configure(text="État initial - Prêt à commencer")
        elif self.current_step <= len(self.solution):
            move = self.solution[self.current_step - 1]
            self.move_description_label.configure(text=move.description)
    
    def _update_button_states(self):
        """Update button enabled/disabled states"""
        self.prev_btn.configure(state="normal" if self.current_step > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_step < len(self.solution) else "disabled")
    
    def _copy_game_state(self, game_state):
        """Create a copy of game state"""
        import copy
        return copy.deepcopy(game_state)
    

class MultiRowSolutionDisplay:
    """Solution display for multi-row puzzles"""
    
    def __init__(self, parent, solution: List[Move], layout_data, multi_row_data):
        self.parent = parent
        self.solution = solution
        self.layout_data = layout_data
        self.multi_row_data = multi_row_data
    
    def show_solution(self):
        """Show multi-row solution"""
        # Create a specialized multi-row solution display
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder for multi-row solution display"""
        window = ctk.CTkToplevel(self.parent)
        window.title("🎯 Solution Multi-Rangées")
        window.geometry("600x400")
        window.grab_set()
        
        frame = ctk.CTkFrame(window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="🎯 Solution Multi-Rangées", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color="#4CAF50").pack(pady=20)
        
        if self.solution:
            info_text = f"Solution trouvée avec {len(self.solution)} étapes pour le puzzle multi-rangées."
        else:
            info_text = "Aucune solution trouvée pour ce puzzle multi-rangées."
        
        ctk.CTkLabel(frame, text=info_text, font=ctk.CTkFont(size=14)).pack(pady=20)
        
        # Features info
        features_text = """Fonctionnalités de visualisation avancées en développement :
• Affichage coordonné des rangées multiples
• Animation synchronisée des mouvements
• Vue d'ensemble et vues détaillées
• Statistiques par rangée
• Optimisation des déplacements inter-rangées"""
        
        ctk.CTkLabel(frame, text=features_text, font=ctk.CTkFont(size=11), 
                    justify="left").pack(pady=20)
        
        ctk.CTkButton(frame, text="✅ Compris", command=window.destroy,
                     fg_color="#2196F3", height=35).pack(pady=20)