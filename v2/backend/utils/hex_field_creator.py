"""
Hex field creation utilities for creating consistent hex objects.
"""

from typing import Dict, Any, Optional
from ..models import LootItem, LootType


def create_common_hex_fields(data: Dict[str, Any], hex_code: str, terrain) -> Dict[str, Any]:
    """
    Create common fields for hex objects.
    
    Args:
        data: Dictionary containing hex data
        hex_code: Hex code
        terrain: Terrain type
        
    Returns:
        Dictionary containing common hex fields
    """
    return {
        'hex_code': hex_code,
        'terrain': terrain,
        'encounter': data.get('encounter', 'Unknown'),
        'denizen': data.get('denizen', 'No denizen information'),
        'territory': data.get('territory', 'Unknown territory'),
        'threat_level': data.get('threat_level', 'Unknown'),
        'notable_feature': data.get('notable_feature', 'No notable features'),
        'atmosphere': data.get('atmosphere', 'Unknown atmosphere'),
        'loot': create_loot_item(data.get('loot')) if data.get('loot') else None,
    }


def create_loot_item(loot_data: Dict[str, Any]) -> Optional[LootItem]:
    """
    Create a LootItem from raw data.
    
    Args:
        loot_data: Dictionary containing loot data
        
    Returns:
        LootItem object or None if invalid
    """
    if not isinstance(loot_data, dict):
        return None
    
    # Convert string type to LootType enum
    loot_type_str = loot_data.get('type', '')
    loot_type = None
    if loot_type_str:
        try:
            loot_type = LootType(loot_type_str)
        except ValueError:
            # If the string doesn't match any enum value, default to UTILITY
            loot_type = LootType.UTILITY
    
    return LootItem(
        description=loot_data.get('description', ''),
        full_description=loot_data.get('full_description', ''),
        item=loot_data.get('item', ''),
        type=loot_type or LootType.UTILITY,
        magical_effect=loot_data.get('magical_effect', None)
    ) 