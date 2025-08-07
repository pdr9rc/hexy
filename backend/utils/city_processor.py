"""
City processor utilities for handling major city data and processing.
"""
from typing import Dict, Any, Optional
from flask import jsonify


def process_major_city_data(city_data: Dict[str, Any], hex_code: str, current_language: str = 'en') -> Dict[str, Any]:
    """
    Process major city data and return standardized response.
    
    Args:
        city_data: City data dictionary from database manager
        hex_code: Hex code for the city
        current_language: Current language ('en' or 'pt')
        
    Returns:
        Dictionary containing processed city data for API response
    """
    # Use the data directly without language-specific suffixes
    title = city_data.get('name', '')
    description = city_data.get('description', '')
    atmosphere = city_data.get('atmosphere', '')
    notable_features = city_data.get('notable_features', [])
    
    return {
        'exists': True,
        'is_major_city': True,
        'title': title,
        'description': description,
        'population': city_data.get('population', 'Unknown'),
        'region': city_data.get('region', 'central'),
        'atmosphere': atmosphere,
        'notable_features': notable_features,
        'key_npcs': city_data.get('key_npcs', []),
        'hex_code': hex_code,
    }


def create_major_city_response(city_data: Dict[str, Any], hex_code: str, current_language: str = 'en'):
    """
    Create a Flask JSON response for major city data.
    
    Args:
        city_data: City data dictionary from lore database
        hex_code: Hex code for the city
        current_language: Current language ('en' or 'pt')
        
    Returns:
        Flask JSON response with major city data
    """
    processed_data = process_major_city_data(city_data, hex_code, current_language)
    return jsonify(processed_data) 