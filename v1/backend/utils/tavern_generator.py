"""
Tavern generation utilities for creating consistent tavern encounters.
"""

import random
from typing import Dict, Any, List, Optional


def generate_tavern_details(db_manager, language: str = 'en') -> Dict[str, Any]:
    """
    Generate Mörk Borg tavern details.
    
    Args:
        db_manager: Database manager instance
        language: Language for content ('en' or 'pt')
        
    Returns:
        Dictionary containing tavern details
    """
    # Get tavern tables from database
    select_menu = db_manager.get_table('tavern_menu', 'select_menu', language) or []
    budget_menu = db_manager.get_table('tavern_menu', 'budget_menu', language) or []
    innkeeper_quirks = db_manager.get_table('tavern_innkeeper', 'innkeeper_quirks', language) or []
    patron_traits = db_manager.get_table('tavern_patrons', 'patron_traits', language) or []
    
    # Generate tavern elements
    select_dish = random.choice(select_menu) if select_menu else {"name": "Mysterious stew", "price": 4, "currency": "silver"}
    budget_dish = random.choice(budget_menu) if budget_menu else {"name": "Watery soup", "price": 2, "currency": "silver"}
    innkeeper_quirk = random.choice(innkeeper_quirks) if innkeeper_quirks else "Seems nervous about something"
    patron_trait = random.choice(patron_traits) if patron_traits else "Mysterious"
    
    return {
        'select_dish': select_dish,
        'budget_dish': budget_dish,
        'innkeeper_quirk': innkeeper_quirk,
        'patron_trait': patron_trait
    }


def generate_weather(db_manager, language: str = 'en') -> str:
    """
    Generate Mörk Borg weather conditions.
    
    Args:
        db_manager: Database manager instance
        language: Language for content ('en' or 'pt')
        
    Returns:
        Weather description string
    """
    weather_conditions = db_manager.get_table('weather', 'weather_conditions', language) or []
    return random.choice(weather_conditions) if weather_conditions else "Lifeless grey"


def generate_city_event(db_manager, language: str = 'en') -> str:
    """
    Generate Mörk Borg city events.
    
    Args:
        db_manager: Database manager instance
        language: Language for content ('en' or 'pt')
        
    Returns:
        City event description string
    """
    city_events = db_manager.get_table('city_events', 'city_events', language) or []
    return random.choice(city_events) if city_events else "Something mysterious happens in the streets" 