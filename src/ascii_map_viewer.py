#!/usr/bin/env python3
"""
The Dying Lands ASCII Map Viewer
Interactive web viewer for the hex-based map with ASCII representation.
"""

import os
import json
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("⚠️  Markdown module not available - using text fallback")

from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
from mork_borg_lore_database import MorkBorgLoreDatabase
from terrain_system import terrain_system
from main_map_generator import MainMapGenerator
from translation_system import translation_system
from city_overlay_analyzer import city_overlay_analyzer

app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')

# Initialize systems
lore_db = MorkBorgLoreDatabase()

# Global language setting - defaults to English
current_language = 'en'

# Initialize main map generator with current language
def get_main_map_generator():
    """Get main map generator with current language configuration."""
    global current_language
    return MainMapGenerator({'language': current_language})

# Initialize with default language
main_map_generator = get_main_map_generator()

def get_map_dimensions():
    """Get map dimensions from terrain system."""
    return terrain_system.get_map_dimensions()

def get_terrain_for_hex(hex_code):
    """Get terrain type for a hex using unified terrain system."""
    return terrain_system.get_terrain_for_hex(hex_code, lore_db)

@app.route('/')
def main_map():
    """Main map page with integrated lore."""
    if not os.path.exists('dying_lands_output'):
        os.makedirs('dying_lands_output', exist_ok=True)
        return render_template('setup.html', 
                             title="The Dying Lands - Setup", 
                             action="Run main_map_generator.py to create the map")
    
    # Get map dimensions
    map_width, map_height = get_map_dimensions()
    
    # Generate ASCII map data
    ascii_map_data = generate_ascii_map_data()
    
    return render_template('main_map.html',
                         ascii_map=ascii_map_data,
                         map_width=map_width,
                         map_height=map_height,
                         major_cities=get_major_cities_data(),
                         total_hexes=map_width * map_height)

@app.route('/api/set-language', methods=['POST'])
def set_language():
    """Set the current language for content generation."""
    global current_language, main_map_generator
    
    data = request.get_json()
    new_language = data.get('language', 'en')
    
    if new_language in ['en', 'pt']:
        current_language = new_language
        # Re-initialize main map generator with new language
        main_map_generator = get_main_map_generator()
        
        return jsonify({
            'success': True,
            'language': current_language,
            'message': f'Language set to {current_language}'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid language. Use "en" or "pt"'
        }), 400

@app.route('/api/hex/<hex_code>')
def get_hex_info(hex_code):
    """Get hex information for popup."""
    hex_file = f"dying_lands_output/hexes/hex_{hex_code}.md"
    
    # Check if it's a major city
    hardcoded = lore_db.get_hardcoded_hex(hex_code)
    if hardcoded and hardcoded.get('type') == 'major_city':
        city_key = hardcoded['city_key']
        city_data = lore_db.major_cities[city_key]
        
        # Use Portuguese fields if available and language is Portuguese
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
    
    # Check if it's a settlement
    if os.path.exists(hex_file):
        try:
            with open(hex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if this is a settlement
            if '⌂ **' in content:
                settlement_data = extract_settlement_data(content, hex_code)
                return jsonify({
                    'exists': True,
                    'is_settlement': True,
                    'hex_type': 'settlement',
                    'terrain': get_terrain_for_hex(hex_code),
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
            
            # Regular hex content
            if MARKDOWN_AVAILABLE:
                html = markdown.markdown(content, extensions=['codehilite', 'fenced_code', 'tables'])
            else:
                # Fallback if markdown module is not available
                html = f'<pre>{content}</pre>'
            title = extract_title(content)
            
            # Extract structured data for the new modal system
            hex_data = extract_hex_data(content, hex_code)
            
            # Determine hex type from content
            hex_type = 'wilderness'
            if '⌂ **' in content:
                hex_type = 'settlement'
            elif '▲ **' in content:
                hex_type = 'dungeon'
            elif '※ **' in content:
                hex_type = 'beast'
            elif '☉ **' in content:
                hex_type = 'npc'
                
            # Get terrain from terrain system if not in parsed data
            terrain = hex_data.get('terrain', 'unknown')
            if terrain == 'unknown':
                terrain = get_terrain_for_hex(hex_code)
            
            # Get translated terrain name for display
            terrain_name = main_map_generator._get_translated_terrain_name(terrain)
            
            return jsonify({
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
                'hex_code': hex_code,
                'terrain': terrain,
                'terrain_name': terrain_name,
                'encounter': hex_data.get('encounter', 'Unknown encounter'),
                'denizen': hex_data.get('denizen', 'No denizen information'),
                'notable_feature': hex_data.get('notable_feature', 'No notable features'),
                'atmosphere': hex_data.get('atmosphere', 'Unknown atmosphere'),
                # NPC specific fields
                'name': hex_data.get('name'),
                'motivation': hex_data.get('motivation', 'Unknown motivation'),
                'feature': hex_data.get('feature', 'No notable features'),
                'demeanor': hex_data.get('demeanor', 'Unknown demeanor'),
                'denizen_type': hex_data.get('denizen_type'),
                # Beast specific fields
                'beast_type': hex_data.get('beast_type'),
                'beast_behavior': hex_data.get('beast_behavior'),
                'beast_feature': hex_data.get('beast_feature'),
                'threat_level': hex_data.get('threat_level', 'Unknown threat level'),
                'territory': hex_data.get('territory', 'No territory claimed'),
                # Sea encounter specific fields
                'encounter_type': hex_data.get('encounter_type'),
                'is_sea_encounter': hex_data.get('is_sea_encounter', False),
                # Dungeon specific fields
                'danger': hex_data.get('danger', 'No dangers present'),
                'treasure': hex_data.get('treasure', 'No treasure found'),
                'loot': hex_data.get('loot'),
                'scroll': hex_data.get('scroll'),
                'ancient_knowledge': hex_data.get('ancient_knowledge', 'No ancient knowledge'),
                # Settlement specific fields
                'population': hex_data.get('population'),
                'local_tavern': hex_data.get('local_tavern'),
                'local_power': hex_data.get('local_power'),
                'settlement_art': hex_data.get('settlement_art'),
                'settlement_layout': hex_data.get('settlement_layout', 'No settlement layout'),
                'location': hex_data.get('location', 'Unknown location')
            })
        except Exception as e:
            return jsonify({
                'exists': False,
                'error': str(e),
                'hex_code': hex_code
            })
    else:
        # Generate hex content on demand with current language
        try:
            terrain = get_terrain_for_hex(hex_code)
            # Use the current main_map_generator which has the correct language
            hex_data = main_map_generator.generate_hex_content(hex_code, terrain)
            
            # Get translated terrain name for display
            terrain_name = main_map_generator._get_translated_terrain_name(terrain)
            
            # Check if it's a settlement
            if hex_data.get('is_settlement'):
                return jsonify({
                    'exists': True,
                    'is_settlement': True,
                    'hex_type': 'settlement',
                    'terrain': hex_data.get('terrain', terrain),
                    'title': hex_data.get('name', f'Settlement {hex_code}'),
                    'description': hex_data.get('denizen', 'A settlement'),
                    'population': hex_data.get('population', 'Unknown'),
                    'atmosphere': hex_data.get('atmosphere', 'Unknown'),
                    'notable_feature': hex_data.get('notable_feature', 'Unknown'),
                    'local_tavern': hex_data.get('local_tavern', 'Unknown'),
                    'local_power': hex_data.get('local_power', 'Unknown'),
                    'settlement_art': hex_data.get('settlement_art', ''),
                    'name': hex_data.get('name', f'Settlement {hex_code}'),
                    'hex_code': hex_code,
                    'redirect_to': 'settlement'
                })
            
            # Generate markdown content
            markdown_content = main_map_generator._generate_markdown_content(hex_data)
            if MARKDOWN_AVAILABLE:
                html = markdown.markdown(markdown_content, extensions=['codehilite', 'fenced_code', 'tables'])
            else:
                # Fallback if markdown module is not available
                html = f'<pre>{markdown_content}</pre>'
            
            # Determine hex type
            hex_type = 'wilderness'
            if hex_data.get('is_settlement'):
                hex_type = 'settlement'
            elif hex_data.get('is_dungeon'):
                hex_type = 'dungeon'
            elif hex_data.get('is_beast'):
                hex_type = 'beast'
            elif hex_data.get('is_npc'):
                hex_type = 'npc'
            
            return jsonify({
                'exists': True,
                'is_major_city': False,
                'is_settlement': hex_data.get('is_settlement', False),
                'is_dungeon': hex_data.get('is_dungeon', False),
                'is_beast': hex_data.get('is_beast', False),
                'is_npc': hex_data.get('is_npc', False),
                'hex_type': hex_type,
                'title': f"Hex {hex_code}",
                'html': html,
                'raw': markdown_content,
                'hex_code': hex_code,
                'terrain': hex_data.get('terrain', terrain),
                'terrain_name': terrain_name,
                'encounter': hex_data.get('encounter', 'Unknown encounter'),
                'denizen': hex_data.get('denizen', 'No denizen information'),
                'notable_feature': hex_data.get('notable_feature', 'No notable features'),
                'atmosphere': hex_data.get('atmosphere', 'Unknown atmosphere'),
                'loot': hex_data.get('loot'),
                'scroll': hex_data.get('scroll'),
                'dungeon_type': hex_data.get('dungeon_type'),
                'beast_type': hex_data.get('beast_type'),
                'name': hex_data.get('name'),
                'population': hex_data.get('population'),
                'local_tavern': hex_data.get('local_tavern'),
                'local_power': hex_data.get('local_power'),
                'settlement_art': hex_data.get('settlement_art'),
                'beast_feature': hex_data.get('beast_feature'),
                'beast_behavior': hex_data.get('beast_behavior'),
                'motivation': hex_data.get('motivation'),
                'feature': hex_data.get('feature'),
                'demeanor': hex_data.get('demeanor'),
                'denizen_type': hex_data.get('denizen_type'),
                'threat_level': hex_data.get('threat_level'),
                'territory': hex_data.get('territory'),
                'encounter_type': hex_data.get('encounter_type'),
                'is_sea_encounter': hex_data.get('is_sea_encounter', False),
                'danger': hex_data.get('danger'),
                'treasure': hex_data.get('treasure')
            })
        except Exception as e:
            return jsonify({
                'exists': False,
                'error': str(e),
                'hex_code': hex_code
            })

@app.route('/api/city/<hex_code>')
def get_city_details(hex_code):
    """Get detailed city information."""
    hardcoded = lore_db.get_hardcoded_hex(hex_code)
    if hardcoded and hardcoded.get('type') == 'major_city':
        city_key = hardcoded['city_key']
        city_data = lore_db.major_cities[city_key]
        
        # Get regional information
        region = city_data['region']
        regional_npcs = lore_db.get_regional_npcs(region)
        regional_factions = lore_db.get_regional_factions(region)
        
        # Get faction details
        faction_details = []
        for faction_key in regional_factions:
            if faction_key in lore_db.factions:
                faction_details.append(lore_db.factions[faction_key])
        
        # Generate city ASCII map
        city_map = generate_city_ascii_map(city_data, hex_code)
        
        return jsonify({
            'success': True,
            'city': city_data,
            'regional_npcs': regional_npcs,
            'factions': faction_details,
            'hex_code': hex_code,
            'city_map': city_map
        })
    
    return jsonify({'success': False, 'error': 'City not found'})

@app.route('/api/settlement/<hex_code>')
def get_settlement_details(hex_code):
    """Get detailed settlement information."""
    hex_file = f"dying_lands_output/hexes/hex_{hex_code}.md"
    
    # Try to load from existing file first
    if os.path.exists(hex_file):
        try:
            with open(hex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if this is a settlement
            if '⌂ **' in content:
                settlement_data = extract_settlement_data(content, hex_code)
                
                # Get terrain for regional context
                terrain = get_terrain_for_hex(hex_code)
                
                # Generate settlement ASCII map
                settlement_map = generate_settlement_ascii_map(settlement_data, hex_code)
                
                return jsonify({
                    'success': True,
                    'settlement': settlement_data,
                    'terrain': terrain,
                    'hex_code': hex_code,
                    'settlement_map': settlement_map,
                    'settlement_art': settlement_data.get('settlement_art', ''),
                    'settlement_layout': settlement_data.get('settlement_art', 'No settlement layout'),
                    'custom_settlement_layout': settlement_data.get('custom_settlement_layout', 'No custom settlement layout')
                })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # Generate settlement on demand
    try:
        terrain = get_terrain_for_hex(hex_code)
        hex_data = main_map_generator.generate_hex_content(hex_code, terrain)
        
        if hex_data.get('is_settlement'):
            # Create settlement data structure expected by frontend
            settlement_data = {
                'name': hex_data.get('name', f'Settlement {hex_code}'),
                'description': hex_data.get('denizen', 'A settlement'),
                'population': hex_data.get('population', 'Unknown'),
                'atmosphere': hex_data.get('atmosphere', 'Unknown'),
                'notable_feature': hex_data.get('notable_feature', 'Unknown'),
                'local_tavern': hex_data.get('local_tavern', 'Unknown'),
                'local_power': hex_data.get('local_power', 'Unknown'),
                'hex_code': hex_code
            }
            
            # Generate settlement ASCII map
            settlement_map = generate_settlement_ascii_map(settlement_data, hex_code)
            
            return jsonify({
                'success': True,
                'settlement': settlement_data,
                'terrain': terrain,
                'hex_code': hex_code,
                'settlement_map': settlement_map,
                'settlement_art': hex_data.get('settlement_art', '')
            })
        else:
            return jsonify({'success': False, 'error': 'Hex is not a settlement'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating settlement: {str(e)}'})

@app.route('/api/lore-overview')
def get_lore_overview():
    """Get complete lore overview."""
    try:
        # Use unified map generator
        result = main_map_generator.get_lore_overview()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/terrain-overview')
def get_terrain_overview():
    """Get terrain analysis."""
    try:
        # Use unified terrain system
        result = main_map_generator.get_terrain_overview()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-hex', methods=['POST'])
def generate_single_hex():
    """Generate content for a single hex."""
    try:
        data = request.get_json()
        hex_code = data.get('hex')
        
        if not hex_code:
            return jsonify({'success': False, 'error': 'Hex code required'})
        
        # Generate hex content using unified system
        result = main_map_generator.generate_single_hex(hex_code)
        
        return jsonify({
            'success': True,
            'hex_code': hex_code,
            'message': f'Generated hex {hex_code}',
            'content_type': result.get('content_type', 'unknown')
        })
        
    except Exception as e:
        print(f"Error generating hex {hex_code}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-full-map', methods=['POST'])
def generate_full_map():
    """Generate content for the entire map."""
    try:
        # Generate using unified system
        hex_data_list = main_map_generator.generate_full_map(options={'skip_existing': False})
        
        return jsonify({
            'success': True,
            'count': len(hex_data_list),
            'message': translation_system.t('generated_hexes', count=len(hex_data_list))
        })
        
    except Exception as e:
        print(f"Generation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reset-continent', methods=['POST'])
def reset_continent():
    """Reset the entire continent by deleting all content and regenerating."""
    try:
        # Reset using unified system
        result = main_map_generator.reset_continent()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Reset error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/city-overlays')
def get_city_overlays():
    """Get list of available city overlay images."""
    try:
        overlays = city_overlay_analyzer.get_available_overlays()
        response = jsonify({
            'success': True,
            'overlays': overlays
        })
        
        # Set headers to prevent caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test')
def api_test():
    """Simple test endpoint to verify API is working."""
    return jsonify({
        'success': True,
        'message': 'API is working',
        'timestamp': str(__import__('datetime').datetime.now())
    })

@app.route('/api/city-overlay/<overlay_name>')
def get_city_overlay(overlay_name):
    """Get or generate city overlay data."""
    try:
        # Check if overlay exists in cache
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        
        if not overlay_data:
            # Generate new overlay
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        
        if not overlay_data:
            return jsonify({'success': False, 'error': 'Failed to generate overlay data'})
        
        # Create a more compact response format to avoid size issues
        compact_overlay = {
            'name': overlay_data['name'],
            'display_name': overlay_data['display_name'],
            'filename': overlay_data['filename'],
            'grid_size': overlay_data['grid_size'],
            'hex_grid': {},
            'total_hexes': overlay_data['total_hexes']
        }
        
        # Only include essential hex data to reduce size
        for hex_id, hex_data in overlay_data['hex_grid'].items():
            compact_overlay['hex_grid'][hex_id] = {
                'id': hex_data['id'],
                'row': hex_data['row'],
                'col': hex_data['col'],
                'content': {
                    'name': hex_data['content']['name'],
                    'type': hex_data['content']['type'],
                    'description': hex_data['content']['description'][:200] + '...' if len(hex_data['content']['description']) > 200 else hex_data['content']['description'],
                    'encounter': hex_data['content']['encounter'][:150] + '...' if len(hex_data['content']['encounter']) > 150 else hex_data['content']['encounter'],
                    'atmosphere': hex_data['content']['atmosphere'][:100] + '...' if len(hex_data['content']['atmosphere']) > 100 else hex_data['content']['atmosphere'],
                    'position_type': hex_data['content']['position_type']
                }
            }
        
        response = jsonify({
            'success': True,
            'overlay': compact_overlay
        })
        
        # Set headers to prevent caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/city-overlay/<overlay_name>/ascii')
def get_city_overlay_ascii(overlay_name):
    """Get ASCII representation of city overlay."""
    try:
        ascii_view = city_overlay_analyzer.get_overlay_ascii_view(overlay_name)
        return jsonify({
            'success': True,
            'ascii': ascii_view
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/city-overlay/<overlay_name>/ascii-map')
def get_city_overlay_ascii_map(overlay_name):
    """Get visual ASCII art representation of city overlay for grid display."""
    try:
        ascii_map = city_overlay_analyzer.get_city_ascii_map(overlay_name)
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        
        if not overlay_data:
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        
        return jsonify({
            'success': True,
            'ascii_map': ascii_map,
            'overlay_data': overlay_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/city-overlay/<overlay_name>/hex/<hex_id>')
def get_city_overlay_hex(overlay_name, hex_id):
    """Get specific hex data from city overlay."""
    try:
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        
        if not overlay_data:
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        
        hex_data = overlay_data['hex_grid'].get(hex_id)
        
        if not hex_data:
            return jsonify({'success': False, 'error': 'Hex not found'})
        
        # Return full hex data for detailed view
        response = jsonify({
            'success': True,
            'hex': hex_data
        })
        
        # Set headers to prevent caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

def generate_ascii_map_data():
    """Generate ASCII map data with city markers."""
    map_width, map_height = get_map_dimensions()
    
    grid = {}
    
    # Initialize grid - match template's x,y system
    for x in range(1, map_width + 1):
        for y in range(1, map_height + 1):
            hex_code = f"{x:02d}{y:02d}"
            
            # Check for major cities
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('type') == 'major_city':
                city_key = hardcoded['city_key']
                city_data = lore_db.major_cities[city_key]
                grid[hex_code] = {
                    'x': x, 'y': y,
                    'terrain': hardcoded['terrain'],
                    'symbol': '◆',
                    'is_city': True,
                    'city_name': city_data['name'],
                    'population': city_data['population'],
                    'region': city_data['region'],
                    'has_content': True,
                    'css_class': 'major-city'
                }
            else:
                # Regular terrain - check for generated content to add visual indicators
                terrain = get_terrain_for_hex(hex_code)
                hex_file_exists = os.path.exists(f"dying_lands_output/hexes/hex_{hex_code}.md")
                
                # Check if hex has loot (this determines bold styling)
                has_loot = False
                content_type = None
                
                if hex_file_exists:
                    # Check what type of content exists to add visual indicators
                    content_type = get_hex_content_type(hex_code)
                    # Check if hex has loot by reading the file
                    has_loot = check_hex_has_loot(hex_code)
                
                # Determine symbol based on content and terrain
                symbol = get_terrain_symbol(terrain)
                
                if hex_file_exists:
                    if content_type == 'settlement':
                        symbol = '⌂'  # Settlement marker
                    elif content_type == 'ruins':
                        symbol = '▲'  # Ruins marker  
                    elif content_type == 'beast':
                        symbol = '※'  # Beast marker
                    elif content_type == 'npc':
                        symbol = '☉'  # NPC marker
                    elif content_type == 'sea_encounter':
                        symbol = '≈'  # Sea encounter marker
                    # Otherwise keep terrain symbol for basic content
                
                # Determine CSS class based on content type
                css_class = f'terrain-{terrain}'
                if content_type == 'settlement':
                    css_class = 'settlement'
                elif has_loot:
                    css_class += ' has-content'
                
                grid[hex_code] = {
                    'x': x, 'y': y,
                    'terrain': terrain,
                    'symbol': symbol,
                    'is_city': False,
                    'has_content': has_loot,  # Now based on loot presence
                    'content_type': content_type,
                    'css_class': css_class
                }
    
    return grid

def get_major_cities_data():
    """Get major cities data for the template."""
    cities = []
    for city_key, city_data in lore_db.major_cities.items():
        x, y = city_data['coordinates']
        hex_code = f"{x:02d}{y:02d}"
        cities.append({
            'hex_code': hex_code,
            'name': city_data['name'],
            'region': city_data['region'],
            'population': city_data['population'],
            'description': city_data['description']
        })
    return cities

def get_terrain_symbol(terrain):
    """Get symbol for terrain type."""
    return terrain_system.get_terrain_symbol(terrain)

def check_hex_has_loot(hex_code):
    """Check if a hex file contains loot/treasure."""
    try:
        hex_file_path = f"dying_lands_output/hexes/hex_{hex_code}.md"
        if not os.path.exists(hex_file_path):
            return False
            
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for loot indicators in the content
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
    """Determine content type from hex file for visual indicators."""
    try:
        hex_file_path = f"dying_lands_output/hexes/hex_{hex_code}.md"
        if not os.path.exists(hex_file_path):
            return None
            
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for content type markers in the encounter section
        if '⌂ **' in content:  # Settlement marker
            return 'settlement'
        elif '▲ **Ancient Ruins**' in content:  # Ruins marker
            return 'ruins'
        elif '※ **' in content:  # Beast marker (any beast)
            return 'beast'
        elif '☉ **Wandering' in content:  # NPC marker
            return 'npc'
        elif '≈ **' in content:  # Sea encounter marker
            return 'sea_encounter'
        else:
            return 'basic'  # Basic terrain content
            
    except Exception:
        return None

def extract_title(content):
    """Extract title from markdown content."""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled"

def extract_hex_data(content, hex_code):
    """Extract structured data from hex content for the new modal system."""
    lines = content.split('\n')
    hex_data = {
        'terrain': 'unknown',
        'encounter': 'Unknown encounter',
        'denizen': 'No denizen information',
        'notable_feature': 'No notable features',
        'atmosphere': 'Unknown atmosphere',
        'loot': None,
        'scroll': None,
        'threat_level': None,
        'territory': None,
        'danger': None,
        'treasure': None,
        'beast_type': None,
        'beast_feature': None,
        'beast_behavior': None,
        'dungeon_type': None,
        'encounter_type': None,
        'name': None,
        'denizen_type': None,
        'motivation': None,
        'feature': None,
        'demeanor': None,
        'carries': None,
        'is_beast': False,
        'is_dungeon': False,
        'is_npc': False,
        'is_sea_encounter': False,
        'is_settlement': False
    }
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Extract terrain from title
        if line.startswith('# Hex ') and ' - ' in line:
            parts = line.split(' - ')
            if len(parts) > 1:
                hex_data['terrain'] = parts[1].strip()
        elif line.startswith('**Terrain:**'):
            hex_data['terrain'] = line.replace('**Terrain:**', '').strip()
        
        # Extract encounter and determine hex type
        elif '**' in line and any(symbol in line for symbol in ['※', '▲', '☉', '⌂', '≈']):
            hex_data['encounter'] = line.strip()
            
            # Determine hex type based on encounter symbol
            if '※ **' in line:
                hex_data['is_beast'] = True
                start = line.find('※ **') + 4
                end = line.find('**', start)
                if start > 3 and end > start:
                    hex_data['beast_type'] = line[start:end]
            elif '▲ **' in line:
                hex_data['is_dungeon'] = True
                start = line.find('▲ **') + 4
                end = line.find('**', start)
                if start > 3 and end > start:
                    hex_data['dungeon_type'] = line[start:end]
            elif '☉ **' in line:
                hex_data['is_npc'] = True
                start = line.find('☉ **') + 4
                end = line.find('**', start)
                if start > 3 and end > start:
                    hex_data['name'] = line[start:end]
            elif '⌂ **' in line:
                hex_data['is_settlement'] = True
                start = line.find('⌂ **') + 4
                end = line.find('**', start)
                if start > 3 and end > start:
                    hex_data['name'] = line[start:end]
                # Extract population from settlement encounter line
                if ' - A ' in line and ' settlement' in line:
                    pop_start = line.find(' - A ') + 4
                    pop_end = line.find(' settlement')
                    if pop_start > 3 and pop_end > pop_start:
                        hex_data['population'] = line[pop_start:pop_end]
            elif '≈ **' in line:
                hex_data['is_sea_encounter'] = True
                start = line.find('≈ **') + 4
                end = line.find('**', start)
                if start > 3 and end > start:
                    hex_data['encounter_type'] = line[start:end]
        
        # Extract denizen information (but not the individual fields we parse separately)
        elif current_section == 'denizen' and line and not line.startswith('#') and not any(field in line for field in ['**Motivation:**', '**Feature:**', '**Demeanor:**', '**Name:**', '**Type:**', '**Behavior:**', '**Danger:**', '**Atmosphere:**', '**Territory:**', '**Threat Level:**', '**Treasure Found:**', '**Ancient Knowledge:**', '**Carries:**']):
            if hex_data['denizen'] == 'No denizen information':
                hex_data['denizen'] = line.strip()
            else:
                hex_data['denizen'] += '\n' + line.strip()
        
        # Extract NPC name from denizen section
        elif current_section == 'denizen' and '**' in line and '**' in line[line.find('**')+2:] and ' - ' in line:
            # Extract name between ** **
            start = line.find('**') + 2
            end = line.find('**', start)
            if start > 1 and end > start:
                hex_data['name'] = line[start:end]
        
        # Extract specific fields from both denizen section and details sections
        elif '**Motivation:**' in line:
            hex_data['motivation'] = line.replace('**Motivation:**', '').strip()
        elif '**Demeanor:**' in line:
            hex_data['demeanor'] = line.replace('**Demeanor:**', '').strip()
        elif '**Name:**' in line:
            hex_data['name'] = line.replace('**Name:**', '').strip()
        elif '**Type:**' in line:
            type_value = line.replace('**Type:**', '').strip()
            # Check context to determine if it's beast or NPC
            if '※ **' in content:  # Beast content
                hex_data['beast_type'] = type_value
            elif '☉ **' in content:  # NPC content
                hex_data['denizen_type'] = type_value
        elif '**Behavior:**' in line:
            hex_data['beast_behavior'] = line.replace('**Behavior:**', '').strip()
        elif '**Feature:**' in line:
            feature_value = line.replace('**Feature:**', '').strip()
            # Check context to determine if it's beast or NPC feature
            if '※ **' in content:  # Beast content
                hex_data['beast_feature'] = feature_value
            else:  # NPC content
                hex_data['feature'] = feature_value
        elif '**Danger:**' in line:
            hex_data['danger'] = line.replace('**Danger:**', '').strip()
        elif '**Treasure:**' in line:
            hex_data['treasure'] = line.replace('**Treasure:**', '').strip()
        elif '**Ancient Knowledge:**' in line:
            hex_data['scroll'] = line.replace('**Ancient Knowledge:**', '').strip()
        elif '**Local Tavern:**' in line:
            hex_data['local_tavern'] = line.replace('**Local Tavern:**', '').strip()
        elif '**Local Power:**' in line:
            hex_data['local_power'] = line.replace('**Local Power:**', '').strip()
        elif '**Threat Level:**' in line:
            hex_data['threat_level'] = line.replace('**Threat Level:**', '').strip()
        elif '**Territory:**' in line:
            hex_data['territory'] = line.replace('**Territory:**', '').strip()
        elif '**Carries:**' in line:
            hex_data['carries'] = line.replace('**Carries:**', '').strip()
        
        # Extract loot information
        elif '**Treasure Found:**' in line:
            loot_text = line.replace('**Treasure Found:**', '').strip()
            if loot_text and loot_text != 'No treasure found':
                hex_data['loot'] = {
                    'description': loot_text,
                    'full_description': loot_text
                }
        
        # Extract loot details from Loot Found section
        elif '**Loot Found:**' in line:
            current_section = 'loot'
        elif current_section == 'loot' and line and not line.startswith('#') and not line.startswith('**'):
            if not hex_data['loot']:
                hex_data['loot'] = {}
            hex_data['loot']['description'] = line.strip()
            current_section = None
        
        # Extract magical effect from loot
        elif '**Magical Effect:**' in line:
            magical_effect = line.replace('**Magical Effect:**', '').strip()
            if hex_data['loot']:
                hex_data['loot']['magical_effect'] = magical_effect
        
        # Extract ancient knowledge details
        elif '**Ancient Knowledge:**' in line:
            current_section = 'ancient_knowledge'
        elif current_section == 'ancient_knowledge' and line and not line.startswith('#') and not line.startswith('**'):
            if not hex_data['scroll']:
                hex_data['scroll'] = {}
            hex_data['scroll']['description'] = line.strip()
            current_section = None
        
        # Extract notable feature
        elif 'Notable Feature' in line or 'NOTABLE FEATURES' in line:
            current_section = 'notable_feature'
        elif current_section == 'notable_feature' and line and not line.startswith('#'):
            hex_data['notable_feature'] = line.strip()
            current_section = None
        
        # Extract threat level
        elif 'Threat Level' in line or 'THREAT LEVEL' in line:
            current_section = 'threat_level'
        elif current_section == 'threat_level' and line and not line.startswith('#'):
            hex_data['threat_level'] = line.strip()
            current_section = None
        
        # Extract territory
        elif 'Territory' in line or 'TERRITORY' in line:
            current_section = 'territory'
        elif current_section == 'territory' and line and not line.startswith('#'):
            hex_data['territory'] = line.strip()
            current_section = None
        
        # Extract atmosphere
        elif 'Atmosphere' in line or 'ATMOSPHERE' in line:
            current_section = 'atmosphere'
        elif current_section == 'atmosphere' and line and not line.startswith('#'):
            hex_data['atmosphere'] = line.strip()
            current_section = None
        
        # Extract denizen section
        elif '## Denizen' in line:
            current_section = 'denizen'
    
    return hex_data

def extract_settlement_data(content, hex_code):
    """Extract settlement data from markdown content."""
    lines = content.split('\n')
    settlement_data = {
        'name': 'Unknown Settlement',
        'description': 'A settlement in the dying lands',
        'population': 'Unknown',
        'atmosphere': 'Unknown',
        'notable_feature': 'Unknown',
        'local_tavern': 'Unknown',
        'local_power': 'Unknown',
        'settlement_art': ''
    }
    
    # Extract settlement name and population from the encounter line
    for line in lines:
        if '⌂ **' in line and '** - A ' in line:
            # Extract name between ** **
            start = line.find('**') + 2
            end = line.find('**', start)
            if start > 1 and end > start:
                settlement_data['name'] = line[start:end]
            
            # Extract population
            if ' - A ' in line:
                population_start = line.find(' - A ') + 4
                population_end = line.find(' settlement')
                if population_start > 3 and population_end > population_start:
                    settlement_data['population'] = line[population_start:population_end]
            break
    
    # Extract other sections
    for i, line in enumerate(lines):
        # Extract notable feature
        if line.strip() == '## Notable Feature':
            if i + 1 < len(lines) and lines[i + 1].strip():
                settlement_data['notable_feature'] = lines[i + 1].strip()
        
        # Extract atmosphere
        elif line.strip() == '## Atmosphere':
            if i + 1 < len(lines) and lines[i + 1].strip():
                settlement_data['atmosphere'] = lines[i + 1].strip()
        
        # Extract local tavern
        elif '**Local Tavern:**' in line:
            tavern_start = line.find('**Local Tavern:**') + 16
            if tavern_start < len(line):
                settlement_data['local_tavern'] = line[tavern_start:].strip()
        
        # Extract local power
        elif '**Local Power:**' in line:
            power_start = line.find('**Local Power:**') + 15
            if power_start < len(line):
                settlement_data['local_power'] = line[power_start:].strip()
        
        # Extract settlement art (ASCII layout) - look for the section with T=, H=, S=
        elif 'T=' in line and 'H=' in line and 'S=' in line:
            # Find the start of the settlement art section (look backwards for the opening ```)
            art_start = i
            while art_start > 0 and not lines[art_start].strip().startswith('```'):
                art_start -= 1
            
            # Find the end of the settlement art section (look forwards for the closing ```)
            art_end = i
            while art_end < len(lines) and not lines[art_end].strip().startswith('```'):
                art_end += 1
            
            if art_start < art_end:
                # Include the lines from art_start to art_end
                settlement_data['settlement_art'] = '\n'.join(lines[art_start:art_end + 1])
    
    return settlement_data

def generate_settlement_ascii_map(settlement_data, hex_code):
    """Generate ASCII map layout for a settlement."""
    settlement_name = settlement_data['name']
    population_size = settlement_data['population']
    terrain = get_terrain_for_hex(hex_code)
    
    # Determine settlement size based on population
    if '1000' in population_size or '501-1000' in population_size:
        size = 'large'
        width, height = 12, 8
    elif '500' in population_size or '101-500' in population_size:
        size = 'medium'
        width, height = 10, 6
    else:
        size = 'small'
        width, height = 8, 5
    
    # Create settlement layout based on terrain
    settlement_layouts = {
        'mountain': {
            'layout': [
                "    ⛰️⛰️⛰️    ",
                "  ⛰️ SETTLEMENT ⛰️",
                "⛰️   🏠  🏠  🏠   ⛰️",
                "⛰️      🏛️      ⛰️",
                "⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️"
            ],
            'legend': [
                "⛰️ Mountain Peaks",
                "🏠 Stone Houses",
                "🏛️ Meeting Hall"
            ]
        },
        'forest': {
            'layout': [
                "🌲🌲🌲🌲🌲🌲🌲🌲🌲🌲",
                "🌲  TREE VILLAGE  🌲",
                "🌲   🏠  🏠  🏠   🌲",
                "🌲      🔮      🌲",
                "🌲🌲🌲🌲🌲🌲🌲🌲🌲🌲"
            ],
            'legend': [
                "🌲 Cursed Forest",
                "🏠 Tree Houses",
                "🔮 Shrine"
            ]
        },
        'coast': {
            'layout': [
                "🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊",
                "🌊  FISHING VILLE 🌊",
                "🌊   🏠  🏠  🏠   🌊",
                "🌊      ⚓      🌊",
                "🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊"
            ],
            'legend': [
                "🌊 Coastal Waters",
                "🏠 Fisher Huts",
                "⚓ Harbor"
            ]
        },
        'plains': {
            'layout': [
                "🌾🌾🌾🌾🌾🌾🌾🌾🌾🌾",
                "🌾  FARM VILLAGE  🌾",
                "🌾   🏠  🏠  🏠   🌾",
                "🌾      🗿      🌾",
                "🌾🌾🌾🌾🌾🌾🌾🌾🌾🌾"
            ],
            'legend': [
                "🌾 Grain Fields",
                "🏠 Farm Houses",
                "🗿 Ancient Stone"
            ]
        },
        'swamp': {
            'layout': [
                "🌿🌿🌿🌿🌿🌿🌿🌿🌿🌿",
                "🌿  BOG VILLAGE   🌿",
                "🌿   🏠  🏠  🏠   🌿",
                "🌿      🐸      🌿",
                "🌿🌿🌿🌿🌿🌿🌿🌿🌿🌿"
            ],
            'legend': [
                "🌿 Swamp Reeds",
                "🏠 Stilt Houses",
                "🐸 Bog Shrine"
            ]
        }
    }
    
    # Get layout for terrain type
    layout_data = settlement_layouts.get(terrain, settlement_layouts['plains'])
    
    # Build the settlement map
    settlement_map = f"""
{settlement_name.upper()} - SETTLEMENT MAP
{'=' * (len(settlement_name) + 20)}

{chr(10).join(layout_data['layout'])}

LEGEND:
{chr(10).join(layout_data['legend'])}

POPULATION: {population_size}
TERRAIN: {terrain.title()}
"""
    
    return settlement_map

def generate_city_ascii_map(city_data, hex_code):
    """Generate ASCII map layout for a specific city."""
    city_name = city_data['name']
    population_size = city_data['population']
    terrain = city_data['terrain']
    features = city_data['notable_features']
    
    # Determine city size based on population
    if '1000' in population_size or '501-1000' in population_size:
        size = 'large'
        width, height = 15, 10
    elif '500' in population_size or '101-500' in population_size:
        size = 'medium'
        width, height = 12, 8
    else:
        size = 'small'
        width, height = 10, 6
    
    # Create city layout based on lore
    city_layouts = {
        'galgenbeck': {
            'layout': [
                "╔═══════════════╗",
                "║ UPPER DISTRICT║",
                "║  🏛️  🏰  🏛️   ║",
                "║═══════════════║",
                "║ MARKET SQUARE ║",
                "║  🏪  ⛲  🏪   ║", 
                "║═══════════════║",
                "║ LOWER CRYPTS  ║",
                "║  ⚰️  💀  ⚰️   ║",
                "╚═══════════════╝"
            ],
            'legend': [
                "🏛️ Council Chambers",
                "🏰 Ancient Fortress", 
                "🏪 Trading Posts",
                "⛲ Corpse Fountain",
                "⚰️ Burial Crypts",
                "💀 Bone Gardens"
            ]
        },
        'bergen_chrypt': {
            'layout': [
                "╔═════════════╗",
                "║ MOUNTAIN    ║",
                "║    GATE     ║",
                "║     🚪      ║",
                "║═════════════║",
                "║ CRYPT HALLS ║",
                "║  ⚰️  👑  ⚰️ ║",
                "║═════════════║",
                "║ UNDERCROFT  ║",
                "║  💀  🗡️  💀 ║",
                "╚═════════════╝"
            ],
            'legend': [
                "🚪 Mountain Gate",
                "👑 Undead Throne",
                "⚰️ Noble Crypts", 
                "🗡️ Armory",
                "💀 Ancient Tombs"
            ]
        },
        'sarkash': {
            'layout': [
                "🌲🌲🌲🌲🌲🌲🌲🌲🌲🌲",
                "🌲  TREE PLATFORMS  🌲",
                "🌲    🏠    🏠     🌲",
                "🌲         🌉       🌲",
                "🌲    🏠    🏠     🌲",
                "🌲  FOREST SHRINE   🌲",
                "🌲       🔮        🌲",
                "🌲🌲🌲🌲🌲🌲🌲🌲🌲🌲"
            ],
            'legend': [
                "🌲 Cursed Forest",
                "🏠 Tree Houses",
                "🌉 Rope Bridges",
                "🔮 Witch Shrine"
            ]
        },
        'tveland': {
            'layout': [
                "╔═══════════════╗",
                "║ WATCHTOWERS   ║",
                "║  🗼    🗼     ║",
                "║═══════════════║",
                "║ MAIN COMPOUND ║",
                "║  🏘️  🛡️  🏘️  ║",
                "║═══════════════║",
                "║ TRADING POST  ║",
                "║  📦  💰  📦   ║",
                "╚═══════════════╝"
            ],
            'legend': [
                "🗼 Watch Towers",
                "🏘️ Barracks",
                "🛡️ Command Center",
                "📦 Supply Depot",
                "💰 Trading Hall"
            ]
        },
        'kergus': {
            'layout': [
                "🌾🌾🌾🌾🌾🌾🌾🌾🌾🌾",
                "🌾  GRAIN FIELDS   🌾",
                "🌾    🏠    🏠    🌾",
                "🌾         🐄      🌾",
                "🌾  STONE CIRCLE   🌾",
                "🌾       🗿       🌾",
                "🌾    🏠    🏠    🌾",
                "🌾🌾🌾🌾🌾🌾🌾🌾🌾🌾"
            ],
            'legend': [
                "🌾 Grain Fields",
                "🏠 Farm Houses",
                "🐄 Cattle Herds",
                "🗿 Ancient Stones"
            ]
        },
        'pyre_chrypt': {
            'layout': [
                "╔═══SEALED═══╗",
                "║ ABANDONED  ║",
                "║    💀💀    ║",
                "║═══════════║",
                "║ IRON      ║",
                "║ ZIGGURAT  ║",
                "║    🏺     ║",
                "║═══════════║",
                "║ PLAGUE    ║",
                "║ VICTIMS   ║",
                "║  ☠️ ☠️ ☠️  ║",
                "╚═══════════╝"
            ],
            'legend': [
                "💀 Abandoned Streets",
                "🏺 Plague Source",
                "☠️ Mass Graves",
                "🚫 Sealed Gates"
            ]
        }
    }
    
    # Get city-specific layout or create generic one
    city_key = None
    for key, data in lore_db.major_cities.items():
        if data['name'] == city_name:
            city_key = key
            break
    
    if city_key and city_key in city_layouts:
        layout_data = city_layouts[city_key]
    else:
        # Generic layout based on terrain and size
        layout_data = generate_generic_city_layout(city_data, size)
    
    # Create the ASCII representation
    ascii_lines = []
    ascii_lines.append(f"🏰 {city_name.upper()} - HEX {hex_code}")
    ascii_lines.append("=" * max(30, len(city_name) + 15))
    ascii_lines.append("")
    
    # Add the city layout
    for line in layout_data['layout']:
        ascii_lines.append(f"  {line}")
    
    ascii_lines.append("")
    ascii_lines.append("🗝️ LEGEND:")
    for legend_item in layout_data['legend']:
        ascii_lines.append(f"  {legend_item}")
    
    ascii_lines.append("")
    ascii_lines.append(f"📊 Population: {population_size}")
    ascii_lines.append(f"🗺️ Terrain: {terrain.title()}")
    
    return "\n".join(ascii_lines)

def generate_generic_city_layout(city_data, size):
    """Generate a generic city layout based on city data."""
    terrain = city_data['terrain']
    features = city_data['notable_features']
    
    if terrain == 'mountain':
        layout = [
            "╔═════════════╗",
            "║   GATES     ║",
            "║     🚪      ║",
            "║═════════════║",
            "║  BUILDINGS  ║",
            "║  🏠  🏠  🏠 ║",
            "║═════════════║",
            "║   SQUARE    ║",
            "║     ⛲      ║",
            "╚═════════════╝"
        ]
        legend = ["🚪 City Gates", "🏠 Buildings", "⛲ Central Square"]
    elif terrain == 'forest':
        layout = [
            "🌲🌲🌲🌲🌲🌲🌲🌲",
            "🌲  SETTLEMENT  🌲",
            "🌲   🏠  🏠   🌲",
            "🌲      🌉     🌲", 
            "🌲   🏠  🏠   🌲",
            "🌲🌲🌲🌲🌲🌲🌲🌲"
        ]
        legend = ["🌲 Forest", "🏠 Houses", "🌉 Bridges"]
    elif terrain == 'coast':
        layout = [
            "🌊🌊🌊🌊🌊🌊🌊🌊",
            "🌊   HARBOR   🌊",
            "🌊    ⚓      🌊",
            "═══════════════",
            "║  PORT TOWN  ║",
            "║  🏠  🏪  🏠 ║",
            "║═════════════║"
        ]
        legend = ["🌊 Sea", "⚓ Harbor", "🏪 Market", "🏠 Houses"]
    else:  # plains or default
        layout = [
            "╔═════════════╗",
            "║   TOWN      ║",
            "║  🏠  🏠  🏠 ║",
            "║     ⛲      ║",
            "║  🏠  🏪  🏠 ║",
            "╚═════════════╝"
        ]
        legend = ["🏠 Houses", "🏪 Market", "⛲ Town Square"]
    
    return {'layout': layout, 'legend': legend}

def create_templates():
    """Create focused HTML templates."""
    
    # Main map template
    main_map_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗺️ The Dying Lands - Interactive Map</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d1b2e 100%);
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
    }
    
    .map-container {
        background: #0a0a0a;
        border: 2px solid #444;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
    }
    
    .hex-grid {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        line-height: 1.1;
        overflow: auto;
        max-height: 70vh;
        background: #111;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        white-space: nowrap;
    }
    
    .hex-cell {
        cursor: pointer;
        padding: 1px 2px;
        border-radius: 2px;
        transition: all 0.2s;
        display: inline-block;
        width: 16px;
        text-align: center;
        margin-right: 0px;
    }
    
    .hex-cell:hover {
        background-color: rgba(255, 255, 255, 0.2);
        transform: scale(1.2);
    }
    
    .major-city {
        color: #FFD700 !important;
        font-weight: bold;
        text-shadow: 0 0 5px #FFD700;
    }
    
    .terrain-mountain { color: #8D6E63; }
    .terrain-forest { color: #4CAF50; }
    .terrain-coast { color: #2196F3; }
    .terrain-plains { color: #FFC107; }
    .terrain-swamp { color: #795548; }
    .terrain-unknown { color: #9E9E9E; }
    
    .has-content {
        font-weight: bold;
        opacity: 1;
    }
    
    .no-content {
        opacity: 0.6;
    }
    
    .control-panel {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    .city-card {
        background: linear-gradient(135deg, #2a2a2a, #3a2a3a);
        border: 1px solid #555;
        border-radius: 8px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    
    .city-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
    }
    
    .modal-content {
        background: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #555;
    }
    
    .modal-header {
        border-bottom: 1px solid #555;
    }
    
    .modal-footer {
        border-top: 1px solid #555;
    }
    
    .badge {
        font-size: 0.8em;
    }
    
    .legend {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 5px;
        padding: 10px;
        font-size: 0.9em;
    }
    
    .map-row {
        display: block;
        text-align: left;
        margin: 0 auto;
        width: fit-content;
    }
    
    .row-number {
        display: inline-block;
        width: 30px;
        text-align: right;
        margin-right: 5px;
        color: #666;
    }
    </style>
</head>
<body>
    <div class="container-fluid">
        <header class="text-center py-3">
            <h1 class="mb-0">🗺️ The Dying Lands</h1>
            <p class="text-muted">Interactive Hex Map - {{ map_width }}×{{ map_height }} ({{ total_hexes }} hexes)</p>
        </header>
        
        <!-- Control Panel -->
        <div class="control-panel">
            <div class="row">
                <div class="col-md-8">
                    <div class="btn-group me-2" role="group">
                        <button class="btn btn-warning btn-sm" onclick="showTerrainOverview()">🗺️ Terrain</button>
                        <button class="btn btn-info btn-sm" onclick="showLoreOverview()">📜 Lore</button>
                        <button class="btn btn-secondary btn-sm" onclick="showLegend()">🗂️ Legend</button>
                    </div>
                    <div class="btn-group" role="group">
                        <button class="btn btn-success btn-sm" onclick="generateFullMap()">⚡ Generate All</button>
                        <button class="btn btn-danger btn-sm" onclick="resetContinent()">🔄 Reset Continent</button>
                        <button class="btn btn-primary btn-sm" onclick="zoomIn()">🔍+</button>
                        <button class="btn btn-primary btn-sm" onclick="zoomOut()">🔍-</button>
                    </div>
                </div>
                <div class="col-md-4">
                    <small class="text-muted">
                        Click hexes to view/generate content<br>
                        <span class="major-city">◆</span> = Major Cities
                    </small>
                </div>
            </div>
        </div>
        
        <!-- Major Cities Overview -->
        <div class="row mb-3">
            <div class="col-12">
                <h5>🏰 Major Cities</h5>
                <div class="row">
                    {% for city in major_cities %}
                    <div class="col-md-4 col-lg-3">
                        <div class="city-card card" onclick="showCityDetails('{{ city.hex_code }}')">
                            <div class="card-body py-2">
                                <h6 class="card-title mb-1">{{ city.name }}</h6>
                                <small class="text-muted">
                                    {{ city.hex_code }} - {{ city.region.title() }}<br>
                                    Pop: {{ city.population }}
                                </small>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <!-- ASCII Map -->
        <div class="map-container">
            <div class="hex-grid" id="map-grid">
                <!-- Column headers -->
                <div class="text-center mb-2">
                    <span style="margin-right: 20px;"></span>
                    {% for x in range(1, map_width + 1) %}
                        {% if x <= 9 %}
                            <span style="margin-right: 4px; font-size: 9px; display: inline-block; width: 12px; text-align: center;">0{{ x }}</span>
                        {% else %}
                            <span style="margin-right: 4px; font-size: 9px; display: inline-block; width: 12px; text-align: center;">{{ x }}</span>
                        {% endif %}
                    {% endfor %}
                </div>
                
                <!-- Map rows -->
                {% for y in range(1, map_height + 1) %}
                <div class="map-row">
                    <span class="row-number">{{ "%02d"|format(y) }}</span>
                    {% for x in range(1, map_width + 1) %}
                        {% set hex_code = "%02d%02d"|format(x, y) %}
                        {% set hex_data = ascii_map[hex_code] %}
                        <span class="hex-cell {{ hex_data.css_class }} {{ 'has-content' if hex_data.has_content else 'no-content' }}"
                              onclick="showHexDetails('{{ hex_code }}')"
                              title="Hex {{ hex_code }}{% if hex_data.is_city %} - {{ hex_data.city_name }}{% endif %}">{{ hex_data.symbol }}</span>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Legend -->
        <div class="legend" id="legend">
            <h6>🗂️ Map Legend</h6>
            <div class="row">
                <div class="col-md-6">
                    <strong>Terrain:</strong><br>
                    <span class="terrain-mountain">^</span> Mountain &nbsp;
                    <span class="terrain-forest">♠</span> Forest &nbsp;
                    <span class="terrain-coast">~</span> Coast<br>
                    <span class="terrain-plains">.</span> Plains &nbsp;
                    <span class="terrain-swamp">#</span> Swamp
                </div>
                <div class="col-md-6">
                    <strong>Locations:</strong><br>
                    <span class="major-city">◆</span> Major Cities<br>
                    <strong>Bold</strong> = Has Content
                </div>
            </div>
        </div>
    </div>
    
    <!-- Hex Details Modal -->
    <div class="modal fade" id="hexModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="hexModalTitle">Hex Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="hexModalBody">
                    Loading...
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="generateHexContent()">Generate Content</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- City Details Modal -->
    <div class="modal fade" id="cityModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="cityModalTitle">City Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="cityModalBody">
                    Loading...
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Terrain Overview Modal -->
    <div class="modal fade" id="terrainModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">🗺️ Terrain Overview</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="terrainModalBody">
                    Loading...
                </div>
            </div>
        </div>
    </div>
    
    <!-- Lore Overview Modal -->
    <div class="modal fade" id="loreModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">📜 Mörk Borg Lore</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="loreModalBody">
                    Loading...
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    let currentHex = '';
    let mapZoom = 1;
    
    function showHexDetails(hexCode) {
        currentHex = hexCode;
        
        fetch(`/api/hex/${hexCode}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('hexModalTitle').textContent = data.title;
                
                if (data.is_major_city) {
                    showCityDetails(hexCode);
                    return;
                }
                
                let html = '';
                if (data.exists) {
                    html = data.html || `<p>${data.description || 'No description available'}</p>`;
                } else {
                    html = `<p>No content generated for hex ${hexCode}</p>`;
                }
                
                document.getElementById('hexModalBody').innerHTML = html;
                new bootstrap.Modal(document.getElementById('hexModal')).show();
            })
            .catch(error => {
                console.error('Error loading hex:', error);
                document.getElementById('hexModalBody').innerHTML = '<p class="text-danger">Error loading hex content</p>';
                new bootstrap.Modal(document.getElementById('hexModal')).show();
            });
    }
    
    function showCityDetails(hexCode) {
        fetch(`/api/city/${hexCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const city = data.city;
                    document.getElementById('cityModalTitle').textContent = city.name;
                    
                    let html = `
                        <div class="row">
                            <div class="col-md-6">
                                <h6>🗺️ City Map</h6>
                                <pre style="background:#111; color:#e0e0e0; padding:15px; border-radius:5px; font-size:11px; line-height:1.1; overflow:auto; max-height:400px;">${data.city_map}</pre>
                            </div>
                            <div class="col-md-6">
                                <h6>🏰 City Information</h6>
                                <p><strong>Location:</strong> Hex ${hexCode} (${city.region.charAt(0).toUpperCase() + city.region.slice(1)})</p>
                                <p><strong>Population:</strong> ${city.population}</p>
                                <p><strong>Description:</strong> ${city.description}</p>
                                <p><strong>Atmosphere:</strong> ${city.atmosphere}</p>
                                
                                <h6 class="mt-3">Notable Features</h6>
                                <ul style="font-size:0.9em;">
                    `;
                    
                    city.notable_features.forEach(feature => {
                        html += `<li>${feature}</li>`;
                    });
                    
                    html += `
                                </ul>
                                
                                <h6 class="mt-3">Key NPCs</h6>
                                <div class="d-flex flex-wrap gap-2">
                    `;
                    
                    city.key_npcs.forEach(npc => {
                        html += `<span class="badge bg-info">${npc}</span>`;
                    });
                    
                    html += `
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <h6>🏰 Regional NPCs</h6>
                                <div class="d-flex flex-wrap gap-2 mb-3">
                    `;
                    
                    data.regional_npcs.forEach(npc => {
                        html += `<span class="badge bg-secondary">${npc}</span>`;
                    });
                    
                    html += `
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>⚔️ Active Factions</h6>
                    `;
                    
                    data.factions.forEach(faction => {
                        const influenceColors = {
                            'religious': 'warning',
                            'apocalyptic': 'danger',
                            'political': 'primary',
                            'biological': 'success',
                            'magical': 'info'
                        };
                        const badgeColor = influenceColors[faction.influence] || 'secondary';
                        
                        html += `
                            <div class="card mb-2">
                                <div class="card-body py-2">
                                    <h6 class="mb-1" style="font-size:0.9em;">${faction.name} <span class="badge bg-${badgeColor}">${faction.influence}</span></h6>
                                    <small class="text-muted">${faction.description}</small>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += `
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('cityModalBody').innerHTML = html;
                    new bootstrap.Modal(document.getElementById('cityModal')).show();
                } else {
                    alert('Error loading city details: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error loading city:', error);
                alert('Error loading city details');
            });
    }
    
    function generateHexContent() {
        if (!currentHex) return;
        
        fetch('/api/generate-hex', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hex: currentHex })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showHexDetails(currentHex);
                setTimeout(() => window.location.reload(), 1000);
            } else {
                alert('Failed to generate content: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error generating hex:', error);
            alert('Error generating hex content');
        });
    }
    
    function generateFullMap() {
        if (confirm('Generate content for the entire map? This may take a while...')) {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '⏳ Generating...';
            btn.disabled = true;
            
            fetch('/api/generate-full-map', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Generated ${data.count} hexes!`);
                    window.location.reload();
                } else {
                    alert('Failed to generate map: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error generating map:', error);
                alert('Error generating full map');
            })
            .finally(() => {
                btn.textContent = originalText;
                btn.disabled = false;
            });
        }
    }
    
    function resetContinent() {
        if (confirm('🚨 RESET ENTIRE CONTINENT? 🚨\\n\\nThis will DELETE ALL generated content and create a completely fresh map.\\n\\nThis action cannot be undone!')) {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '🔄 Resetting...';
            btn.disabled = true;
            
            // Disable all other buttons during reset
            const allButtons = document.querySelectorAll('button');
            allButtons.forEach(button => button.disabled = true);
            
            fetch('/api/reset-continent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ ${data.message}`);
                    window.location.reload();
                } else {
                    alert('❌ Failed to reset continent: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error resetting continent:', error);
                alert('❌ Error resetting continent');
            })
            .finally(() => {
                // Re-enable all buttons
                allButtons.forEach(button => button.disabled = false);
                btn.textContent = originalText;
            });
        }
    }
    
    function showTerrainOverview() {
        fetch('/api/terrain-overview')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const [width, height] = data.dimensions;
                    let html = `
                        <div class="row">
                            <div class="col-md-8">
                                <pre style="background:#111; color:#e0e0e0; padding:15px; border-radius:5px; font-size:10px; line-height:1.1; overflow:auto; max-height:60vh;">${data.terrain_map}</pre>
                            </div>
                            <div class="col-md-4">
                                <h6>📊 Terrain Statistics</h6>
                    `;
                    
                    for (const [terrain, count] of Object.entries(data.distribution)) {
                        const percentage = ((count / (width * height)) * 100).toFixed(1);
                        html += `<div class="mb-2">
                            <span class="terrain-${terrain}">${getTerrainSymbol(terrain)}</span>
                            <strong>${terrain.charAt(0).toUpperCase() + terrain.slice(1)}</strong>: 
                            ${count} hexes (${percentage}%)
                        </div>`;
                    }
                    
                    html += `
                                <hr>
                                <h6>🗺️ Map Info</h6>
                                <div class="small">
                                    <strong>Dimensions:</strong> ${width}×${height}<br>
                                    <strong>Total Hexes:</strong> ${width * height}<br>
                                    <strong>Lore Integration:</strong> ✅ Active
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('terrainModalBody').innerHTML = html;
                    new bootstrap.Modal(document.getElementById('terrainModal')).show();
                } else {
                    alert('Error loading terrain overview: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error loading terrain overview:', error);
                alert('Error loading terrain overview');
            });
    }
    
    function showLoreOverview() {
        fetch('/api/lore-overview')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let html = `
                        <div class="row">
                            <div class="col-md-6">
                                <h6>🏰 Major Cities (${data.major_cities})</h6>
                    `;
                    
                    data.cities_data.forEach(city => {
                        html += `
                            <div class="card mb-2" onclick="showCityDetails('${city.hex_code}')" style="cursor:pointer;">
                                <div class="card-body py-2">
                                    <h6 class="mb-1">${city.name} <span class="badge bg-secondary">${city.hex_code}</span></h6>
                                    <small class="text-muted">${city.region} - ${city.population}</small>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += `
                            </div>
                            <div class="col-md-6">
                                <h6>⚔️ Major Factions (${data.factions})</h6>
                    `;
                    
                    data.factions_data.forEach(faction => {
                        const influenceColors = {
                            'religious': 'warning',
                            'apocalyptic': 'danger',
                            'political': 'primary',
                            'biological': 'success',
                            'magical': 'info'
                        };
                        const badgeColor = influenceColors[faction.influence] || 'secondary';
                        
                        html += `
                            <div class="card mb-2">
                                <div class="card-body py-2">
                                    <h6 class="mb-1">${faction.name} <span class="badge bg-${badgeColor}">${faction.influence}</span></h6>
                                    <small class="text-muted">Active in: ${faction.regions.join(', ')}</small>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += `
                            </div>
                        </div>
                        <div class="mt-3 text-center">
                            <div class="alert alert-info">
                                <strong>🎲 Game Master Note:</strong> This lore is integrated into hex generation. 
                                Cities and factions influence content in their regions.
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('loreModalBody').innerHTML = html;
                    new bootstrap.Modal(document.getElementById('loreModal')).show();
                } else {
                    alert('Error loading lore overview: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error loading lore overview:', error);
                alert('Error loading lore overview');
            });
    }
    
    function getTerrainSymbol(terrain) {
        const symbols = {
            'mountain': '^', 'forest': '♠', 'coast': '~',
            'plains': '.', 'swamp': '#', 'unknown': '?'
        };
        return symbols[terrain] || '?';
    }
    
    function zoomIn() {
        mapZoom = Math.min(mapZoom * 1.2, 3);
        applyZoom();
    }
    
    function zoomOut() {
        mapZoom = Math.max(mapZoom / 1.2, 0.5);
        applyZoom();
    }
    
    function applyZoom() {
        const mapElement = document.getElementById('map-grid');
        if (mapElement) {
            mapElement.style.transform = `scale(${mapZoom})`;
            mapElement.style.transformOrigin = 'top left';
        }
    }
    
    function showLegend() {
        document.getElementById('legend').scrollIntoView({ behavior: 'smooth' });
    }
    </script>
</body>
</html>"""

    # Setup template for when content doesn't exist
    setup_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗺️ Setup Required - The Dying Lands</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d1b2e 100%);
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .setup-card {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #444;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
    }
    </style>
</head>
<body>
    <div class="setup-card">
        <h1 class="mb-4">🗺️ The Dying Lands</h1>
        <h3 class="text-warning mb-3">{{ message }}</h3>
        <p class="mb-4">{{ action }}</p>
        <div class="d-flex gap-3 justify-content-center">
            <button class="btn btn-success btn-lg" onclick="generateMap()">🚀 Generate Full Map</button>
            <button class="btn btn-warning btn-lg" onclick="resetAndGenerate()">🔄 Reset & Generate</button>
        </div>
        <div id="status" class="mt-3"></div>
    </div>
    
    <script>
    function generateMap() {
        const btn = event.target;
        const status = document.getElementById('status');
        
        btn.disabled = true;
        btn.textContent = '⏳ Generating Map...';
        status.innerHTML = '<div class="text-info">This may take a few minutes...</div>';
        
        fetch('/api/generate-full-map', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                status.innerHTML = `<div class="text-success">✅ Generated ${data.count} hexes!</div>`;
                setTimeout(() => window.location.reload(), 2000);
            } else {
                status.innerHTML = `<div class="text-danger">❌ Error: ${data.error}</div>`;
                btn.disabled = false;
                btn.textContent = '🚀 Generate Full Map';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            status.innerHTML = '<div class="text-danger">❌ Generation failed</div>';
            btn.disabled = false;
            btn.textContent = '🚀 Generate Full Map';
        });
    }
    
    function resetAndGenerate() {
        const btn = event.target;
        const status = document.getElementById('status');
        
        btn.disabled = true;
        btn.textContent = '🔄 Resetting & Generating...';
        status.innerHTML = '<div class="text-warning">🗑️ Clearing old content and generating fresh map...</div>';
        
        fetch('/api/reset-continent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                status.innerHTML = `<div class="text-success">✅ ${data.message}</div>`;
                setTimeout(() => window.location.reload(), 2000);
            } else {
                status.innerHTML = `<div class="text-danger">❌ Error: ${data.error}</div>`;
                btn.disabled = false;
                btn.textContent = '🔄 Reset & Generate';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            status.innerHTML = '<div class="text-danger">❌ Reset failed</div>';
            btn.disabled = false;
            btn.textContent = '🔄 Reset & Generate';
        });
    }
    </script>
</body>
</html>"""

    # Create templates directory
    os.makedirs('../web/templates', exist_ok=True)
    
    with open('../web/templates/main_map.html', 'w') as f:
        f.write(main_map_template)
    
    with open('../web/templates/setup.html', 'w') as f:
        f.write(setup_template)

@app.route('/generate', methods=['POST'])
def generate_map():
    global main_map_generator
    language = request.form.get('language', 'en')
    # Re-instantiate the map generator with the new language
    main_map_generator = MainMapGenerator({'language': language})
    main_map_generator.generate_full_map({'language': language})
    return redirect(url_for('main_map'))

if __name__ == '__main__':
    # Create templates
    # create_templates()
    
    print("🌐 Starting The Dying Lands ASCII Map Viewer...")
    print("   Open http://localhost:5000 in your browser")
    print("   Features:")
    print("   • Interactive ASCII map with clickable hexes")
    print("   • Major cities with lore information")
    print("   • Terrain overview and faction details")
    print("   • Full map generation capabilities")
    print("   Press Ctrl+C to stop the server")
    
    app.run(debug=False, host='127.0.0.1', port=5000) 