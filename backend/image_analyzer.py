#!/usr/bin/env python3
"""
Official Map Image Analyzer for The Dying Lands
Extracts terrain information from the official Mork Borg map image.
"""

import os
from typing import Dict, Optional, Tuple, List
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️  Pillow not available - image analysis disabled")

class ImageAnalyzer:
    """
    Analyzes a map image to determine terrain for a hex grid.
    Supports multiple mapping modes and robust debug output.
    """
    def __init__(self, map_image_path: str, map_width: int, map_height: int, mapping_mode: str = "letterbox", debug: bool = False):
        self.map_image_path = map_image_path
        self.map_width = map_width
        self.map_height = map_height
        self.mapping_mode = mapping_mode  # 'stretch', 'letterbox', or 'crop'
        self.debug = debug
        self.terrain_cache: Dict[str, str] = {}
        self._debug_counter = 0
        self.terrain_colors = {
            'sea': [
                (34, 71, 142), (33, 70, 141), (33, 70, 140), (34, 70, 144), (35, 72, 143), (33, 68, 136),
                (32, 74, 135), (0, 87, 183), (0, 105, 148), (0, 119, 190), (25, 25, 112), (0, 0, 128)
            ],
            'forest': [
                (64, 115, 22), (81, 197, 26), (62, 115, 23),
                (44, 94, 36), (0, 100, 0), (85, 107, 47), (50, 120, 50), (120, 180, 60), (140, 200, 80), (60, 120, 40)
            ],
            'mountain': [
                (69, 57, 15), (26, 20, 6), (63, 33, 22), (69, 57, 17), (27, 21, 5), (24, 21, 4),
                (101, 67, 33), (139, 69, 19), (160, 82, 45), (139, 115, 85), (90, 60, 30), (80, 40, 20)
            ],
            'plains': [
                (196, 186, 75), (148, 153, 71),
                (34, 139, 34), (120, 180, 60), (140, 200, 80)
            ],
            'swamp': [
                (148, 153, 71), (196, 186, 75),
                (170, 170, 80), (150, 180, 90), (180, 180, 100), (160, 170, 90)
            ],
            'desert': [
                (255, 255, 255), (254, 254, 254),
                (244, 220, 96), (255, 255, 153), (255, 255, 102), (255, 255, 204)
            ],
            'snow': [
                (255, 255, 255), (254, 254, 254), (240, 240, 240), (220, 220, 220)
            ],
            'unknown': [
                (129, 136, 146), (30, 20, 10), (20, 10, 5), (10, 5, 2)
            ],
        }
        self.map_image = self._load_map_image()
    
    def _load_map_image(self):
        if not PILLOW_AVAILABLE:
            return None
        if os.path.exists(self.map_image_path):
            try:
                img = Image.open(self.map_image_path)
                if self.debug:
                    print(f"✅ Loaded map image: {self.map_image_path} size={img.size}")
                return img
            except Exception as e:
                print(f"⚠️  Could not load map image: {e}")
        else:
            print(f"⚠️  Map image not found: {self.map_image_path}")
        return None
    
    def get_terrain_for_hex(self, hex_code: str) -> str:
        if not self.map_image:
            return 'unknown'
        if hex_code in self.terrain_cache:
            return self.terrain_cache[hex_code]
        try:
            x, y = self._hex_code_to_coordinates(hex_code)
            pixel_x, pixel_y, in_image = self._hex_to_pixel_coordinates(x, y)
            if self.mapping_mode == "letterbox" and not in_image:
                self.terrain_cache[hex_code] = "sea"
                return "sea"
            terrain = self._analyze_pixel_terrain(pixel_x, pixel_y, hex_code)
            self.terrain_cache[hex_code] = terrain
            return terrain
        except Exception as e:
            if self.debug:
                print(f"⚠️  Error analyzing hex {hex_code}: {e}")
            return 'unknown'
    
    def _hex_code_to_coordinates(self, hex_code: str) -> Tuple[int, int]:
            if len(hex_code) != 4:
                raise ValueError(f"Invalid hex code format: {hex_code}")
            x = int(hex_code[:2])
            y = int(hex_code[2:])
            if x < 1 or x > self.map_width or y < 1 or y > self.map_height:
                raise ValueError(f"Hex coordinates out of bounds: {x}, {y}")
            return x, y
    
    def _hex_to_pixel_coordinates(self, hex_x: int, hex_y: int) -> Tuple[int, int, bool]:
        img_width, img_height = self.map_image.size
        grid_width, grid_height = self.map_width, self.map_height
        if self.mapping_mode == "letterbox":
            scale = min(img_width / grid_width, img_height / grid_height)
            scaled_width = grid_width * scale
            scaled_height = grid_height * scale
            x_offset = (img_width - scaled_width) / 2
            y_offset = (img_height - scaled_height) / 2
            # Map hex center to image coordinates (float, not int)
            pixel_x_f = x_offset + (hex_x - 0.5) * scale
            pixel_y_f = y_offset + (hex_y - 0.5) * scale
            # Check if the center is within the image bounds (before clamping)
            in_image = (0 <= pixel_x_f < img_width) and (0 <= pixel_y_f < img_height)
            # Clamp after checking
            pixel_x = int(max(0, min(pixel_x_f, img_width - 1)))
            pixel_y = int(max(0, min(pixel_y_f, img_height - 1)))
        elif self.mapping_mode == "stretch":
            pixel_x = int((hex_x - 1) / (grid_width - 1) * (img_width - 1))
            pixel_y = int((hex_y - 1) / (grid_height - 1) * (img_height - 1))
            in_image = True
        elif self.mapping_mode == "crop":
            scale_x = img_width / grid_width
            scale_y = img_height / grid_height
            scale = min(scale_x, scale_y)
            offset_x = int((img_width - grid_width * scale) / 2)
            offset_y = int((img_height - grid_height * scale) / 2)
            pixel_x = int((hex_x - 1) * scale + offset_x)
            pixel_y = int((hex_y - 1) * scale + offset_y)
            in_image = (offset_x <= pixel_x < offset_x + grid_width * scale) and (offset_y <= pixel_y < offset_y + grid_height * scale)
        else:
            raise ValueError(f"Unknown mapping mode: {self.mapping_mode}")
        if self.debug and self._debug_counter < 20:
            
            self._debug_counter += 1
        return pixel_x, pixel_y, in_image
        
    def get_average_color_for_hex(self, hex_x: int, hex_y: int) -> Tuple[int, int, int]:
        """Return the average RGB color for the region of the image corresponding to this hex."""
        img_width, img_height = self.map_image.size
        grid_width, grid_height = self.map_width, self.map_height
        scale = min(img_width / grid_width, img_height / grid_height)
        scaled_width = grid_width * scale
        scaled_height = grid_height * scale
        x_offset = int((img_width - scaled_width) / 2)
        y_offset = int((img_height - scaled_height) / 2)
        # Region bounds in image
        left = int(x_offset + (hex_x - 1) * scale)
        right = int(x_offset + hex_x * scale)
        top = int(y_offset + (hex_y - 1) * scale)
        bottom = int(y_offset + hex_y * scale)
        pixels = []
        for x in range(left, right):
            for y in range(top, bottom):
                if 0 <= x < img_width and 0 <= y < img_height:
                    color = self.map_image.getpixel((x, y))
                    if isinstance(color, tuple) and len(color) >= 3:
                        pixels.append(color[:3])
        if not pixels:
            return (0, 0, 0)
        r = sum(c[0] for c in pixels) // len(pixels)
        g = sum(c[1] for c in pixels) // len(pixels)
        b = sum(c[2] for c in pixels) // len(pixels)
        return (r, g, b)

    def _analyze_pixel_terrain(self, pixel_x: int, pixel_y: int, hex_code: Optional[str] = None) -> str:
        if not self.map_image:
            return 'unknown'
        sample_size = 5
        colors: List[Tuple[int, int, int]] = []
        for dx in range(-sample_size, sample_size + 1):
            for dy in range(-sample_size, sample_size + 1):
                x = max(0, min(pixel_x + dx, self.map_image.size[0] - 1))
                y = max(0, min(pixel_y + dy, self.map_image.size[1] - 1))
                try:
                    color = self.map_image.getpixel((x, y))
                    if isinstance(color, tuple) and len(color) >= 3:
                        colors.append(color[:3])
                except Exception:
                    continue
        if not colors:
            return 'unknown'
        # Use Euclidean distance for color matching
        def color_distance(c1, c2):
            return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5
        terrain_scores: Dict[str, float] = {}
        color_matches: Dict[str, List[Tuple[int, int, int]]] = {t: [] for t in self.terrain_colors}
        tolerance = 30
        for color in colors:
            best_terrain = 'unknown'
            best_dist = float('inf')
            palette_distances = {}
            for terrain, color_list in self.terrain_colors.items():
                for tcolor in color_list:
                    dist = color_distance(color, tcolor)
                    if dist < best_dist:
                        best_dist = dist
                        best_terrain = terrain
                    # Track min distance for each terrain
                    if terrain not in palette_distances or dist < palette_distances[terrain]:
                        palette_distances[terrain] = dist
            if hex_code == "0503":
                
                for t, d in palette_distances.items():
                    print(f"  {t}: distance={d}")
                print(f"  -> chosen terrain: {best_terrain} (distance={best_dist})")
            if best_dist <= tolerance:
                terrain_scores[best_terrain] = terrain_scores.get(best_terrain, 0) + 1
                color_matches[best_terrain].append(color)
            else:
                r, g, b = color
                if r < 60 and g < 100 and b > 100:
                    terrain_scores['sea'] = terrain_scores.get('sea', 0) + 1
                    color_matches['sea'].append(color)
                else:
                    terrain_scores['unknown'] = terrain_scores.get('unknown', 0) + 1
                    color_matches['unknown'].append(color)
        if terrain_scores:
            best_terrain = max(terrain_scores, key=terrain_scores.get)
            if self.debug and self._debug_counter < 40:
                        
                self._debug_counter += 1
            return best_terrain
        return 'unknown'

    def _most_common_color(self, color_list: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
        from collections import Counter
        if not color_list:
            return (0, 0, 0)
        return Counter(color_list).most_common(1)[0][0]

    def analyze_palette_suggestions(self, sample_limit=10000):
        """Analyze the image and print the most common colors, suggesting palette updates."""
        from collections import Counter
        if not self.map_image:
            print("[ImageAnalyzer] No image loaded.")
            return
        img = self.map_image.convert('RGB')
        width, height = img.size
        pixels = []
        step = max(1, int((width * height) / sample_limit) ** 0.5)
        for x in range(0, width, int(step)):
            for y in range(0, height, int(step)):
                color = img.getpixel((x, y))
                if isinstance(color, tuple) and len(color) >= 3:
                    pixels.append(color[:3])
        counter = Counter(pixels)
        print("[ImageAnalyzer] Most common colors in image:")
        for color, count in counter.most_common(20):
            print(f"  {color}: {count}")
        print("[ImageAnalyzer] Suggest adding these to your palette if they match terrain:")
        for color, count in counter.most_common(10):
            print(f"    {color},")

    def get_map_info(self) -> Dict:
        if not self.map_image:
            return {'available': False}
        return {
            'available': True,
            'image_path': self.map_image_path,
            'image_size': self.map_image.size,
            'map_dimensions': (self.map_width, self.map_height),
            'total_hexes': self.map_width * self.map_height,
            'terrain_types': list(self.terrain_colors.keys()),
        }