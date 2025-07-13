#!/usr/bin/env python3
"""
The Dying Lands ASCII Map Viewer
Interactive web viewer for the hex-based map with ASCII representation.
"""

import os
import json
import markdown
from flask import Flask, render_template, jsonify, request, send_from_directory
from mork_borg_lore_database import MorkBorgLoreDatabase
from terrain_system import terrain_system
from hex_generator import hex_generator
from map_generator import map_generator
from translation_system import translation_system

app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')

# Initialize systems
lore_db = MorkBorgLoreDatabase()

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
                             action="Run map_generator.py to create the map")
    
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

@app.route('/api/hex/<hex_code>')
def get_hex_info(hex_code):
    """Get hex information for popup."""
    hex_file = f"dying_lands_output/hexes/hex_{hex_code}.md"
    
    # Check if it's a major city
    hardcoded = lore_db.get_hardcoded_hex(hex_code)
    if hardcoded and hardcoded.get('type') == 'major_city':
        city_key = hardcoded['city_key']
        city_data = lore_db.major_cities[city_key]
        
        return jsonify({
            'exists': True,
            'is_major_city': True,
            'title': city_data['name'],
            'description': city_data['description'],
            'population': city_data['population'],
            'region': city_data['region'],
            'atmosphere': city_data['atmosphere'],
            'notable_features': city_data['notable_features'],
            'key_npcs': city_data['key_npcs'],
            'hex_code': hex_code
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
            html = markdown.markdown(content, extensions=['codehilite', 'fenced_code', 'tables'])
            title = extract_title(content)
            
            # Extract structured data for the new modal system
            hex_data = extract_hex_data(content, hex_code)
            
            return jsonify({
                'exists': True,
                'is_major_city': False,
                'is_settlement': False,
                'title': title,
                'html': html,
                'raw': content,
                'hex_code': hex_code,
                'terrain': hex_data.get('terrain', 'unknown'),
                'encounter': hex_data.get('encounter', 'Unknown encounter'),
                'denizen': hex_data.get('denizen', 'No denizen information'),
                'notable_feature': hex_data.get('notable_feature', 'No notable features'),
                'atmosphere': hex_data.get('atmosphere', 'Unknown atmosphere'),
                'treasure': hex_data.get('treasure', 'No treasure found'),
                'ancient_knowledge': hex_data.get('ancient_knowledge', 'No ancient knowledge'),
                'danger': hex_data.get('danger', 'No dangers present'),
                'threat_level': hex_data.get('threat_level', 'Unknown threat level'),
                'territory': hex_data.get('territory', 'No territory claimed'),
                'location': hex_data.get('location', 'Unknown location'),
                'motivation': hex_data.get('motivation', 'Unknown motivation'),
                'demeanor': hex_data.get('demeanor', 'Unknown demeanor'),
                'feature': hex_data.get('feature', 'No notable features'),
                'settlement_layout': hex_data.get('settlement_layout', 'No settlement layout')
            })
        except Exception as e:
            return jsonify({
                'exists': False,
                'error': str(e),
                'hex_code': hex_code
            })
    else:
        return jsonify({
            'exists': False,
            'title': f'Hex {hex_code}',
            'html': f'<p>No content generated for hex {hex_code}</p>',
            'raw': f'No content for hex {hex_code}',
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
                    'settlement_layout': settlement_data.get('settlement_art', 'No settlement layout'),
                    'custom_settlement_layout': settlement_data.get('custom_settlement_layout', 'No custom settlement layout')
                })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Settlement not found'})

@app.route('/api/save-hex/<hex_code>', methods=['POST'])
def save_hex_content(hex_code):
    """Save edited hex content."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'success': False, 'error': 'No content provided'})
        
        edited_content = data['content']
        hex_file = f"dying_lands_output/hexes/hex_{hex_code}.md"
        
        # Ensure the hexes directory exists
        os.makedirs(os.path.dirname(hex_file), exist_ok=True)
        
        # Convert the ASCII content back to markdown format
        markdown_content = convert_ascii_to_markdown(edited_content, hex_code)
        
        # Save the content to the hex file
        with open(hex_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return jsonify({
            'success': True,
            'message': f'Hex {hex_code} content saved successfully',
            'hex_code': hex_code
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lore-overview')
def get_lore_overview():
    """Get complete lore overview."""
    try:
        # Use unified map generator
        result = map_generator.get_lore_overview()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/terrain-overview')
def get_terrain_overview():
    """Get terrain analysis."""
    try:
        # Use unified terrain system
        result = map_generator.get_terrain_overview()
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
        hex_data = map_generator.generate_single_hex(hex_code)
        
        return jsonify({
            'success': True,
            'hex_code': hex_code,
            'message': translation_system.t('hex_generated', hex_code=hex_code)
        })
        
    except Exception as e:
        print(f"Error generating hex {hex_code}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-full-map', methods=['POST'])
def generate_full_map():
    """Generate content for the entire map."""
    try:
        # Generate using unified system
        hex_data_list = map_generator.generate_full_map(skip_existing=False)
        
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
        result = map_generator.reset_continent()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Reset error: {e}")
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
                    'terrain': str(hardcoded['terrain']),
                    'symbol': '◆',
                    'is_city': True,
                    'city_name': str(city_data['name']),
                    'population': str(city_data['population']),
                    'region': str(city_data['region']),
                    'has_content': True,
                    'css_class': 'major-city'
                }
            else:
                # Regular terrain - check for generated content to add visual indicators
                terrain = get_terrain_for_hex(hex_code)
                has_content = os.path.exists(f"dying_lands_output/hexes/hex_{hex_code}.md")
                
                # Determine symbol based on content and terrain
                symbol = get_terrain_symbol(terrain)
                content_type = None
                
                if has_content:
                    # Check what type of content exists to add visual indicators
                    content_type = get_hex_content_type(hex_code)
                    if content_type == 'settlement':
                        symbol = '⌂'  # Settlement marker
                    elif content_type == 'ruins':
                        symbol = '▲'  # Ruins marker  
                    elif content_type == 'beast':
                        symbol = '※'  # Beast marker
                    elif content_type == 'npc':
                        symbol = '☉'  # NPC marker
                    # Otherwise keep terrain symbol for basic content
                
                # Determine CSS class based on content type
                css_class = f'terrain-{terrain}'
                if content_type == 'settlement':
                    css_class = 'settlement'
                elif has_content:
                    css_class += ' has-content'
                
                grid[hex_code] = {
                    'x': x, 'y': y,
                    'terrain': str(terrain),
                    'symbol': str(symbol),
                    'is_city': False,
                    'has_content': bool(has_content),
                    'content_type': str(content_type) if content_type else None,
                    'css_class': str(css_class)
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
        elif '※ **Wild Beast' in content:  # Beast marker
            return 'beast'
        elif '☉ **Wandering' in content:  # NPC marker
            return 'npc'
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
        'treasure': 'No treasure found',
        'ancient_knowledge': 'No ancient knowledge',
        'danger': 'No dangers present',
        'threat_level': 'Unknown threat level',
        'territory': 'No territory claimed',
        'location': 'Unknown location',
        'motivation': 'Unknown motivation',
        'demeanor': 'Unknown demeanor',
        'feature': 'No notable features',
        'settlement_layout': 'No settlement layout'
    }
    
    current_section = None
    section_content = []
    
    for line in lines:
        line = line.strip()
        
        # Extract terrain from **Terrain:** line
        if line.startswith('**Terrain:**'):
            terrain_start = line.find('**Terrain:**') + 11
            hex_data['terrain'] = line[terrain_start:].strip()
        
        # Extract encounter
        elif line.startswith('**Encounter:**') or line == '## Encounter':
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            current_section = 'encounter'
            section_content = []
        elif current_section == 'encounter' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract denizen information
        elif line.startswith('**Denizen:**') or line == '## Denizen':
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            current_section = 'denizen'
            section_content = []
        elif current_section == 'denizen' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract notable feature
        elif line.startswith('**Notable Features:**') or line == '## Notable Feature':
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            current_section = 'notable_feature'
            section_content = []
        elif current_section == 'notable_feature' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract atmosphere (handle both inline and section formats)
        elif line.startswith('**Atmosphere:**'):
            # Extract atmosphere from the same line
            atmosphere_start = line.find('**Atmosphere:**') + 14
            hex_data['atmosphere'] = line[atmosphere_start:].strip()
            current_section = None
            section_content = []
        elif line == '## Atmosphere':
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            current_section = 'atmosphere'
            section_content = []
        elif current_section == 'atmosphere' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract treasure
        elif line.startswith('**Treasure Found:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract treasure from the same line
            treasure_start = line.find('**Treasure Found:**') + 18
            hex_data['treasure'] = line[treasure_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'treasure' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract ancient knowledge
        elif line.startswith('**Ancient Knowledge:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            current_section = 'ancient_knowledge'
            section_content = []
        elif current_section == 'ancient_knowledge' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract danger
        elif line.startswith('**Danger:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract danger from the same line
            danger_start = line.find('**Danger:**') + 10
            hex_data['danger'] = line[danger_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'danger' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract threat level
        elif line.startswith('**Threat Level:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract threat level from the same line
            threat_start = line.find('**Threat Level:**') + 16
            hex_data['threat_level'] = line[threat_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'threat_level' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract territory
        elif line.startswith('**Territory:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract territory from the same line
            territory_start = line.find('**Territory:**') + 13
            hex_data['territory'] = line[territory_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'territory' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract location
        elif line.startswith('**Location:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract location from the same line
            location_start = line.find('**Location:**') + 12
            hex_data['location'] = line[location_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'location' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract motivation
        elif line.startswith('**Motivation:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract motivation from the same line
            motivation_start = line.find('**Motivation:**') + 14
            hex_data['motivation'] = line[motivation_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'motivation' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract demeanor
        elif line.startswith('**Demeanor:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract demeanor from the same line
            demeanor_start = line.find('**Demeanor:**') + 12
            hex_data['demeanor'] = line[demeanor_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'demeanor' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Extract feature
        elif line.startswith('**Feature:**'):
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            # Extract feature from the same line
            feature_start = line.find('**Feature:**') + 11
            hex_data['feature'] = line[feature_start:].strip()
            current_section = None
            section_content = []
        elif current_section == 'feature' and line and not line.startswith('**') and not line.startswith('```') and not line.startswith('##'):
            section_content.append(line)
        
        # Add support for settlement layout
        if line == '## Settlement Layout':
            if current_section and section_content:
                hex_data[current_section] = '\n'.join(section_content).strip()
            current_section = 'settlement_layout'
            section_content = []
        elif current_section == 'settlement_layout' and line and not line.startswith('##'):
            section_content.append(line)
    
    # Handle the last section
    if current_section and section_content:
        hex_data[current_section] = '\n'.join(section_content).strip()
    
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
        'settlement_art': '',
        'custom_settlement_layout': ''
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
        
        # Extract custom settlement layout from ## Settlement Layout section
        elif line.strip() == '## Settlement Layout':
            # Find the start of the code block (look for opening ```)
            layout_start = i + 1
            while layout_start < len(lines) and not lines[layout_start].strip().startswith('```'):
                layout_start += 1
            
            if layout_start < len(lines):
                # Find the end of the code block (look for closing ```)
                layout_end = layout_start + 1
                while layout_end < len(lines) and not lines[layout_end].strip().startswith('```'):
                    layout_end += 1
                
                if layout_end < len(lines):
                    # Include the lines from layout_start to layout_end
                    settlement_data['custom_settlement_layout'] = '\n'.join(lines[layout_start:layout_end + 1])
        
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
    """Create template files for the project."""
    templates_dir = "dying_lands_output/templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create various template files...
    # (existing template creation code)

def convert_ascii_to_markdown(ascii_content, hex_code):
    """Convert edited ASCII content back to markdown format."""
    lines = ascii_content.strip().split('\n')
    markdown_lines = []
    
    # Extract hex info from the first few lines
    hex_info = None
    terrain = 'unknown'
    
    for line in lines:
        line = line.strip()
        if 'HEX' in line and '-' in line:
            # Extract hex code and terrain
            parts = line.split('-')
            if len(parts) >= 2:
                hex_part = parts[0].strip()
                terrain_part = parts[1].strip()
                if 'HEX' in hex_part:
                    hex_info = hex_part.replace('║', '').strip()
                    terrain = terrain_part.replace('║', '').strip().lower()
            break
    
    # Start building markdown content
    markdown_lines.append(f"# Hex {hex_code}")
    markdown_lines.append("")
    markdown_lines.append(f"**Terrain:** {terrain.title()}")
    markdown_lines.append("")
    
    # Parse the ASCII content sections
    current_section = None
    section_content = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('╔') or line.startswith('╠') or line.startswith('╚'):
            continue
            
        # Remove box characters
        line = line.replace('║', '').strip()
        
        if 'TERRAIN ART:' in line:
            current_section = 'terrain_art'
            section_content = []
        elif 'ENCOUNTER:' in line:
            if current_section and section_content:
                markdown_lines.extend(format_section_for_markdown(current_section, section_content))
            current_section = 'encounter'
            section_content = []
        elif 'DENIZEN:' in line:
            if current_section and section_content:
                markdown_lines.extend(format_section_for_markdown(current_section, section_content))
            current_section = 'denizen'
            section_content = []
        elif 'NOTABLE FEATURES:' in line:
            if current_section and section_content:
                markdown_lines.extend(format_section_for_markdown(current_section, section_content))
            current_section = 'notable_features'
            section_content = []
        elif 'ATMOSPHERE:' in line:
            if current_section and section_content:
                markdown_lines.extend(format_section_for_markdown(current_section, section_content))
            current_section = 'atmosphere'
            section_content = []
        elif current_section:
            if line:
                section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        markdown_lines.extend(format_section_for_markdown(current_section, section_content))
    
    return '\n'.join(markdown_lines)

def format_section_for_markdown(section, content):
    """Format a section's content for markdown."""
    lines = []
    
    if section == 'terrain_art':
        lines.append("**Terrain Art:**")
        lines.append("```")
        lines.extend(content)
        lines.append("```")
        lines.append("")
    elif section == 'encounter':
        lines.append("**Encounter:**")
        lines.append(' '.join(content))
        lines.append("")
    elif section == 'denizen':
        lines.append("**Denizen:**")
        lines.append(' '.join(content))
        lines.append("")
    elif section == 'notable_features':
        lines.append("**Notable Features:**")
        lines.append(' '.join(content))
        lines.append("")
    elif section == 'atmosphere':
        lines.append("**Atmosphere:**")
        lines.append(' '.join(content))
        lines.append("")
    
    return lines

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