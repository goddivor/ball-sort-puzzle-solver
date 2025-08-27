"""
Game modeling system for Ball Sort Puzzle Solver
Handles the reconstruction of the game state from analyzed data
"""

class Ball:
    """Represents a single ball with its properties"""
    def __init__(self, color, position, tube_index, level_index):
        self.color = color  # RGB tuple
        self.position = position  # (x, y) coordinates from original image
        self.tube_index = tube_index  # Which tube (0-based)
        self.level_index = level_index  # Position in tube (0 = bottom)
        self.color_name = self._generate_color_name()
    
    def _generate_color_name(self):
        """Generate a readable name for the color"""
        # Simple color naming based on RGB dominance
        r, g, b = self.color
        if r > g and r > b:
            if r > 200:
                return "Rouge vif"
            elif r > 150:
                return "Rouge"
            else:
                return "Rouge sombre"
        elif g > r and g > b:
            if g > 200:
                return "Vert vif"
            elif g > 150:
                return "Vert"
            else:
                return "Vert sombre"
        elif b > r and b > g:
            if b > 200:
                return "Bleu vif"
            elif b > 150:
                return "Bleu"
            else:
                return "Bleu sombre"
        else:
            # Mixed colors
            if r > 150 and g > 150:
                return "Jaune"
            elif r > 150 and b > 150:
                return "Magenta"
            elif g > 150 and b > 150:
                return "Cyan"
            else:
                return "Gris"
    
    def to_dict(self):
        """Convert ball to dictionary for serialization"""
        return {
            'color': self.color,
            'color_name': self.color_name,
            'position': self.position,
            'tube_index': self.tube_index,
            'level_index': self.level_index
        }

class Tube:
    """Represents a test tube containing balls"""
    def __init__(self, index, capacity, is_empty=False):
        self.index = index
        self.capacity = capacity
        self.balls = []
        self.is_empty = is_empty
    
    def add_ball(self, ball):
        """Add a ball to the tube"""
        if len(self.balls) < self.capacity:
            ball.tube_index = self.index
            ball.level_index = len(self.balls)
            self.balls.append(ball)
            return True
        return False
    
    def get_ball_count(self):
        """Get number of balls in tube"""
        return len(self.balls)
    
    def is_complete(self):
        """Check if tube is completely filled with same color"""
        if not self.balls or len(self.balls) != self.capacity:
            return False
        first_color = self.balls[0].color
        return all(ball.color == first_color for ball in self.balls)
    
    def is_pure(self):
        """Check if all balls in tube are same color (but not necessarily full)"""
        if not self.balls:
            return True
        first_color = self.balls[0].color
        return all(ball.color == first_color for ball in self.balls)
    
    def get_top_ball(self):
        """Get the top ball (last added)"""
        return self.balls[-1] if self.balls else None
    
    def get_available_space(self):
        """Get number of free slots in tube"""
        return self.capacity - len(self.balls)
    
    def to_dict(self):
        """Convert tube to dictionary for serialization"""
        return {
            'index': self.index,
            'capacity': self.capacity,
            'is_empty': self.is_empty,
            'ball_count': self.get_ball_count(),
            'balls': [ball.to_dict() for ball in self.balls],
            'is_complete': self.is_complete(),
            'is_pure': self.is_pure(),
            'available_space': self.get_available_space()
        }

class GameState:
    """Represents the complete game state"""
    def __init__(self, tubes_with_balls, empty_tubes, balls_per_tube):
        self.tubes_with_balls = tubes_with_balls
        self.empty_tubes = empty_tubes
        self.balls_per_tube = balls_per_tube
        self.total_tubes = tubes_with_balls + empty_tubes
        self.tubes = []
        self.total_balls = 0
        self.color_stats = {}
        
    def add_tube(self, tube):
        """Add a tube to the game state"""
        self.tubes.append(tube)
    
    def get_tube(self, index):
        """Get tube by index"""
        return self.tubes[index] if 0 <= index < len(self.tubes) else None
    
    def get_total_balls(self):
        """Get total number of balls in game"""
        return sum(tube.get_ball_count() for tube in self.tubes)
    
    def get_color_statistics(self):
        """Get statistics about colors in the game"""
        color_counts = {}
        for tube in self.tubes:
            for ball in tube.balls:
                color = ball.color
                if color not in color_counts:
                    color_counts[color] = {
                        'count': 0,
                        'color_name': ball.color_name,
                        'positions': [],
                        'tubes': set()
                    }
                color_counts[color]['count'] += 1
                color_counts[color]['positions'].append(ball.position)
                color_counts[color]['tubes'].add(ball.tube_index)
        
        # Convert sets to lists for serialization
        for color_data in color_counts.values():
            color_data['tubes'] = list(color_data['tubes'])
        
        return color_counts
    
    def get_completion_status(self):
        """Get game completion analysis"""
        complete_tubes = sum(1 for tube in self.tubes if tube.is_complete())
        pure_tubes = sum(1 for tube in self.tubes if tube.is_pure())
        empty_tubes = sum(1 for tube in self.tubes if tube.get_ball_count() == 0)
        
        return {
            'complete_tubes': complete_tubes,
            'pure_tubes': pure_tubes,
            'empty_tubes': empty_tubes,
            'total_tubes': len(self.tubes),
            'completion_percentage': (complete_tubes / max(1, len(self.tubes) - empty_tubes)) * 100
        }
    
    def to_dict(self):
        """Convert game state to dictionary for serialization"""
        return {
            'tubes_with_balls': self.tubes_with_balls,
            'empty_tubes': self.empty_tubes,
            'balls_per_tube': self.balls_per_tube,
            'total_tubes': self.total_tubes,
            'total_balls': self.get_total_balls(),
            'tubes': [tube.to_dict() for tube in self.tubes],
            'color_statistics': self.get_color_statistics(),
            'completion_status': self.get_completion_status()
        }

class GameModelGenerator:
    """Generates game model from analysis results"""
    
    @staticmethod
    def create_game_state(analysis_results, empty_tubes_count, balls_per_tube):
        """
        Create a complete game state from analysis results
        
        Args:
            analysis_results: Results from color analysis (single or multi-row)
            empty_tubes_count: Number of empty tubes in the game
            balls_per_tube: Maximum balls per tube
        
        Returns:
            GameState object representing the complete game
        """
        # Determine if single or multi-row results
        if 'colors_by_row' in analysis_results:
            return GameModelGenerator._create_from_multi_row(
                analysis_results, empty_tubes_count, balls_per_tube
            )
        else:
            return GameModelGenerator._create_from_single_row(
                analysis_results, empty_tubes_count, balls_per_tube
            )
    
    @staticmethod
    def _create_from_single_row(results, empty_tubes_count, balls_per_tube):
        """Create game state from single row results"""
        # Count tubes with balls from the results
        if 'colors' in results:
            color_groups = results['colors']
            tubes_with_balls = results.get('num_tubes', 0)
        else:
            color_groups = results
            tubes_with_balls = len(set(
                ball.get('tube_index', 0) 
                for balls in color_groups.values() 
                for ball in balls
            ))
        
        game_state = GameState(tubes_with_balls, empty_tubes_count, balls_per_tube)
        
        # Create tubes with balls
        for i in range(tubes_with_balls):
            tube = Tube(i, balls_per_tube, is_empty=False)
            game_state.add_tube(tube)
        
        # Create empty tubes
        for i in range(empty_tubes_count):
            tube = Tube(tubes_with_balls + i, balls_per_tube, is_empty=True)
            game_state.add_tube(tube)
        
        # Add balls to tubes
        GameModelGenerator._populate_tubes_from_colors(game_state, color_groups)
        
        return game_state
    
    @staticmethod
    def _create_from_multi_row(results, empty_tubes_count, balls_per_tube):
        """Create game state from multi-row results"""
        # Aggregate all colors from all rows
        all_colors = {}
        tubes_with_balls = 0
        
        if 'colors_by_row' in results:
            for color_key, balls in results['colors_by_row'].items():
                row_info, color_str = color_key.split('_', 1)
                try:
                    color = eval(color_str) if color_str.startswith('(') else (128, 128, 128)
                    if color not in all_colors:
                        all_colors[color] = []
                    all_colors[color].extend(balls)
                except:
                    continue
            
            tubes_with_balls = results.get('total_tubes', 0)
        
        game_state = GameState(tubes_with_balls, empty_tubes_count, balls_per_tube)
        
        # Create all tubes
        for i in range(tubes_with_balls + empty_tubes_count):
            is_empty = i >= tubes_with_balls
            tube = Tube(i, balls_per_tube, is_empty=is_empty)
            game_state.add_tube(tube)
        
        # Populate tubes
        GameModelGenerator._populate_tubes_from_colors(game_state, all_colors)
        
        return game_state
    
    @staticmethod
    def _populate_tubes_from_colors(game_state, color_groups):
        """Populate tubes with balls based on color groups"""
        for color, balls in color_groups.items():
            for ball_data in balls:
                # Extract position and tube information
                position = (ball_data.get('x', 0), ball_data.get('y', 0))
                tube_index = ball_data.get('tube_idx', 0)
                
                # Create ball
                ball = Ball(color, position, tube_index, 0)
                
                # Add to appropriate tube
                if tube_index < len(game_state.tubes):
                    tube = game_state.tubes[tube_index]
                    tube.add_ball(ball)