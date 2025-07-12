#!/usr/bin/env python3
"""
Refactored Map Generator for The Dying Lands
Uses unified terrain and hex generation systems for cleaner, more maintainable code.
"""

import os
import random
from typing import Dict, List, Tuple, Optional
from terrain_system import terrain_system
from hex_generator import HexGenerator
from translation_system import translation_system
from mork_borg_lore_database import MorkBorgLoreDatabase

class MapGenerator:
    """Refactored map generator using unified systems."""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.translation_system = translation_system
        self.translation_system.set_language(language)
        self.hex_generator = HexGenerator(language)
        self.lore_db = MorkBorgLoreDatabase()
        
        # Map dimensions
        self.map_width, self.map_height = terrain_system.get_map_dimensions()
        self.start_x, self.start_y = 1, 1
    
    def generate_full_map(self, skip_existing: bool = True) -> List[Dict]:
        """Generate content for the entire map."""
        print(f"🗺️ {self.translation_system.t('generating_full_map')}...")
        print(f"📍 {self.translation_system.t('map_size')}: {self.map_width}x{self.map_height} hexes")
        print(f"🎯 {self.translation_system.t('language')}: {self.language}")
        
        self._create_output_dirs()
        
        all_hex_data = []
        generated_count = 0
        skipped_count = 0
        
        # Generate content for each hex
        for x in range(self.start_x, self.start_x + self.map_width):
            for y in range(self.start_y, self.start_y + self.map_height):
                hex_code = f"{x:02d}{y:02d}"
                hex_file = f"dying_lands_output/hexes/hex_{hex_code}.md"
                
                # Skip if file exists and skip_existing is True
                if skip_existing and os.path.exists(hex_file):
                    print(f"⏭️  {self.translation_system.t('skipping_existing')} {hex_code}")
                    skipped_count += 1
                    continue
                
                print(f"🎲 {self.translation_system.t('generating_hex')} {hex_code}...")
                
                # Generate hex content using unified system
                hex_data = self.hex_generator.generate_hex_content(hex_code, lore_db=self.lore_db)
                all_hex_data.append(hex_data)
                
                # Write individual hex file
                self.hex_generator.write_hex_file(hex_data)
                generated_count += 1
        
        # Update summary file
        self.hex_generator.write_summary_file(all_hex_data)
        
        # Create ASCII map
        self._create_ascii_map(all_hex_data)
        
        print(f"\n✅ {self.translation_system.t('generation_complete')}!")
        print(f"📊 {self.translation_system.t('generated_hexes', count=generated_count)}")
        print(f"⏭️  {self.translation_system.t('skipping_existing')}: {skipped_count}")
        print(f"📁 Files in 'dying_lands_output/' directory")
        
        return all_hex_data
    
    def generate_single_hex(self, hex_code: str) -> Dict:
        """Generate content for a single hex."""
        print(f"🎲 {self.translation_system.t('generating_hex')} {hex_code}...")
        
        # Validate hex code format
        if not self._is_valid_hex_code(hex_code):
            raise ValueError(f"Invalid hex code format: {hex_code}. Expected XXYY format (e.g., 0101)")
        
        # Generate hex content
        hex_data = self.hex_generator.generate_hex_content(hex_code, lore_db=self.lore_db)
        
        # Write hex file
        self.hex_generator.write_hex_file(hex_data)
        
        print(f"✅ {self.translation_system.t('hex_generated', hex_code=hex_code)}")
        return hex_data
    
    def reset_continent(self) -> Dict:
        """Reset the entire continent and regenerate all content."""
        print(f"🔄 {self.translation_system.t('resetting_continent')}...")
        
        # Clear terrain cache
        terrain_system.clear_cache()
        
        # Remove existing output directory
        if os.path.exists('dying_lands_output'):
            import shutil
            shutil.rmtree('dying_lands_output')
        
        # Generate fresh content
        hex_data_list = self.generate_full_map(skip_existing=False)
        
        return {
            'success': True,
            'count': len(hex_data_list),
            'message': self.translation_system.t('continent_reset', count=len(hex_data_list))
        }
    
    def _create_output_dirs(self):
        """Create necessary output directories."""
        dirs = [
            'dying_lands_output',
            'dying_lands_output/hexes',
            'dying_lands_output/npcs'
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _is_valid_hex_code(self, hex_code: str) -> bool:
        """Validate hex code format."""
        if not hex_code.isdigit() or len(hex_code) != 4:
            return False
        
        x, y = int(hex_code[:2]), int(hex_code[2:])
        return 1 <= x <= self.map_width and 1 <= y <= self.map_height
    
    def _create_ascii_map(self, hex_data_list: List[Dict]):
        """Create a simple ASCII map overview."""
        print(f"🗺️ {self.translation_system.t('creating_ascii_map')}...")
        
        # Create terrain-based ASCII map
        terrain_map = terrain_system.create_terrain_overview_map()
        
        # Add content indicators
        content_map = {}
        for hex_data in hex_data_list:
            hex_code = hex_data['hex_code']
            if hex_data.get('is_settlement'):
                content_map[hex_code] = '⌂'
            elif hex_data.get('lore_location'):
                content_map[hex_code] = '◆'
            else:
                content_map[hex_code] = terrain_system.get_terrain_symbol(hex_data['terrain'])
        
        # Write ASCII map file
        self._write_ascii_map_file(content_map, terrain_map)
    
    def _write_ascii_map_file(self, content_map: Dict[str, str], terrain_map: Dict[str, str]):
        """Write ASCII map to file."""
        filename = "dying_lands_output/ascii_map.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("THE DYING LANDS - ASCII MAP\n")
            f.write("=" * 40 + "\n\n")
            
            # Write column headers
            f.write("   ")
            for x in range(1, self.map_width + 1):
                f.write(f"{x:2d} ")
            f.write("\n")
            
            # Write map rows
            for y in range(1, self.map_height + 1):
                f.write(f"{y:2d} ")
                for x in range(1, self.map_width + 1):
                    hex_code = f"{x:02d}{y:02d}"
                    symbol = content_map.get(hex_code, '?')
                    f.write(f" {symbol} ")
                f.write("\n")
            
            f.write("\nLEGEND:\n")
            f.write("◆ = Major Cities\n")
            f.write("⌂ = Settlements\n")
            f.write("^ = Mountains\n")
            f.write("♠ = Forest\n")
            f.write("~ = Coast\n")
            f.write(". = Plains\n")
            f.write("# = Swamp\n")
            f.write("? = Unknown\n")
    
    def get_terrain_overview(self) -> Dict:
        """Get terrain analysis overview."""
        terrain_map = terrain_system.create_terrain_overview_map()
        distribution = terrain_system.get_terrain_distribution()
        
        return {
            'success': True,
            'terrain_map': terrain_map,
            'dimensions': [self.map_width, self.map_height],
            'distribution': distribution
        }
    
    def get_lore_overview(self) -> Dict:
        """Get lore overview."""
        return {
            'success': True,
            'major_cities': len(self.lore_db.major_cities),
            'factions': len(self.lore_db.factions),
            'cities_data': [
                {
                    'hex_code': f"{coords[0]:02d}{coords[1]:02d}",
                    'name': data['name'],
                    'region': data['region'],
                    'population': data['population']
                }
                for data in self.lore_db.major_cities.values()
                for coords in [data['coordinates']]
            ],
            'factions_data': [
                {
                    'name': data['name'],
                    'influence': data['influence'],
                    'regions': data['regions']
                }
                for data in self.lore_db.factions.values()
            ]
        }

# Global map generator instance
map_generator = MapGenerator()

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate The Dying Lands map content')
    parser.add_argument('--language', '-l', default='en', choices=['en', 'pt'],
                       help='Language for content generation (default: en)')
    parser.add_argument('--hex', type=str, help='Generate single hex (XXYY format)')
    parser.add_argument('--reset', action='store_true', help='Reset continent and regenerate all')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip existing hex files (default: True)')
    
    args = parser.parse_args()
    
    # Initialize map generator
    generator = MapGenerator(args.language)
    
    try:
        if args.hex:
            # Generate single hex
            result = generator.generate_single_hex(args.hex)
            print(f"✅ Generated hex {args.hex}")
        elif args.reset:
            # Reset continent
            result = generator.reset_continent()
            print(f"✅ {result['message']}")
        else:
            # Generate full map
            result = generator.generate_full_map(skip_existing=args.skip_existing)
            print(f"✅ Generated {len(result)} hexes")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 