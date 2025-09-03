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
        """Get all valid moves from current state with optimization"""
        moves = []
        
        for from_tube in range(len(self.tubes)):
            if len(self.tubes[from_tube]) == 0:  # Empty source tube
                continue
            
            top_ball = self.tubes[from_tube][-1]  # Top ball
            
            # Optimization: prioritize moves that make sense
            for to_tube in range(len(self.tubes)):
                if from_tube == to_tube:  # Same tube
                    continue
                
                # Check if move is valid
                if self._is_valid_move(from_tube, to_tube):
                    # Calculate move priority (lower = better)
                    priority = self._calculate_move_priority(from_tube, to_tube)
                    moves.append((from_tube, to_tube, priority))
        
        # Sort moves by priority (best moves first)
        moves.sort(key=lambda x: x[2])
        return [(from_tube, to_tube) for from_tube, to_tube, _ in moves]
    
    def _calculate_move_priority(self, from_tube: int, to_tube: int) -> float:
        """Calculate priority score for a move (lower = better)"""
        priority = 0
        
        # Prefer moves to empty tubes
        if len(self.tubes[to_tube]) == 0:
            priority -= 20
        
        # Prefer moves that create pure tubes
        if len(self.tubes[to_tube]) > 0:
            dest_color = self.tubes[to_tube][-1]
            source_color = self.tubes[from_tube][-1]
            if dest_color == source_color:
                priority -= 10
        
        # Avoid breaking pure tubes unless necessary
        if self._is_tube_pure(from_tube) and len(self.tubes[from_tube]) > 1:
            priority += 15
        
        # Prefer moves that help complete tubes
        if self._would_complete_tube(to_tube, self.tubes[from_tube][-1]):
            priority -= 25
        
        return priority
    
    def _is_tube_pure(self, tube_idx: int) -> bool:
        """Check if all balls in tube are same color"""
        tube = self.tubes[tube_idx]
        if not tube:
            return True
        first_color = tube[0]
        return all(ball == first_color for ball in tube)
    
    def _would_complete_tube(self, tube_idx: int, ball_color: Tuple[int, int, int]) -> bool:
        """Check if adding this ball would complete the tube"""
        tube = self.tubes[tube_idx]
        if len(tube) == self.max_balls_per_tube - 1:  # One space left
            if tube and tube[0] == ball_color:  # Same color as tube
                return True
        return False
    
    def _is_valid_move(self, from_tube: int, to_tube: int) -> bool:
        """Check if a move from one tube to another is valid (Ball Sort rules)"""
        if len(self.tubes[from_tube]) == 0:  # Source tube empty
            return False
        
        # Check destination capacity (only moving ONE ball)
        if len(self.tubes[to_tube]) >= self.max_balls_per_tube:  # Destination full
            return False
        
        # If destination is empty, move is always valid
        if len(self.tubes[to_tube]) == 0:
            return True
        
        # Check if colors match (Ball Sort rule: can only place on same color)
        source_color = self.tubes[from_tube][0]  # Top ball from source (index 0 = top)
        dest_color = self.tubes[to_tube][0]      # Top ball from destination (index 0 = top)
        
        return source_color == dest_color
    
    def _get_consecutive_top_balls(self, tube_idx: int) -> List[Tuple[int, int, int]]:
        """Get all consecutive balls of same color from the top of tube"""
        tube = self.tubes[tube_idx]
        if not tube:
            return []
        
        top_color = tube[-1]
        consecutive_balls = []
        
        # Go from top to bottom, collecting same-colored balls
        for i in range(len(tube) - 1, -1, -1):
            if tube[i] == top_color:
                consecutive_balls.append(tube[i])
            else:
                break
        
        # Reverse to get correct order (bottom to top)
        return list(reversed(consecutive_balls))
    
    def make_move(self, from_tube: int, to_tube: int) -> 'GameState':
        """Create a new game state after making a move (moves ONE ball only - Ball Sort rules)"""
        new_state = GameState(self.tubes, self.max_balls_per_tube)
        
        if self._is_valid_move(from_tube, to_tube):
            # Move only ONE ball (the top one - index 0)
            ball = new_state.tubes[from_tube].pop(0)  # Take from top (index 0)
            new_state.tubes[to_tube].insert(0, ball)  # Add to top (index 0)
        
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
    
    def __init__(self, from_tube: int, to_tube: int, ball_color: Tuple[int, int, int], balls_count: int = 1):
        self.from_tube = from_tube
        self.to_tube = to_tube
        self.ball_color = ball_color
        self.balls_count = balls_count  # Always 1 for Ball Sort
        
        # Ball Sort moves only ONE ball at a time
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
        """Solve the puzzle using optimized BFS algorithm"""
        start_time = time.time()
        
        # Convert game model to internal representation
        initial_state = self._convert_game_model_to_state()
        
        if initial_state.is_solved():
            return []  # Already solved
        
        # Check if puzzle is solvable (basic check)
        if not self._is_puzzle_solvable(initial_state):
            self.stats['solve_time'] = time.time() - start_time
            return None
        
        # BFS with optimizations
        queue = deque([(initial_state, [])])
        visited = {initial_state}
        
        self.stats['states_explored'] = 0
        self.stats['max_queue_size'] = 0
        
        # Dynamic search limits based on puzzle complexity
        max_states = self._calculate_search_limit(initial_state)
        max_depth = min(50, len(initial_state.tubes) * 10)  # Depth limit
        
        while queue:
            self.stats['max_queue_size'] = max(self.stats['max_queue_size'], len(queue))
            current_state, moves = queue.popleft()
            self.stats['states_explored'] += 1
            
            # Depth limit check
            if len(moves) >= max_depth:
                continue
            
            # Get prioritized moves
            valid_moves = current_state.get_valid_moves()
            
            for from_tube, to_tube in valid_moves:
                # Skip obviously bad moves
                if self._is_wasteful_move(current_state, from_tube, to_tube):
                    continue
                
                # Create new state after move
                new_state = current_state.make_move(from_tube, to_tube)
                
                if new_state in visited:
                    continue
                
                visited.add(new_state)
                
                # Create move object (single ball only)
                ball_color = current_state.tubes[from_tube][0]  # Top ball (index 0)
                move = Move(from_tube, to_tube, ball_color, 1)  # Always 1 ball
                new_moves = moves + [move]
                
                # Check if solved
                if new_state.is_solved():
                    self.stats['solve_time'] = time.time() - start_time
                    self.stats['solution_length'] = len(new_moves)
                    return new_moves
                
                # Add to queue with early termination check
                queue.append((new_state, new_moves))
                
                # Dynamic search limit
                if self.stats['states_explored'] > max_states:
                    break
            
            # Time limit check (prevent hanging)
            if time.time() - start_time > 30:  # 30 second limit
                break
        
        # No solution found
        self.stats['solve_time'] = time.time() - start_time
        return None
    
    def _is_puzzle_solvable(self, state: GameState) -> bool:
        """Basic solvability check"""
        # Count colors and balls
        color_counts = {}
        total_balls = 0
        
        for tube in state.tubes:
            for ball in tube:
                color_counts[ball] = color_counts.get(ball, 0) + 1
                total_balls += 1
        
        # Check if any color has wrong count
        expected_balls_per_color = state.max_balls_per_tube
        for count in color_counts.values():
            if count != expected_balls_per_color:
                return False  # Impossible configuration
        
        # Count empty tubes needed
        empty_tubes = sum(1 for tube in state.tubes if len(tube) == 0)
        colors = len(color_counts)
        tubes_needed = colors
        
        if len(state.tubes) < tubes_needed:
            return False  # Not enough tubes
        
        return True
    
    def _calculate_search_limit(self, state: GameState) -> int:
        """Calculate dynamic search limit based on puzzle complexity"""
        base_limit = 50000
        
        # Adjust based on number of tubes
        tube_factor = len(state.tubes) * 1000
        
        # Adjust based on mixed colors
        mixed_penalty = 0
        for tube in state.tubes:
            if len(tube) > 1:
                colors = set(tube)
                if len(colors) > 1:
                    mixed_penalty += 5000
        
        return min(200000, base_limit + tube_factor + mixed_penalty)
    
    def _is_wasteful_move(self, state: GameState, from_tube: int, to_tube: int) -> bool:
        """Check if a move is obviously wasteful"""
        # Don't move from empty tube to another empty tube
        if len(state.tubes[from_tube]) == 0 and len(state.tubes[to_tube]) == 0:
            return True
        
        # Don't move ball that's already in correct pure tube
        if (len(state.tubes[from_tube]) > 0 and 
            state._is_tube_pure(from_tube) and 
            len(state.tubes[from_tube]) == state.max_balls_per_tube):
            return True
        
        return False
    
    def _convert_game_model_to_state(self) -> GameState:
        """Convert game model to internal GameState representation"""
        tubes = []
        game_dict = self.initial_game_state.to_dict()
        
        # Get balls per tube capacity
        balls_per_tube = game_dict.get('balls_per_tube', 4)
        
        for tube_data in game_dict['tubes']:
            tube_balls = []
            # Sort balls by level_index to maintain correct order (bottom to top)
            sorted_balls = sorted(tube_data['balls'], key=lambda b: b['level_index'])
            
            for ball in sorted_balls:
                color_rgb = tuple(ball['color'])
                tube_balls.append(color_rgb)
            tubes.append(tube_balls)
        
        return GameState(tubes, balls_per_tube)
    
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