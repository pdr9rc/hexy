"""
ASCII art processing utilities for parsing and handling ASCII art blocks in content.
"""
from typing import Dict, Any, List, Optional


def process_ascii_blocks(content: str) -> Dict[str, Any]:
    """
    Process content and extract ASCII art blocks.
    
    Args:
        content: Content string that may contain ASCII art blocks
        
    Returns:
        Dictionary containing processed data with ASCII art sections
    """
    data = {
        'name': None,
        'description': None,
        'encounter': None,
        'atmosphere': None,
        'notable_feature': None,
        'local_tavern': None,
        'local_power': None,
        'settlement_art': None,
        'tavern_details': None
    }
    
    current_section = None
    section_content = []
    in_ascii = False
    ascii_lines = []
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # ASCII art block detection
        if line == '```':
            in_ascii = not in_ascii
            if not in_ascii:
                # End of ASCII art block
                if ascii_lines:
                    data['settlement_art'] = '\n'.join(ascii_lines)
                    ascii_lines = []
            continue
            
        if in_ascii:
            ascii_lines.append(line)
            continue
            
        # Section header detection
        if line.startswith('## '):
            # Save previous section
            if current_section and section_content:
                section_text = '\n'.join(section_content).strip()
                if current_section in data:
                    if current_section == 'tavern_details':
                        # Don't overwrite tavern_details with string content
                        pass
                    else:
                        data[current_section] = section_text
                section_content = []
            
            # Start new section
            current_section = line[3:].lower().replace(' ', '_')
            continue
            
        # Content line
        if current_section:
            section_content.append(line)
        else:
            # Handle lines before first section
            if line.startswith('**') and line.endswith('**'):
                # This might be a title
                data['name'] = line.strip('*')
            elif not data.get('description'):
                # First non-empty line might be description
                data['description'] = line
    
    # Save last section
    if current_section and section_content:
        section_text = '\n'.join(section_content).strip()
        if current_section in data:
            if current_section == 'tavern_details':
                # Don't overwrite tavern_details with string content
                pass
            else:
                data[current_section] = section_text
    
    return data


def extract_ascii_art(content: str) -> Optional[str]:
    """
    Extract ASCII art from content.
    
    Args:
        content: Content string that may contain ASCII art
        
    Returns:
        ASCII art string or None if not found
    """
    lines = content.split('\n')
    ascii_lines = []
    in_ascii = False
    
    for line in lines:
        line = line.strip()
        
        if line == '```':
            in_ascii = not in_ascii
            continue
            
        if in_ascii:
            ascii_lines.append(line)
    
    return '\n'.join(ascii_lines) if ascii_lines else None


def parse_loot_section_from_ascii(content: str) -> Optional[Dict[str, str]]:
    """
    Parse loot section from content that may contain ASCII art.
    
    Args:
        content: Content string that may contain loot information
        
    Returns:
        Dictionary containing loot data or None if not found
    """
    if 'loot_found' not in content.lower():
        return None
        
    # Split by sections to get the first loot_found section
    sections = content.split('## ')
    for section in sections:
        if section.startswith('Loot Found'):
            loot_content = section.replace('Loot Found', '').strip()
            return _parse_loot_section(loot_content)
    
    return None


def _parse_loot_section(loot_content: str) -> Optional[Dict[str, str]]:
    """
    Parse loot section content.
    
    Args:
        loot_content: Content of loot section
        
    Returns:
        Dictionary containing parsed loot data or None
    """
    import re
    
    # Parse loot content using regex patterns
    loot_data = {
        'type': 'Unknown',
        'item': 'Unknown item',
        'description': '',
        'full_description': loot_content
    }
    
    # Try to extract type from markdown patterns
    type_match = re.search(r'\*\*Type:\*\*\s*([^\n]+)', loot_content, re.IGNORECASE)
    if type_match:
        loot_data['type'] = type_match.group(1).strip()
    
    # Try to extract item from markdown patterns
    item_match = re.search(r'\*\*Item:\*\*\s*([^\n]+)', loot_content, re.IGNORECASE)
    if item_match:
        loot_data['item'] = item_match.group(1).strip()
    
    # Try to extract description from markdown patterns
    desc_match = re.search(r'\*\*Description:\*\*\s*([^\n]+)', loot_content, re.IGNORECASE)
    if desc_match:
        loot_data['description'] = desc_match.group(1).strip()
    
    # If no structured data found, try to extract from plain text
    if loot_data['type'] == 'Unknown' and loot_data['item'] == 'Unknown item':
        lines = loot_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('**'):
                # First non-empty line without markdown might be the item
                if loot_data['item'] == 'Unknown item':
                    loot_data['item'] = line
                elif not loot_data['description']:
                    loot_data['description'] = line
                break
    
    # Create a short description if none found
    if not loot_data['description']:
        loot_data['description'] = loot_content[:100] + '...' if len(loot_content) > 100 else loot_content
    
    return loot_data 