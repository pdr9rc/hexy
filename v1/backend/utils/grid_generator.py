"""
Grid generation utilities for creating consistent hex grids.
"""

from typing import Dict, Any, Tuple
from backend.mork_borg_lore_database import MorkBorgLoreDatabase


def get_map_dimensions() -> Tuple[int, int]:
    """
    Get the map dimensions.
    
    Returns:
        Tuple of (width, height)
    """
    # Import terrain system to get map dimensions
    try:
        from backend.terrain_system import terrain_system
        return terrain_system.get_map_dimensions()
    except ImportError:
        # Fallback to default dimensions
        return 16, 16


def generate_hex_grid(lore_db: MorkBorgLoreDatabase) -> Dict[str, Any]:
    """
    Generate a hex grid with major cities and terrain.
    
    Args:
        lore_db: Mork Borg lore database instance
        
    Returns:
        Dictionary containing hex grid data
    """
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
                    'is_city': True,
                    'city_key': city_key,
                    'city_data': city_data
                }
            else:
                # Regular hex - will be populated by terrain system
                grid[hex_code] = {
                    'x': x, 'y': y,
                    'terrain': None,
                    'is_city': False
                }
    
    return grid


def get_terrain_for_hex(hex_code: str) -> str:
    """
    Get terrain for a specific hex.
    
    Args:
        hex_code: Hex code to get terrain for
        
    Returns:
        Terrain string
    """
    # Import terrain system to get terrain for hex
    try:
        from backend.terrain_system import terrain_system
        from backend.mork_borg_lore_database import MorkBorgLoreDatabase
        lore_db = MorkBorgLoreDatabase()
        return terrain_system.get_terrain_for_hex(hex_code, lore_db)
    except ImportError:
        # Fallback to default
        return 'unknown'


def get_terrain_symbol(terrain: str) -> str:
    """
    Get terrain symbol for display.
    
    Args:
        terrain: Terrain type
        
    Returns:
        Terrain symbol string
    """
    # Import terrain system to get terrain symbol
    try:
        from backend.terrain_system import terrain_system
        return terrain_system.get_terrain_symbol(terrain)
    except ImportError:
        # Fallback to hardcoded symbols
        terrain_symbols = {
            'mountain': '^',
            'forest': 'T',
            'coast': '~',
            'plains': '.',
            'swamp': 'S',
            'desert': 'D',
            'sea': '≈'
        }
        return terrain_symbols.get(terrain, '.')


def determine_content_symbol(content_type: str, terrain: str) -> str:
    """
    Determine the appropriate symbol based on content type and terrain.
    
    Args:
        content_type: Type of content in the hex
        terrain: Terrain type
        
    Returns:
        Symbol string for display
    """
    if content_type == 'settlement':
        return '⌂'  # Settlement marker
    elif content_type == 'ruins':
        return '▲'  # Ruins marker  
    elif content_type == 'beast':
        return '※'  # Beast marker
    elif content_type == 'npc':
        return '☉'  # NPC marker
    elif content_type == 'sea_encounter':
        return '≈'  # Sea encounter marker
    else:
        # Otherwise keep terrain symbol for basic content
        return get_terrain_symbol(terrain)


def determine_css_class(content_type: str, terrain: str) -> str:
    """
    Determine CSS class based on content type and terrain.
    
    Args:
        content_type: Type of content in the hex
        terrain: Terrain type
        
    Returns:
        CSS class string
    """
    if content_type == 'settlement':
        return 'settlement'
    else:
        return f'terrain-{terrain}' 