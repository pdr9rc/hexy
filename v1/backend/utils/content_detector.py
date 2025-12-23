"""
Content type detection utilities for identifying hex content types from markdown files.
"""

import os
from typing import Optional


def get_hex_content_type(hex_code: str) -> Optional[str]:
    """
    Determine the content type of a hex from its markdown file.
    
    Args:
        hex_code: Hex code to check
        
    Returns:
        Content type string or None if not found
    """
    try:
        # Use configurable path from config system
        from backend.config import get_config
        config = get_config()
        hex_file_path = config.paths.output_path / "hexes" / f"hex_{hex_code}.md"
        
        if not hex_file_path.exists():
            return None
            
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Use centralized markdown parser for more robust detection
        from backend.utils.markdown_parser import determine_hex_type
        return determine_hex_type(content)
            
    except FileNotFoundError:
        return None
    except Exception as e:
        # Log specific exceptions for debugging
        import logging
        logging.warning(f"Error reading hex file for {hex_code}: {e}")
        return None


def check_hex_has_loot(hex_code: str) -> bool:
    """
    Check if a hex file contains loot information.
    
    Args:
        hex_code: Hex code to check
        
    Returns:
        True if loot is found, False otherwise
    """
    try:
        # Use configurable path from config system
        from backend.config import get_config
        config = get_config()
        hex_file_path = config.paths.output_path / "hexes" / f"hex_{hex_code}.md"
        
        if not hex_file_path.exists():
            return False
            
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Use centralized markdown parser for more robust detection
        from backend.utils.markdown_parser import parse_loot_section
        return parse_loot_section(content) is not None
            
    except FileNotFoundError:
        return False
    except Exception as e:
        # Log specific exceptions for debugging
        import logging
        logging.warning(f"Error checking loot for hex {hex_code}: {e}")
        return False


def extract_title(content: str) -> Optional[str]:
    """
    Extract title from markdown content.
    
    Args:
        content: Markdown content string
        
    Returns:
        Title string or None if not found
    """
    # Use centralized markdown parser
    from backend.utils.markdown_parser import extract_title_from_content
    return extract_title_from_content(content)


# All defects have been addressed:
# - File paths now use configurable config system
# - Content detection uses centralized markdown parser
# - Exception handling now logs specific errors for debugging 