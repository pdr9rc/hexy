"""
Settlement data creation utilities for creating consistent settlement responses.
"""

from typing import Dict, Any


def create_settlement_response_data(hex_data: Dict[str, Any], hex_code: str, terrain: str) -> Dict[str, Any]:
    """
    Create standardized settlement response data.
    
    Args:
        hex_data: Dictionary containing hex data
        hex_code: Hex code
        terrain: Terrain type
        
    Returns:
        Dictionary containing settlement response data
    """
    return {
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
    }


def create_major_city_response_data(city_data: Dict[str, Any], hex_code: str, terrain: str) -> Dict[str, Any]:
    """
    Create standardized major city response data.
    
    Args:
        city_data: Dictionary containing city data
        hex_code: Hex code
        terrain: Terrain type
        
    Returns:
        Dictionary containing major city response data
    """
    return {
        'exists': True,
        'is_major_city': True,
        'is_settlement': False,
        'hex_type': 'major_city',
        'terrain': terrain,
        'title': city_data.get('name', f'City {hex_code}'),
        'description': city_data.get('description', 'A major city'),
        'population': city_data.get('population', 'Unknown'),
        'region': city_data.get('region', 'Unknown'),
        'name': city_data.get('name', f'City {hex_code}'),
        'hex_code': hex_code,
        'redirect_to': 'city'
    } 