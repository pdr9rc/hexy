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
        self.map_width = 30  # Standard Mork Borg hex map width
        self.map_height = 25  # Standard Mork Borg hex map height
        self.terrain_cache = {}
        
        # Color mappings for terrain detection (RGB values)
        self.terrain_colors = {
            'mountain': [(139, 69, 19), (101, 67, 33), (160, 82, 45)],  # Brown tones
            'forest': [(34, 139, 34), (0, 100, 0), (85, 107, 47)],      # Green tones  
            'coast': [(70, 130, 180), (30, 144, 255), (135, 206, 235)], # Blue tones
            'plains': [(255, 222, 173), (238, 203, 173), (205, 133, 63)], # Tan/beige
            'swamp': [(107, 142, 35), (85, 107, 47), (124, 135, 42)],   # Dark green
            'desert': [(244, 164, 96), (255, 218, 185), (210, 180, 140)] # Sandy colors
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
        """Convert hex coordinates to pixel coordinates on the image."""
        if not self.map_image:
            raise RuntimeError("No map image loaded")
        
        img_width, img_height = self.map_image.size
        
        # Calculate pixel position based on hex grid
        # Hex grids have offset rows, so we need to account for that
        pixel_x = int((hex_x - 1) * (img_width / self.map_width))
        pixel_y = int((hex_y - 1) * (img_height / self.map_height))
        
        # Add offset for hex grid (every other row is shifted)
        if hex_y % 2 == 0:
            pixel_x += int((img_width / self.map_width) / 2)
        
        # Ensure coordinates are within image bounds
        pixel_x = max(0, min(pixel_x, img_width - 1))
        pixel_y = max(0, min(pixel_y, img_height - 1))
        
        return pixel_x, pixel_y
    
    def _analyze_pixel_terrain(self, pixel_x: int, pixel_y: int) -> str:
        """Analyze the terrain at a specific pixel location."""
        if not self.map_image:
            return 'plains'
        
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
            for terrain, terrain_color_list in self.terrain_colors.items():
                for terrain_color in terrain_color_list:
                    # Calculate color distance
                    distance = sum(abs(c1 - c2) for c1, c2 in zip(color, terrain_color))
                    
                    # Closer colors get higher scores
                    score = max(0, 255 * 3 - distance)  # Max distance is 255*3
                    
                    if terrain not in terrain_scores:
                        terrain_scores[terrain] = 0
                    terrain_scores[terrain] += score
        
        # Return the terrain with the highest score
        if terrain_scores:
            best_terrain = max(terrain_scores, key=terrain_scores.get)
            return best_terrain
        
        return 'plains'  # Default fallback
    
    def _fallback_terrain(self, hex_code: str) -> str:
        """Fallback terrain detection when image analysis is not available."""
        try:
            x, y = self._hex_code_to_coordinates(hex_code)
            
            # Simple coordinate-based terrain assignment
            # This mimics the layout of a typical Mork Borg map
            
            # Mountains in the northern regions
            if y <= 8:
                if x <= 10 or x >= 25:
                    return 'mountain'
                else:
                    return 'forest' if x % 3 == 0 else 'plains'
            
            # Coastal areas
            elif x <= 3 or x >= 28:
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
            return 'plains'
    
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