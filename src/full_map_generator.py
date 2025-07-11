#!/usr/bin/env python3
"""
Complete Map Generator for The Dying Lands
Generates the entire 25x30 hex map with terrain-aware content and lore placement.
"""

import os
import random
from typing import Dict, List, Tuple, Optional
import dying_lands_generator
from mork_borg_lore_database import MorkBorgLoreDatabase

# Translation system
TRANSLATIONS = {
    'en': {
        'generating_full_map': 'Generating Full Map',
        'map_size': 'Map Size',
        'language': 'Language',
        'generation_complete': 'Generation Complete',
        'creating_ascii_map': 'Creating ASCII Map'
    },
    'pt': {
        'generating_full_map': 'Gerando Mapa Completo',
        'map_size': 'Tamanho do Mapa',
        'language': 'Idioma',
        'generation_complete': 'Geração Completa',
        'creating_ascii_map': 'Criando Mapa ASCII'
    }
}

CURRENT_LANG = 'en'

def t(key):
    """Translate a key to the current language."""
    return TRANSLATIONS.get(CURRENT_LANG, {}).get(key, key)

def generate_lore_hex_content(hex_code, hardcoded_data, language='en'):
    """Generate content for lore-specific hexes (cities, special locations)."""
    location_type = hardcoded_data.get('type', 'special_location')
    name = hardcoded_data.get('name', f'Unknown Location {hex_code}')
    description = hardcoded_data.get('description', 'A mysterious location of unknown origin.')
    terrain = hardcoded_data.get('terrain', 'plains')
    
    hex_data = {
        'hex_code': hex_code,
        'terrain': terrain,
        'encounter': f"Major Location: {name}",
        'denizen': f"**{name}** - {location_type.replace('_', ' ').title()}\n\n{description}",
        'notable_feature': '\n'.join(hardcoded_data.get('notable_features', ['Ancient and mysterious location'])),
        'atmosphere': hardcoded_data.get('atmosphere', 'Ancient and mysterious'),
        'lore_location': True,
        'location_type': location_type
    }
    
    # Add special content based on location type
    if location_type == 'major_city':
        hex_data['population'] = hardcoded_data.get('population', 'Unknown')
        hex_data['encounter'] = f"Major City: {name} (Population: {hardcoded_data.get('population', 'Unknown')})"
        
        # Add key NPCs to denizen description
        key_npcs = hardcoded_data.get('key_npcs', [])
        if key_npcs:
            hex_data['denizen'] += f"\n\n**Key NPCs:** {', '.join(key_npcs)}"
            
    elif location_type == 'special_location':
        hex_data['special_properties'] = hardcoded_data.get('special_properties', [])
    
    return hex_data

# Simple terrain detection without external dependencies
def get_terrain_for_hex(hex_code: str, lore_db: MorkBorgLoreDatabase) -> str:
    """Get terrain type for a specific hex using coordinate heuristics."""
    x, y = int(hex_code[:2]), int(hex_code[2:])
    
    # Check for hardcoded lore locations first
    hardcoded = lore_db.get_hardcoded_hex(hex_code)
    if hardcoded and hardcoded.get('locked', False):
        return hardcoded['terrain']
    
    # Simple coordinate-based terrain detection
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

# Map dimensions
MAP_WIDTH, MAP_HEIGHT = 25, 30
START_X, START_Y = 1, 1

def generate_full_map(language='en', skip_existing=True):
    """Generate content for the entire map."""
    global CURRENT_LANG
    CURRENT_LANG = language
    
    # Also set the language in the dying_lands_generator module
    dying_lands_generator.CURRENT_LANG = language
    
    print(f"🗺️ {t('generating_full_map')}...")
    print(f"📍 {t('map_size')}: {MAP_WIDTH}x{MAP_HEIGHT} hexes")
    print(f"🎯 {t('language')}: {language}")
    
    create_output_dirs()
    
    # Initialize lore database
    lore_db = MorkBorgLoreDatabase()
    
    all_hex_data = []
    generated_count = 0
    skipped_count = 0
    
    # Generate content for each hex
    for x in range(START_X, START_X + MAP_WIDTH):
        for y in range(START_Y, START_Y + MAP_HEIGHT):
            hex_code = f"{x:02d}{y:02d}"
            hex_file = f"dying_lands_output/hexes/hex_{hex_code}.md"
            
            # Skip if file exists and skip_existing is True
            if skip_existing and os.path.exists(hex_file):
                print(f"⏭️  Skipping existing hex {hex_code}")
                skipped_count += 1
                continue
            
            print(f"🎲 Generating hex {hex_code}...")
            
            # Check for hardcoded lore locations first
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('locked', False):
                # Use lore-specific content for hardcoded locations
                hex_data = generate_lore_hex_content(hex_code, hardcoded, language)
            else:
                # Generate terrain-aware content using simple detection
                terrain = get_terrain_for_hex(hex_code, lore_db)
                hex_data = dying_lands_generator.generate_hex_content(hex_code, terrain)
            
            all_hex_data.append(hex_data)
            
            # Write individual hex file
            dying_lands_generator.write_hex_file(hex_data)
            generated_count += 1
    
    # Update summary file
    dying_lands_generator.write_summary_file(all_hex_data)
    
    # Create simple ASCII map
    create_simple_ascii_map(all_hex_data, lore_db)
    
    print(f"\n✅ {t('generation_complete')}!")
    print(f"📊 Generated: {generated_count} hexes")
    print(f"⏭️  Skipped: {skipped_count} existing hexes")
    print(f"📁 Files in 'dying_lands_output/' directory")
    
    return all_hex_data

def create_output_dirs():
    """Create necessary output directories."""
    dirs = [
        'dying_lands_output',
        'dying_lands_output/hexes',
        'dying_lands_output/npcs'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def create_simple_ascii_map(hex_data_list, lore_db):
    """Create a simple ASCII representation of the map."""
    print(f"\n🎨 {t('creating_ascii_map')}...")
    
    # Create a grid to hold hex representations
    grid = {}
    for x in range(START_X, START_X + MAP_WIDTH):
        for y in range(START_Y, START_Y + MAP_HEIGHT):
            hex_code = f"{x:02d}{y:02d}"
            terrain = get_terrain_for_hex(hex_code, lore_db)
            
            # Check for major cities
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('type') == 'major_city':
                symbol = '◆'
            else:
                symbol = get_terrain_symbol(terrain)
            
            grid[(x, y)] = symbol
    
    # Generate ASCII map
    ascii_lines = []
    ascii_lines.append("🗺️ THE DYING LANDS - FULL MAP")
    ascii_lines.append("=" * 50)
    ascii_lines.append("")
    ascii_lines.append("Legend:")
    ascii_lines.append("  ^ = Mountain    ♠ = Forest    ~ = Coast")
    ascii_lines.append("  . = Plains     # = Swamp     ◆ = Major City")
    ascii_lines.append("")
    
    # Create coordinate headers
    header = "    "
    for x in range(START_X, START_X + MAP_WIDTH):
        if x % 5 == 0:
            header += f"{x:02d}"
        else:
            header += "  "
    ascii_lines.append(header)
    ascii_lines.append("")
    
    # Create map rows
    for y in range(START_Y, START_Y + MAP_HEIGHT):
        line = f"{y:02d}  "
        for x in range(START_X, START_X + MAP_WIDTH):
            if (x, y) in grid:
                symbol = grid[(x, y)]
                line += f"[{symbol}]" if symbol == '◆' else f" {symbol} "
            else:
                line += " ? "
        ascii_lines.append(line)
    
    # Add city information
    ascii_lines.append("")
    ascii_lines.append("🏰 MAJOR CITIES:")
    ascii_lines.append("-" * 30)
    for city_key, city_data in lore_db.major_cities.items():
        x, y = city_data['coordinates']
        ascii_lines.append(f"◆ {city_data['name']} ({x:02d},{y:02d}) - {city_data['region'].title()}")
    
    ascii_map = "\n".join(ascii_lines)
    
    # Save ASCII map
    ascii_file = 'dying_lands_output/ascii_map.txt'
    with open(ascii_file, 'w', encoding='utf-8') as f:
        f.write(ascii_map)
    
    print(f"🗺️ ASCII map saved to {ascii_file}")
    return ascii_map

def get_terrain_symbol(terrain):
    """Get ASCII symbol for terrain type."""
    symbols = {
        'mountain': '^',
        'forest': '♠',
        'coast': '~',
        'plains': '.',
        'swamp': '#',
        'unknown': '?'
    }
    return symbols.get(terrain, '?')

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate complete Dying Lands map')
    parser.add_argument('--language', choices=['en', 'pt'], default='en',
                        help='Language for generated content')
    parser.add_argument('--regenerate', action='store_true',
                        help='Regenerate all hexes (skip existing files)')
    
    args = parser.parse_args()
    
    skip_existing = not args.regenerate
    hex_data = generate_full_map(args.language, skip_existing)
    
    print(f"\n🎉 Process complete! Check 'dying_lands_output/' directory.")
    print(f"🌐 Launch web viewer: python3 src/ascii_map_viewer.py")

if __name__ == "__main__":
    main() 