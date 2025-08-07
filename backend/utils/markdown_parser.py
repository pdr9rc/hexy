"""
Markdown parsing utilities for extracting structured data from hex content.
"""

import re
from typing import Dict, Any, Optional


def parse_content_sections(content: str) -> Dict[str, Any]:
    """
    Parse common markdown sections from hex content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Dictionary containing parsed sections
    """
    data = {}
    
    # Parse common sections
    encounter_match = re.search(r'## Encounter\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if encounter_match:
        data['encounter'] = encounter_match.group(1).strip()
    
    denizen_match = re.search(r'## Denizen\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if denizen_match:
        data['denizen'] = denizen_match.group(1).strip()
    
    notable_feature_match = re.search(r'## Notable Feature\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if notable_feature_match:
        data['notable_feature'] = notable_feature_match.group(1).strip()
    
    atmosphere_match = re.search(r'## Atmosphere\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if atmosphere_match:
        data['atmosphere'] = atmosphere_match.group(1).strip()
    
    description_match = re.search(r'## NPC Details\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if description_match:
        data['description'] = description_match.group(1).strip()
    
    return data


def parse_loot_section(content: str) -> Optional[Dict[str, str]]:
    """
    Parse loot section from markdown content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Dictionary containing loot data or None if not found
    """
    loot_match = re.search(r'## Loot Found\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if loot_match:
        loot_content = loot_match.group(1).strip()
        return {
            'type': 'Unknown',
            'item': 'Unknown item',
            'description': loot_content[:100] + '...' if len(loot_content) > 100 else loot_content,
            'full_description': loot_content
        }
    return None


def parse_magical_effect(content: str) -> Optional[str]:
    """
    Parse magical effect from markdown content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Magical effect string or None if not found
    """
    effect_match = re.search(r'## Magical Effect\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if effect_match:
        return effect_match.group(1).strip()
    return None


def extract_title_from_content(content: str) -> str:
    """
    Extract title from markdown content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Title string or "Untitled" if not found
    """
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Look for NPC title pattern
        if line.startswith('☉ **') and '**' in line[4:]:
            start = line.find('☉ **') + 4
            end = line.find('**', start)
            if start > 3 and end > start:
                return line[start:end]
        
        # Look for other title patterns
        elif line.startswith('**') and line.endswith('**'):
            return line.strip('*')
        
        # Look for markdown headers
        elif line.startswith('# '):
            return line[2:].strip()
    
    return "Untitled"


def determine_hex_type(content: str) -> str:
    """
    Determine hex type from markdown content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Hex type string
    """
    if '⌂ **' in content:
        return 'settlement'
    elif '▲ **Ancient Ruins**' in content:
        return 'ruins'
    elif '※ **' in content:
        return 'beast'
    elif '☉ **Wandering' in content:
        return 'npc'
    elif '≈ **' in content:
        return 'sea_encounter'
    else:
        return 'basic' 