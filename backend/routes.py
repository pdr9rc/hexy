#!/usr/bin/env python3
"""
Flask Routes for The Dying Lands
Separated route definitions for better organization.
"""

import re
import logging
import traceback
from flask import Blueprint, jsonify, request, abort, render_template
from backend.config import get_config
from backend.utils import setup_project_paths, validate_hex_code

# Setup project paths for imports
setup_project_paths()

# Import after path setup
from backend.mork_borg_lore_database import MorkBorgLoreDatabase
from backend.terrain_system import terrain_system
from backend.main_map_generator import MainMapGenerator
from backend.translation_system import translation_system
from backend.city_overlay_analyzer import city_overlay_analyzer
from backend.hex_service import hex_service
from backend.hex_model import hex_manager

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize systems
config = get_config()
lore_db = MorkBorgLoreDatabase()
current_language = config.language

def get_main_map_generator():
    """Get main map generator with current language configuration."""
    global current_language
    return MainMapGenerator({'language': current_language})

# Initialize with default language
main_map_generator = get_main_map_generator()

# Add this normalization function near the top (after imports)
def normalize_terrain_name(name: str) -> str:
    name = name.strip().lower()
    mapping = {
        "plain": "plains",
        "plains": "plains",
        "forest": "forest",
        "mountain": "mountain",
        "mountains": "mountain",
        "coast": "coast",
        "swamp": "swamp",
        "desert": "desert",
        "sea": "sea",
        "ocean": "sea",
        "snow": "snow",
        "tundra": "snow",
        "unknown": "unknown",
    }
    return mapping.get(name, "unknown")

# ===== MAIN ROUTES =====

@main_bp.route('/')
def main_map():
    """Main map page with integrated lore."""
    config = get_config()
    
    if not config.paths.output_path.exists():
        config.paths.output_path.mkdir(parents=True, exist_ok=True)
        return render_template('setup.html', 
                             title="The Dying Lands - Setup", 
                             action="Run main_map_generator.py to create the map")
    
    # Auto-regenerate output if flag is set
    if getattr(config, 'auto_regenerate_output', False):
        print("[AUTO] Regenerating Dying Lands output (auto_regenerate_output=True)...")
        main_map_generator.generate_full_map()
    
    # Get map dimensions
    map_width, map_height = terrain_system.get_map_dimensions()
    
    # Generate ASCII map data
    ascii_map_data = generate_ascii_map_data()

    # If map is empty, regenerate and reload
    if not ascii_map_data:
        print("[AUTO] Map data empty, regenerating full map...")
        main_map_generator.generate_full_map()
        ascii_map_data = generate_ascii_map_data()
    
    # Ensure all keys are strings
    ascii_map_data = {str(k): v for k, v in ascii_map_data.items()}
    import json
    print("DEBUG: ascii_map_data sample:", json.dumps(dict(list(ascii_map_data.items())[:2]), indent=2))
    
    # Debug output
    print(f"DEBUG: Map dimensions: {map_width}x{map_height}")
    print(f"DEBUG: ASCII map data keys: {len(ascii_map_data.keys())}")
    print(f"DEBUG: Sample hex 0101: {ascii_map_data.get('0101', 'Not found')}")
    
    return render_template('main_map.html',
                         ascii_map=ascii_map_data,
                         map_width=map_width,
                         map_height=map_height,
                         major_cities=get_major_cities_data(),
                         total_hexes=map_width * map_height)

# ===== API ROUTES =====

@api_bp.route('/reset-continent', methods=['POST'])
def reset_continent():
    """Reset the entire continent and regenerate all content."""
    try:
        result = main_map_generator.reset_continent()
        # Clear hex service cache after reset
        hex_service.hex_data_cache.clear()
        hex_manager.clear_cache()
        logging.info("Continent reset and caches cleared.")
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error resetting continent: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/hex/<hex_code>')
def get_hex_info(hex_code):
    if not validate_hex_code(hex_code):
        return jsonify({'error': 'Invalid hex code format'}), 400

    hex_data = hex_service.get_hex_dict(hex_code)
    if hex_data:
        return jsonify(hex_data)

    # If not in cache, check for a hex file and parse it for content
    hex_file_path = config.paths.output_path / "hexes" / f"hex_{hex_code}.md"
    if hex_file_path.exists():
        from backend.utils import safe_file_read
        content = safe_file_read(hex_file_path)
        hex_type = _determine_hex_type(content)
        if hex_type == 'settlement':
            parsed = extract_settlement_data(content)
            return jsonify({
                "hex_code": hex_code,
                "hex_type": "settlement",
                "is_settlement": True,
                "is_major_city": False,
                "terrain": parsed.get('terrain', 'unknown'),
                "name": parsed.get('name'),
                "description": parsed.get('description'),
                "population": parsed.get('population'),
                "atmosphere": parsed.get('atmosphere'),
                "notable_feature": parsed.get('notable_feature'),
                "local_tavern": parsed.get('local_tavern'),
                "local_power": parsed.get('local_power'),
                "settlement_art": parsed.get('settlement_art'),
            })
        elif hex_type == 'beast':
            parsed = extract_beast_data(content)
            return jsonify({
                "hex_code": hex_code,
                "hex_type": "beast",
                "is_beast": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "beast_type": parsed.get('beast_type'),
                "beast_feature": parsed.get('beast_feature'),
                "beast_behavior": parsed.get('beast_behavior'),
                "denizen": parsed.get('denizen'),
                "territory": parsed.get('territory'),
                "threat_level": parsed.get('threat_level'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
                "loot": parsed.get('loot'),
                "magical_effect": parsed.get('magical_effect'),
            })
        elif hex_type == 'dungeon':
            parsed = extract_dungeon_data(content)
            return jsonify({
                "hex_code": hex_code,
                "hex_type": "dungeon",
                "is_dungeon": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "dungeon_type": parsed.get('dungeon_type'),
                "denizen": parsed.get('denizen'),
                "danger": parsed.get('danger'),
                "atmosphere": parsed.get('atmosphere'),
                "notable_feature": parsed.get('notable_feature'),
                "treasure": parsed.get('treasure'),
                "ancient_knowledge": parsed.get('ancient_knowledge'),
                "loot": parsed.get('loot'),
                "magical_effect": parsed.get('magical_effect'),
                "description": parsed.get('description'),
            })
        elif hex_type == 'npc':
            parsed = extract_npc_data(content)
            return jsonify({
                "hex_code": hex_code,
                "hex_type": "npc",
                "is_npc": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "name": parsed.get('name'),
                "denizen_type": parsed.get('denizen_type'),
                "motivation": parsed.get('motivation'),
                "feature": parsed.get('feature'),
                "demeanor": parsed.get('demeanor'),
                "location": parsed.get('location'),
                "key_npcs": parsed.get('key_npcs'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
                "description": parsed.get('description'),
                "denizen": parsed.get('denizen'),
            })
        elif hex_type == 'sea_encounter':
            parsed = extract_sea_encounter_data(content)
            return jsonify({
                "hex_code": hex_code,
                "hex_type": "sea_encounter",
                "is_sea_encounter": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "encounter_type": parsed.get('encounter_type'),
                "origin": parsed.get('origin'),
                "behavior": parsed.get('behavior'),
                "denizen": parsed.get('denizen'),
                "territory": parsed.get('territory'),
                "threat_level": parsed.get('threat_level'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
                "sunken_treasure": parsed.get('sunken_treasure'),
                "loot": parsed.get('loot'),
                "magical_effect": parsed.get('magical_effect'),
                "description": parsed.get('description'),
            })
        elif hex_type == 'ruins':
            parsed = extract_ruins_data(content)
            return jsonify({
                "hex_code": hex_code,
                "hex_type": "ruins",
                "is_ruins": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "description": parsed.get('description'),
                "danger": parsed.get('danger'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
            })
        else:
            parsed = extract_hex_data(content)
            return jsonify({
                "hex_code": hex_code,
                "terrain": parsed.get('terrain', 'unknown'),
                "exists": True,
                "hex_type": "wilderness",
                "is_settlement": False,
                "is_major_city": False,
                "description": parsed.get('description'),
                "encounter": parsed.get('encounter'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
            })

    # Default fallback for missing hexes
    return jsonify({
        "hex_code": hex_code,
        "terrain": "unknown",
        "exists": True,
        "hex_type": "wilderness",
        "is_settlement": False,
        "is_major_city": False,
        "description": None,
        "encounter": None,
        "notable_feature": None,
        "atmosphere": None,
    })

@api_bp.route('/city/<hex_code>')
def get_city_details(hex_code):
    """Get detailed information for a major city."""
    city_data = hex_service.get_city_details(hex_code)
    
    if city_data:
        return jsonify(city_data)
    else:
        return jsonify({'success': False, 'error': 'Not a major city'}), 404

@api_bp.route('/settlement/<hex_code>')
def get_settlement_details(hex_code):
    """Get detailed information for a settlement."""
    settlement_data = hex_service.get_settlement_details(hex_code)
    
    if settlement_data:
        return jsonify(settlement_data)
    else:
        return jsonify({'success': False, 'error': 'Not a settlement or not found'}), 404

@api_bp.route('/lore-overview')
def get_lore_overview():
    """Get overview of lore and world information."""
    try:
        # Get major cities
        major_cities = [city_data['name'] for city_data in lore_db.major_cities.values()]
        
        # Get factions (this would need to be implemented based on your lore structure)
        factions = ['The Church of the Basilisk', 'The Heretical Priests', 'The Mercenary Companies']
        
        # Get notable NPCs (this would need to be implemented based on your lore structure)
        notable_npcs = ['The Basilisk', 'The Queen', 'The King']
        
        # Get regional lore (this would need to be implemented based on your lore structure)
        regional_lore = ['The Dying Lands', 'The Two-Headed Basilisks', 'The End Times']
        
        return jsonify({
            'success': True,
            'lore': {
                'major_cities': major_cities,
                'factions': factions,
                'notable_npcs': notable_npcs,
                'regional_lore': regional_lore
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/city-overlays')
def get_city_overlays():
    overlays = [
        {"name": key, "display_name": city["name"]}
        for key, city in lore_db.major_cities.items()
    ]
    return jsonify({"success": True, "overlays": overlays})

@api_bp.route('/city-overlay/<overlay_name>')
def get_city_overlay(overlay_name):
    try:
        print(f"DEBUG: Requested overlay: '{overlay_name}'")
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        if not overlay_data:
            print(f"DEBUG: No cached overlay data, generating new overlay for '{overlay_name}'")
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        if not overlay_data:
            return jsonify({'success': False, 'error': 'Failed to generate overlay data'}), 404

        print(f"DEBUG: Overlay data keys: {list(overlay_data.keys())}")
        print(f"DEBUG: Hex grid has {len(overlay_data.get('hex_grid', {}))} hexes")
        print(f"DEBUG: Hex grid keys: {list(overlay_data.get('hex_grid', {}).keys())}")

        compact_overlay = {
            'name': overlay_data['name'],
            'display_name': overlay_data['display_name'],
            'filename': overlay_data['filename'],
            'grid_type': overlay_data.get('grid_type', 'round'),
            'radius': overlay_data.get('radius', 3),
            'hex_grid': {},
            'total_hexes': overlay_data['total_hexes']
        }
        for hex_id, hex_data in overlay_data['hex_grid'].items():
            content = hex_data.get('content', {})
            compact_overlay['hex_grid'][hex_id] = {
                'id': hex_data.get('id', hex_id),
                'row': hex_data.get('row', 0),
                'col': hex_data.get('col', 0),
                'district': hex_data.get('district', 'unknown'),  # Include district information
                'content': {
                    'name': content.get('name', 'Unknown'),
                    'type': content.get('type', 'unknown'),
                    'description': content.get('description', 'No description available'),
                    'encounter': content.get('encounter', 'No encounter available'),
                    'atmosphere': content.get('atmosphere', 'No atmosphere available'),
                    'position_type': content.get('position_type', 'unknown')
                }
            }
            # Truncate long text fields
            if len(compact_overlay['hex_grid'][hex_id]['content']['description']) > 200:
                compact_overlay['hex_grid'][hex_id]['content']['description'] = compact_overlay['hex_grid'][hex_id]['content']['description'][:200] + '...'
            if len(compact_overlay['hex_grid'][hex_id]['content']['encounter']) > 150:
                compact_overlay['hex_grid'][hex_id]['content']['encounter'] = compact_overlay['hex_grid'][hex_id]['content']['encounter'][:150] + '...'
            if len(compact_overlay['hex_grid'][hex_id]['content']['atmosphere']) > 100:
                compact_overlay['hex_grid'][hex_id]['content']['atmosphere'] = compact_overlay['hex_grid'][hex_id]['content']['atmosphere'][:100] + '...'
        
        print(f"DEBUG: Compact overlay hex grid has {len(compact_overlay['hex_grid'])} hexes")
        print(f"DEBUG: Compact overlay hex grid keys: {list(compact_overlay['hex_grid'].keys())}")
        
        response = jsonify({'success': True, 'overlay': compact_overlay})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/city-overlay/<overlay_name>/ascii')
def get_city_overlay_ascii(overlay_name):
    try:
        ascii_view = city_overlay_analyzer.get_overlay_ascii_view(overlay_name)
        return jsonify({
            'success': True,
            'ascii': ascii_view
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/city-overlay/<overlay_name>/hex/<hex_id>')
def get_city_overlay_hex(overlay_name, hex_id):
    try:
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        if not overlay_data:
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        hex_data = overlay_data['hex_grid'].get(hex_id)
        if not hex_data:
            return jsonify({'success': False, 'error': 'Hex not found'})
        response = jsonify({
            'success': True,
            'hex': hex_data
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/regenerate-hex/<overlay_name>/<hex_id>', methods=['POST'])
def regenerate_hex(overlay_name, hex_id):
    """Regenerate a specific hex in a city overlay."""
    try:
        # Load or generate the city overlay
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        if not overlay_data:
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        
        # Parse hex_id to get row and column
        try:
            # hex_id format is typically "row_col" (e.g., "0_0", "1_2")
            row, col = map(int, hex_id.split('_'))
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid hex ID format'}), 400
        
        # Load city data for context
        city_data = city_overlay_analyzer.load_city_database(overlay_name.lower())
        
        # Generate new content for the hex
        # First, determine if this is a district hex or position-based hex
        district_name = None
        if 'district_matrix' in overlay_data:
            # Check if this position has a district
            matrix = overlay_data['district_matrix']
            if 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
                district_name = matrix[row][col]
        
        if district_name and district_name.lower() not in ['empty', 'unknown']:
            # Generate district-based content
            new_hex_data = city_overlay_analyzer.generate_district_based_content(
                district_name, row, col, overlay_name, city_data
            )
        else:
            # Generate position-based content
            radius = overlay_data.get('radius', 3)
            distance = city_overlay_analyzer.hex_distance(row, col, radius, radius)
            new_hex_data = city_overlay_analyzer.generate_position_based_content(
                row, col, distance, radius, overlay_name, city_data
            )
        
        # Update the overlay data with the new hex
        overlay_data['hex_grid'][hex_id] = new_hex_data
        
        # Save the updated overlay data
        city_overlay_analyzer.save_overlay_data(overlay_name, overlay_data)
        
        return jsonify({
            'success': True,
            'hex_data': new_hex_data,
            'message': f'Hex {hex_id} regenerated successfully'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== HELPER FUNCTIONS =====

def _get_major_city_info(hex_code: str, hardcoded: dict) -> dict:
    city_key = hardcoded['city_key']
    city_data = lore_db.major_cities[city_key]
    if current_language == 'pt':
        title = city_data.get('name_pt', city_data['name'])
        description = city_data.get('description_pt', city_data['description'])
        atmosphere = city_data.get('atmosphere_pt', city_data['atmosphere'])
        notable_features = city_data.get('notable_features_pt', city_data['notable_features'])
    else:
        title = city_data['name']
        description = city_data['description']
        atmosphere = city_data['atmosphere']
        notable_features = city_data['notable_features']
    return jsonify({
        'exists': True,
        'is_major_city': True,
        'title': title,
        'description': description,
        'population': city_data['population'],
        'region': city_data['region'],
        'atmosphere': atmosphere,
        'notable_features': notable_features,
        'key_npcs': city_data['key_npcs'],
        'hex_code': hex_code,
    })

def _get_hex_file_info(hex_code: str, hex_file) -> dict:
    try:
        from backend.utils import safe_file_read
        content = safe_file_read(hex_file)
        if '⌂ **' in content:
            settlement_data = extract_settlement_data(content)
            return jsonify({
                'exists': True,
                'is_settlement': True,
                'hex_type': 'settlement',
                'terrain': 'unknown',
                'title': settlement_data['name'],
                'description': settlement_data['description'],
                'population': settlement_data['population'],
                'atmosphere': settlement_data['atmosphere'],
                'notable_feature': settlement_data['notable_feature'],
                'local_tavern': settlement_data['local_tavern'],
                'local_power': settlement_data['local_power'],
                'settlement_art': settlement_data['settlement_art'],
                'hex_code': hex_code,
                'redirect_to': 'settlement'
            })
        try:
            import markdown
            html = markdown.markdown(content, extensions=['codehilite', 'fenced_code', 'tables'])
        except ImportError:
            html = f'<pre>{content}</pre>'
        title = extract_title(content)
        hex_data = extract_hex_data(content)
        hex_type = _determine_hex_type(content)
        terrain = hex_data.get('terrain', 'unknown')
        terrain_name = main_map_generator._get_translated_terrain_name(terrain)
        response_data = {
            'exists': True,
            'is_major_city': False,
            'is_settlement': hex_type == 'settlement',
            'is_dungeon': hex_type == 'dungeon',
            'is_beast': hex_type == 'beast',
            'is_npc': hex_type == 'npc',
            'hex_type': hex_type,
            'title': title,
            'html': html,
            'raw': content,
            'terrain': terrain,
            'terrain_name': terrain_name,
            'hex_code': hex_code,
            'encounter': hex_data.get('encounter', 'Unknown encounter'),
            'denizen': hex_data.get('denizen', 'No denizen information'),
            'notable_feature': hex_data.get('notable_feature', 'No notable features'),
            'atmosphere': hex_data.get('atmosphere', 'Unknown atmosphere'),
            'loot': hex_data.get('loot'),
            'scroll': hex_data.get('scroll'),
            'threat_level': hex_data.get('threat_level'),
            'territory': hex_data.get('territory'),
            'danger': hex_data.get('danger'),
            'treasure': hex_data.get('treasure'),
            'beast_type': hex_data.get('beast_type'),
            'beast_feature': hex_data.get('beast_feature'),
            'beast_behavior': hex_data.get('beast_behavior'),
            'dungeon_type': hex_data.get('dungeon_type'),
            'encounter_type': hex_data.get('encounter_type'),
            'name': hex_data.get('name'),
            'denizen_type': hex_data.get('denizen_type'),
            'motivation': hex_data.get('motivation'),
            'feature': hex_data.get('feature'),
            'demeanor': hex_data.get('demeanor'),
            'carries': hex_data.get('carries'),
            'local_tavern': hex_data.get('local_tavern'),
            'local_power': hex_data.get('local_power'),
            'ancient_knowledge': hex_data.get('ancient_knowledge'),
            'hex_data': hex_data
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': f'Failed to read hex file: {e}'}), 500

def generate_ascii_map_data():
    map_width, map_height = terrain_system.get_map_dimensions()
    grid = {}
    for x in range(1, map_width + 1):
        for y in range(1, map_height + 1):
            hex_code = f"{x:02d}{y:02d}"
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('type') == 'major_city':
                city_key = hardcoded['city_key']
                city_data = lore_db.major_cities[city_key]
                grid[hex_code] = {
                    'x': x, 'y': y,
                    'terrain': normalize_terrain_name(hardcoded['terrain']),
                    'symbol': '◆',
                    'is_city': True,
                    'city_name': city_data['name'],
                    'population': city_data['population'],
                    'region': city_data['region'],
                    'has_content': True,
                    'css_class': 'major-city'
                }
            else:
                terrain = terrain_system.get_terrain_for_hex(hex_code, lore_db)
                hex_file_exists = (config.paths.output_path / "hexes" / f"hex_{hex_code}.md").exists()
                has_loot = False
                content_type = None
                if hex_file_exists:
                    with open(config.paths.output_path / "hexes" / f"hex_{hex_code}.md", "r", encoding="utf-8") as f:
                        content = f.read()
                    hex_data = extract_hex_data(content)
                    terrain = normalize_terrain_name(hex_data.get('terrain', 'unknown'))
                    content_type = get_hex_content_type(hex_code)
                    has_loot = check_hex_has_loot(hex_code)
                symbol = get_terrain_symbol(terrain)
                if hex_file_exists:
                    if content_type == 'settlement':
                        symbol = '⌂'
                    elif content_type == 'ruins':
                        symbol = '▲'
                    elif content_type == 'beast':
                        symbol = '※'
                    elif content_type == 'npc':
                        symbol = '☉'
                    elif content_type == 'sea_encounter':
                        symbol = '≈'
                # Always set css_class from terrain
                css_class = f'terrain-{terrain}'
                if content_type == 'settlement':
                    css_class = 'settlement'
                if has_loot:
                    css_class += ' has-content'
                if hex_code == "1606":
                    print(f"DEBUG 1606: terrain={terrain}, content_type={content_type}, css_class={css_class}")
                grid[hex_code] = {
                    'x': x, 'y': y,
                    'terrain': terrain,
                    'symbol': symbol,
                    'is_city': False,
                    'has_content': has_loot,
                    'content_type': content_type,
                    'css_class': css_class
                }
    if not isinstance(grid, dict):
        return {}
    return grid

def get_major_cities_data():
    cities = []
    for city_key, city_data in lore_db.major_cities.items():
        if current_language == 'pt':
            name = city_data.get('name_pt', city_data['name'])
        else:
            name = city_data['name']
        cities.append({
            'key': city_key,
            'name': name,
            'coordinates': city_data['coordinates'],
            'population': city_data['population'],
            'region': city_data['region']
        })
    return cities

def extract_title(content: str) -> str:
    from backend.utils import extract_title_from_content
    return extract_title_from_content(content)

def extract_hex_data(content):
    """Extract structured data from hex content."""
    if not content:
        return {}
    data = {}
    def extract_field(field):
        # Matches both 'Field: value' and '**Field:** value' (Markdown bold)
        pattern = rf'(?:\*\*)?{field}:(?:\*\*)?\s*([^\n]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    data['terrain'] = extract_field('Terrain')
    data['features'] = extract_field('Notable Features?')
    data['encounters'] = extract_field('Encounters?')
    data['resources'] = extract_field('Resources?')
    return data

def extract_settlement_data(content):
    """Extract settlement-specific data from content."""
    if not content:
        return {}
    data = {}
    def extract_field(field):
        pattern = rf'(?:\*\*)?{field}:(?:\*\*)?\s*([^\n]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    data['population'] = extract_field('Population')
    data['ruler'] = extract_field('Ruler|Leader')
    data['locations'] = extract_field('Notable Locations?')
    data['trade'] = extract_field('Trade Goods?')
    return data

def _determine_hex_type(content: str) -> str:
    if '⌂ **' in content:
        return 'settlement'
    elif '▲ **' in content:
        return 'dungeon'
    elif '※ **' in content:
        return 'beast'
    elif '☉ **' in content:
        return 'npc'
    else:
        return 'wilderness'

def get_terrain_symbol(terrain):
    return terrain_system.get_terrain_symbol(terrain)

def check_hex_has_loot(hex_code):
    try:
        hex_file_path = config.paths.output_path / "hexes" / f"hex_{hex_code}.md"
        if not hex_file_path.exists():
            return False
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        loot_indicators = [
            '## Loot Found',
            '**Treasure Found:**',
            '**Loot:**',
            '**Treasure:**'
        ]
        return any(indicator in content for indicator in loot_indicators)
    except Exception:
        return False

def get_hex_content_type(hex_code):
    try:
        hex_file_path = config.paths.output_path / "hexes" / f"hex_{hex_code}.md"
        if not hex_file_path.exists():
            return None
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '⌂ **' in content:
            return 'settlement'
        elif '▲ **Ancient Ruins**' in content:
            return 'ruins'
        elif '※ **' in content:
            return 'beast'
        elif '☉ **Wandering' in content:
            return 'npc'
        elif '≈ **' in content:
            return 'sea_encounter'
        else:
            return 'basic'
    except Exception:
        return None 

# Extraction stubs for missing types

def extract_beast_data(content):
    data = {}
    beast_type_match = re.search(r'## Beast Details\n\*\*Type:\*\*\s*([^\n]+)', content)
    if beast_type_match:
        data['beast_type'] = beast_type_match.group(1).strip()
    feature_match = re.search(r'## Beast Details\n.*\*\*Feature:\*\*\s*([^\n]+)', content)
    if feature_match:
        data['beast_feature'] = feature_match.group(1).strip()
    behavior_match = re.search(r'## Beast Details\n.*\*\*Behavior:\*\*\s*([^\n]+)', content)
    if behavior_match:
        data['beast_behavior'] = behavior_match.group(1).strip()
    threat_level_match = re.search(r'## Threat Level\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if threat_level_match:
        data['threat_level'] = threat_level_match.group(1).strip()
    territory_match = re.search(r'## Territory\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if territory_match:
        data['territory'] = territory_match.group(1).strip()
    # Fallbacks for common fields
    encounter_match = re.search(r'## Encounter\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if encounter_match:
        data['encounter'] = encounter_match.group(1).strip()
    denizen_match = re.search(r'## Denizen\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if denizen_match:
        data['denizen'] = denizen_match.group(1).strip()
    notable_feature_match = re.search(r'## Notable Feature\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if notable_feature_match:
        data['notable_feature'] = notable_feature_match.group(1).strip()
    atmosphere_match = re.search(r'## Atmosphere\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if atmosphere_match:
        data['atmosphere'] = atmosphere_match.group(1).strip()
    # Loot and magical effect
    loot_match = re.search(r'## Loot Found\n\*\*Type:\*\*\s*([^\n]+).*\*\*Item:\*\*\s*([^\n]+).*\*\*Description:\*\*\s*([^\n]+).*\*\*Full Description:\*\*\s*([^\n]+)', content, re.DOTALL)
    if loot_match:
        data['loot'] = {
            'type': loot_match.group(1).strip(),
            'item': loot_match.group(2).strip(),
            'description': loot_match.group(3).strip(),
            'full_description': loot_match.group(4).strip()
        }
    magical_effect_match = re.search(r'\*\*Magical Effect:\*\*\s*([^\n]+)', content)
    if magical_effect_match:
        data['magical_effect'] = magical_effect_match.group(1).strip()
    return data

def extract_dungeon_data(content):
    data = {}
    dungeon_type_match = re.search(r'## Dungeon Details\n\*\*Type:\*\*\s*([^\n]+)', content)
    if dungeon_type_match:
        data['dungeon_type'] = dungeon_type_match.group(1).strip()
    danger_match = re.search(r'## Dungeon Details\n.*\*\*Danger:\*\*\s*([^\n]+)', content)
    if danger_match:
        data['danger'] = danger_match.group(1).strip()
    treasure_match = re.search(r'## Dungeon Details\n.*\*\*Treasure:\*\*\s*([^\n]+)', content)
    if treasure_match:
        data['treasure'] = treasure_match.group(1).strip()
    # Ancient Knowledge
    ancient_knowledge_match = re.search(r'## Ancient Knowledge\n\*\*Type:\*\*\s*([^\n]+).*\*\*Content:\*\*\s*([^\n]+).*\*\*Effect:\*\*\s*([^\n]+).*\*\*Description:\*\*\s*([^\n]+)', content, re.DOTALL)
    if ancient_knowledge_match:
        data['ancient_knowledge'] = {
            'type': ancient_knowledge_match.group(1).strip(),
            'content': ancient_knowledge_match.group(2).strip(),
            'effect': ancient_knowledge_match.group(3).strip(),
            'description': ancient_knowledge_match.group(4).strip()
        }
    # Loot and magical effect
    loot_match = re.search(r'## Loot Found\n\*\*Type:\*\*\s*([^\n]+).*\*\*Item:\*\*\s*([^\n]+).*\*\*Description:\*\*\s*([^\n]+).*\*\*Full Description:\*\*\s*([^\n]+)', content, re.DOTALL)
    if loot_match:
        data['loot'] = {
            'type': loot_match.group(1).strip(),
            'item': loot_match.group(2).strip(),
            'description': loot_match.group(3).strip(),
            'full_description': loot_match.group(4).strip()
        }
    magical_effect_match = re.search(r'\*\*Magical Effect:\*\*\s*([^\n]+)', content)
    if magical_effect_match:
        data['magical_effect'] = magical_effect_match.group(1).strip()
    # Fallbacks for common fields
    encounter_match = re.search(r'## Encounter\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if encounter_match:
        data['encounter'] = encounter_match.group(1).strip()
    denizen_match = re.search(r'## Denizen\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if denizen_match:
        data['denizen'] = denizen_match.group(1).strip()
    notable_feature_match = re.search(r'## Notable Feature\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if notable_feature_match:
        data['notable_feature'] = notable_feature_match.group(1).strip()
    atmosphere_match = re.search(r'## Atmosphere\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if atmosphere_match:
        data['atmosphere'] = atmosphere_match.group(1).strip()
    description_match = re.search(r'## Dungeon Details\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if description_match:
        data['description'] = description_match.group(1).strip()
    return data

def extract_npc_data(content):
    data = {}
    name_match = re.search(r'\*\*Name:\*\*\s*([^\n]+)', content)
    if name_match:
        data['name'] = name_match.group(1).strip()
    type_match = re.search(r'\*\*Type:\*\*\s*([^\n]+)', content)
    if type_match:
        data['denizen_type'] = type_match.group(1).strip()
    motivation_match = re.search(r'\*\*Motivation:\*\*\s*([^\n]+)', content)
    if motivation_match:
        data['motivation'] = motivation_match.group(1).strip()
    feature_match = re.search(r'\*\*Feature:\*\*\s*([^\n]+)', content)
    if feature_match:
        data['feature'] = feature_match.group(1).strip()
    demeanor_match = re.search(r'\*\*Demeanor:\*\*\s*([^\n]+)', content)
    if demeanor_match:
        data['demeanor'] = demeanor_match.group(1).strip()
    location_match = re.search(r'\*\*Location:\*\*\s*([^\n]+)', content)
    if location_match:
        data['location'] = location_match.group(1).strip()
    key_npcs_match = re.search(r'\*\*Key NPCs:\*\*\s*([^\n]+)', content)
    if key_npcs_match:
        data['key_npcs'] = [npc.strip() for npc in key_npcs_match.group(1).split(',')]
    # Fallbacks for common fields
    encounter_match = re.search(r'## Encounter\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if encounter_match:
        data['encounter'] = encounter_match.group(1).strip()
    denizen_match = re.search(r'## Denizen\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if denizen_match:
        data['denizen'] = denizen_match.group(1).strip()
    notable_feature_match = re.search(r'## Notable Feature\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if notable_feature_match:
        data['notable_feature'] = notable_feature_match.group(1).strip()
    atmosphere_match = re.search(r'## Atmosphere\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if atmosphere_match:
        data['atmosphere'] = atmosphere_match.group(1).strip()
    description_match = re.search(r'## NPC Details\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if description_match:
        data['description'] = description_match.group(1).strip()
    return data

def extract_sea_encounter_data(content):
    data = {}
    type_match = re.search(r'## Sea Encounter Details\n\*\*Type:\*\*\s*([^\n]+)', content)
    if type_match:
        data['encounter_type'] = type_match.group(1).strip()
    origin_match = re.search(r'\*\*Origin:\*\*\s*([^\n]+)', content)
    if origin_match:
        data['origin'] = origin_match.group(1).strip()
    behavior_match = re.search(r'\*\*Behavior:\*\*\s*([^\n]+)', content)
    if behavior_match:
        data['behavior'] = behavior_match.group(1).strip()
    threat_level_match = re.search(r'## Threat Level\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if threat_level_match:
        data['threat_level'] = threat_level_match.group(1).strip()
    territory_match = re.search(r'## Territory\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if territory_match:
        data['territory'] = territory_match.group(1).strip()
    sunken_treasure_match = re.search(r'\*\*Sunken Treasure:\*\*\s*([^\n]+)', content)
    if sunken_treasure_match:
        data['sunken_treasure'] = sunken_treasure_match.group(1).strip()
    # Loot and magical effect
    loot_match = re.search(r'## Loot Found\n\*\*Type:\*\*\s*([^\n]+).*\*\*Item:\*\*\s*([^\n]+).*\*\*Description:\*\*\s*([^\n]+).*\*\*Full Description:\*\*\s*([^\n]+)', content, re.DOTALL)
    if loot_match:
        data['loot'] = {
            'type': loot_match.group(1).strip(),
            'item': loot_match.group(2).strip(),
            'description': loot_match.group(3).strip(),
            'full_description': loot_match.group(4).strip()
        }
    magical_effect_match = re.search(r'\*\*Magical Effect:\*\*\s*([^\n]+)', content)
    if magical_effect_match:
        data['magical_effect'] = magical_effect_match.group(1).strip()
    # Fallbacks for common fields
    encounter_match = re.search(r'## Encounter\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if encounter_match:
        data['encounter'] = encounter_match.group(1).strip()
    denizen_match = re.search(r'## Denizen\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if denizen_match:
        data['denizen'] = denizen_match.group(1).strip()
    notable_feature_match = re.search(r'## Notable Feature\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if notable_feature_match:
        data['notable_feature'] = notable_feature_match.group(1).strip()
    atmosphere_match = re.search(r'## Atmosphere\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if atmosphere_match:
        data['atmosphere'] = atmosphere_match.group(1).strip()
    description_match = re.search(r'## Sea Encounter Details\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if description_match:
        data['description'] = description_match.group(1).strip()
    return data

def extract_ruins_data(content):
    # TODO: Implement real parsing logic
    return extract_hex_data(content) 