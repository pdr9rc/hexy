"""
Settlement generation utilities for creating consistent settlement atmospheres and features.
"""

from typing import Dict, Any


def generate_settlement_atmosphere(terrain: str) -> str:
    """
    Generate settlement atmosphere based on terrain.
    
    Args:
        terrain: Terrain type (mountain, forest, coast, plains, swamp, desert)
        
    Returns:
        Atmosphere description string
    """
    atmospheres = {
        'mountain': 'Cold and windswept',
        'forest': 'Dark and mysterious',
        'coast': 'Salty and windswept',
        'plains': 'Open and exposed',
        'swamp': 'Misty and damp',
        'desert': 'Hot and dry'
    }
    return atmospheres.get(terrain, 'Strange and unsettling')


def generate_settlement_feature(terrain: str) -> str:
    """
    Generate settlement feature based on terrain.
    
    Args:
        terrain: Terrain type (mountain, forest, coast, plains, swamp, desert)
        
    Returns:
        Feature description string
    """
    features = {
        'mountain': 'Built into the rock face',
        'forest': 'Hidden among ancient trees',
        'coast': 'Perched on rocky cliffs',
        'plains': 'Surrounded by endless fields',
        'swamp': 'Built on stilts above the mire',
        'desert': 'Protected by high walls'
    }
    return features.get(terrain, 'Mysterious and foreboding')


def generate_tavern_details(db_manager=None, language: str = 'en') -> Dict[str, Any]:
    """
    Generate Mörk Borg tavern details.
    
    Args:
        db_manager: Database manager instance (optional)
        language: Language for content ('en' or 'pt')
        
    Returns:
        Dictionary containing tavern details
    """
    import random
    
    # Use centralized tavern generator if available
    try:
        from backend.utils.tavern_generator import generate_tavern_details as centralized_generate
        return centralized_generate(db_manager, language)
    except ImportError:
        # Fallback to hardcoded values
        return {
            'select_dish': {"name": "Mysterious stew", "price": 4, "currency": "silver"},
            'budget_dish': {"name": "Watery soup", "price": 2, "currency": "silver"},
            'innkeeper_quirk': "Seems nervous about something",
            'patron_trait': "Mysterious"
        }


def generate_weather(db_manager=None, language: str = 'en') -> str:
    """
    Generate Mörk Borg weather conditions.
    
    Args:
        db_manager: Database manager instance (optional)
        language: Language for content ('en' or 'pt')
        
    Returns:
        Weather description string
    """
    # Use centralized weather generator if available
    try:
        from backend.utils.tavern_generator import generate_weather as centralized_generate
        return centralized_generate(db_manager, language)
    except ImportError:
        # Fallback to hardcoded value
        return "Lifeless grey"


def generate_city_event(db_manager=None, language: str = 'en') -> str:
    """
    Generate Mörk Borg city events.
    
    Args:
        db_manager: Database manager instance (optional)
        language: Language for content ('en' or 'pt')
        
    Returns:
        City event description string
    """
    # Use centralized city event generator if available
    try:
        from backend.utils.tavern_generator import generate_city_event as centralized_generate
        return centralized_generate(db_manager, language)
    except ImportError:
        # Fallback to hardcoded value
        return "Something mysterious happens in the streets" 