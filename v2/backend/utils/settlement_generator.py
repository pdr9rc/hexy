"""
Settlement generation utilities for creating consistent settlement atmospheres and features.
Prefer data-backed lookups with graceful fallbacks.
"""

import random
from typing import Dict, Any


def _resolve_db(db_manager=None):
    if db_manager is not None:
        return db_manager
    try:
        from ..database_manager import database_manager
        return database_manager
    except Exception:
        return None


def _terrain_entry(db_manager, terrain: str, language: str):
    if db_manager is None:
        return {}
    entry = db_manager.get_table("terrain", terrain, language)
    return entry if isinstance(entry, dict) else {}


def generate_settlement_atmosphere(terrain: str, db_manager=None, language: str = "en") -> str:
    """
    Generate settlement atmosphere based on terrain.
    
    Args:
        terrain: Terrain type (mountain, forest, coast, plains, swamp, desert)
        
    Returns:
        Atmosphere description string
    """
    db = _resolve_db(db_manager)
    terrain_data = _terrain_entry(db, terrain, language)
    atmospheres = terrain_data.get("atmospheres") or terrain_data.get("features") or []
    if atmospheres:
        return random.choice(atmospheres)
    fallback = {
        'mountain': 'Cold and windswept',
        'forest': 'Dark and oppressive',
        'coast': 'Salty and windswept',
        'plains': 'Open and exposed',
        'swamp': 'Misty and damp',
        'desert': 'Hot and dry'
    }
    return fallback.get(terrain, 'Strange and unsettling')


def generate_settlement_feature(terrain: str, db_manager=None, language: str = "en") -> str:
    """
    Generate settlement feature based on terrain.
    
    Args:
        terrain: Terrain type (mountain, forest, coast, plains, swamp, desert)
        
    Returns:
        Feature description string
    """
    db = _resolve_db(db_manager)
    terrain_data = _terrain_entry(db, terrain, language)
    features = terrain_data.get("features") or terrain_data.get("encounters") or []
    if features:
        return random.choice(features)
    fallback = {
        'mountain': 'Built into the rock face',
        'forest': 'Hidden among ancient trees',
        'coast': 'Perched on rocky cliffs',
        'plains': 'Surrounded by endless fields',
        'swamp': 'Built on stilts above the mire',
        'desert': 'Protected by high walls'
    }
    return fallback.get(terrain, 'Foreboding and unknown')


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
        from .tavern_generator import generate_tavern_details as centralized_generate
        return centralized_generate(db_manager, language)
    except ImportError:
        # Fallback to hardcoded values
        return {
            'select_dish': {"name": "Hearty stew", "price": 4, "currency": "silver"},
            'budget_dish': {"name": "Watery soup", "price": 2, "currency": "silver"},
            'innkeeper_quirk': "Seems nervous about something",
            'patron_trait': "Quiet"
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
        from .tavern_generator import generate_weather as centralized_generate
        return centralized_generate(db_manager, language)
    except ImportError:
        db = _resolve_db(db_manager)
        conditions = []
        if db:
            data = db.get_table("weather", "weather_conditions", language)
            if isinstance(data, list):
                conditions = data
        return random.choice(conditions) if conditions else "Lifeless grey"


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
        from .tavern_generator import generate_city_event as centralized_generate
        return centralized_generate(db_manager, language)
    except ImportError:
        db = _resolve_db(db_manager)
        events = []
        if db:
            data = db.get_table("city_events", "city_events", language)
            if isinstance(data, list):
                events = data
        return random.choice(events) if events else "Something unsettling happens in the streets"