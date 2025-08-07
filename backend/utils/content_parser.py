"""
Content parser utilities for extracting structured data from markdown content.
"""
import re
from typing import Dict, Any, Optional


def parse_content_sections(content: str) -> Dict[str, str]:
    """
    Parse markdown content and extract sections using regex patterns.
    
    Args:
        content: Markdown content string
        
    Returns:
        Dictionary containing parsed sections
    """
    # Use centralized markdown parser
    from backend.utils.markdown_parser import parse_content_sections as centralized_parse
    data = centralized_parse(content)
    
    # Add territory parsing (not in centralized version)
    territory_match = re.search(r'## Territory\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if territory_match:
        data['territory'] = territory_match.group(1).strip()
    
    # Add dungeon details parsing (not in centralized version)
    description_match = re.search(r'## Dungeon Details\n(.+?)(?:\n##|$)', content, re.DOTALL)
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
    # Use centralized markdown parser
    from backend.utils.markdown_parser import parse_loot_section as centralized_parse
    return centralized_parse(content)


def parse_magical_effect(content: str) -> Optional[str]:
    """
    Parse magical effect from markdown content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Magical effect string or None if not found
    """
    # Use centralized markdown parser
    from backend.utils.markdown_parser import parse_magical_effect as centralized_parse
    return centralized_parse(content)


def extract_field_value(content: str, field_name: str) -> Optional[str]:
    """
    Extract a specific field value from markdown content.
    
    Args:
        content: Markdown content string
        field_name: Name of the field to extract
        
    Returns:
        Field value or None if not found
    """
    # Try both 'Field: value' and '**Field:** value' (Markdown bold) patterns
    patterns = [
        rf'{field_name}:\s*([^\n]+)',
        rf'\*\*{field_name}:\*\*\s*([^\n]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def parse_hex_data(content: str) -> Dict[str, Any]:
    """
    Parse hex data from markdown content using field extraction.
    
    Args:
        content: Markdown content string
        
    Returns:
        Dictionary containing parsed hex data
    """
    data = {}
    
    # Common fields to extract
    fields = [
        'encounter', 'denizen', 'notable_feature', 'atmosphere',
        'threat_level', 'territory', 'danger', 'treasure',
        'beast_type', 'beast_feature', 'beast_behavior',
        'dungeon_type', 'encounter_type', 'name', 'denizen_type',
        'motivation', 'feature', 'demeanor', 'carries',
        'local_tavern', 'local_power', 'ancient_knowledge'
    ]
    
    for field in fields:
        value = extract_field_value(content, field)
        if value:
            data[field] = value
    
    # Parse loot if present
    loot_data = parse_loot_section(content)
    if loot_data:
        data['loot'] = loot_data
    
    # Parse magical effect if present
    magical_effect = parse_magical_effect(content)
    if magical_effect:
        data['magical_effect'] = magical_effect
    
    return data 