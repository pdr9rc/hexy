#!/usr/bin/env python3
"""
Unified Hex Generator for The Dying Lands
Handles all hex content generation, including terrain-aware content and lore integration.
"""

import os
import random
import re
from typing import Dict, List, Optional, Any
from content_tables import get_all_tables, get_table
from terrain_system import terrain_system

class HexGenerator:
    """Unified hex content generator."""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.content_tables = get_all_tables(language)
        self.terrain_tables = self.content_tables.get('terrain_tables', {})
        self.core_tables = self.content_tables.get('core_tables', {})
    
    def generate_hex_content(self, hex_code: str, terrain: Optional[str] = None, lore_db=None) -> Dict[str, Any]:
        """Generate complete content for a hex."""
        # Determine terrain if not provided
        if terrain is None:
            terrain = terrain_system.get_terrain_for_hex(hex_code, lore_db)
        
        # Check for hardcoded lore locations first
        if lore_db:
            hardcoded = lore_db.get_hardcoded_hex(hex_code)
            if hardcoded and hardcoded.get('locked', False):
                return self._generate_lore_hex_content(hex_code, hardcoded)
        
        # Generate terrain-aware content
        return self._generate_terrain_hex_content(hex_code, terrain)
    
    def _generate_lore_hex_content(self, hex_code: str, hardcoded_data: Dict) -> Dict[str, Any]:
        """Generate content for lore-specific hexes (cities, special locations)."""
        location_type = hardcoded_data.get('type', 'special_location')
        name = hardcoded_data.get('name', f'Unknown Location {hex_code}')
        description = hardcoded_data.get('description', 'A mysterious location of unknown origin.')
        terrain = hardcoded_data.get('terrain', 'plains')
        
        hex_data = {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"Major Location: {name}",
            'denizen': f"**{name}** - {location_type.replace('_', ' ').title()}\n\n{description}",
            'notable_feature': '\n'.join(hardcoded_data.get('notable_features', ['Ancient and mysterious location'])),
            'atmosphere': hardcoded_data.get('atmosphere', 'Ancient and mysterious'),
            'lore_location': True,
            'location_type': location_type
        }
        
        # Add special content based on location type
        if location_type == 'major_city':
            hex_data['population'] = hardcoded_data.get('population', 'Unknown')
            hex_data['encounter'] = f"Major City: {name} (Population: {hardcoded_data.get('population', 'Unknown')})"
            
            # Add key NPCs to denizen description
            key_npcs = hardcoded_data.get('key_npcs', [])
            if key_npcs:
                hex_data['denizen'] += f"\n\n**Key NPCs:** {', '.join(key_npcs)}"
                
        elif location_type == 'special_location':
            hex_data['special_properties'] = hardcoded_data.get('special_properties', [])
        
        return hex_data
    
    def _generate_terrain_hex_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate terrain-aware content for a hex."""
        # Get terrain-specific tables
        terrain_data = self.terrain_tables.get(terrain, {})
        encounters = terrain_data.get('encounters', [])
        denizen_types = terrain_data.get('denizen_types', [])
        features = terrain_data.get('features', [])
        
        # Generate notable feature
        notable_feature = self._generate_notable_feature(hex_code, terrain, features)
        
        # Generate atmosphere
        atmosphere = self._generate_atmosphere()
        
        # Determine content type based on roll
        content_roll = random.randint(1, 100)
        
        if content_roll <= 15:  # 15% chance of settlement
            settlement_data = self._generate_settlement_content(hex_code, terrain)
            return {**settlement_data, 'terrain': terrain}
            
        elif content_roll <= 35:  # 20% chance of dungeon/ruins
            dungeon_data = self._generate_dungeon_content(hex_code, terrain)
            return {**dungeon_data, 'terrain': terrain}
            
        elif content_roll <= 55:  # 20% chance of beast encounter
            beast_data = self._generate_beast_content(hex_code, terrain)
            return {**beast_data, 'terrain': terrain}
            
        else:  # 45% chance of NPCs/denizens
            npc_data = self._generate_npc_content(hex_code, terrain, denizen_types)
            return {**npc_data, 'terrain': terrain}
    

    
    def _generate_notable_feature(self, hex_code: str, terrain: str, features: List[str]) -> str:
        """Generate a notable feature description."""
        if features:
            return random.choice(features)
        else:
            return f"Strange {terrain} feature"
    
    def _generate_atmosphere(self) -> str:
        """Generate an atmosphere description."""
        atmospheres = self.core_tables.get('atmospheres', [])
        if atmospheres:
            return random.choice(atmospheres)
        else:
            return "Oppressive silence"
    
    def _generate_settlement_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate settlement-specific content."""
        # Generate settlement name
        settlement_names = self._get_settlement_names(terrain)
        name = random.choice(settlement_names) if settlement_names else f"Settlement {hex_code}"
        
        # Generate population
        population = self._generate_population()
        
        # Generate settlement details
        atmosphere = self._generate_settlement_atmosphere(terrain)
        notable_feature = self._generate_settlement_feature(terrain)
        local_tavern = self._generate_local_tavern()
        local_power = self._generate_local_power()
        
        # Generate settlement art
        settlement_art = self._generate_settlement_art(name, terrain)
        
        return {
            'hex_code': hex_code,
            'encounter': f"⌂ **{name}** - A {population} settlement",
            'denizen': f"**{name}** - Settlement\n\nA {population} settlement in the {terrain}.",
            'notable_feature': notable_feature,
            'atmosphere': atmosphere,
            'local_tavern': local_tavern,
            'local_power': local_power,
            'settlement_art': settlement_art,
            'population': population,
            'is_settlement': True
        }
    
    def _get_settlement_names(self, terrain: str) -> List[str]:
        """Get settlement names based on terrain."""
        # This could be expanded with more terrain-specific names
        base_names = [
            "Shadow", "Grave", "Mournful", "Bloody", "Omen", "Beggar", "Boar", 
            "Verhu", "Trollblood", "Resurrection", "Witch", "Weeping", "Arkh"
        ]
        suffixes = ["Hill", "Grove", "Creek", "End", "Cove", "Alley", "Hollow", "Henge", "Lot", "Ford", "Harbour", "Lake", "Plain", "Moor", "Pass", "Horn"]
        
        names = []
        for base in base_names:
            for suffix in suffixes:
                names.append(f"{base} {suffix}")
        
        return names
    
    def _generate_population(self) -> str:
        """Generate a population range."""
        populations = ["20-50", "51-100", "101-500", "501-1000"]
        return random.choice(populations)
    
    def _generate_settlement_atmosphere(self, terrain: str) -> str:
        """Generate settlement atmosphere based on terrain."""
        atmospheres = {
            'mountain': 'Cold and windswept',
            'forest': 'Dark and mysterious',
            'coast': 'Salty and windswept',
            'plains': 'Open and exposed',
            'swamp': 'Misty and damp',
            'desert': 'Hot and dry'
        }
        return atmospheres.get(terrain, 'Strange and unsettling')
    
    def _generate_settlement_feature(self, terrain: str) -> str:
        """Generate a notable feature for the settlement."""
        features = {
            'mountain': 'Ancient stone circle',
            'forest': 'Twisted tree grove',
            'coast': 'Old lighthouse',
            'plains': 'Ancient standing stones',
            'swamp': 'Witch\'s hut on stilts',
            'desert': 'Oasis with strange water'
        }
        return features.get(terrain, 'Mysterious landmark')
    
    def _generate_local_tavern(self) -> str:
        """Generate a local tavern description."""
        taverns = [
            "The Rusty Blade", "The Crow's Nest", "The Moldy Barrel", "The Rotting Corpse",
            "The Doomed Traveler", "The Blighted Inn", "The Ash and Bone", "The Thorn and Rust"
        ]
        return random.choice(taverns)
    
    def _generate_local_power(self) -> str:
        """Generate a local power description."""
        powers = [
            "Corrupt mayor", "Mysterious hermit", "Witch coven", "Bandit chief",
            "Religious fanatic", "Undead noble", "Cult leader", "Mad prophet"
        ]
        return random.choice(powers)
    
    def _generate_settlement_art(self, name: str, terrain: str) -> str:
        """Generate ASCII art for the settlement."""
        # Simple ASCII layout
        layout = f"""
```
T=Tavern  H=House  S=Shrine  G=Gate  W=Well

{name.upper()}
{'=' * len(name)}

   H H H
  H T S H
   H G H
    W
```
"""
        return layout
    
    def _generate_dungeon_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate dungeon/ruins content."""
        # Get dungeon tables
        dungeon_types = get_table('dungeon', 'dungeon_types', self.language)
        dungeon_features = get_table('dungeon', 'dungeon_features', self.language)
        dungeon_dangers = get_table('dungeon', 'dungeon_dangers', self.language)
        dungeon_treasures = get_table('dungeon', 'dungeon_treasures', self.language)
        dungeon_atmospheres = get_table('dungeon', 'dungeon_atmospheres', self.language)
        
        # Generate dungeon elements
        dungeon_type = random.choice(dungeon_types) if dungeon_types else "Ancient ruins"
        feature = random.choice(dungeon_features) if dungeon_features else "filled with mystery"
        danger = random.choice(dungeon_dangers) if dungeon_dangers else "Unknown dangers"
        treasure = random.choice(dungeon_treasures) if dungeon_treasures else "Hidden treasures"
        atmosphere = random.choice(dungeon_atmospheres) if dungeon_atmospheres else "Oppressive silence"
        
        # Generate loot
        loot = self._generate_loot()
        
        # Generate scroll
        scroll = self._generate_scroll()
        
        # Build description
        description = f"{dungeon_type.capitalize()}, {feature}.\n\n"
        description += f"**Danger:** {danger}\n"
        description += f"**Atmosphere:** {atmosphere}\n\n"
        
        # Add loot and scroll if present
        if loot:
            description += f"**Treasure Found:** {loot['description']}\n"
        if scroll:
            description += f"**Ancient Knowledge:** {scroll['description']}\n"
        
        # ASCII ruins layout
        ruins_art = '''
      /\\  /\\  /\\
     /  \\/  \\/  \\
    [    ][    ]
    | ?? || ?? |
    [____][____]
        '''
        
        description += f"\n```{ruins_art}```\n"
        
        return {
            'hex_code': hex_code,
            'encounter': "▲ **Ancient Ruins**",
            'denizen': description,
            'notable_feature': f"Ancient {dungeon_type.lower()}",
            'atmosphere': atmosphere,
            'loot': loot,
            'scroll': scroll,
            'is_dungeon': True
        }
    
    def _generate_beast_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate beast encounter content."""
        # Get bestiary tables
        beast_types = get_table('bestiary', 'beast_types', self.language)
        beast_features = get_table('bestiary', 'beast_features', self.language)
        beast_behaviors = get_table('bestiary', 'beast_behaviors', self.language)
        
        # Generate beast elements
        beast_type = random.choice(beast_types) if beast_types else "Wild beast"
        feature = random.choice(beast_features) if beast_features else "unnatural appearance"
        behavior = random.choice(beast_behaviors) if beast_behaviors else "hunts in the area"
        
        # Build description
        description = f"A {beast_type} with {feature} that {behavior}.\n\n"
        description += f"**Territory:** This creature has claimed this area of {terrain} as its hunting ground.\n"
        description += f"**Threat Level:** High - approach with extreme caution.\n"
        
        # ASCII beast tracks
        beast_art = '''
     o   o   o   o
    / \\ / \\ / \\ / \\
        '''
        
        description += f"\n```{beast_art}```\n"
        description += f"Fresh tracks lead into the {terrain}..."
        
        return {
            'hex_code': hex_code,
            'encounter': f"※ **Wild Beast Encounter**",
            'denizen': description,
            'notable_feature': f"Beast territory",
            'atmosphere': "Tense and dangerous",
            'is_beast': True
        }
    
    def _generate_npc_content(self, hex_code: str, terrain: str, denizen_types: List[str]) -> Dict[str, Any]:
        """Generate NPC/denizen content."""
        # Get core tables
        name_prefixes = self.core_tables.get('denizen_names_prefix', [])
        name_suffixes = self.core_tables.get('denizen_names_suffix', [])
        motivations = self.core_tables.get('denizen_motivations', [])
        features = self.core_tables.get('denizen_features', [])
        demeanors = self.core_tables.get('denizen_demeanors', [])
        
        # Generate NPC elements
        if name_prefixes and name_suffixes:
            prefix = random.choice(name_prefixes)
            suffix = random.choice(name_suffixes)
            name = f"{prefix} {suffix}"
        else:
            name = f"Unknown Denizen of {hex_code}"
        
        # Generate denizen type
        if denizen_types:
            denizen_type = random.choice(denizen_types)
        else:
            denizen_type = f"{terrain.title()} dweller"
        
        # Generate additional details
        motivation = random.choice(motivations) if motivations else "seeks something unknown"
        feature = random.choice(features) if features else "Has an unsettling presence"
        demeanor = random.choice(demeanors) if demeanors else "Cryptic"
        
        # Build description
        description = f"**{name}** - {denizen_type}\n\n"
        description += f"**Motivation:** {motivation}\n"
        description += f"**Feature:** {feature}\n"
        description += f"**Demeanor:** {demeanor}\n"
        description += f"**Location:** Wandering the {terrain}\n"
        
        # ASCII figure
        figure_art = '''
        O
       /|\\
       / \\
        '''
        
        description += f"\n```{figure_art}```\n"
        
        return {
            'hex_code': hex_code,
            'encounter': f"☉ **Wandering {denizen_type}**",
            'denizen': description,
            'notable_feature': f"NPC territory",
            'atmosphere': "Mysterious and unpredictable",
            'is_npc': True
        }
    
    def _generate_loot(self) -> Optional[Dict[str, Any]]:
        """Generate treasure/loot."""
        # 30% chance of loot
        if random.random() > 0.3:
            return None
        
        # Roll for loot type
        loot_roll = random.randint(1, 100)
        
        if loot_roll <= 30:  # 30% weapons
            loot_item = random.choice(get_table('enhanced_loot', 'weapon_loot', self.language))
            loot_type = 'weapon'
        elif loot_roll <= 50:  # 20% armor
            loot_item = random.choice(get_table('enhanced_loot', 'armor_loot', self.language))
            loot_type = 'armor'
        elif loot_roll <= 80:  # 30% valuable items
            loot_item = random.choice(get_table('enhanced_loot', 'valuable_loot', self.language))
            loot_type = 'valuable'
        else:  # 20% utility items
            loot_item = random.choice(get_table('enhanced_loot', 'utility_loot', self.language))
            loot_type = 'utility'
        
        # Generate magical effect
        effects = ["Glimmers with dark energy", "Whispers ancient secrets", "Pulses with unholy power", "Radiates cold"]
        effect = random.choice(effects)
        
        return {
            'type': loot_type,
            'item': loot_item,
            'description': loot_item,
            'full_description': f"**{loot_item}**\n\n**Magical Effect:** {effect}"
        }
    
    def _generate_scroll(self) -> Optional[Dict[str, Any]]:
        """Generate ancient scroll/knowledge."""
        # 20% chance of scroll
        if random.random() > 0.2:
            return None
        
        # Get scroll tables
        scroll_types = get_table('scroll', 'scroll_types', self.language)
        scroll_content = get_table('scroll', 'scroll_content', self.language)
        scroll_effects = get_table('scroll', 'scroll_effects', self.language)
        
        # Generate scroll elements
        scroll_type = random.choice(scroll_types) if scroll_types else "Ancient parchment"
        content = random.choice(scroll_content) if scroll_content else "forbidden knowledge"
        effect = random.choice(scroll_effects) if scroll_effects else "causes nightmares when read"
        
        description = f"**{scroll_type}** containing {content} that {effect}."
        
        return {
            'type': scroll_type,
            'content': content,
            'effect': effect,
            'description': description
        }
    
    def write_hex_file(self, hex_data: Dict[str, Any]):
        """Write hex content to a markdown file."""
        hex_code = hex_data['hex_code']
        filename = f"dying_lands_output/hexes/hex_{hex_code}.md"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Generate markdown content
        content = self._generate_markdown_content(hex_data)
        
        # Write file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_markdown_content(self, hex_data: Dict[str, Any]) -> str:
        """Generate markdown content for the hex."""
        lines = []
        
        # Title
        lines.append(f"# Hex {hex_data['hex_code']}")
        lines.append("")
        
        # Terrain
        lines.append(f"**Terrain:** {hex_data['terrain'].title()}")
        lines.append("")
        
        # Encounter
        lines.append("## Encounter")
        lines.append(hex_data['encounter'])
        lines.append("")
        
        # Denizen
        lines.append("## Denizen")
        lines.append(hex_data['denizen'])
        lines.append("")
        
        # Notable Feature
        lines.append("## Notable Feature")
        lines.append(hex_data['notable_feature'])
        lines.append("")
        
        # Atmosphere
        lines.append("## Atmosphere")
        lines.append(hex_data['atmosphere'])
        lines.append("")
        
        # Settlement-specific content
        if hex_data.get('is_settlement'):
            lines.append("**Local Tavern:** " + hex_data.get('local_tavern', 'Unknown'))
            lines.append("")
            lines.append("**Local Power:** " + hex_data.get('local_power', 'Unknown'))
            lines.append("")
            lines.append("## Settlement Layout")
            lines.append(hex_data.get('settlement_art', ''))
            lines.append("")
        
        return '\n'.join(lines)
    
    def write_summary_file(self, all_hex_data: List[Dict[str, Any]]):
        """Write a summary file of all generated hexes."""
        filename = "dying_lands_output/hex_summary.md"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Generate summary content
        content = self._generate_summary_content(all_hex_data)
        
        # Write file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_summary_content(self, all_hex_data: List[Dict[str, Any]]) -> str:
        """Generate summary content."""
        lines = []
        lines.append("# The Dying Lands - Hex Summary")
        lines.append("")
        lines.append(f"Generated {len(all_hex_data)} hexes")
        lines.append("")
        
        # Group by terrain
        terrain_groups = {}
        for hex_data in all_hex_data:
            terrain = hex_data['terrain']
            if terrain not in terrain_groups:
                terrain_groups[terrain] = []
            terrain_groups[terrain].append(hex_data)
        
        # Write terrain sections
        for terrain, hexes in terrain_groups.items():
            lines.append(f"## {terrain.title()} ({len(hexes)} hexes)")
            lines.append("")
            
            for hex_data in hexes:
                lines.append(f"- **{hex_data['hex_code']}:** {hex_data['encounter']}")
            
            lines.append("")
        
        return '\n'.join(lines)

# Global hex generator instance
hex_generator = HexGenerator() 