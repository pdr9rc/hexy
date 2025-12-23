"""
NPC generation utilities for creating consistent NPC encounters.
"""

import random
from typing import Dict, Any, List, Optional


def generate_npc_encounter(db_manager, language: str = 'en') -> Dict[str, Any]:
    """
    Generate NPC encounter using Mörk Borg tables.
    
    Args:
        db_manager: Database manager instance
        language: Language for content ('en' or 'pt')
        
    Returns:
        Dictionary containing NPC encounter data
    """
    # Get NPC tables from database
    # Names: use first/second name tables as the base for actual names
    first_names: List[str] = db_manager.get_table('npc_names', 'first_names', language) or []
    second_names: List[str] = db_manager.get_table('npc_names', 'second_names', language) or []
    npc_traits = db_manager.get_table('npc_traits', 'traits', language) or []
    npc_trades = db_manager.get_table('npc_trades', 'trades', language) or []
    npc_concerns = db_manager.get_table('npc_concerns', 'concerns', language) or []
    npc_wants = db_manager.get_table('npc_wants', 'wants', language) or []
    npc_apocalypse = db_manager.get_table('npc_apocalypse', 'apocalypse_attitudes', language) or []
    npc_secrets = db_manager.get_table('npc_secrets', 'secrets', language) or []
    
    # Generate NPC name: compose from first + second; use prefix/suffix only as modifiers
    name_prefixes: List[str] = db_manager.get_table('core', 'denizen_names_prefix', language) or []
    name_suffixes: List[str] = db_manager.get_table('core', 'denizen_names_suffix', language) or []

    # Base name
    if first_names and second_names:
        base_first = random.choice(first_names)
        base_second = random.choice(second_names)
        name = f"{base_first} {base_second}"
    elif first_names:
        name = random.choice(first_names)
    elif second_names:
        name = random.choice(second_names)
    else:
        name = "Unknown Denizen"

    # Optional modifiers
    if name_prefixes and random.random() < 0.5:
        name = f"{random.choice(name_prefixes)} {name}"
    if name_suffixes and random.random() < 0.5:
        name = f"{name} {random.choice(name_suffixes)}"
    
    # Generate Mörk Borg elements
    trait = random.choice(npc_traits) if npc_traits else "Unsettling"
    trade = random.choice(npc_trades) if npc_trades else "wanderer"
    concern = random.choice(npc_concerns) if npc_concerns else "seeks an angle"
    want = random.choice(npc_wants) if npc_wants else "safety"
    apocalypse_attitude = random.choice(npc_apocalypse) if npc_apocalypse else "Expects the worst"
    secret = random.choice(npc_secrets) if npc_secrets else "Hides a minor vice"
    
    return {
        'name': name,
        'trait': trait,
        'trade': trade,
        'concern': concern,
        'want': want,
        'apocalypse_attitude': apocalypse_attitude,
        'secret': secret
    }


def generate_npc_description(npc_data: Dict[str, Any]) -> str:
    """
    Generate NPC description from NPC data.
    
    Args:
        npc_data: Dictionary containing NPC information
        
    Returns:
        Formatted NPC description string
    """
    name = npc_data.get('name', 'Unknown')
    trait = npc_data.get('trait', 'unnerving')
    trade = npc_data.get('trade', 'wanderer')
    
    return f"{name} is a {trait} {trade}."


def generate_npc_markdown(npc_data: Dict[str, Any], hex_code: str, language: str = 'en') -> str:
    """
    Generate markdown content for NPC encounter.
    
    Args:
        npc_data: Dictionary containing NPC information
        hex_code: Hex code for the encounter
        language: Language for content ('en' or 'pt')
        
    Returns:
        Markdown formatted NPC encounter content
    """
    from ..translation_system import translation_system
    
    name = npc_data.get('name', 'Unknown')
    trait = npc_data.get('trait', 'unnerving')
    trade = npc_data.get('trade', 'wanderer')
    concern = npc_data.get('concern', 'seeks something unknown')
    want = npc_data.get('want', 'knowledge')
    apocalypse_attitude = npc_data.get('apocalypse_attitude', 'We\'re doomed!')
    secret = npc_data.get('secret', 'Just a regular person')
    location = npc_data.get('location', 'Wandering the area')
    carries = npc_data.get('carries', 'Nothing of note')
    notes = npc_data.get('notes')
    
    # Get translated field labels
    trait_label = translation_system.t('ui.npc_trait', language=language)
    concern_label = translation_system.t('ui.npc_concern', language=language)
    want_label = translation_system.t('ui.npc_want', language=language)
    apocalypse_label = translation_system.t('ui.npc_apocalypse_attitude', language=language)
    secret_label = translation_system.t('ui.npc_secret', language=language)
    location_label = translation_system.t('ui.npc_location', language=language)
    carries_label = translation_system.t('ui.npc_carries', language=language)
    
    lines = []
    lines.append(f"☉ **{name} - {trade}**")
    if notes:
        lines.append(f"**Notes:** {notes}")
    lines.append("")
    lines.append(f"**{name}** - {trade}")
    lines.append("")
    lines.append(f"**{trait_label}:** {trait}")
    lines.append(f"**{concern_label}:** {concern}")
    lines.append(f"**{want_label}:** {want}")
    lines.append(f"**{apocalypse_label}:** {apocalypse_attitude}")
    lines.append(f"**{secret_label}:** {secret}")
    lines.append(f"**{location_label}:** {location}")
    lines.append("")
    lines.append(f"**{carries_label}:** {carries}")
    lines.append("")
    lines.append("")
    lines.append("## Notable Feature")
    lines.append("NPC territory")
    lines.append("")
    lines.append("## Atmosphere")
    lines.append(npc_data.get('atmosphere', 'Tense and watchful'))
    lines.append("")
    lines.append("## NPC Details")
    lines.append(f"**Name:** {name}")
    lines.append(f"**Type:** {trade}")
    lines.append(f"**{trait_label}:** {trait}")
    lines.append(f"**{concern_label}:** {concern}")
    lines.append(f"**{want_label}:** {want}")
    lines.append(f"**{apocalypse_label}:** {apocalypse_attitude}")
    lines.append(f"**{secret_label}:** {secret}")
    lines.append("")
    
    return '\n'.join(lines) 