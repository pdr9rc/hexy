"""
Data models for The Dying Lands

This module contains the core data model classes used across the application.
Separated from hex_model.py to avoid circular imports.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class LootType(Enum):
    """Types of loot items."""
    VALUABLE = "valuable"
    ARMOR = "armor"
    WEAPON = "weapon"
    UTILITY = "utility"


@dataclass
class LootItem:
    """Represents a loot item found in a hex."""
    description: str
    full_description: str
    item: str
    type: LootType
    magical_effect: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert loot item to dictionary for API response."""
        return {
            "description": self.description,
            "full_description": self.full_description,
            "item": self.item,
            "type": self.type.value,
            "magical_effect": self.magical_effect
        }


@dataclass
class AncientKnowledge:
    """Represents ancient knowledge or scrolls found in a hex."""
    content: str
    description: str
    effect: str
    type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ancient knowledge to dictionary for API response."""
        return {
            "content": self.content,
            "description": self.description,
            "effect": self.effect,
            "type": self.type
        }
