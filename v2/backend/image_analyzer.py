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
        # Mapping modes:
        # - 'letterbox': Scales to fit (preserves aspect ratio, entire image visible, may have unused space)
        # - 'stretch': Stretches to fill (may distort aspect ratio, entire image used)
        # - 'crop': Crops to fill (preserves aspect ratio, may cut off parts of image)
        self.mapping_mode = mapping_mode
        self.debug = debug
        self.terrain_cache: Dict[str, str] = {}
        self._debug_counter = 0
        self.terrain_colors = {
            'sea': [
                # Exact color from map: #22478e = (34, 71, 142)
                (34, 71, 142),
                # Variations around sea blue
                (33, 70, 141), (33, 70, 140), (34, 70, 144), (35, 72, 143), (33, 68, 136),
                (32, 74, 135), (30, 65, 130), (40, 75, 140), (25, 55, 125), (35, 70, 135),
                (20, 60, 120), (15, 50, 110), (10, 40, 100), (0, 50, 120), (0, 60, 140),
                (30, 50, 120), (40, 60, 130), (10, 30, 90), (15, 35, 100), (20, 40, 110),
            ],
            'river': [
                # Exact color from map: #87a9eb = (135, 169, 235)
                (135, 169, 235),
                # Variations around river blue (light blue)
                (130, 165, 230), (140, 173, 240), (125, 160, 225), (145, 175, 245),
                (120, 155, 220), (150, 180, 250), (110, 150, 215), (155, 185, 255),
                # Similar light blues
                (135, 170, 240), (140, 175, 245), (130, 165, 235), (145, 180, 250),
                (125, 160, 230), (150, 185, 255), (120, 155, 225), (155, 190, 255),
            ],
            'bridge': [
                # Exact color from map: #818b9a = (129, 139, 154)
                (129, 139, 154),
                # Variations around bridge gray
                (125, 135, 150), (130, 140, 158), (120, 130, 145), (135, 145, 160),
                (115, 125, 140), (140, 150, 165), (110, 120, 135), (145, 155, 170),
                # Similar grays
                (128, 138, 153), (131, 141, 156), (127, 137, 152), (132, 142, 157),
            ],
            'forest': [
                (64, 115, 22), (81, 197, 26), (62, 115, 23),
                (44, 94, 36), (0, 100, 0), (85, 107, 47), (50, 120, 50), (120, 180, 60), (140, 200, 80), (60, 120, 40)
            ],
            'mountain': [
                # Exact color from map: #45390f = (69, 57, 15)
                (69, 57, 15),
                # Variations around mountain brown
                (65, 53, 11), (73, 61, 19), (61, 49, 9), (77, 65, 23),
                (67, 55, 13), (71, 59, 17), (63, 51, 10), (75, 63, 21),
                # Similar dark browns
                (70, 58, 16), (68, 56, 14), (72, 60, 18), (66, 54, 12),
                # Slightly darker/lighter variations
                (60, 50, 10), (80, 70, 25), (55, 45, 5), (85, 75, 30),
            ],
            'plains': [
                # Exact color from map: #51c51a = (81, 197, 26) - bright green!
                (81, 197, 26),
                # Variations around plains green
                (75, 190, 20), (85, 205, 30), (70, 185, 15), (90, 210, 35),
                (80, 195, 25), (88, 200, 32), (78, 192, 24), (82, 198, 28),
                # Similar bright greens
                (85, 200, 30), (77, 195, 22), (83, 199, 27), (79, 196, 23),
                (84, 201, 29), (76, 194, 21), (86, 202, 31), (80, 198, 25),
                # Slightly darker/lighter variations
                (70, 180, 20), (90, 210, 35), (65, 175, 15), (95, 215, 40),
            ],
            'swamp': [
                # Exact color from map: #949947 = (148, 153, 71)
                (148, 153, 71),
                # Variations around swamp olive/brown
                (145, 150, 68), (150, 155, 74), (143, 148, 65), (152, 157, 76),
                (144, 149, 67), (151, 156, 75), (146, 151, 69), (149, 154, 72),
                # Similar olive/brownish colors
                (147, 152, 70), (150, 155, 73), (145, 150, 68), (151, 156, 74),
                # Slightly darker/lighter variations
                (140, 145, 65), (155, 160, 80), (135, 140, 60), (160, 165, 85),
            ],
            'desert': [
                # Exact color from map: #c4ba4b = (196, 186, 75)
                (196, 186, 75),
                # Variations around desert yellow
                (192, 182, 71), (200, 190, 79), (188, 178, 67), (204, 194, 83),
                (194, 184, 73), (198, 188, 77), (190, 180, 69), (202, 192, 81),
                # Similar yellowish colors
                (195, 185, 74), (197, 187, 76), (193, 183, 72), (199, 189, 78),
                # Slightly darker/lighter variations
                (185, 175, 65), (210, 200, 90), (180, 170, 60), (215, 205, 95),
            ],
            'snow': [
                # Exact color from map: #ffffff = (255, 255, 255)
                (255, 255, 255),
                # Pure whites and very light grays - prioritize whites
                (254, 254, 254), (253, 253, 253), (252, 252, 252), (251, 251, 251),
                (250, 250, 250), (249, 249, 249), (248, 248, 248), (247, 247, 247), (246, 246, 246),
                # Very light grays (snow shadows)
                (240, 240, 240), (235, 235, 235), (230, 230, 230), (225, 225, 225), (220, 220, 220),
                (245, 245, 245), (242, 242, 242), (238, 238, 238), (232, 232, 232), (228, 228, 228),
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
            # Calculate grid aspect ratio
            w = 40.0  # hex width in pixels (from frontend CSS)
            h = 35.0  # hex height in pixels (from frontend CSS)
            grid_aspect = (w * (grid_width + 0.5)) / (h * (grid_height * 0.75 + 0.25))
            img_aspect = img_width / img_height
            
            # If grid aspect ratio is very close to image aspect ratio (within 0.5%),
            # use the full image dimensions to avoid unused space
            aspect_diff = abs(grid_aspect - img_aspect) / img_aspect
            if aspect_diff < 0.005:  # Less than 0.5% difference
                # Use full image dimensions - scale to fill width and height
                scale_x = img_width / grid_width
                scale_y = img_height / grid_height
                # Use the average scale to minimize distortion
                scale = (scale_x + scale_y) / 2
                scaled_width = img_width  # Use full width
                scaled_height = img_height  # Use full height
                x_offset = 0
                y_offset = 0
            else:
                # Standard letterbox: use the smaller scale to preserve aspect ratio
                scale = min(img_width / grid_width, img_height / grid_height)
                scaled_width = grid_width * scale
                scaled_height = grid_height * scale
                # Center the scaled image within the original image bounds
                x_offset = (img_width - scaled_width) / 2
                y_offset = (img_height - scaled_height) / 2
            # Map hex positions (1-based) to cover the full mapped area
            # hex 1 maps to left edge, hex N maps to right edge (but not beyond image bounds)
            # When using full image, map hex N to pixel (img_width - 1), not img_width
            if grid_width > 1:
                # Map hex positions 1..N to pixel range 0..(scaled_width-1) when using full image
                # or to the mapped area bounds when letterboxing
                if x_offset == 0 and scaled_width == img_width:
                    # Using full image: map to 0..(img_width-1)
                    pixel_x_f = (hex_x - 1) / (grid_width - 1) * (img_width - 1)
                else:
                    # Letterbox mode: map to mapped area
                    pixel_x_f = x_offset + (hex_x - 1) / (grid_width - 1) * scaled_width
            else:
                pixel_x_f = x_offset + scaled_width / 2
            if grid_height > 1:
                if y_offset == 0 and scaled_height == img_height:
                    # Using full image: map to 0..(img_height-1)
                    pixel_y_f = (hex_y - 1) / (grid_height - 1) * (img_height - 1)
                else:
                    # Letterbox mode: map to mapped area
                    pixel_y_f = y_offset + (hex_y - 1) / (grid_height - 1) * scaled_height
            else:
                pixel_y_f = y_offset + scaled_height / 2
            # Check if the center is within the mapped area (before clamping)
            in_image = (0 <= pixel_x_f < img_width) and (0 <= pixel_y_f < img_height)
            # Clamp after checking to handle edge cases
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
        
        # Use the same mapping mode as _hex_to_pixel_coordinates to ensure consistency
        if self.mapping_mode == "letterbox":
            # Calculate grid aspect ratio (same logic as _hex_to_pixel_coordinates)
            w = 40.0  # hex width in pixels (from frontend CSS)
            h = 35.0  # hex height in pixels (from frontend CSS)
            grid_aspect = (w * (grid_width + 0.5)) / (h * (grid_height * 0.75 + 0.25))
            img_aspect = img_width / img_height
            
            # If grid aspect ratio is very close to image aspect ratio (within 0.5%),
            # use the full image dimensions to avoid unused space
            aspect_diff = abs(grid_aspect - img_aspect) / img_aspect
            if aspect_diff < 0.005:  # Less than 0.5% difference
                # Use full image dimensions
                scale_x = img_width / grid_width
                scale_y = img_height / grid_height
                scale = (scale_x + scale_y) / 2
                scaled_width = img_width
                scaled_height = img_height
                x_offset = 0
                y_offset = 0
            else:
                # Standard letterbox: use the smaller scale to preserve aspect ratio
                scale = min(img_width / grid_width, img_height / grid_height)
                scaled_width = grid_width * scale
                scaled_height = grid_height * scale
                x_offset = (img_width - scaled_width) / 2
                y_offset = (img_height - scaled_height) / 2
            # Map hex regions to cover the full mapped area
            # When using full image, map hex N to pixel (img_width - 1), not img_width
            if grid_width > 1:
                if x_offset == 0 and scaled_width == img_width:
                    # Using full image: map to 0..(img_width-1)
                    left_f = (hex_x - 1) / grid_width * img_width
                    right_f = hex_x / grid_width * img_width
                    # Ensure rightmost hex doesn't exceed bounds
                    if hex_x == grid_width:
                        right_f = img_width
                else:
                    # Letterbox mode: map to mapped area
                    left_f = x_offset + (hex_x - 1) / grid_width * scaled_width
                    right_f = x_offset + hex_x / grid_width * scaled_width
            else:
                left_f = x_offset
                right_f = x_offset + scaled_width
            if grid_height > 1:
                if y_offset == 0 and scaled_height == img_height:
                    # Using full image: map to 0..(img_height-1)
                    top_f = (hex_y - 1) / grid_height * img_height
                    bottom_f = hex_y / grid_height * img_height
                    # Ensure bottommost hex doesn't exceed bounds
                    if hex_y == grid_height:
                        bottom_f = img_height
                else:
                    # Letterbox mode: map to mapped area
                    top_f = y_offset + (hex_y - 1) / grid_height * scaled_height
                    bottom_f = y_offset + hex_y / grid_height * scaled_height
            else:
                top_f = y_offset
                bottom_f = y_offset + scaled_height
            # Region bounds in image (convert to int for pixel sampling)
            left = int(max(0, left_f))
            right = int(min(img_width, right_f))
            top = int(max(0, top_f))
            bottom = int(min(img_height, bottom_f))
        elif self.mapping_mode == "stretch":
            # Stretch to fill - may distort aspect ratio
            scale_x = img_width / grid_width
            scale_y = img_height / grid_height
            left = int((hex_x - 1) * scale_x)
            right = int(hex_x * scale_x)
            top = int((hex_y - 1) * scale_y)
            bottom = int(hex_y * scale_y)
            x_offset = 0
            y_offset = 0
        elif self.mapping_mode == "crop":
            # Crop to fill - may cut off parts of image
            scale_x = img_width / grid_width
            scale_y = img_height / grid_height
            scale = min(scale_x, scale_y)
            x_offset = int((img_width - grid_width * scale) / 2)
            y_offset = int((img_height - grid_height * scale) / 2)
            left = int((hex_x - 1) * scale + x_offset)
            right = int(hex_x * scale + x_offset)
            top = int((hex_y - 1) * scale + y_offset)
            bottom = int(hex_y * scale + y_offset)
        else:
            # Default to letterbox for safety
            scale = min(img_width / grid_width, img_height / grid_height)
            scaled_width = grid_width * scale
            scaled_height = grid_height * scale
            x_offset = int((img_width - scaled_width) / 2)
            y_offset = int((img_height - scaled_height) / 2)
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
        
        # Terrain detection heuristics
        def is_sea_color(r: int, g: int, b: int) -> bool:
            """Detect deep sea colors - #22478e (34, 71, 142) dark blue."""
            # Exact match: #22478e = (34, 71, 142) - blue dominant, darker
            if 25 <= r <= 45 and 60 <= g <= 85 and 130 <= b <= 155:
                return True
            # Blue is the dominant channel and darker
            if b > max(r, g) + 50 and b < 160 and r < 50 and g < 90:
                return True
            # Blue is high and red/green are relatively low (darker blues)
            if b > 120 and b < 160 and r < b - 80 and g < b - 50:
                return True
            # Classic deep blue water: low red, medium green, high blue (but not too light)
            if r < 50 and g < 90 and 120 < b < 160:
                return True
            return False
        
        def is_river_color(r: int, g: int, b: int) -> bool:
            """Detect river colors - #87a9eb (135, 169, 235) light blue."""
            # Exact match: #87a9eb = (135, 169, 235)
            if 130 <= r <= 140 and 165 <= g <= 175 and 230 <= b <= 240:
                return True
            # Light blue: blue is clearly dominant and bright
            if b > 200 and b > max(r, g) + 40 and r > 120 and g > 150:
                return True
            # Lighter blues with more green (cyan-ish) - blue still dominant
            if b > 180 and g > 140 and r > 100 and b > r + 30 and b > g + 20:
                return True
            # Soft cyan-blues: high blue and green, but blue is higher
            if 180 < b < 250 and 140 < g < 200 and 100 < r < 160 and b > r + 50 and b > g + 30:
                return True
            return False
        
        def is_bridge_color(r: int, g: int, b: int) -> bool:
            """Detect bridge colors - #818b9a (129, 139, 154) gray."""
            # Exact match: #818b9a = (129, 139, 154)
            if 120 <= r <= 140 and 130 <= g <= 150 and 145 <= b <= 165:
                return True
            # Gray: all channels similar and moderate
            if 110 < r < 150 and 120 < g < 160 and 135 < b < 175:
                if abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 30:
                    return True
            return False
        
        def is_snow_color(r: int, g: int, b: int) -> bool:
            """Detect snow - pure whites and very light grays."""
            # Pure white or near-white (very aggressive)
            if r > 240 and g > 240 and b > 240:
                return True
            # Very bright - all channels very high
            if r > 230 and g > 230 and b > 230:
                return True
            # Very light gray (snow shadows) - all channels high and similar
            if r > 220 and g > 220 and b > 220 and abs(r - g) < 15 and abs(g - b) < 15:
                return True
            # Light gray - all channels moderately high and similar (more lenient)
            if r > 200 and g > 200 and b > 200 and abs(r - g) < 20 and abs(g - b) < 20:
                return True
            # Pure white (255, 255, 255) or very close
            if r >= 250 and g >= 250 and b >= 250:
                return True
            return False
        
        def is_desert_color(r: int, g: int, b: int) -> bool:
            """Detect desert - #c4ba4b (196, 186, 75) yellow."""
            # Exclude whites (those are snow)
            if r > 240 and g > 240 and b > 240:
                return False
            # Exact match: #c4ba4b = (196, 186, 75) - high red/green, lower blue
            if 185 <= r <= 210 and 175 <= g <= 200 and 65 <= b <= 90:
                return True
            # Yellow: high red and green, lower blue
            if r > 180 and g > 170 and b < r - 100 and b < g - 90:
                return True
            # Golden yellow: high red, high green, moderate blue
            if r > 180 and g > 160 and 50 < b < 100 and g > b + 80:
                return True
            # Sandy yellow: all channels high but red/green dominant
            if r > 180 and g > 170 and 60 < b < 100 and r > b + 100 and g > b + 90:
                return True
            return False
        
        def is_plains_color(r: int, g: int, b: int) -> bool:
            """Detect plains - #51c51a (81, 197, 26) bright green."""
            # Exclude blues - if blue is clearly dominant, it's not plains
            if b > max(r, g) + 25:
                return False
            # Exact match: #51c51a = (81, 197, 26) - green is very high, red moderate, blue low
            if 70 <= r <= 95 and 180 <= g <= 210 and 15 <= b <= 40:
                return True
            # Very bright green: high green, green clearly dominant
            if g > 180 and g > r + 100 and g > b + 150:
                return True
            # Bright green: high green, green clearly dominant (more lenient)
            if g > 150 and g > r + 80 and g > b + 120:
                return True
            # Light green: green is clearly dominant and bright (even more lenient)
            if g > 120 and g > r + 60 and g > b + 90:
                return True
            return False
        
        def is_swamp_color(r: int, g: int, b: int) -> bool:
            """Detect swamp - #949947 (148, 153, 71) olive/brown."""
            # Exclude bright greens (those are plains)
            if g > 180 and g > max(r, b) + 100:
                return False
            # Exact match: #949947 = (148, 153, 71) - all channels moderate, green slightly higher
            if 140 <= r <= 160 and 145 <= g <= 165 and 60 <= b <= 85:
                return True
            # Olive/brown: moderate red/green, lower blue
            if 130 < r < 170 and 140 < g < 170 and 60 < b < 90:
                if abs(r - g) < 15 and b < min(r, g) - 50:
                    return True
            # Brownish: all channels moderate, red/green higher than blue
            if 130 < r < 170 and 140 < g < 170 and 60 < b < 90 and r > b + 60 and g > b + 70:
                return True
            return False
        
        terrain_scores: Dict[str, float] = {}
        color_matches: Dict[str, List[Tuple[int, int, int]]] = {t: [] for t in self.terrain_colors}
        # Use different tolerances for different terrains
        terrain_tolerances = {
            'sea': 50,      # More lenient for sea colors
            'river': 45,    # Lenient for river colors
            'bridge': 40,   # Lenient for bridge (grays vary)
            'plains': 40,   # Lenient for plains (bright greens vary)
            'swamp': 40,   # Lenient for swamp (brownish colors vary)
            'desert': 35,  # Moderate for desert
            'snow': 50,    # More lenient for snow (whites can vary slightly)
            'unknown': 30,
        }
        default_tolerance = 30
        
        for color in colors:
            r, g, b = color
            best_terrain = 'unknown'
            best_dist = float('inf')
            palette_distances = {}
            
            # First, check heuristics (priority order matters)
            # Check water types BEFORE plains to avoid blues being misclassified
            heuristic_match = None
            if is_snow_color(r, g, b):
                heuristic_match = 'snow'
            elif is_bridge_color(r, g, b):
                heuristic_match = 'bridge'  # Check bridge early
            elif is_river_color(r, g, b):
                heuristic_match = 'river'  # Check river BEFORE plains to catch light blues
            elif is_sea_color(r, g, b):
                heuristic_match = 'sea'  # Check sea before plains too
            elif is_plains_color(r, g, b):
                heuristic_match = 'plains'  # Check plains after water to catch bright greens
            elif is_desert_color(r, g, b):
                heuristic_match = 'desert'
            elif is_swamp_color(r, g, b):
                heuristic_match = 'swamp'
            
            # Also check palette distances
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
                if heuristic_match:
                    print(f"  -> heuristic match: {heuristic_match}")
            
            # Use heuristic if it matches, otherwise use palette distance
            final_terrain = best_terrain
            if heuristic_match:
                # ALWAYS prefer heuristic for snow - it should never be overridden
                if heuristic_match == 'snow':
                    final_terrain = 'snow'
                # Prefer heuristic for desert/plains/river/sea/bridge to avoid conflicts
                elif heuristic_match in ('desert', 'plains', 'river', 'sea', 'bridge'):
                    final_terrain = heuristic_match
                # For swamp, trust heuristic if palette match is weak
                elif heuristic_match == 'swamp' and best_dist > 35:
                    final_terrain = heuristic_match
            
            # Check if color matches any terrain within tolerance
            tolerance = terrain_tolerances.get(final_terrain, default_tolerance)
            # For snow, always trust the heuristic if it matched
            if heuristic_match == 'snow':
                terrain_scores['snow'] = terrain_scores.get('snow', 0) + 1
                color_matches['snow'].append(color)
            elif best_dist <= tolerance or (heuristic_match and final_terrain == heuristic_match):
                terrain_scores[final_terrain] = terrain_scores.get(final_terrain, 0) + 1
                color_matches[final_terrain].append(color)
            else:
                # Fallback: use heuristic if available
                if heuristic_match:
                    terrain_scores[heuristic_match] = terrain_scores.get(heuristic_match, 0) + 1
                    color_matches[heuristic_match].append(color)
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