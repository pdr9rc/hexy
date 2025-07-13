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

class TerrainType(Enum):
    """Enumeration of terrain types."""
    MOUNTAIN = "mountain"
    FOREST = "forest"
    COAST = "coast"
    PLAINS = "plains"
    SWAMP = "swamp"
    DESERT = "desert"
    UNKNOWN = "unknown"

class TerrainSystem:
    """Unified terrain system for The Dying Lands."""
    
    def __init__(self, use_image_analysis: bool = True):
        self.use_image_analysis = use_image_analysis
        self.terrain_cache = {}
        self.image_analyzer = None
        
        if use_image_analysis:
            self._initialize_image_analyzer()
    
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
                self.terrain_cache[hex_code] = terrain
                return terrain
        
        # Try image analysis if available
        if self.use_image_analysis and self.image_analyzer:
            try:
                terrain = self.image_analyzer.get_terrain_for_hex(hex_code)
                if terrain and terrain != 'unknown':
                    self.terrain_cache[hex_code] = terrain
                    return terrain
            except Exception as e:
                print(f"⚠️  Image analysis failed for hex {hex_code}: {e}")
        
        # Fallback to coordinate-based detection
        terrain = self._get_coordinate_based_terrain(hex_code)
        self.terrain_cache[hex_code] = terrain
        return terrain
    
    def _get_coordinate_based_terrain(self, hex_code: str) -> str:
        """Get terrain based on hex coordinates using heuristics."""
        try:
            x, y = int(hex_code[:2]), int(hex_code[2:])
        except (ValueError, IndexError):
            return 'plains'
        
        # Western coast (x <= 4)
        if x <= 4:
            if y <= 10:
                return 'coast'
            elif y >= 22:
                return 'swamp'
            else:
                return 'plains'
        
        # Eastern mountains (x >= 22)
        elif x >= 22:
            return 'mountain'
        
        # Central regions
        else:
            # Northern forests (y <= 10)
            if y <= 10:
                if 5 <= x <= 15:
                    return 'forest'
                else:
                    return 'plains'
            
            # Southern regions (y >= 20)
            elif y >= 20:
                if x <= 10:
                    return 'swamp'
                elif x >= 18:
                    return 'mountain'
                else:
                    return 'plains'
            
            # Central belt
            else:
                if 8 <= x <= 16 and 12 <= y <= 18:
                    return 'forest'
                elif x >= 18:
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
            'unknown': '?'
        }
        return symbols.get(terrain, '?')
    
    def get_terrain_color(self, terrain: str) -> str:
        """Get CSS color class for terrain type."""
        return f'terrain-{terrain}'
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        """Get the map dimensions."""
        return (25, 30)  # Width, Height
    
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