"""
Multi-row manager for handling multiple rows of test tubes
"""

class MultiRowManager:
    def __init__(self):
        self.num_rows = 1
        self.current_row = 0
        self.rows_data = {}
        self.is_multi_row_mode = False
        
    def set_num_rows(self, num_rows):
        """Set total number of rows"""
        self.num_rows = max(1, num_rows)
        self.is_multi_row_mode = num_rows > 1
        self.current_row = 0
        self.rows_data = {}
        
        # Initialize row data structure
        for i in range(self.num_rows):
            self.rows_data[i] = {
                'corners': [],
                'num_tubes': 5,
                'balls_per_tube': 4,
                'grid': [],
                'colors': {},
                'completed': False,
                'cropped_image': None,
                'processed_image': None,
                'grid_matrix': [],
                'color_matrix': []
            }
    
    def get_current_row_data(self):
        """Get data for current row"""
        if self.current_row in self.rows_data:
            return self.rows_data[self.current_row]
        return None
    
    def set_current_row_corners(self, corners):
        """Set corners for current row"""
        if self.current_row in self.rows_data:
            self.rows_data[self.current_row]['corners'] = corners
    
    def set_current_row_tube_params(self, num_tubes, balls_per_tube):
        """Set tube parameters for current row"""
        if self.current_row in self.rows_data:
            self.rows_data[self.current_row]['num_tubes'] = num_tubes
            self.rows_data[self.current_row]['balls_per_tube'] = balls_per_tube
    
    def set_current_row_grid(self, grid):
        """Set grid for current row"""
        if self.current_row in self.rows_data:
            self.rows_data[self.current_row]['grid'] = grid
    
    def set_current_row_colors(self, colors):
        """Set color analysis for current row"""
        if self.current_row in self.rows_data:
            self.rows_data[self.current_row]['colors'] = colors
            self.rows_data[self.current_row]['completed'] = True
    
    def set_current_row_images(self, cropped_image, processed_image):
        """Set cropped and processed images for current row"""
        if self.current_row in self.rows_data:
            self.rows_data[self.current_row]['cropped_image'] = cropped_image
            self.rows_data[self.current_row]['processed_image'] = processed_image
    
    def set_current_row_matrices(self, grid_matrix, color_matrix):
        """Set grid and color matrices for current row"""
        if self.current_row in self.rows_data:
            self.rows_data[self.current_row]['grid_matrix'] = grid_matrix
            self.rows_data[self.current_row]['color_matrix'] = color_matrix
    
    def can_go_to_next_row(self):
        """Check if we can proceed to next row"""
        current_data = self.get_current_row_data()
        if not current_data:
            return False
        
        # Check if current row has required data
        return (current_data['cropped_image'] is not None and
                len(current_data['corners']) == 4 and 
                len(current_data['grid']) > 0)
    
    def can_finish_all_rows(self):
        """Check if all rows are ready to finish"""
        current_data = self.get_current_row_data()
        return (self.is_last_row() and 
                current_data and 
                len(current_data['colors']) > 0)
    
    def go_to_next_row(self):
        """Move to next row"""
        if self.current_row < self.num_rows - 1 and self.can_go_to_next_row():
            self.current_row += 1
            return True
        return False
    
    def go_to_previous_row(self):
        """Move to previous row"""
        if self.current_row > 0:
            self.current_row -= 1
            return True
        return False
    
    def is_last_row(self):
        """Check if current row is the last one"""
        return self.current_row == self.num_rows - 1
    
    def is_first_row(self):
        """Check if current row is the first one"""
        return self.current_row == 0
    
    def get_progress_text(self):
        """Get progress text for UI"""
        if not self.is_multi_row_mode:
            return ""
        return f"Rangée {self.current_row + 1}/{self.num_rows}"
    
    def get_all_completed_rows(self):
        """Get all completed rows count"""
        completed = 0
        for row_data in self.rows_data.values():
            if row_data['completed']:
                completed += 1
        return completed
    
    def is_all_rows_completed(self):
        """Check if all rows are completed"""
        return self.get_all_completed_rows() == self.num_rows
    
    def get_color_name(self, rgb_color):
        """Get human-readable name for RGB color"""
        try:
            r, g, b = rgb_color
        except:
            return "Couleur inconnue"
        
        # Define color ranges with names
        color_ranges = [
            ((200, 255), (0, 50), (0, 50), "Rouge"),
            ((0, 50), (200, 255), (0, 50), "Vert"),
            ((0, 50), (0, 50), (200, 255), "Bleu"),
            ((200, 255), (200, 255), (0, 100), "Jaune"),
            ((200, 255), (0, 100), (200, 255), "Magenta"),
            ((0, 100), (200, 255), (200, 255), "Cyan"),
            ((200, 255), (100, 200), (0, 100), "Orange"),
            ((100, 200), (0, 100), (200, 255), "Violet"),
            ((100, 200), (50, 150), (0, 100), "Marron"),
            ((180, 255), (180, 255), (180, 255), "Blanc"),
            ((0, 80), (0, 80), (0, 80), "Noir"),
            ((100, 180), (100, 180), (100, 180), "Gris"),
        ]
        
        # Find best match
        for r_range, g_range, b_range, name in color_ranges:
            if (r_range[0] <= r <= r_range[1] and 
                g_range[0] <= g <= g_range[1] and 
                b_range[0] <= b <= b_range[1]):
                return name
        
        # Default fallback
        return f"Couleur ({r},{g},{b})"
    
    def color_distance(self, color1, color2):
        """Calculate Euclidean distance between two RGB colors"""
        try:
            r1, g1, b1 = color1
            r2, g2, b2 = color2
            return ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) ** 0.5
        except:
            return float('inf')
    
    def group_similar_colors(self, all_row_colors, tolerance=40):
        """Group similar colors across all rows with tolerance"""
        color_groups = []
        
        for row_idx, row_data in all_row_colors.items():
            for color, balls in row_data.items():
                # Try to find existing group for this color
                found_group = None
                for group in color_groups:
                    if self.color_distance(color, group['representative_color']) <= tolerance:
                        found_group = group
                        break
                
                if found_group:
                    # Add to existing group
                    found_group['total_count'] += len(balls)
                    found_group['rows'][f"R{row_idx+1}"] = len(balls)
                    found_group['all_balls'].extend(balls)
                    
                    # Update representative color (average)
                    total_balls = len(found_group['all_balls'])
                    if total_balls > 0:
                        avg_r = sum(ball.get('color', color)[0] if isinstance(ball.get('color', color), tuple) else color[0] for ball in found_group['all_balls']) / total_balls
                        avg_g = sum(ball.get('color', color)[1] if isinstance(ball.get('color', color), tuple) else color[1] for ball in found_group['all_balls']) / total_balls
                        avg_b = sum(ball.get('color', color)[2] if isinstance(ball.get('color', color), tuple) else color[2] for ball in found_group['all_balls']) / total_balls
                        found_group['representative_color'] = (int(avg_r), int(avg_g), int(avg_b))
                else:
                    # Create new group
                    color_groups.append({
                        'representative_color': color,
                        'color_name': self.get_color_name(color),
                        'total_count': len(balls),
                        'rows': {f"R{row_idx+1}": len(balls)},
                        'all_balls': balls.copy()
                    })
        
        return color_groups
    
    def get_aggregated_results(self):
        """Get aggregated results from all rows"""
        total_balls = 0
        all_colors = {}
        total_tubes = 0
        
        # Collect all row colors
        all_row_colors = {}
        for row_idx, row_data in self.rows_data.items():
            if not row_data['completed']:
                continue
            
            total_tubes += row_data['num_tubes']
            all_row_colors[row_idx] = row_data['colors']
            
            # Add colors with row prefix for backward compatibility
            for color, balls in row_data['colors'].items():
                color_key = f"R{row_idx+1}_{color}"
                all_colors[color_key] = balls
                total_balls += len(balls)
        
        # Group similar colors with tolerance
        combined_colors_groups = self.group_similar_colors(all_row_colors)
        
        # Convert to dictionary format
        combined_colors = {}
        for i, group in enumerate(combined_colors_groups):
            key = f"{group['color_name']}_{group['representative_color']}"
            combined_colors[key] = {
                'representative_color': group['representative_color'],
                'color_name': group['color_name'],
                'total_count': group['total_count'],
                'rows': group['rows']
            }
        
        return {
            'total_balls': total_balls,
            'total_tubes': total_tubes,
            'colors_by_row': all_colors,
            'combined_colors': combined_colors,
            'completed_rows': self.get_all_completed_rows(),
            'total_rows': self.num_rows
        }
    
    def reset(self):
        """Reset manager to initial state"""
        self.num_rows = 1
        self.current_row = 0
        self.rows_data = {}
        self.is_multi_row_mode = False
    
    def get_current_row_number(self):
        """Get current row number (1-based)"""
        return self.current_row + 1
    
    def get_total_expected_balls(self):
        """Get total expected balls across all rows"""
        total = 0
        for row_data in self.rows_data.values():
            total += row_data['num_tubes'] * row_data['balls_per_tube']
        return total