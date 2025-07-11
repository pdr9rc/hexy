#!/usr/bin/env python3
"""
Terrain Analyzer for The Dying Lands
Analyzes terrain from the campaign sheet PNG image to determine terrain types for each hex.
"""

import cv2
import numpy as np
import os
from typing import Dict, Tuple, Optional

class DyingLandsTerrainAnalyzer:
    """Analyzes terrain from PNG images for The Dying Lands."""
    
    def __init__(self):
        self.official_map_path = "../data/mork_borg_official_map.jpg"
        self.terrain_image_path = "../data/TheDyingLands-Terrain Sheet.png.png"
        self.campaign_image_path = "../data/TheDyingLands-Campaign Sheet.png"
        self.official_map = None
        self.terrain_image = None
        self.campaign_image = None
        self.terrain_cache = {}
        self.load_images()
        
    def load_images(self):
        """Load the official map and other images."""
        try:
            # Priority 1: Official Mörk Borg map
            if os.path.exists(self.official_map_path):
                self.official_map = cv2.imread(self.official_map_path)
                print(f"✅ Loaded official Mörk Borg map: {self.official_map.shape}")
                
            # Priority 2: Terrain sheet
            if os.path.exists(self.terrain_image_path):
                self.terrain_image = cv2.imread(self.terrain_image_path)
                print(f"✅ Loaded terrain sheet: {self.terrain_image.shape}")
            else:
                print(f"❌ Terrain sheet not found: {self.terrain_image_path}")
                
            # Priority 3: Campaign sheet
            if os.path.exists(self.campaign_image_path):
                self.campaign_image = cv2.imread(self.campaign_image_path)
                print(f"✅ Loaded campaign sheet: {self.campaign_image.shape}")
            else:
                print(f"❌ Campaign sheet not found: {self.campaign_image_path}")
                
        except Exception as e:
            print(f"❌ Error loading images: {e}")
            
    def get_terrain_for_hex(self, hex_code: str) -> str:
        """Get terrain type for a hex based on image analysis."""
        if hex_code in self.terrain_cache:
            return self.terrain_cache[hex_code]
            
        # Parse hex coordinates
        try:
            row = int(hex_code[:2])
            col = int(hex_code[2:])
        except:
            return 'plains'  # Default fallback
            
        terrain = self._analyze_hex_terrain(row, col)
        self.terrain_cache[hex_code] = terrain
        return terrain
        
    def _analyze_hex_terrain(self, row: int, col: int) -> str:
        """Analyze terrain type for specific hex coordinates."""
        # Try official map first
        if self.official_map is not None:
            terrain = self._analyze_from_official_map(row, col)
            if terrain:
                return terrain
                
        # Fallback to terrain sheet
        if self.terrain_image is not None:
            terrain = self._analyze_from_terrain_sheet(row, col)
            if terrain:
                return terrain
            
        # Final fallback to procedural generation
        return self._get_procedural_terrain(row, col)
        
    def _analyze_from_official_map(self, row: int, col: int) -> str:
        """Analyze terrain from the official Mörk Borg map."""
        try:
            img_height, img_width = self.official_map.shape[:2]
            
            # Map hex coordinates to image coordinates
            # The official map shows the canonical world layout
            hex_x = int((col - 1) * (img_width / 30))
            hex_y = int((row - 1) * (img_height / 25))
            
            # Sample a small area around the hex center
            sample_size = min(img_width // 40, img_height // 35, 5)
            x1 = max(0, hex_x - sample_size)
            x2 = min(img_width, hex_x + sample_size)
            y1 = max(0, hex_y - sample_size)
            y2 = min(img_height, hex_y + sample_size)
            
            # Extract color sample
            sample = self.official_map[y1:y2, x1:x2]
            avg_color = np.mean(sample, axis=(0, 1))
            return self._classify_official_map_terrain(avg_color)
        except:
            return None
            
    def _analyze_from_terrain_sheet(self, row: int, col: int) -> str:
        """Analyze terrain from the terrain sheet."""
        try:
            img_height, img_width = self.terrain_image.shape[:2]
            
            # Calculate pixel coordinates for this hex
            hex_x = int((col - 1) * (img_width / 30))
            hex_y = int((row - 1) * (img_height / 25))
            
            # Sample a small area around the hex center
            sample_size = min(img_width // 40, img_height // 35, 10)
            x1 = max(0, hex_x - sample_size)
            x2 = min(img_width, hex_x + sample_size)
            y1 = max(0, hex_y - sample_size)
            y2 = min(img_height, hex_y + sample_size)
            
            # Extract color sample
            sample = self.terrain_image[y1:y2, x1:x2]
            avg_color = np.mean(sample, axis=(0, 1))
            return self._classify_terrain_by_color(avg_color)
        except:
            return None
            
    def _classify_official_map_terrain(self, color: np.ndarray) -> str:
        """Classify terrain from the official Mörk Borg map colors."""
        b, g, r = color
        
        # Debug: Print color values for analysis
        # print(f"Color analysis: R={r:.1f}, G={g:.1f}, B={b:.1f}")
        
        # Color analysis specific to the official map
        # The official map has distinct visual styles for different regions
        
        # Water/Ocean: Blue colors (be more lenient for dark map)
        if b > 120 and (b > r + 15 or b > g + 15):
            return 'coast'
            
        # Additional water detection for lighter blues
        if b > r and b > g and b > 90:
            return 'coast'
            
        # Dark water detection for muted colors (common in official map)
        if b > 45 and g > 50 and r < 50 and abs(b - g) < 15:
            return 'coast'
            
        # Very dark water areas (edge regions)
        if r < 45 and g < 65 and b < 65 and (b >= r or g >= r):
            return 'coast'
            
        # Mountains: Dark gray/brown regions  
        if r < 120 and g < 120 and b < 120 and max(r, g, b) - min(r, g, b) < 40:
            return 'mountain'
            
        # Forests: Green areas
        if g > r + 20 and g > b + 10 and g > 100:
            return 'forest'
            
        # Swamps: Dark mixed colors
        if r > 80 and g > 80 and b < 100 and abs(r - g) < 30:
            return 'swamp'
            
        # Desert/Wasteland: Yellow/tan areas
        if r > 140 and g > 120 and b < 100:
            return 'desert'
            
        # Plains: Light areas
        return 'plains'
        
    def _classify_terrain_by_color(self, color: np.ndarray) -> str:
        """Classify terrain type based on average color (generic method)."""
        b, g, r = color
        
        # Color thresholds for different terrains (BGR format)
        # These are rough estimates - adjust based on actual terrain sheet colors
        
        # Mountains: Gray/brown colors
        if r < 100 and g < 100 and b < 100:  # Dark colors
            return 'mountain'
            
        # Forest: Green colors
        if g > r and g > b and g > 80:
            return 'forest'
            
        # Water/Coast: Blue colors
        if b > r and b > g and b > 100:
            return 'coast'
            
        # Swamp: Dark green/brown
        if g > 60 and r > 60 and b < 80:
            return 'swamp'
            
        # Desert: Yellow/tan colors
        if r > 120 and g > 100 and b < 80:
            return 'desert'
            
        # Default to plains for light colors
        return 'plains'
        
    def _get_procedural_terrain(self, row: int, col: int) -> str:
        """Generate terrain procedurally when image analysis fails."""
        # Use position-based rules to create realistic terrain distribution
        
        # Mountains in the north and scattered throughout
        if row <= 5 or (row <= 10 and (col % 7 == 0 or (row + col) % 11 == 0)):
            return 'mountain'
            
        # Forests scattered throughout, more common in northwest
        if (row + col) % 13 == 0 or (row <= 12 and col <= 10 and (row + col) % 8 == 0):
            return 'forest'
            
        # Coast along edges
        if col == 1 or col == 30 or row == 1 or row == 25:
            if (row + col) % 3 == 0:
                return 'coast'
                
        # Swamps in low-lying areas
        if row >= 15 and col >= 15 and (row + col) % 17 == 0:
            return 'swamp'
            
        # Desert in the southeast
        if row >= 20 and col >= 20 and (row + col) % 9 == 0:
            return 'desert'
            
        # Default to plains
        return 'plains'
        
    def get_map_dimensions(self) -> Tuple[int, int]:
        """Get the standard map dimensions."""
        return 25, 30
        
    def create_terrain_overview_map(self) -> Dict[str, str]:
        """Create a complete terrain map for all hexes."""
        terrain_map = {}
        width, height = self.get_map_dimensions()
        
        for row in range(1, width + 1):
            for col in range(1, height + 1):
                hex_code = f"{row:02d}{col:02d}"
                terrain_map[hex_code] = self.get_terrain_for_hex(hex_code)
                
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
            center_row = int(center_hex[:2])
            center_col = int(center_hex[2:])
        except:
            return {}
            
        regional_terrain = {}
        
        for row in range(max(1, center_row - radius), min(26, center_row + radius + 1)):
            for col in range(max(1, center_col - radius), min(31, center_col + radius + 1)):
                hex_code = f"{row:02d}{col:02d}"
                terrain = self.get_terrain_for_hex(hex_code)
                regional_terrain[terrain] = regional_terrain.get(terrain, 0) + 1
                
        return regional_terrain

def main():
    """Test the terrain analyzer."""
    analyzer = DyingLandsTerrainAnalyzer()
    
    # Test some specific hexes
    test_hexes = ['0101', '0805', '1215', '2530', '1525']
    
    print("\n🗺️ Terrain Analysis Test:")
    for hex_code in test_hexes:
        terrain = analyzer.get_terrain_for_hex(hex_code)
        print(f"  Hex {hex_code}: {terrain}")
        
    # Show overall distribution
    distribution = analyzer.get_terrain_distribution()
    print(f"\n📊 Terrain Distribution:")
    for terrain, count in distribution.items():
        percentage = (count / 750) * 100
        print(f"  {terrain.title()}: {count} hexes ({percentage:.1f}%)")

if __name__ == "__main__":
    main() 