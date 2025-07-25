#!/usr/bin/env python3
"""
Unified Terrain System for The Dying Lands
Handles all terrain detection, analysis, and generation.
"""

import cv2
import numpy as np
import os
import random
from typing import Dict, Tuple, Optional
from enum import Enum
import json
import math
try:
    from src.image_analyzer import ImageAnalyzer
except ImportError:
    from image_analyzer import ImageAnalyzer

class TerrainType(Enum):
    """Enumeration of terrain types."""
    MOUNTAIN = "mountain"
    FOREST = "forest"
    COAST = "coast"
    PLAINS = "plains"
    SWAMP = "swamp"
    DESERT = "desert"
    SEA = "sea"
    UNKNOWN = "unknown"

class TerrainSystem:
    """
    Unified terrain system for The Dying Lands.
    Handles terrain assignment using (in order):
    - Locked/hardcoded hexes
    - Image analysis
    - Coordinate-based fallback
    All logic is config-driven and supports any map size.
    """
    def __init__(self, map_width: int, map_height: int, image_path: Optional[str] = None, mapping_mode: str = "letterbox", debug: bool = False):
        # If image analysis is enabled and image is available, auto-set grid size to match image aspect ratio (flat-topped hexes)
        self.image_analyzer = None
        self.use_image_analysis = False
        if image_path:
            temp_width = map_width
            temp_height = map_height
            self.image_analyzer = ImageAnalyzer(image_path, temp_width, temp_height, mapping_mode=mapping_mode, debug=debug)
            if self.image_analyzer.map_image is not None:
                self.use_image_analysis = True
                img_width, img_height = self.image_analyzer.map_image.size
                img_aspect = img_width / img_height
                # Use actual frontend hex dimensions (flat-topped):
                w = 40.0  # px, from --hex-width-base
                h = 35.0  # px, from --hex-height-base
                grid_px_width = w * (temp_width + 0.5)
                # grid_px_height = h * (map_height * 0.75 + 0.25)
                # (w * (map_width + 0.5)) / (h * (map_height * 0.75 + 0.25)) = img_aspect
                map_height = int(round(((w * (temp_width + 0.5)) / (img_aspect * h) - 0.25) / 0.75))
                map_width = temp_width
        self.map_width = map_width
        self.map_height = map_height
        self.terrain_types = [
            'plains',    # .terrain-plains
            'forest',    # .terrain-forest
            'mountain',  # .terrain-mountain
            'coast',     # .terrain-coast
            'swamp',     # .terrain-swamp
            'desert',    # .terrain-desert
            'sea',       # .terrain-sea
            'road',      # .terrain-road
            'snow',      # .terrain-snow
            'unknown'    # .terrain-unknown (fallback)
        ]
        self.terrain_cache: Dict[str, str] = {}
        self.debug = debug

    def get_terrain_for_hex(self, hex_code: str, lore_db=None) -> str:
        if hex_code in self.terrain_cache:
            return self.terrain_cache[hex_code]
        # 1. Locked/hardcoded hexes
        if lore_db:
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('locked', False):
                terrain = hardcoded.get('terrain', 'plains')
                if self.debug:
                    print(f"[TerrainSystem] HEX {hex_code} locked: {terrain}")
                self.terrain_cache[hex_code] = terrain
                return terrain
        # 2. Image analysis
        if self.use_image_analysis and self.image_analyzer:
            try:
                terrain = self.image_analyzer.get_terrain_for_hex(hex_code)
                if terrain and terrain != 'unknown':
                    if self.debug:
                        print(f"[TerrainSystem] HEX {hex_code} image: {terrain}")
                    self.terrain_cache[hex_code] = terrain
                    return terrain
            except Exception as e:
                if self.debug:
                    print(f"[TerrainSystem] Image analysis failed for {hex_code}: {e}")
        # 3. Coordinate-based fallback
        terrain = self._get_coordinate_based_terrain(hex_code, lore_db)
        if self.debug:
            print(f"[TerrainSystem] HEX {hex_code} fallback: {terrain}")
        self.terrain_cache[hex_code] = terrain
        return terrain

    def analyze_image_colors_and_update_biases(self, lore_db=None):
        """Analyze the average color for each hex and compute new terrain biases based on image colors."""
        if not self.use_image_analysis or not self.image_analyzer:
            print("[TerrainSystem] Image analysis not available.")
            return
        import collections
        region_color_counts = collections.defaultdict(lambda: collections.Counter())
        region_terrain_counts = collections.defaultdict(lambda: collections.Counter())
        for x in range(1, self.map_width + 1):
            for y in range(1, self.map_height + 1):
                hex_code = f"{x:02d}{y:02d}"
                avg_color = self.image_analyzer.get_average_color_for_hex(x, y)
                # Find closest terrain by color
                best_terrain = 'unknown'
                best_dist = float('inf')
                for terrain, color_list in self.image_analyzer.terrain_colors.items():
                    for tcolor in color_list:
                        dist = sum(abs(c1 - c2) for c1, c2 in zip(avg_color, tcolor))
                        if dist < best_dist:
                            best_dist = dist
                            best_terrain = terrain
                if lore_db:
                    region = lore_db.get_regional_bias(x, y)
                else:
                    region = 'all'
                region_color_counts[region][avg_color] += 1
                region_terrain_counts[region][best_terrain] += 1
        # Print summary and suggested biases
        for region in region_terrain_counts:
            total = sum(region_terrain_counts[region].values())
            print(f"\n[TerrainSystem] Region: {region}")
            for terrain, count in region_terrain_counts[region].most_common():
                weight = round(count / total, 2) if total else 0
                print(f"  {terrain}: {count} ({weight})")
            print(f"  Suggested bias: {{ {', '.join(f'\'{t}\': {round(c/total,2)}' for t,c in region_terrain_counts[region].items())} }}")
        return region_terrain_counts

    def _get_coordinate_based_terrain(self, hex_code: str, lore_db=None) -> str:
        import random
        try:
            x, y = int(hex_code[:2]), int(hex_code[2:])
        except (ValueError, IndexError):
            return 'plains'
        if x < 1 or x > self.map_width or y < 1 or y > self.map_height:
            return 'sea'
        # Use image color-based bias if available
        # if self.use_image_analysis and self.image_analyzer:
        #     avg_color = self.image_analyzer.get_average_color_for_hex(x, y)
        #     best_terrain = 'unknown'
        #     best_dist = float('inf')
        #     for terrain, color_list in self.image_analyzer.terrain_colors.items():
        #         for tcolor in color_list:
        #             dist = sum(abs(c1 - c2) for c1, c2 in zip(avg_color, tcolor))
        #             if dist < best_dist:
        #                 best_dist = dist
        #                 best_terrain = terrain
        #     return best_terrain
        # Otherwise, use regional bias if available
        if lore_db:
            region = lore_db.get_regional_bias(x, y)
            bias = getattr(lore_db, 'regional_lore', {}).get(region, {}).get('terrain_bias', {})
            if bias:
                terrains, weights = zip(*bias.items())
                return random.choices(terrains, weights=weights, k=1)[0]
        return 'plains'

    def get_terrain_symbol(self, terrain: str) -> str:
        """Get ASCII symbol for terrain type."""
        symbols = {
            'mountain': '^',
            'forest': '♠',
            'coast': '~',
            'plains': '.',
            'swamp': '#',
            'desert': 'ä',
            'sea': '≈',
            'unknown': '?'
        }
        return symbols.get(terrain, '?')
    
    def get_terrain_color(self, terrain: str) -> str:
        """Get CSS color class for terrain type."""
        return f'terrain-{terrain}'
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        return self.map_width, self.map_height
    
    def create_terrain_overview_map(self) -> Dict[str, str]:
        overview = {}
        for x in range(1, self.map_width + 1):
            for y in range(1, self.map_height + 1):
                hex_code = f"{x:02d}{y:02d}"
                overview[hex_code] = self.get_terrain_for_hex(hex_code)
        return overview
    
    def get_terrain_distribution(self) -> Dict[str, int]:
        dist = {t: 0 for t in self.terrain_types}
        for x in range(1, self.map_width + 1):
            for y in range(1, self.map_height + 1):
                hex_code = f"{x:02d}{y:02d}"
                terrain = self.get_terrain_for_hex(hex_code)
                if terrain in dist:
                    dist[terrain] += 1
                else:
                    dist[terrain] = 1
        return dist
    
    def analyze_region(self, center_hex: str, radius: int = 3) -> Dict[str, int]:
        """Analyze terrain distribution in a region around a hex."""
        try:
            center_x, center_y = int(center_hex[:2]), int(center_hex[2:])
        except (ValueError, IndexError):
            return {}
        
        region_terrain = {}
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                if 1 <= x <= self.map_width and 1 <= y <= self.map_height:
                    hex_code = f"{x:02d}{y:02d}"
                    terrain = self.get_terrain_for_hex(hex_code)
                    region_terrain[terrain] = region_terrain.get(terrain, 0) + 1
        
        return region_terrain
    
    def clear_cache(self):
        self.terrain_cache.clear()
    
    def get_terrain_description(self, terrain: str, language: str = 'en') -> str:
        """Get a description of the terrain type."""
        descriptions = {
            'en': {
                'mountain': 'Rugged peaks and treacherous cliffs',
                'forest': 'Dense, cursed woodlands',
                'coast': 'Rocky shores and crashing waves',
                'plains': 'Rolling hills and open grasslands',
                'swamp': 'Misty bogs and stagnant waters',
                'desert': 'Barren wastelands and scorched earth',
                'unknown': 'Mysterious and uncharted territory'
            },
            'pt': {
                'mountain': 'Picos acidentados e penhascos traiçoeiros',
                'forest': 'Bosques densos e amaldiçoados',
                'coast': 'Costas rochosas e ondas quebrando',
                'plains': 'Colinas ondulantes e pastagens abertas',
                'swamp': 'Pântanos nebulosos e águas estagnadas',
                'desert': 'Terras áridas e solo queimado',
                'unknown': 'Território misterioso e inexplorado'
            }
        }
        return descriptions.get(language, descriptions['en']).get(terrain, 'Unknown terrain')

# Global terrain system instance
terrain_system = TerrainSystem(map_width=30, map_height=60) 