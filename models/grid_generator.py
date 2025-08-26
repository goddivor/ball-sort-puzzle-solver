"""
Grid generation for ball detection
"""
import math

class GridGenerator:
    def __init__(self):
        self.corner_points = []
        self.grid_spacing = 30
        self.ball_radius = 15
        self.num_tubes = 5
        self.balls_per_tube = 4
        self.total_expected_balls = 0
    
    def set_corner_points(self, points):
        """Set the 4 corner points for grid generation"""
        if len(points) == 4:
            self.corner_points = points
            return True
        return False
    
    def add_corner_point(self, x, y):
        """Add a corner point (max 4)"""
        if len(self.corner_points) < 4:
            self.corner_points.append({'x': x, 'y': y})
            return True
        return False
    
    def remove_corner_point(self, index):
        """Remove a corner point by index"""
        if 0 <= index < len(self.corner_points):
            self.corner_points.pop(index)
            return True
        return False
    
    def clear_corner_points(self):
        """Clear all corner points"""
        self.corner_points = []
    
    def set_grid_spacing(self, spacing):
        """Set spacing between grid points"""
        self.grid_spacing = max(10, spacing)
    
    def set_ball_radius(self, radius):
        """Set ball radius for circle generation"""
        self.ball_radius = max(5, radius)
    
    def set_tube_parameters(self, num_tubes, balls_per_tube):
        """Set tube count and capacity parameters"""
        self.num_tubes = max(1, num_tubes)
        self.balls_per_tube = max(1, balls_per_tube)
        self.total_expected_balls = self.num_tubes * self.balls_per_tube
    
    def get_tube_parameters(self):
        """Get current tube parameters"""
        return self.num_tubes, self.balls_per_tube
    
    def generate_grid(self):
        """Generate grid of circles from corner points using tube parameters"""
        if len(self.corner_points) != 4:
            return []
        
        # Sort points to get proper rectangle corners
        points = self.corner_points.copy()
        points.sort(key=lambda p: (p['y'], p['x']))
        
        top_points = points[:2]
        bottom_points = points[2:]
        top_points.sort(key=lambda p: p['x'])
        bottom_points.sort(key=lambda p: p['x'])
        
        top_left = top_points[0]
        top_right = top_points[1]
        bottom_left = bottom_points[0]
        bottom_right = bottom_points[1]
        
        grid_circles = []
        
        # Calculate dimensions
        width = max(abs(top_right['x'] - top_left['x']), abs(bottom_right['x'] - bottom_left['x']))
        height = max(abs(bottom_left['y'] - top_left['y']), abs(bottom_right['y'] - top_right['y']))
        
        # Calculate grid based on tube parameters
        # Horizontal: number of tubes
        # Vertical: balls per tube
        steps_x = self.num_tubes - 1  # Number of gaps between tubes
        steps_y = self.balls_per_tube - 1  # Number of gaps between balls in a tube
        
        # Generate grid points using tube layout
        for tube_idx in range(self.num_tubes):
            for ball_idx in range(self.balls_per_tube):
                # Calculate interpolation factors
                fx = tube_idx / max(1, steps_x) if steps_x > 0 else 0
                fy = ball_idx / max(1, steps_y) if steps_y > 0 else 0
                
                # Bilinear interpolation for position
                top_x = top_left['x'] * (1 - fx) + top_right['x'] * fx
                top_y = top_left['y'] * (1 - fx) + top_right['y'] * fx
                
                bottom_x = bottom_left['x'] * (1 - fx) + bottom_right['x'] * fx
                bottom_y = bottom_left['y'] * (1 - fx) + bottom_right['y'] * fx
                
                final_x = int(top_x * (1 - fy) + bottom_x * fy)
                final_y = int(top_y * (1 - fy) + bottom_y * fy)
                
                grid_circles.append({
                    'x': final_x,
                    'y': final_y,
                    'radius': self.ball_radius,
                    'tube_idx': tube_idx,
                    'ball_idx': ball_idx,
                    'grid_i': tube_idx,
                    'grid_j': ball_idx
                })
        
        return grid_circles
    
    def get_expected_ball_count(self):
        """Get expected total number of balls"""
        return self.total_expected_balls
    
    def get_corner_points(self):
        """Get current corner points"""
        return self.corner_points.copy()
    
    def is_ready(self):
        """Check if grid is ready to be generated"""
        return len(self.corner_points) == 4