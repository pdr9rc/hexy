#!/usr/bin/env python3
"""
Base Generator for The Dying Lands
Abstract base class for all content generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from src.config import get_config
from src.utils import weighted_choice, log_operation

class BaseGenerator(ABC):
    """Abstract base class for all content generators."""
    
    def __init__(self, language: str = 'en'):
        """Initialize the base generator."""
        self.language = language
        self.config = get_config()
        self.content_tables = self._load_content_tables()
        
    def _load_content_tables(self) -> Dict[str, Any]:
        """Load content tables for the current language."""
        from database_manager import database_manager
        return database_manager.load_tables(self.language)
    
    @abstractmethod
    def generate(self, hex_code: str, terrain: str, **kwargs) -> Dict[str, Any]:
        """Generate content for a hex. Must be implemented by subclasses."""
        pass
    
    def _get_table_entry(self, category: str, table_name: str) -> str:
        """Get a random entry from a content table."""
        tables = self.content_tables.get(f"{category}_tables", {})
        table = tables.get(table_name, [])
        
        if not table:
            log_operation(f"get_table_entry_{category}_{table_name}", False, "Table not found")
            return "Unknown"
        
        if isinstance(table, list):
            return self._random_choice(table)
        elif isinstance(table, dict):
            return self._random_choice(list(table.keys()))
        else:
            return str(table)
    
    def _random_choice(self, options: List[str]) -> str:
        """Make a random choice from a list of options."""
        if not options:
            return "Unknown"
        import random
        return random.choice(options)
    
    def _weighted_table_choice(self, category: str, table_name: str) -> str:
        """Make a weighted choice from a table with weights."""
        tables = self.content_tables.get(f"{category}_tables", {})
        table = tables.get(table_name, {})
        
        if not table:
            log_operation(f"weighted_table_choice_{category}_{table_name}", False, "Table not found")
            return "Unknown"
        
        if isinstance(table, dict):
            return weighted_choice(table)
        else:
            return self._random_choice(table if isinstance(table, list) else [table])
    
    def _get_terrain_modifier(self, terrain: str) -> str:
        """Get terrain-specific modifier for content generation."""
        terrain_tables = self.content_tables.get('terrain_tables', {})
        modifiers = terrain_tables.get('terrain_modifiers', {}).get(terrain, [])
        
        if modifiers:
            return self._random_choice(modifiers)
        return ""
    
    def _generate_atmosphere(self) -> str:
        """Generate atmospheric description."""
        return self._get_table_entry('core', 'atmospheres')
    
    def _generate_notable_feature(self, terrain: str) -> str:
        """Generate notable feature for the hex."""
        features = self.content_tables.get('core_tables', {}).get('notable_features', [])
        terrain_features = self.content_tables.get('terrain_tables', {}).get('terrain_features', {}).get(terrain, [])
        
        all_features = features + terrain_features
        if all_features:
            return self._random_choice(all_features)
        return "A mysterious landmark"
    
    def _format_content(self, content_type: str, **kwargs) -> str:
        """Format content with proper markdown formatting."""
        if content_type == 'settlement':
            return self._format_settlement(**kwargs)
        elif content_type == 'dungeon':
            return self._format_dungeon(**kwargs)
        elif content_type == 'beast':
            return self._format_beast(**kwargs)
        elif content_type == 'npc':
            return self._format_npc(**kwargs)
        else:
            return self._format_wilderness(**kwargs)
    
    def _format_settlement(self, **kwargs) -> str:
        """Format settlement content."""
        name = kwargs.get('name', 'Unknown Settlement')
        description = kwargs.get('description', 'A mysterious settlement.')
        population = kwargs.get('population', 'Unknown')
        atmosphere = kwargs.get('atmosphere', 'Mysterious')
        feature = kwargs.get('feature', 'A notable landmark')
        tavern = kwargs.get('tavern', 'A local tavern')
        power = kwargs.get('power', 'A local authority')
        
        return f"""# {name}

⌂ **{name}** - Population: {population}

{description}

**Atmosphere:** {atmosphere}

**Notable Feature:** {feature}

**Local Tavern:** {tavern}

**Local Power:** {power}"""

    def _format_dungeon(self, **kwargs) -> str:
        """Format dungeon content."""
        name = kwargs.get('name', 'Unknown Dungeon')
        description = kwargs.get('description', 'A mysterious dungeon.')
        atmosphere = kwargs.get('atmosphere', 'Dark and foreboding')
        feature = kwargs.get('feature', 'Ancient architecture')
        
        return f"""# {name}

▲ **{name}**

{description}

**Atmosphere:** {atmosphere}

**Notable Feature:** {feature}"""

    def _format_beast(self, **kwargs) -> str:
        """Format beast content."""
        name = kwargs.get('name', 'Unknown Beast')
        description = kwargs.get('description', 'A mysterious creature.')
        behavior = kwargs.get('behavior', 'Aggressive')
        
        return f"""# {name}

※ **{name}**

{description}

**Behavior:** {behavior}"""

    def _format_npc(self, **kwargs) -> str:
        """Format NPC content."""
        name = kwargs.get('name', 'Unknown NPC')
        description = kwargs.get('description', 'A mysterious figure.')
        role = kwargs.get('role', 'Wanderer')
        
        return f"""# {name}

☉ **{name}**

{description}

**Role:** {role}"""

    def _format_wilderness(self, **kwargs) -> str:
        """Format wilderness content."""
        terrain = kwargs.get('terrain', 'Unknown terrain')
        atmosphere = kwargs.get('atmosphere', 'Mysterious')
        feature = kwargs.get('feature', 'A notable landmark')
        
        return f"""# {terrain.title()} Hex

**Terrain:** {terrain.title()}

**Atmosphere:** {atmosphere}

**Notable Feature:** {feature}""" 