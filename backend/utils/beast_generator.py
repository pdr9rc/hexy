"""
Beast generation utilities for creating consistent beast encounters.
"""

import random
from typing import Dict, Any, List, Optional


def generate_beast_encounter(db_manager, language: str = 'en') -> Dict[str, Any]:
    """
    Generate beast encounter using Mörk Borg tables.
    
    Args:
        db_manager: Database manager instance
        language: Language for content ('en' or 'pt')
        
    Returns:
        Dictionary containing beast encounter data
    """
    # Get beast tables from database
    beast_types = db_manager.get_table('bestiary', 'beast_types', language)
    beast_features = db_manager.get_table('bestiary', 'beast_features', language)
    beast_behaviors = db_manager.get_table('bestiary', 'beast_behaviors', language)
    
    # Generate elements - use same index for all tables to get matching beast
    if beast_types and beast_features and beast_behaviors:
        # Select random index to get matching beast across all tables
        beast_index = random.randint(0, len(beast_types) - 1)
        beast_type = beast_types[beast_index]
        feature = beast_features[beast_index] if beast_index < len(beast_features) else "unnatural appearance"
        behavior = beast_behaviors[beast_index] if beast_index < len(beast_behaviors) else "hunts in the area"
    else:
        # Fallback to random selection if tables are missing
        beast_type = random.choice(beast_types) if beast_types else "Wild beast"
        feature = random.choice(beast_features) if beast_features else "unnatural appearance"
        behavior = random.choice(beast_behaviors) if beast_behaviors else "hunts in the area"
    
    return {
        'beast_type': beast_type,
        'beast_feature': feature,
        'beast_behavior': behavior
    }


def generate_beast_description(beast_data: Dict[str, Any]) -> str:
    """
    Generate beast description from beast data.
    
    Args:
        beast_data: Dictionary containing beast information
        
    Returns:
        Formatted beast description string
    """
    beast_type = beast_data.get('beast_type', 'Unknown beast')
    feature = beast_data.get('beast_feature', 'mysterious appearance')
    behavior = beast_data.get('beast_behavior', 'hunts in the area')
    
    return f"A {beast_type} with {feature} that {behavior}."


def generate_beast_markdown(beast_data: Dict[str, Any], hex_code: str) -> str:
    """
    Generate markdown content for beast encounter.
    
    Args:
        beast_data: Dictionary containing beast information
        hex_code: Hex code for the encounter
        
    Returns:
        Markdown formatted beast encounter content
    """
    beast_type = beast_data.get('beast_type', 'Unknown beast')
    feature = beast_data.get('beast_feature', 'mysterious appearance')
    behavior = beast_data.get('beast_behavior', 'hunts in the area')
    
    lines = []
    lines.append(f"※ **{beast_type}**")
    lines.append("")
    lines.append(f"A {beast_type} with {feature} that {behavior}.")
    lines.append("")
    lines.append("## Encounter")
    lines.append(f"The {beast_type} is encountered in this area.")
    lines.append("")
    lines.append("## Denizen")
    lines.append(f"The {beast_type} is the primary denizen of this hex.")
    lines.append("")
    lines.append("## Notable Feature")
    lines.append(f"The {beast_type}'s {feature} makes it distinctive.")
    lines.append("")
    lines.append("## Atmosphere")
    lines.append(f"The presence of the {beast_type} creates a tense atmosphere.")
    lines.append("")
    lines.append("## Threat Level")
    lines.append("High - this beast is dangerous to travelers.")
    lines.append("")
    lines.append("## Territory")
    lines.append(f"The {beast_type} claims this area as its territory.")
    lines.append("")
    
    return '\n'.join(lines) 