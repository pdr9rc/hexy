#!/usr/bin/env python3
"""
Official Map Image Analyzer for The Dying Lands
Extracts terrain information from the official Mork Borg map image.
"""

import os
from typing import Dict, Optional, Tuple
try:
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️  Pillow not available - image analysis disabled")

class ImageAnalyzer:
    """Analyzes the official Mork Borg map image for terrain detection."""
    
    def __init__(self, map_image_path: str = "data/mork_borg_official_map.jpg"):
        """Initialize the image analyzer with the official map."""
        self.map_image_path = map_image_path
        self.map_image = None
        self.map_width = 25  # Standard Mork Borg hex map width (X axis)
        self.map_height = 30  # Standard Mork Borg hex map height (Y axis)
        self.terrain_cache = {}
        
        # Color mappings for terrain detection (RGB values)
        self.terrain_colors = {
            'mountain': [(139, 69, 19), (101, 67, 33), (160, 82, 45), (139, 115, 85)],  # Brown tones
            'forest': [(34, 139, 34), (0, 100, 0), (85, 107, 47), (50, 120, 50)],      # Green tones  
            'coast': [(70, 130, 180), (30, 144, 255), (100, 149, 237), (64, 224, 208)], # Lighter blue/cyan
            'plains': [(149, 142, 90), (222, 184, 135), (210, 180, 140), (255, 222, 173), (238, 203, 173), (205, 133, 63), (245, 222, 179)], # Tan/brown
            'swamp': [(107, 142, 35), (85, 107, 47), (124, 135, 42), (105, 130, 40)],   # Dark green
            'desert': [(244, 164, 96), (255, 218, 185), (210, 180, 140), (238, 203, 173)], # Sandy colors
            'sea': [(0, 87, 183), (0, 105, 148), (0, 119, 190), (25, 25, 112), (0, 0, 128)] # Deep blue only
        }
        
        self._load_map_image()
    
    def _load_map_image(self):
        """Load the official map image if available."""
        if not PILLOW_AVAILABLE:
            return False
            
        if os.path.exists(self.map_image_path):
            try:
                self.map_image = Image.open(self.map_image_path)
                print(f"✅ Loaded official map: {self.map_image_path}")
                print(f"   Map size: {self.map_image.size}")
                return True
            except Exception as e:
                print(f"⚠️  Could not load map image: {e}")
                return False
        else:
            print(f"⚠️  Map image not found: {self.map_image_path}")
            return False
    
    def get_terrain_for_hex(self, hex_code: str) -> str:
        """Get terrain type for a hex by analyzing the map image."""
        if not self.map_image:
            return self._fallback_terrain(hex_code)
        
        if hex_code in self.terrain_cache:
            return self.terrain_cache[hex_code]
        
        try:
            # Convert hex code to coordinates
            x, y = self._hex_code_to_coordinates(hex_code)
            
            # Get pixel coordinates on the image
            pixel_x, pixel_y = self._hex_to_pixel_coordinates(x, y)
            
            # Sample the color at that location
            terrain = self._analyze_pixel_terrain(pixel_x, pixel_y)
            
            # Cache the result
            self.terrain_cache[hex_code] = terrain
            return terrain
            
        except Exception as e:
            print(f"⚠️  Error analyzing hex {hex_code}: {e}")
            return self._fallback_terrain(hex_code)
    
    def _hex_code_to_coordinates(self, hex_code: str) -> Tuple[int, int]:
        """Convert hex code (like '0101') to map coordinates."""
        try:
            if len(hex_code) != 4:
                raise ValueError(f"Invalid hex code format: {hex_code}")
            
            x = int(hex_code[:2])
            y = int(hex_code[2:])
            
            # Validate coordinates are within map bounds
            if x < 1 or x > self.map_width or y < 1 or y > self.map_height:
                raise ValueError(f"Hex coordinates out of bounds: {x}, {y}")
            
            return x, y
        except ValueError as e:
            raise ValueError(f"Invalid hex code {hex_code}: {e}")
    
    def _hex_to_pixel_coordinates(self, hex_x: int, hex_y: int) -> Tuple[int, int]:
        """Convert hex coordinates to pixel coordinates on the image, scaling the image to fit the entire grid."""
        if not self.map_image:
            raise RuntimeError("No map image loaded")

        img_width, img_height = self.map_image.size
        grid_width, grid_height = self.map_width, self.map_height

        # Calculate scale to fit image within grid bounds
        scale_x = grid_width / img_width
        scale_y = grid_height / img_height
        
        # Use the smaller scale to ensure image fits completely
        scale = min(scale_x, scale_y)
        
        # Calculate scaled image dimensions
        scaled_img_width = int(img_width * scale)
        scaled_img_height = int(img_height * scale)
        
        # Calculate padding to center the scaled image
        pad_x = (grid_width - scaled_img_width) // 2
        pad_y = (grid_height - scaled_img_height) // 2
        
        # Map hex coordinates to scaled image coordinates
        # First, map hex to grid position (0-based)
        grid_x = hex_x - 1
        grid_y = hex_y - 1
        
        # Adjust for padding
        adjusted_x = grid_x - pad_x
        adjusted_y = grid_y - pad_y
        
        # Convert to original image coordinates
        if 0 <= adjusted_x < scaled_img_width and 0 <= adjusted_y < scaled_img_height:
            pixel_x = int(adjusted_x / scale)
            pixel_y = int(adjusted_y / scale)
            
            # Ensure coordinates are within image bounds
            if 0 <= pixel_x < img_width and 0 <= pixel_y < img_height:
                return pixel_x, pixel_y
        
        # If outside the scaled image area, return -1, -1
        return -1, -1

    def _analyze_pixel_terrain(self, pixel_x: int, pixel_y: int) -> str:
        """Analyze the terrain at a specific pixel location."""
        if pixel_x == -1 or pixel_y == -1 or not self.map_image:
            return 'sea'
        # Sample a small area around the pixel for better accuracy
        sample_size = 5
        colors = []
        for dx in range(-sample_size, sample_size + 1):
            for dy in range(-sample_size, sample_size + 1):
                x = max(0, min(pixel_x + dx, self.map_image.size[0] - 1))
                y = max(0, min(pixel_y + dy, self.map_image.size[1] - 1))
                try:
                    color = self.map_image.getpixel((x, y))
                    if isinstance(color, tuple) and len(color) >= 3:
                        colors.append(color[:3])  # RGB only
                except Exception:
                    continue
        if not colors:
            return 'plains'
        # Find the most common terrain type based on color matching
        terrain_scores = {}
        for color in colors:
            r, g, b = color  # Ensure r, g, b are defined for each color
            for terrain, terrain_color_list in self.terrain_colors.items():
                for terrain_color in terrain_color_list:
                    # Calculate color distance
                    distance = sum(abs(c1 - c2) for c1, c2 in zip(color, terrain_color))
                    # Closer colors get higher scores
                    score = max(0, 255 * 3 - distance)  # Max distance is 255*3
                    # Reduce score for green detection to avoid false positives
                    if terrain == 'forest' and g > r + 30 and g > b + 30:
                        score *= 0.7  # Reduce forest score for very green pixels
                    if terrain not in terrain_scores:
                        terrain_scores[terrain] = 0
                    terrain_scores[terrain] += score
        # Return the terrain with the highest score
        if terrain_scores:
            best_terrain = max(terrain_scores, key=terrain_scores.get)
            return best_terrain
        return 'plains'  # Default to plains for unknown areas
    
    def _fallback_terrain(self, hex_code: str) -> str:
        """Fallback terrain detection when image analysis is not available."""
        try:
            x, y = self._hex_code_to_coordinates(hex_code)
            
            # Define the continent boundaries (rough approximation)
            # Areas outside these bounds should be sea
            continent_x_min, continent_x_max = 2, 23  # Continent spans roughly X=2 to X=23
            continent_y_min, continent_y_max = 3, 27  # Continent spans roughly Y=3 to Y=27
            
            # Check if hex is outside continent bounds
            if (x < continent_x_min or x > continent_x_max or 
                y < continent_y_min or y > continent_y_max):
                return 'sea'
            
            # Simple coordinate-based terrain assignment for continent areas
            # This mimics the layout of a typical Mork Borg map
            
            # Mountains in the northern regions
            if y <= 8:
                if x <= 10 or x >= 20:
                    return 'mountain'
                else:
                    return 'forest' if x % 3 == 0 else 'plains'
            
            # Coastal areas
            elif x <= 5 or x >= 20:
                return 'coast'
            
            # Central dying lands
            elif 9 <= y <= 16:
                if x % 4 == 0:
                    return 'swamp'
                elif x % 3 == 0:
                    return 'forest'
                else:
                    return 'plains'
            
            # Southern regions
            else:
                if y >= 20:
                    return 'desert' if x % 5 == 0 else 'plains'
                else:
                    return 'forest' if (x + y) % 3 == 0 else 'plains'
                    
        except Exception:
            return 'plains'  # Default to plains for unknown areas
    
    def generate_terrain_overview(self) -> Dict[str, int]:
        """Generate an overview of terrain distribution across the map."""
        terrain_count = {}
        
        for x in range(1, self.map_width + 1):
            for y in range(1, self.map_height + 1):
                hex_code = f"{x:02d}{y:02d}"
                terrain = self.get_terrain_for_hex(hex_code)
                
                if terrain not in terrain_count:
                    terrain_count[terrain] = 0
                terrain_count[terrain] += 1
        
        return terrain_count
    
    def is_available(self) -> bool:
        """Check if image analysis is available."""
        return PILLOW_AVAILABLE and self.map_image is not None
    
    def get_map_info(self) -> Dict[str, any]:
        """Get information about the loaded map."""
        if not self.map_image:
            return {'available': False, 'reason': 'No map image loaded'}
        
        return {
            'available': True,
            'image_path': self.map_image_path,
            'image_size': self.map_image.size,
            'map_dimensions': (self.map_width, self.map_height),
            'total_hexes': self.map_width * self.map_height,
            'terrain_types': list(self.terrain_colors.keys())
        }

# Global instance for easy import
image_analyzer = ImageAnalyzer()