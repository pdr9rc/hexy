"""
Markdown formatting utilities for generating consistent hex content.
"""

from typing import Dict, Any, List


def format_threat_level_and_territory(hex_data: Dict[str, Any], translation_system=None) -> List[str]:
    """
    Format threat level and territory sections for markdown.
    
    Args:
        hex_data: Dictionary containing hex data
        translation_system: Translation system instance
        
    Returns:
        List of markdown lines
    """
    lines = []
    
    # Add threat level and territory as separate sections
    if hex_data.get('threat_level'):
        threat_label = translation_system.t('ui.threat_level', fallback='Threat Level') if translation_system else 'Threat Level'
        lines.append(f"## {threat_label}")
        lines.append(hex_data['threat_level'])
        lines.append("")
    
    if hex_data.get('territory'):
        territory_label = translation_system.t('ui.territory', fallback='Territory') if translation_system else 'Territory'
        lines.append(f"## {territory_label}")
        lines.append(hex_data['territory'])
        lines.append("")
    
    return lines


def format_loot_section(hex_data: Dict[str, Any], translation_system=None) -> List[str]:
    """
    Format loot section for markdown.
    
    Args:
        hex_data: Dictionary containing hex data
        translation_system: Translation system instance
        
    Returns:
        List of markdown lines
    """
    lines = []
    
    if hex_data.get('loot'):
        loot_label = translation_system.t('ui.loot_found', fallback='Loot Found') if translation_system else 'Loot Found'
        lines.append(f"## {loot_label}")
        lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
        lines.append("")
    
    return lines


def format_beast_details(hex_data: Dict[str, Any], translation_system=None) -> List[str]:
    """
    Format beast details for markdown.
    
    Args:
        hex_data: Dictionary containing hex data
        translation_system: Translation system instance
        
    Returns:
        List of markdown lines
    """
    lines = []
    
    lines.append("## Beast Details")
    type_label = translation_system.t('type') if translation_system else 'Type'
    feature_label = translation_system.t('feature') if translation_system else 'Feature'
    behavior_label = translation_system.t('behavior') if translation_system else 'Behavior'
    
    beast_name = hex_data.get('beast_name') or hex_data.get('beast_type', 'Unknown')
    lines.append(f"**{type_label}:** {beast_name}")
    lines.append(f"**{feature_label}:** {hex_data.get('beast_feature', 'Unknown')}")
    lines.append(f"**{behavior_label}:** {hex_data.get('beast_behavior', 'Unknown')}")
    
    # Beast description
    if hex_data.get('beast_description'):
        lines.append(f"**Description:** {hex_data['beast_description']}")
    
    # Beast stats (HP, morale, etc.)
    if hex_data.get('beast_stats'):
        stats = hex_data['beast_stats']
        if isinstance(stats, dict):
            stats_str = ", ".join(f"{k}: {v}" for k, v in stats.items())
            lines.append(f"**Stats:** {stats_str}")
        else:
            lines.append(f"**Stats:** {stats}")
    
    # Special abilities
    if hex_data.get('beast_special'):
        lines.append(f"**Special:** {hex_data['beast_special']}")
    
    # Notes
    if hex_data.get('beast_notes'):
        lines.append(f"**Notes:** {hex_data['beast_notes']}")
    
    lines.append("")
    
    # Add common sections
    lines.extend(format_threat_level_and_territory(hex_data, translation_system))
    lines.extend(format_loot_section(hex_data, translation_system))
    
    return lines


def format_sea_encounter_details(hex_data: Dict[str, Any], translation_system=None) -> List[str]:
    """
    Format sea encounter details for markdown.
    
    Args:
        hex_data: Dictionary containing hex data
        translation_system: Translation system instance
        
    Returns:
        List of markdown lines
    """
    lines = []
    
    lines.append("## Sea Encounter Details")
    type_label = translation_system.t('type') if translation_system else 'Type'
    lines.append(f"**{type_label}:** {hex_data.get('encounter_type', 'Unknown')}")
    lines.append("")
    
    # Add common sections
    lines.extend(format_threat_level_and_territory(hex_data, translation_system))
    lines.extend(format_loot_section(hex_data, translation_system))
    
    return lines


def format_npc_details(hex_data: Dict[str, Any], translation_system=None) -> List[str]:
    """
    Format NPC details for markdown.
    
    Args:
        hex_data: Dictionary containing hex data
        translation_system: Translation system instance
        
    Returns:
        List of markdown lines
    """
    lines = []
    
    lines.append("## NPC Details")
    name_label = translation_system.t('name') if translation_system else 'Name'
    type_label = translation_system.t('type') if translation_system else 'Type'
    
    # Support both npc_name and name
    npc_name = hex_data.get('npc_name') or hex_data.get('name', 'Unknown')
    lines.append(f"**{name_label}:** {npc_name}")
    lines.append(f"**{type_label}:** {hex_data.get('denizen_type', hex_data.get('npc_occupation', 'Unknown'))}")
    
    # Mörk Borg NPC details
    if hex_data.get('trait') or hex_data.get('npc_personality'):
        trait_label = translation_system.t('npc_trait') if translation_system else 'Trait'
        lines.append(f"**{trait_label}:** {hex_data.get('trait') or hex_data.get('npc_personality')}")
    if hex_data.get('concern'):
        concern_label = translation_system.t('npc_concern') if translation_system else 'Concern'
        lines.append(f"**{concern_label}:** {hex_data.get('concern')}")
    if hex_data.get('want'):
        want_label = translation_system.t('npc_want') if translation_system else 'Want'
        lines.append(f"**{want_label}:** {hex_data.get('want')}")
    if hex_data.get('apocalypse_attitude'):
        apocalypse_label = translation_system.t('npc_apocalypse_attitude') if translation_system else 'Apocalypse Attitude'
        lines.append(f"**{apocalypse_label}:** {hex_data.get('apocalypse_attitude')}")
    if hex_data.get('secret') or hex_data.get('npc_secret'):
        secret_label = translation_system.t('npc_secret') if translation_system else 'Secret'
        lines.append(f"**{secret_label}:** {hex_data.get('secret') or hex_data.get('npc_secret')}")
    
    # NPC carries (equipment, items)
    if hex_data.get('npc_carries'):
        lines.append(f"**Carries:** {hex_data['npc_carries']}")
    
    # NPC notes
    if hex_data.get('npc_notes'):
        lines.append(f"**Notes:** {hex_data['npc_notes']}")
    
    # Fallback to old fields if new ones not available
    if not hex_data.get('trait') and not hex_data.get('npc_personality') and hex_data.get('motivation'):
        motivation_label = translation_system.t('motivation') if translation_system else 'Motivation'
        lines.append(f"**{motivation_label}:** {hex_data.get('motivation')}")
    if not hex_data.get('concern') and hex_data.get('feature'):
        feature_label = translation_system.t('feature') if translation_system else 'Feature'
        lines.append(f"**{feature_label}:** {hex_data.get('feature')}")
    if not hex_data.get('want') and hex_data.get('demeanor'):
        demeanor_label = translation_system.t('demeanor') if translation_system else 'Demeanor'
        lines.append(f"**{demeanor_label}:** {hex_data.get('demeanor')}")
    
    lines.append("")
    
    # Add loot section
    lines.extend(format_loot_section(hex_data, translation_system))
    
    return lines 