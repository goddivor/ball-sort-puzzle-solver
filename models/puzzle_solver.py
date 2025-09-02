"""
Ball Sort Puzzle Solver
Implements advanced algorithms to solve Ball Sort puzzles optimally
"""
import time
from collections import deque
from typing import List, Dict, Tuple, Optional, Set
import copy

class GameState:
    """Represents a state of the Ball Sort puzzle"""
    
    def __init__(self, tubes: List[List[Tuple[int, int, int]]], max_balls_per_tube: int = 4):
        self.tubes = [tube.copy() for tube in tubes]  # Deep copy
        self.max_balls_per_tube = max_balls_per_tube
    
    def __hash__(self):
        """Make GameState hashable for use in sets"""
        return hash(tuple(tuple(tube) for tube in self.tubes))
    
    def __eq__(self, other):
        """Check equality for GameState"""
        if not isinstance(other, GameState):
            return False
        return self.tubes == other.tubes
    
    def is_solved(self) -> bool:
        """Check if the puzzle is solved"""
        for tube in self.tubes:
            if len(tube) == 0:  # Empty tube is valid
                continue
            if len(tube) != self.max_balls_per_tube:  # Tube must be full
                return False
            # All balls in tube must be same color
            first_color = tube[0]
            if not all(ball == first_color for ball in tube):
                return False
        return True
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves from current state"""
        moves = []
        
        for from_tube in range(len(self.tubes)):
            if len(self.tubes[from_tube]) == 0:  # Empty source tube
                continue
            
            top_ball = self.tubes[from_tube][-1]  # Top ball
            
            for to_tube in range(len(self.tubes)):
                if from_tube == to_tube:  # Same tube
                    continue
                
                # Check if move is valid
                if self._is_valid_move(from_tube, to_tube):
                    moves.append((from_tube, to_tube))
        
        return moves
    
    def _is_valid_move(self, from_tube: int, to_tube: int) -> bool:
        """Check if a move from one tube to another is valid"""
        if len(self.tubes[from_tube]) == 0:  # Source tube empty
            return False
        
        if len(self.tubes[to_tube]) >= self.max_balls_per_tube:  # Destination full
            return False
        
        # If destination is empty, move is always valid
        if len(self.tubes[to_tube]) == 0:
            return True
        
        # Check if colors match
        source_color = self.tubes[from_tube][-1]
        dest_color = self.tubes[to_tube][-1]
        
        return source_color == dest_color
    
    def make_move(self, from_tube: int, to_tube: int) -> 'GameState':
        """Create a new game state after making a move"""
        new_state = GameState(self.tubes, self.max_balls_per_tube)
        
        if self._is_valid_move(from_tube, to_tube):
            ball = new_state.tubes[from_tube].pop()
            new_state.tubes[to_tube].append(ball)
        
        return new_state
    
    def get_heuristic_score(self) -> float:
        """Calculate heuristic score for A* algorithm"""
        score = 0
        
        for tube in self.tubes:
            if len(tube) == 0:  # Empty tube bonus
                score += 10
                continue
            
            # Check color consistency in tube
            colors_count = {}
            for ball in tube:
                colors_count[ball] = colors_count.get(ball, 0) + 1
            
            # Penalty for mixed colors
            if len(colors_count) > 1:
                score -= len(colors_count) * 5
            
            # Bonus for complete tubes
            if len(colors_count) == 1 and len(tube) == self.max_balls_per_tube:
                score += 50
        
        return score

class Move:
    """Represents a move in the solution"""
    
    def __init__(self, from_tube: int, to_tube: int, ball_color: Tuple[int, int, int]):
        self.from_tube = from_tube
        self.to_tube = to_tube
        self.ball_color = ball_color
        self.description = f"Déplacer balle {self._color_to_name(ball_color)} du tube {from_tube + 1} vers le tube {to_tube + 1}"
    
    def _color_to_name(self, color: Tuple[int, int, int]) -> str:
        """Convert RGB color to readable name"""
        r, g, b = color
        
        # Common color mapping
        color_names = {
            (255, 0, 0): "Rouge",
            (0, 255, 0): "Vert",
            (0, 0, 255): "Bleu",
            (255, 255, 0): "Jaune",
            (255, 0, 255): "Magenta",
            (0, 255, 255): "Cyan",
            (255, 165, 0): "Orange",
            (128, 0, 128): "Violet",
            (255, 192, 203): "Rose",
            (165, 42, 42): "Marron"
        }
        
        # Find closest color
        min_distance = float('inf')
        closest_name = f"RGB({r},{g},{b})"
        
        for rgb, name in color_names.items():
            distance = sum(abs(a - b) for a, b in zip(color, rgb))
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        
        return closest_name

class PuzzleSolver:
    """Main puzzle solver using BFS with optimizations"""
    
    def __init__(self, game_state):
        self.initial_game_state = game_state
        self.solution_moves = []
        self.stats = {
            'states_explored': 0,
            'max_queue_size': 0,
            'solve_time': 0,
            'solution_length': 0
        }
    
    def solve(self) -> Optional[List[Move]]:
        """Solve the puzzle using BFS algorithm"""
        start_time = time.time()
        
        # Convert game model to internal representation
        initial_state = self._convert_game_model_to_state()
        
        if initial_state.is_solved():
            return []  # Already solved
        
        # BFS with state tracking
        queue = deque([(initial_state, [])])
        visited = {initial_state}
        
        self.stats['states_explored'] = 0
        self.stats['max_queue_size'] = 0
        
        while queue:
            self.stats['max_queue_size'] = max(self.stats['max_queue_size'], len(queue))
            current_state, moves = queue.popleft()
            self.stats['states_explored'] += 1
            
            # Get all possible moves
            valid_moves = current_state.get_valid_moves()
            
            for from_tube, to_tube in valid_moves:
                # Create new state after move
                new_state = current_state.make_move(from_tube, to_tube)
                
                if new_state in visited:
                    continue
                
                visited.add(new_state)
                
                # Create move object
                ball_color = current_state.tubes[from_tube][-1]
                move = Move(from_tube, to_tube, ball_color)
                new_moves = moves + [move]
                
                # Check if solved
                if new_state.is_solved():
                    self.stats['solve_time'] = time.time() - start_time
                    self.stats['solution_length'] = len(new_moves)
                    return new_moves
                
                # Add to queue
                queue.append((new_state, new_moves))
                
                # Prevent infinite search (safety limit)
                if self.stats['states_explored'] > 100000:
                    break
        
        # No solution found
        self.stats['solve_time'] = time.time() - start_time
        return None
    
    def _convert_game_model_to_state(self) -> GameState:
        """Convert game model to internal GameState representation"""
        tubes = []
        game_dict = self.initial_game_state.to_dict()
        
        for tube_data in game_dict['tubes']:
            tube_balls = []
            for ball in tube_data['balls']:
                color_rgb = tuple(ball['color'])
                tube_balls.append(color_rgb)
            tubes.append(tube_balls)
        
        # Add empty tubes if any
        total_tubes = game_dict['total_tubes']
        empty_tubes = game_dict['empty_tubes']
        
        for _ in range(empty_tubes):
            tubes.append([])
        
        return GameState(tubes)
    
    def get_solution_stats(self) -> Dict:
        """Get statistics about the solving process"""
        return self.stats.copy()

class MultiRowPuzzleSolver:
    """Solver for multi-row puzzle configurations"""
    
    def __init__(self, layout_data, multi_row_data):
        self.layout_data = layout_data
        self.multi_row_data = multi_row_data
        self.solution_moves = []
        self.stats = {
            'rows_processed': 0,
            'total_states_explored': 0,
            'total_solve_time': 0,
            'complexity_score': 0
        }
    
    def solve(self) -> Optional[List[Move]]:
        """Solve multi-row puzzle"""
        start_time = time.time()
        
        # Convert multi-row data to unified game state
        unified_state = self._convert_multi_row_to_unified_state()
        
        if not unified_state:
            return None
        
        # Use standard solver on unified state
        solver = PuzzleSolver(unified_state)
        solution = solver.solve()
        
        # Update stats
        self.stats['total_solve_time'] = time.time() - start_time
        self.stats['rows_processed'] = len(self.layout_data['rows_info'])
        self.stats['total_states_explored'] = solver.stats['states_explored']
        self.stats['complexity_score'] = self._calculate_complexity_score()
        
        return solution
    
    def _convert_multi_row_to_unified_state(self):
        """Convert multi-row layout to unified game state"""
        # This is a placeholder - would need actual implementation
        # based on the multi-row data structure
        return None
    
    def _calculate_complexity_score(self) -> float:
        """Calculate complexity score for multi-row puzzle"""
        score = 0
        score += len(self.layout_data['rows_info']) * 10  # Row count
        score += self.layout_data.get('total_tubes', 0) * 2  # Tube count
        score += self.layout_data.get('total_balls', 0) * 0.5  # Ball count
        return score
    
    def get_solution_stats(self) -> Dict:
        """Get multi-row solving statistics"""
        return self.stats.copy()