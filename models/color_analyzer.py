"""
Color analysis for ball detection
"""
from collections import Counter
import math

class ColorAnalyzer:
    def __init__(self, tolerance=40):
        self.tolerance = tolerance
        self.detected_balls = []
        self.color_groups = {}
    
    def set_tolerance(self, tolerance):
        """Set color similarity tolerance"""
        self.tolerance = max(10, min(100, tolerance))
    
    def colors_similar(self, color1, color2):
        """Check if two colors are similar within tolerance"""
        if not color1 or not color2:
            return False
        
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        # Manhattan distance in RGB space
        distance = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
        return distance < self.tolerance
    
    def get_dominant_color_in_circle(self, image, x, y, radius):
        """Extract dominant color from circular region"""
        if not image:
            return None
        
        width, height = image.size
        color_histogram = {}
        sample_count = 0
        
        # Sample pixels within the circle (inner 70% to avoid edges)
        inner_radius = int(radius * 0.7)
        
        for r in range(0, inner_radius, 2):
            circumference = max(1, int(2 * math.pi * r))
            angle_step = 360 / circumference
            
            for angle in range(0, 360, max(1, int(angle_step))):
                px = int(x + r * math.cos(math.radians(angle)))
                py = int(y + r * math.sin(math.radians(angle)))
                
                if 0 <= px < width and 0 <= py < height:
                    color = image.getpixel((px, py))
                    color_histogram[color] = color_histogram.get(color, 0) + 1
                    sample_count += 1
        
        if not color_histogram:
            return None
        
        # Find dominant color (exclude very dark/light/gray colors)
        dominant_color = None
        max_count = 0
        
        for color, count in color_histogram.items():
            r, g, b = color
            brightness = (r + g + b) / 3
            color_variance = max(r, g, b) - min(r, g, b)
            
            # Filter criteria:
            # - Not too dark or too bright
            # - Has some color variance (not gray)
            # - Most frequent color
            if (30 < brightness < 220 and 
                color_variance > 15 and 
                count > max_count):
                dominant_color = color
                max_count = count
        
        return dominant_color
    
    def analyze_grid_circles(self, image, circles):
        """Analyze all circles in the grid for colors"""
        if not image or not circles:
            return []
        
        self.detected_balls = []
        
        for circle in circles:
            dominant_color = self.get_dominant_color_in_circle(
                image, circle['x'], circle['y'], circle['radius']
            )
            
            if dominant_color:
                ball_info = {
                    'x': circle['x'],
                    'y': circle['y'],
                    'radius': circle['radius'],
                    'color': dominant_color,
                    'grid_position': (circle.get('grid_i', 0), circle.get('grid_j', 0))
                }
                self.detected_balls.append(ball_info)
        
        return self.detected_balls
    
    def group_balls_by_color(self, balls=None):
        """Group balls by similar colors"""
        if balls is None:
            balls = self.detected_balls
        
        if not balls:
            return {}
        
        color_groups = {}
        
        for ball in balls:
            ball_color = ball['color']
            
            # Find existing similar color group
            group_key = None
            for existing_color in color_groups.keys():
                if self.colors_similar(ball_color, existing_color):
                    group_key = existing_color
                    break
            
            # Create new group if no similar color found
            if group_key is None:
                group_key = ball_color
                color_groups[group_key] = []
            
            color_groups[group_key].append(ball)
        
        self.color_groups = color_groups
        return color_groups
    
    def get_analysis_summary(self):
        """Get summary of color analysis"""
        if not self.color_groups:
            return {
                'total_balls': 0,
                'unique_colors': 0,
                'color_distribution': []
            }
        
        total_balls = sum(len(balls) for balls in self.color_groups.values())
        unique_colors = len(self.color_groups)
        
        color_distribution = []
        for color, balls in self.color_groups.items():
            color_distribution.append({
                'color': color,
                'count': len(balls),
                'percentage': (len(balls) / total_balls * 100) if total_balls > 0 else 0
            })
        
        # Sort by count descending
        color_distribution.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_balls': total_balls,
            'unique_colors': unique_colors,
            'color_distribution': color_distribution
        }
    
    def get_detected_balls(self):
        """Get list of detected balls"""
        return self.detected_balls.copy()
    
    def get_color_groups(self):
        """Get color groups"""
        return self.color_groups.copy()