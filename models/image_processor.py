"""
Image processing utilities for Ball Sort Puzzle Solver
"""
from PIL import Image, ImageTk, ImageDraw
import math

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.scale_factor = 1.0
    
    def load_image(self, image_path):
        """Load image from file path"""
        self.original_image = Image.open(image_path).convert('RGB')
        self.processed_image = self.original_image.copy()
        return self.original_image
    
    def crop_image(self, x1, y1, x2, y2):
        """Crop image to specified rectangle"""
        if not self.original_image:
            return None
        
        # Ensure coordinates are in correct order
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        self.processed_image = self.original_image.crop((left, top, right, bottom))
        return self.processed_image
    
    def resize_for_display(self, max_width=500, max_height=400):
        """Resize image for display while maintaining aspect ratio"""
        if not self.processed_image:
            return None, 1.0
        
        width, height = self.processed_image.size
        scale_x = max_width / width
        scale_y = max_height / height
        scale_factor = min(scale_x, scale_y, 1.0)
        
        if scale_factor < 1.0:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            display_image = self.processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            display_image = self.processed_image.copy()
        
        return display_image, scale_factor
    
    def get_pixel_color(self, x, y):
        """Get pixel color at coordinates"""
        if not self.processed_image:
            return None
        
        width, height = self.processed_image.size
        if 0 <= x < width and 0 <= y < height:
            return self.processed_image.getpixel((x, y))
        return None
    
    def draw_circles_on_image(self, circles):
        """Draw circles on image for visualization"""
        if not self.processed_image or not circles:
            return self.processed_image
        
        img_copy = self.processed_image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        for circle in circles:
            x, y, radius = circle['x'], circle['y'], circle['radius']
            left = x - radius
            top = y - radius
            right = x + radius
            bottom = y + radius
            
            # Draw circle outline
            draw.ellipse([left, top, right, bottom], outline="red", width=2)
            # Draw center point
            draw.ellipse([x-3, y-3, x+3, y+3], fill="red")
        
        return img_copy