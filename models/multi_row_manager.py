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
    
    def get_aggregated_results(self):
        """Get aggregated results from all rows"""
        total_balls = 0
        all_colors = {}
        total_tubes = 0
        
        # Aggregate data from all completed rows
        for row_idx, row_data in self.rows_data.items():
            if not row_data['completed']:
                continue
            
            total_tubes += row_data['num_tubes']
            
            # Add colors with row prefix
            for color, balls in row_data['colors'].items():
                color_key = f"R{row_idx+1}_{color}"
                all_colors[color_key] = balls
                total_balls += len(balls)
        
        return {
            'total_balls': total_balls,
            'total_tubes': total_tubes,
            'colors_by_row': all_colors,
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