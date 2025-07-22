#!/usr/bin/env python3
"""
Unified Terrain System for The Dying Lands
Handles all terrain detection, analysis, and generation.
"""

import cv2
import numpy as np
import os
import random
from typing import Dict, Tuple, Optional, List
from enum import Enum
import json

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
    """Unified terrain system for The Dying Lands."""
    DEFAULT_TERRAIN_TYPES = [
        'mountain', 'forest', 'coast', 'plains', 'swamp', 'desert', 'sea', 'unknown'
    ]
    DEFAULT_BOUNDARIES = {
        'continent_x_min': 2, 'continent_x_max': 23,
        'continent_y_min': 3, 'continent_y_max': 27,
        'western_coast_x': 4, 'eastern_mountain_x': 21,
        'northern_forest_y': 10, 'southern_swamp_y': 22,
        'central_forest_x_min': 6, 'central_forest_x_max': 15,
        'central_belt_x_min': 8, 'central_belt_x_max': 16,
        'central_belt_y_min': 12, 'central_belt_y_max': 18,
        'southern_y': 20, 'eastern_mountain_x2': 18,
    }
    def __init__(self, use_image_analysis: bool = True, config_path: str = None):
        self.use_image_analysis = use_image_analysis
        self.terrain_cache = {}
        self.image_analyzer = None
        self.terrain_types = self.DEFAULT_TERRAIN_TYPES.copy()
        self.boundaries = self.DEFAULT_BOUNDARIES.copy()
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        if use_image_analysis:
            self._initialize_image_analyzer()
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if 'terrain_types' in config:
                self.terrain_types = config['terrain_types']
            if 'boundaries' in config:
                self.boundaries.update(config['boundaries'])
            print(f"✅ Loaded terrain config from {config_path}")
        except Exception as e:
            print(f"⚠️  Failed to load terrain config: {e}")
    def reload_config(self, config_path: str):
        self._load_config(config_path)
        self.clear_cache()
    def _initialize_image_analyzer(self):
        """Initialize image-based terrain analysis if images are available."""
        try:
            from image_analyzer import image_analyzer
            self.image_analyzer = image_analyzer
            if image_analyzer.is_available():
                print("✅ Official Mork Borg map analysis enabled")
                print(f"   Map info: {image_analyzer.get_map_info()}")
                self.use_image_analysis = True
            else:
                print("✅ Coordinate-based terrain analysis enabled")
                self.use_image_analysis = False
        except Exception as e:
            print(f"⚠️  Image analysis disabled: {e}")
            self.use_image_analysis = False
    def get_terrain_for_hex(self, hex_code: str, lore_db=None) -> str:
        """Get terrain type for a hex using the best available method."""
        if hex_code in self.terrain_cache:
            return self.terrain_cache[hex_code]
        # Check for hardcoded lore locations first
        if lore_db:
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('locked', False):
                terrain = hardcoded.get('terrain', 'plains')
                if terrain not in self.terrain_types:
                    print(f"⚠️  Unknown terrain type in lore: {terrain}")
                self.terrain_cache[hex_code] = terrain
                return terrain
        # Try image analysis if available
        if self.use_image_analysis and self.image_analyzer:
            try:
                terrain = self.image_analyzer.get_terrain_for_hex(hex_code)
                if terrain and terrain != 'unknown':
                    if terrain not in self.terrain_types:
                        print(f"⚠️  Unknown terrain type from image analysis: {terrain}")
                    self.terrain_cache[hex_code] = terrain
                    return terrain
            except Exception as e:
                print(f"⚠️  Image analysis failed for hex {hex_code}: {e}")
        # Fallback to coordinate-based detection
        try:
            terrain = self._get_coordinate_based_terrain(hex_code)
            if terrain not in self.terrain_types:
                print(f"⚠️  Unknown terrain type from coordinate rules: {terrain}")
            self.terrain_cache[hex_code] = terrain
            return terrain
        except Exception as e:
            print(f"⚠️  Coordinate-based terrain detection failed for hex {hex_code}: {e}")
            self.terrain_cache[hex_code] = 'unknown'
            return 'unknown'
    def _get_coordinate_based_terrain(self, hex_code: str) -> str:
        """Get terrain based on hex coordinates using heuristics (now data-driven)."""
        try:
            x, y = int(hex_code[:2]), int(hex_code[2:])
        except (ValueError, IndexError):
            return 'plains'
        b = self.boundaries
        # Define continent boundaries
        if (x < b['continent_x_min'] or x > b['continent_x_max'] or 
            y < b['continent_y_min'] or y > b['continent_y_max']):
            return 'sea'
        # Western coast
        if x <= b['western_coast_x']:
            if y <= b['northern_forest_y']:
                return 'coast'
            elif y >= b['southern_swamp_y']:
                return 'swamp'
            else:
                return 'plains'
        # Eastern mountains
        elif x >= b['eastern_mountain_x']:
            return 'mountain'
        # Central regions
        else:
            # Northern forests
            if y <= b['northern_forest_y']:
                if b['central_forest_x_min'] <= x <= b['central_forest_x_max']:
                    return 'forest'
                else:
                    return 'plains'
            # Southern regions
            elif y >= b['southern_y']:
                if x <= 10:
                    return 'swamp'
                elif x >= b['eastern_mountain_x2']:
                    return 'mountain'
                else:
                    return 'plains'
            # Central belt
            else:
                if (b['central_belt_x_min'] <= x <= b['central_belt_x_max'] and 
                    b['central_belt_y_min'] <= y <= b['central_belt_y_max']):
                    return 'forest'
                elif x >= b['eastern_mountain_x2']:
                    return 'mountain'
                else:
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
        """Get the map dimensions."""
        return (25, 30)  # Width, Height (X, Y)
    
    def create_terrain_overview_map(self) -> Dict[str, str]:
        """Create a terrain overview map for all hexes."""
        width, height = self.get_map_dimensions()
        terrain_map = {}
        
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                hex_code = f"{x:02d}{y:02d}"
                terrain = self.get_terrain_for_hex(hex_code)
                terrain_map[hex_code] = terrain
        
        return terrain_map
    
    def get_terrain_distribution(self) -> Dict[str, int]:
        """Get distribution of terrain types across the map."""
        terrain_map = self.create_terrain_overview_map()
        distribution = {}
        
        for terrain in terrain_map.values():
            distribution[terrain] = distribution.get(terrain, 0) + 1
        
        return distribution
    
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
                
                if 1 <= x <= 25 and 1 <= y <= 30:
                    hex_code = f"{x:02d}{y:02d}"
                    terrain = self.get_terrain_for_hex(hex_code)
                    region_terrain[terrain] = region_terrain.get(terrain, 0) + 1
        
        return region_terrain
    
    def clear_cache(self):
        """Clear the terrain cache."""
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
terrain_system = TerrainSystem() 