#!/usr/bin/env python3
"""
Main Map Generator for The Dying Lands
Single entry point for all map generation functionality.
Consolidates MapGenerator and HexGenerator into one unified system.
"""

import os
import random
import shutil
from typing import Dict, List, Tuple, Optional, Any
from content_tables import get_all_tables, get_table
from terrain_system import terrain_system
from translation_system import translation_system
from mork_borg_lore_database import MorkBorgLoreDatabase

class MainMapGenerator:
    """Unified map generator - single entry point for all map generation."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the main map generator with optional configuration."""
        # Load configuration
        self.config = self._load_config(config or {})
        
        # Initialize core systems
        self.language = self.config.get('language', 'en')
        self.translation_system = translation_system
        self.translation_system.set_language(self.language)
        self.lore_db = MorkBorgLoreDatabase()
        
        # Load content tables
        self.content_tables = get_all_tables(self.language)
        self.terrain_tables = self.content_tables.get('terrain_tables', {})
        self.core_tables = self.content_tables.get('core_tables', {})
        
        # Map configuration
        self.map_width, self.map_height = self.config.get('map_dimensions', terrain_system.get_map_dimensions())
        self.start_x, self.start_y = self.config.get('map_start', (1, 1))
        self.output_dir = self.config.get('output_directory', 'dying_lands_output')
        
        # Generation rules
        self.generation_rules = self.config.get('generation_rules', {
            'settlement_chance': 0.15,
            'dungeon_chance': 0.20,
            'beast_chance': 0.20,
            'npc_chance': 0.45,
            'loot_chance': 0.30,
            'scroll_chance': 0.20
        })
        
        # Output formats
        self.output_formats = self.config.get('output_formats', ['markdown', 'ascii'])
        
        # Custom content tables
        self.custom_tables = {}
    
    def _load_config(self, config: Dict) -> Dict:
        """Load and validate configuration."""
        default_config = {
            'language': 'en',
            'map_dimensions': (30, 25),
            'map_start': (1, 1),
            'output_directory': 'dying_lands_output',
            'generation_rules': {
                'settlement_chance': 0.15,
                'dungeon_chance': 0.20,
                'beast_chance': 0.20,
                'npc_chance': 0.45,
                'loot_chance': 0.30,
                'scroll_chance': 0.20
            },
            'output_formats': ['markdown', 'ascii'],
            'skip_existing': True,
            'create_summary': True,
            'create_ascii_map': True
        }
        
        if config:
            default_config.update(config)
        
        return default_config
    
    # ===== MAIN GENERATION METHODS =====
    
    def generate_full_map(self, options: Optional[Dict] = None) -> Dict:
        """Generate content for the entire map."""
        print(f"🗺️ {self.translation_system.t('generating_full_map')}...")
        print(f"📍 {self.translation_system.t('map_size')}: {self.map_width}x{self.map_height} hexes")
        print(f"🎯 {self.translation_system.t('language')}: {self.language}")
        
        # Apply options
        if options:
            skip_existing = options.get('skip_existing', self.config.get('skip_existing', True))
        else:
            skip_existing = self.config.get('skip_existing', True)
        
        self._create_output_dirs()
        
        all_hex_data = []
        generated_count = 0
        skipped_count = 0
        
        # Generate content for each hex
        for x in range(self.start_x, self.start_x + self.map_width):
            for y in range(self.start_y, self.start_y + self.map_height):
                hex_code = f"{x:02d}{y:02d}"
                hex_file = f"{self.output_dir}/hexes/hex_{hex_code}.md"
                
                # Skip if file exists and skip_existing is True
                if skip_existing and os.path.exists(hex_file):
                    print(f"⏭️  {self.translation_system.t('skipping_existing')} {hex_code}")
                    skipped_count += 1
                    continue
                
                print(f"🎲 {self.translation_system.t('generating_hex')} {hex_code}...")
                
                # Generate hex content
                hex_data = self.generate_hex_content(hex_code)
                all_hex_data.append(hex_data)
                
                # Write hex file
                self._write_hex_file(hex_data)
                generated_count += 1
        
        # Create additional outputs
        if self.config.get('create_summary', True):
            self._write_summary_file(all_hex_data)
        
        if self.config.get('create_ascii_map', True):
            self._create_ascii_map(all_hex_data)
        
        print(f"\n✅ {self.translation_system.t('generation_complete')}!")
        print(f"📊 Generated: {generated_count} hexes")
        print(f"⏭️  Skipped: {skipped_count} hexes")
        print(f"📁 Files in '{self.output_dir}/' directory")
        
        return {
            'success': True,
            'generated_count': generated_count,
            'skipped_count': skipped_count,
            'total_hexes': len(all_hex_data),
            'hex_data': all_hex_data
        }
    
    def generate_single_hex(self, hex_code: str) -> Dict:
        """Generate content for a single hex."""
        print(f"🎲 {self.translation_system.t('generating_hex')} {hex_code}...")
        
        # Validate hex code format
        if not self._is_valid_hex_code(hex_code):
            raise ValueError(f"Invalid hex code format: {hex_code}. Expected XXYY format (e.g., 0101)")
        
        # Generate hex content
        hex_data = self.generate_hex_content(hex_code)
        
        # Write hex file
        self._write_hex_file(hex_data)
        
        print(f"✅ Generated hex {hex_code}")
        return hex_data
    
    def generate_hex_content(self, hex_code: str, terrain: Optional[str] = None) -> Dict[str, Any]:
        """Generate complete content for a hex."""
        # Determine terrain if not provided
        if terrain is None:
            terrain = terrain_system.get_terrain_for_hex(hex_code, self.lore_db)
        
        # Check for hardcoded lore locations first
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('locked', False):
            return self._generate_lore_hex_content(hex_code, hardcoded)
        
        # Generate terrain-aware content
        return self._generate_terrain_hex_content(hex_code, terrain)
    
    def reset_continent(self) -> Dict:
        """Reset the entire continent and regenerate all content."""
        print(f"🔄 Resetting continent...")
        
        # Clear terrain cache
        terrain_system.clear_cache()
        
        # Remove existing output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        
        # Generate fresh content
        result = self.generate_full_map({'skip_existing': False})
        
        return {
            'success': True,
            'message': f"Continent reset complete. Generated {result['generated_count']} hexes.",
            'generated_count': result['generated_count']
        }
    
    def customize_generation(self, custom_tables: Dict):
        """Add or update custom content tables."""
        self.custom_tables.update(custom_tables)
        print(f"✅ Custom tables updated: {list(custom_tables.keys())}")
    
    # ===== CONTENT GENERATION METHODS =====
    
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
        
        return hex_data
    
    def _generate_terrain_hex_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate terrain-aware content for a hex."""
        # Get terrain-specific tables
        terrain_data = self.terrain_tables.get(terrain, {})
        encounters = terrain_data.get('encounters', [])
        denizen_types = terrain_data.get('denizen_types', [])
        features = terrain_data.get('features', [])
        
        # Generate base content
        notable_feature = self._generate_notable_feature(terrain, features)
        atmosphere = self._generate_atmosphere()
        
        # Determine content type based on generation rules
        content_roll = random.random()
        
        if content_roll <= self.generation_rules['settlement_chance']:
            return self._generate_settlement_content(hex_code, terrain)
        elif content_roll <= self.generation_rules['settlement_chance'] + self.generation_rules['dungeon_chance']:
            return self._generate_dungeon_content(hex_code, terrain)
        elif content_roll <= self.generation_rules['settlement_chance'] + self.generation_rules['dungeon_chance'] + self.generation_rules['beast_chance']:
            return self._generate_beast_content(hex_code, terrain)
        else:
            return self._generate_npc_content(hex_code, terrain, denizen_types)
    
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
            'terrain': terrain,
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
        
        # Generate loot and scroll
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] else None
        scroll = self._generate_scroll() if random.random() <= self.generation_rules['scroll_chance'] else None
        
        # Build description
        description = f"{dungeon_type.capitalize()}, {feature}.\n\n"
        description += f"**Danger:** {danger}\n"
        description += f"**Atmosphere:** {atmosphere}\n\n"
        
        # Add loot and scroll if present
        if loot:
            description += f"**Treasure Found:** {loot['description']}\n"
        if scroll:
            description += f"**Ancient Knowledge:** {scroll['description']}\n"
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
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
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
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
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"☉ **Wandering {denizen_type}**",
            'denizen': description,
            'notable_feature': f"NPC territory",
            'atmosphere': "Mysterious and unpredictable",
            'is_npc': True
        }
    
    # ===== UTILITY METHODS =====
    
    def _generate_notable_feature(self, terrain: str, features: List[str]) -> str:
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
    
    def _get_settlement_names(self, terrain: str) -> List[str]:
        """Get settlement names based on terrain."""
        base_names = ["Shadow", "Grave", "Mournful", "Bloody", "Omen", "Beggar", "Boar", "Verhu", "Trollblood", "Resurrection", "Witch", "Weeping", "Arkh"]
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
        taverns = ["The Rusty Blade", "The Crow's Nest", "The Moldy Barrel", "The Rotting Corpse", "The Doomed Traveler", "The Blighted Inn", "The Ash and Bone", "The Thorn and Rust"]
        return random.choice(taverns)
    
    def _generate_local_power(self) -> str:
        """Generate a local power description."""
        powers = ["Corrupt mayor", "Mysterious hermit", "Witch coven", "Bandit chief", "Religious fanatic", "Undead noble", "Cult leader", "Mad prophet"]
        return random.choice(powers)
    
    def _generate_settlement_art(self, name: str, terrain: str) -> str:
        """Generate ASCII art for the settlement."""
        layout = f"""
```
T=Tavern  H=House  S=Shrine  G=Gate  W=Well

{name.upper()}
{'=' * len(name)}

   H H H
  H T S H
   H G H
    W
```"""
        return layout
    
    def _generate_loot(self) -> Optional[Dict[str, Any]]:
        """Generate treasure/loot."""
        # Roll for loot type
        loot_roll = random.randint(1, 100)
        
        if loot_roll <= 30:  # 30% weapons
            loot_item = random.choice(get_table('enhanced_loot', 'weapon_loot', self.language) or ["Rusty sword"])
            loot_type = 'weapon'
        elif loot_roll <= 50:  # 20% armor
            loot_item = random.choice(get_table('enhanced_loot', 'armor_loot', self.language) or ["Leather armor"])
            loot_type = 'armor'
        elif loot_roll <= 80:  # 30% valuable items
            loot_item = random.choice(get_table('enhanced_loot', 'valuable_loot', self.language) or ["Silver coins"])
            loot_type = 'valuable'
        else:  # 20% utility items
            loot_item = random.choice(get_table('enhanced_loot', 'utility_loot', self.language) or ["Rope"])
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
        # Get scroll tables
        scroll_types = get_table('scroll', 'scroll_types', self.language) or ["Ancient parchment"]
        scroll_content = get_table('scroll', 'scroll_content', self.language) or ["forbidden knowledge"]
        scroll_effects = get_table('scroll', 'scroll_effects', self.language) or ["causes nightmares when read"]
        
        # Generate scroll elements
        scroll_type = random.choice(scroll_types)
        content = random.choice(scroll_content)
        effect = random.choice(scroll_effects)
        
        description = f"**{scroll_type}** containing {content} that {effect}."
        
        return {
            'type': scroll_type,
            'content': content,
            'effect': effect,
            'description': description
        }
    
    # ===== FILE I/O METHODS =====
    
    def _write_hex_file(self, hex_data: Dict[str, Any]):
        """Write hex content to a markdown file."""
        if 'markdown' not in self.output_formats:
            return
        
        hex_code = hex_data['hex_code']
        filename = f"{self.output_dir}/hexes/hex_{hex_code}.md"
        
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
    
    def _write_summary_file(self, all_hex_data: List[Dict[str, Any]]):
        """Write a summary file of all generated hexes."""
        filename = f"{self.output_dir}/hex_summary.md"
        
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
    
    def _create_ascii_map(self, hex_data_list: List[Dict]):
        """Create a simple ASCII map overview."""
        if 'ascii' not in self.output_formats:
            return
        
        print(f"🗺️ Creating ASCII map...")
        
        # Create terrain-based ASCII map
        terrain_map = terrain_system.create_terrain_overview_map()
        
        # Add content indicators
        content_map = {}
        for hex_data in hex_data_list:
            hex_code = hex_data['hex_code']
            if hex_data.get('is_settlement'):
                content_map[hex_code] = '⌂'
            elif hex_data.get('lore_location'):
                content_map[hex_code] = '◆'
            else:
                content_map[hex_code] = terrain_system.get_terrain_symbol(hex_data['terrain'])
        
        # Write ASCII map file
        self._write_ascii_map_file(content_map, terrain_map)
    
    def _write_ascii_map_file(self, content_map: Dict[str, str], terrain_map: Dict[str, str]):
        """Write ASCII map to file."""
        filename = f"{self.output_dir}/ascii_map.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("THE DYING LANDS - ASCII MAP\n")
            f.write("=" * 40 + "\n\n")
            
            # Write column headers
            f.write("   ")
            for x in range(1, self.map_width + 1):
                f.write(f"{x:2d} ")
            f.write("\n")
            
            # Write map rows
            for y in range(1, self.map_height + 1):
                f.write(f"{y:2d} ")
                for x in range(1, self.map_width + 1):
                    hex_code = f"{x:02d}{y:02d}"
                    symbol = content_map.get(hex_code, '?')
                    f.write(f" {symbol} ")
                f.write("\n")
            
            f.write("\nLEGEND:\n")
            f.write("◆ = Major Cities\n")
            f.write("⌂ = Settlements\n")
            f.write("^ = Mountains\n")
            f.write("♠ = Forest\n")
            f.write("~ = Coast\n")
            f.write(". = Plains\n")
            f.write("# = Swamp\n")
            f.write("? = Unknown\n")
    
    def _create_output_dirs(self):
        """Create necessary output directories."""
        dirs = [
            self.output_dir,
            f"{self.output_dir}/hexes",
            f"{self.output_dir}/npcs"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _is_valid_hex_code(self, hex_code: str) -> bool:
        """Validate hex code format."""
        if not hex_code.isdigit() or len(hex_code) != 4:
            return False
        
        x, y = int(hex_code[:2]), int(hex_code[2:])
        return 1 <= x <= self.map_width and 1 <= y <= self.map_height
    
    # ===== INFORMATION METHODS =====
    
    def get_terrain_overview(self) -> Dict:
        """Get terrain analysis overview."""
        terrain_map = terrain_system.create_terrain_overview_map()
        distribution = terrain_system.get_terrain_distribution()
        
        return {
            'success': True,
            'terrain_map': terrain_map,
            'dimensions': [self.map_width, self.map_height],
            'distribution': distribution
        }
    
    def get_lore_overview(self) -> Dict:
        """Get lore overview."""
        return {
            'success': True,
            'major_cities': len(self.lore_db.major_cities),
            'factions': len(self.lore_db.factions),
            'cities_data': [
                {
                    'hex_code': f"{coords[0]:02d}{coords[1]:02d}",
                    'name': data['name'],
                    'region': data['region'],
                    'population': data['population']
                }
                for data in self.lore_db.major_cities.values()
                for coords in [data['coordinates']]
            ],
            'factions_data': [
                {
                    'name': data['name'],
                    'influence': data['influence'],
                    'regions': data['regions']
                }
                for data in self.lore_db.factions.values()
            ]
        }
    
    def get_config(self) -> Dict:
        """Get current configuration."""
        return self.config.copy()
    
    def update_config(self, new_config: Dict):
        """Update configuration."""
        self.config.update(new_config)
        
        # Update language if changed
        if 'language' in new_config:
            self.language = new_config['language']
            self.translation_system.set_language(self.language)
            self.content_tables = get_all_tables(self.language)
            self.terrain_tables = self.content_tables.get('terrain_tables', {})
            self.core_tables = self.content_tables.get('core_tables', {})
        
        # Update map dimensions if changed
        if 'map_dimensions' in new_config:
            self.map_width, self.map_height = new_config['map_dimensions']
        
        # Update output directory if changed
        if 'output_directory' in new_config:
            self.output_dir = new_config['output_directory']
        
        # Update generation rules if changed
        if 'generation_rules' in new_config:
            self.generation_rules.update(new_config['generation_rules'])
        
        print(f"✅ Configuration updated")


# ===== MAIN FUNCTION =====

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate The Dying Lands map content')
    parser.add_argument('--language', '-l', default='en', choices=['en', 'pt'],
                       help='Language for content generation (default: en)')
    parser.add_argument('--hex', type=str, help='Generate single hex (XXYY format)')
    parser.add_argument('--reset', action='store_true', help='Reset continent and regenerate all')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip existing hex files (default: True)')
    parser.add_argument('--output-dir', default='dying_lands_output',
                       help='Output directory (default: dying_lands_output)')
    parser.add_argument('--config', type=str, help='Path to JSON configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {'language': args.language, 'output_directory': args.output_dir}
    
    if args.config:
        import json
        try:
            with open(args.config, 'r') as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"⚠️  Error loading config file: {e}")
    
    # Initialize main map generator
    generator = MainMapGenerator(config)
    
    try:
        if args.hex:
            # Generate single hex
            result = generator.generate_single_hex(args.hex)
            print(f"✅ Generated hex {args.hex}")
        elif args.reset:
            # Reset continent
            result = generator.reset_continent()
            print(f"✅ {result['message']}")
        else:
            # Generate full map
            result = generator.generate_full_map({'skip_existing': args.skip_existing})
            print(f"✅ Generated {result['generated_count']} hexes")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())