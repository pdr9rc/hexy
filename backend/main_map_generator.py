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

from backend.database_manager import database_manager
from backend.terrain_system import TerrainSystem
from backend.translation_system import translation_system
from backend.mork_borg_lore_database import MorkBorgLoreDatabase

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
        self.content_tables = database_manager.load_tables(self.language)
        # Fix terrain tables access for new unified structure
        terrain_tables_raw = self.content_tables.get('terrain_tables', {})
        self.terrain_tables = {}
        
        # Extract language-specific terrain data
        for terrain_type, terrain_data in terrain_tables_raw.items():
            if isinstance(terrain_data, dict) and self.language in terrain_data:
                self.terrain_tables[terrain_type] = terrain_data[self.language]
        
        self.core_tables = self.content_tables.get('core_tables', {})
        
        # Map configuration
        self.map_width, self.map_height = self.config.get('map_dimensions', (30, 60))
        self.start_x, self.start_y = self.config.get('map_start', (1, 1))
        self.output_dir = self.config.get('output_directory', 'dying_lands_output')
        
        # Generation rules
        self.generation_rules = self.config.get('generation_rules', {
            'settlement_chance': 0.15,  # Reduced to make room for more dungeons/beasts
            'dungeon_chance': 0.45,     # Increased from 0.30 - more dungeons!
            'beast_chance': 0.50,       # Increased from 0.35 - more beasts!
            'npc_chance': 0.40,         # Reduced to make room for more dungeons/beasts
            'loot_chance': 0.60,        # Increased from 0.50 - more loot!
            'scroll_chance': 0.35       # Increased from 0.30
        })
        
        # Output formats
        self.output_formats = self.config.get('output_formats', ['markdown', 'ascii'])
        
        # Custom content tables
        self.custom_tables = {}
        
        # Initialize terrain system with correct map size
        global terrain_system
        from backend.terrain_system import TerrainSystem
        terrain_system = TerrainSystem(
            map_width=self.map_width,
            map_height=self.map_height,
            image_path="data/mork_borg_official_map.jpg",
            mapping_mode="letterbox",
            debug=False
        )
    
    def _load_config(self, config: Dict) -> Dict:
        """Load and validate configuration."""
        default_config = {
            'language': 'en',
            'map_dimensions': (30, 60),
            'map_start': (1, 1),
            'output_directory': 'dying_lands_output',
            'generation_rules': {
                'settlement_chance': 0.15,  # Reduced to make room for more dungeons/beasts
                'dungeon_chance': 0.45,     # Increased from 0.30 - more dungeons!
                'beast_chance': 0.50,       # Increased from 0.35 - more beasts!
                'npc_chance': 0.40,         # Reduced to make room for more dungeons/beasts
                'loot_chance': 0.60,        # Increased from 0.50 - more loot!
                'scroll_chance': 0.35       # Increased from 0.30
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
            'loot': hardcoded_data.get('loot', None),
            'scroll': hardcoded_data.get('scroll', None),
            'is_special_location': True,
            'name': name,
            'denizen_type': location_type,
            'motivation': hardcoded_data.get('motivation', 'Unknown'),
            'feature': hardcoded_data.get('feature', 'Unknown'),
            'demeanor': hardcoded_data.get('demeanor', 'Unknown'),
            'hex_art': hardcoded_data.get('hex_art', None),
            'hex_code': hex_code,
            'is_lore_location': True,
            'is_major_city': location_type == 'major_city',
            'is_minor_city': location_type == 'minor_city',
            'is_special_location': location_type in ['special_location', 'ancient_ruins', 'forgotten_temple'],
            'is_wilderness': location_type == 'wilderness',
            'is_dungeon': location_type == 'dungeon',
            'is_npc': location_type == 'npc',
            'is_beast': location_type == 'beast',
            'is_settlement': location_type == 'settlement',
            'is_terrain': location_type == 'terrain',
            'is_sea_encounter': location_type == 'sea',
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
        # Special handling for sea terrain
        if terrain == 'sea':
            hex_data = self._generate_sea_content(hex_code, terrain)
            if hex_code == "1606":
                print(f"DEBUG 1606: terrain={hex_data.get('terrain')}, content_type={hex_data.get('content_type')}")
            return hex_data
        # Get terrain-specific tables
        terrain_data = self.terrain_tables.get(terrain, {})
        encounters = terrain_data.get('encounters', [])
        denizen_types = terrain_data.get('denizen_types', [])
        features = terrain_data.get('features', [])
        # Generate base content
        notable_feature = self._generate_notable_feature(terrain, features)
        atmosphere = self._generate_atmosphere()
        # Determine content type based on generation rules
        weights = [
            ('settlement', self.generation_rules['settlement_chance']),
            ('dungeon', self.generation_rules['dungeon_chance']),
            ('beast', self.generation_rules['beast_chance']),
            ('npc', self.generation_rules['npc_chance']),
        ]
        total = sum(w for _, w in weights)
        roll = random.uniform(0, total)
        upto = 0
        for kind, weight in weights:
            if upto + weight >= roll:
                if kind == 'settlement':
                    hex_data = self._generate_settlement_content(hex_code, terrain)
                elif kind == 'dungeon':
                    hex_data = self._generate_dungeon_content(hex_code, terrain)
                elif kind == 'beast':
                    hex_data = self._generate_beast_content(hex_code, terrain)
                elif kind == 'npc':
                    hex_data = self._generate_npc_content(hex_code, terrain, denizen_types)
                if hex_code == "1606":
                    print(f"DEBUG 1606: terrain={hex_data.get('terrain')}, content_type={hex_data.get('content_type')}")
                return hex_data
            upto += weight
        # fallback (shouldn't happen)
        hex_data = self._generate_npc_content(hex_code, terrain, denizen_types)
        if hex_code == "1606":
            print(f"DEBUG 1606: terrain={hex_data.get('terrain')}, content_type={hex_data.get('content_type')}")
        return hex_data

    def _generate_sea_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate sea encounter content with Tephrotic nightmares and oceanic horrors."""
        # Sea encounter types
        sea_encounters = [
            "Tephrotic Nightmare",
            "Sea Horror",
            "Oceanic Terror", 
            "Abyssal Entity",
            "Drowned Horror",
            "Sea Wraith",
            "Oceanic Nightmare",
            "Abyssal Nightmare"
        ]
        # Tephrotic nightmare descriptions
        tephrotic_descriptions = [
            "A writhing mass of tentacles and eyes that defies mortal comprehension",
            "A being of pure nightmare that swims through the depths of the dying world",
            "An entity that exists between dreams and reality, haunting the ocean's edge",
            "A horror from beyond the stars that has made the sea its domain",
            "A creature of pure malevolence that feeds on the fear of those who gaze upon it",
            "An ancient terror that has slumbered beneath the waves for eons"
        ]
        # Sea atmosphere descriptions
        sea_atmospheres = [
            "The air is thick with the stench of decay and salt",
            "A cold wind carries whispers of ancient horrors",
            "The water seems to pulse with an unnatural rhythm",
            "Shadows dance beneath the surface, hinting at things best left unseen",
            "The sea itself seems to breathe with malevolent intent",
            "An oppressive silence broken only by distant, unearthly sounds"
        ]
        # Notable sea features
        sea_features = [
            "Waters that whisper of forgotten terrors",
            "A place where reality and nightmare blur",
            "Ancient ruins visible beneath the waves",
            "A spot where the sea seems to bleed darkness",
            "Waters that reflect impossible geometries",
            "A location where time itself seems to flow differently"
        ]
        # Generate encounter
        encounter_type = random.choice(sea_encounters)
        description = random.choice(tephrotic_descriptions)
        atmosphere = random.choice(sea_atmospheres)
        feature = random.choice(sea_features)
        # Generate loot (sea encounters might have sunken treasure)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.8 else None
        # Build the encounter description
        encounter_desc = f"**{encounter_type}**\n\n"
        encounter_desc += f"{description}.\n\n"
        encounter_desc += f"**Origin:** This entity emerged from the depths when the world began to die. "
        encounter_desc += f"It is said to be one of the Tephrotic nightmares that plague the dying lands.\n\n"
        encounter_desc += f"**Behavior:** The creature {random.choice(['stalks', 'hunts', 'haunts', 'terrorizes'])} "
        encounter_desc += f"this area of the sea, {random.choice(['seeking prey', 'spreading corruption', 'gathering power', 'performing ancient rituals'])}.\n\n"
        encounter_desc += f"**Threat Level:** Catastrophic - this entity represents an existential threat to all who encounter it.\n\n"
        encounter_desc += f"**Territory:** This section of the sea has been claimed by the nightmare, "
        encounter_desc += f"its influence corrupting the very waters themselves."
        # Add loot if present
        if loot:
            encounter_desc += f"\n\n**Sunken Treasure:** {loot['description']} (lost to the depths)"
        return {
            'hex_code': hex_code,
            'terrain': terrain,  # always use the passed terrain
            'encounter': f"≈ **{encounter_type} Encounter**",
            'denizen': encounter_desc,
            'notable_feature': feature,
            'atmosphere': atmosphere,
            'threat_level': "Catastrophic - this entity represents an existential threat to all who encounter it.",
            'territory': f"This section of the sea has been claimed by the nightmare, its influence corrupting the very waters themselves.",
            'loot': loot,
            'is_sea_encounter': True,
            'encounter_type': encounter_type,
            'content_type': 'sea_encounter'
        }
    
    def _generate_settlement_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate settlement-specific content with Mörk Borg tavern details."""
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
        
        # Generate Mörk Borg tavern details
        tavern_details = self._generate_tavern_details()
        weather = self._generate_weather()
        city_event = self._generate_city_event()
        
        # Generate settlement art
        settlement_art = self._generate_settlement_art(name, terrain)
        
        # Generate loot (settlements might have valuable items)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.5 else None
        
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
            'name': name,
            'settlement_type': population,
            'loot': loot,
            'tavern_details': tavern_details,
            'weather': weather,
            'city_event': city_event,
            'is_settlement': True
        }
    
    def _generate_dungeon_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate dungeon/ruins content with Mörk Borg trap details."""
        # Get dungeon tables
        dungeon_types = database_manager.get_table('dungeon', 'dungeon_types', self.language)
        dungeon_features = database_manager.get_table('dungeon', 'dungeon_features', self.language)
        dungeon_dangers = database_manager.get_table('dungeon', 'dungeon_dangers', self.language)
        dungeon_treasures = database_manager.get_table('dungeon', 'dungeon_treasures', self.language)
        dungeon_atmospheres = database_manager.get_table('dungeon', 'dungeon_atmospheres', self.language)
        
        # Generate dungeon elements
        dungeon_type = random.choice(dungeon_types) if dungeon_types else "Ancient ruins"
        feature = random.choice(dungeon_features) if dungeon_features else "filled with mystery"
        danger = random.choice(dungeon_dangers) if dungeon_dangers else "Unknown dangers"
        treasure = random.choice(dungeon_treasures) if dungeon_treasures else "Hidden treasures"
        atmosphere = random.choice(dungeon_atmospheres) if dungeon_atmospheres else "Oppressive silence"
        
        # Generate Mörk Borg trap (30% chance)
        trap_section = None
        if random.random() <= 0.3:
            trap_section = self._generate_trap()
        
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
            'terrain': terrain,
            'encounter': f"▲ **{dungeon_type}**",
            'denizen': description,
            'notable_feature': f"Ancient {dungeon_type.lower()}",
            'atmosphere': atmosphere,
            'loot': loot,
            'scroll': scroll,
            'dungeon_type': dungeon_type,
            'danger': danger,
            'treasure': treasure,
            'trap_section': trap_section,
            'is_dungeon': True
        }
    
    def _generate_beast_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate beast encounter content."""
        # Get bestiary tables
        beast_types = database_manager.get_table('bestiary', 'beast_types', self.language)
        beast_features = database_manager.get_table('bestiary', 'beast_features', self.language)
        beast_behaviors = database_manager.get_table('bestiary', 'beast_behaviors', self.language)
        
        # Generate beast elements
        beast_type = random.choice(beast_types) if beast_types else "Wild beast"
        feature = random.choice(beast_features) if beast_features else "unnatural appearance"
        behavior = random.choice(beast_behaviors) if beast_behaviors else "hunts in the area"
        
        # Generate loot (beasts might have treasure from their victims)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.7 else None
        
        # Build description
        description = f"A {beast_type} with {feature} that {behavior}.\n\n"
        description += f"**Territory:** This creature has claimed this area of {terrain} as its hunting ground.\n"
        description += f"**Threat Level:** High - approach with extreme caution.\n"
        
        # Add loot if present
        if loot:
            description += f"\n**Treasure Found:** {loot['description']} (remains of previous victims)\n"
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"※ **{beast_type.title()} Encounter**",
            'denizen': description,
            'notable_feature': f"Beast territory",
            'atmosphere': "Tense and dangerous",
            'beast_type': beast_type,
            'beast_feature': feature,
            'beast_behavior': behavior,
            'threat_level': "High - approach with extreme caution.",
            'territory': f"This creature has claimed this area of {terrain} as its hunting ground.",
            'loot': loot,
            'is_beast': True
        }
    
    def _generate_npc_content(self, hex_code: str, terrain: str, denizen_types: List[str]) -> Dict[str, Any]:
        """Generate NPC/denizen content using Mörk Borg tables."""
        # Get Mörk Borg NPC tables
        npc_names = database_manager.get_table('npc_names', 'first_names', self.language)
        npc_surnames = database_manager.get_table('npc_names', 'second_names', self.language)
        npc_traits = database_manager.get_table('npc_traits', 'traits', self.language)
        npc_trades = database_manager.get_table('npc_trades', 'trades', self.language)
        npc_concerns = database_manager.get_table('npc_concerns', 'concerns', self.language)
        npc_wants = database_manager.get_table('npc_wants', 'wants', self.language)
        npc_apocalypse = database_manager.get_table('npc_apocalypse', 'apocalypse_attitudes', self.language)
        npc_secrets = database_manager.get_table('npc_secrets', 'secrets', self.language)
        
        # Generate Mörk Borg name
        name_prefixes = None
        name_suffixes = None
        
        if npc_names and npc_surnames:
            first_name = random.choice(npc_names)
            second_name = random.choice(npc_surnames)
            name = f"{first_name} {second_name}"
        else:
            # Fallback to old system
            name_prefixes = database_manager.get_table('names', 'denizen_names_prefix', self.language)
            name_suffixes = database_manager.get_table('names', 'denizen_names_suffix', self.language)
            if name_prefixes and name_suffixes:
                prefix = random.choice(name_prefixes)
                suffix = random.choice(name_suffixes)
                name = f"{prefix} {suffix}"
            else:
                name = f"Unknown Denizen of {hex_code}"
        
        # Generate Mörk Borg elements
        trait = random.choice(npc_traits) if npc_traits else "Mysterious"
        trade = random.choice(npc_trades) if npc_trades else f"{terrain.title()} dweller"
        concern = random.choice(npc_concerns) if npc_concerns else "seeks something unknown"
        want = random.choice(npc_wants) if npc_wants else "knowledge"
        apocalypse_attitude = random.choice(npc_apocalypse) if npc_apocalypse else "We're doomed!"
        secret = random.choice(npc_secrets) if npc_secrets else "Just a regular person"
        
        # Fallback to old system if Mörk Borg tables not available
        if not npc_trades:
            if denizen_types:
                trade = random.choice(denizen_types)
        else:
            trade = f"{terrain.title()} dweller"
        
        if not npc_concerns:
            motivations = database_manager.get_table('denizen', 'denizen_motivations', self.language)
            concern = random.choice(motivations) if motivations else "seeks something unknown"
            
        if not npc_traits:
            features = database_manager.get_table('denizen', 'denizen_features', self.language)
            trait = random.choice(features) if features else "Has an unsettling presence"
            
        if not npc_wants:
            demeanors = database_manager.get_table('denizen', 'denizen_demeanors', self.language)
            want = random.choice(demeanors) if demeanors else "Cryptic"
        
        # Generate loot (NPCs might carry valuable items)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.6 else None
        
        # Build description with Mörk Borg format
        description = f"**{name}** - {trade}\n\n"
        description += f"**Trait:** {trait}\n"
        description += f"**Concern:** {concern}\n"
        description += f"**Want:** {want}\n"
        description += f"**Apocalypse Attitude:** {apocalypse_attitude}\n"
        description += f"**Secret:** {secret}\n"
        description += f"**Location:** Wandering the {terrain}\n"
        
        # Add loot if present
        if loot:
            description += f"\n**Carries:** {loot['description']}\n"
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"☉ **{name} - {trade}**",
            'denizen': description,
            'notable_feature': f"NPC territory",
            'atmosphere': "Mysterious and unpredictable",
            'name': name,
            'denizen_type': trade,
            'trait': trait,
            'concern': concern,
            'want': want,
            'apocalypse_attitude': apocalypse_attitude,
            'secret': secret,
            'loot': loot,
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
    
    def _generate_tavern_details(self) -> Dict[str, Any]:
        """Generate Mörk Borg tavern details."""
        # Get tavern tables
        select_menu = database_manager.get_table('tavern_menu', 'select_menu', self.language) or []
        budget_menu = database_manager.get_table('tavern_menu', 'budget_menu', self.language) or []
        innkeeper_quirks = database_manager.get_table('tavern_innkeeper', 'innkeeper_quirks', self.language) or []
        patron_traits = database_manager.get_table('tavern_patrons', 'patron_traits', self.language) or []
        
        # Generate tavern elements
        select_dish = random.choice(select_menu) if select_menu else {"name": "Mysterious stew", "price": 4, "currency": "silver"}
        budget_dish = random.choice(budget_menu) if budget_menu else {"name": "Watery soup", "price": 2, "currency": "silver"}
        innkeeper_quirk = random.choice(innkeeper_quirks) if innkeeper_quirks else "Seems nervous about something"
        patron_trait = random.choice(patron_traits) if patron_traits else "Mysterious"
        
        return {
            'select_dish': select_dish,
            'budget_dish': budget_dish,
            'innkeeper_quirk': innkeeper_quirk,
            'patron_trait': patron_trait
        }
    
    def _generate_weather(self) -> str:
        """Generate Mörk Borg weather conditions."""
        weather_conditions = database_manager.get_table('weather', 'weather_conditions', self.language) or []
        return random.choice(weather_conditions) if weather_conditions else "Lifeless grey"
    
    def _generate_city_event(self) -> str:
        """Generate Mörk Borg city events."""
        city_events = database_manager.get_table('city_events', 'city_events', self.language) or []
        return random.choice(city_events) if city_events else "Something mysterious happens in the streets"
    
    def _generate_trap(self) -> Dict[str, Any]:
        """Generate a trap from Mörk Borg tables."""
        trap_triggers = database_manager.get_table('traps_triggers', 'trap_triggers', self.language)
        trap_effects = database_manager.get_table('traps_effects', 'trap_effects', self.language)
        trap_builders = database_manager.get_table('traps_builders', 'trap_builders', self.language)
        
        trigger = random.choice(trap_triggers) if trap_triggers else "A hidden mechanism"
        effect_data = random.choice(trap_effects) if trap_effects else {"description": "Unknown effect", "effect": "Unknown damage"}
        builder = random.choice(trap_builders) if trap_builders else "Unknown builder"
        
        return {
            'description': trigger,
            'effect': effect_data.get('effect', 'Unknown damage'),
            'builder': builder
        }
    
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
        """Generate treasure/loot using Mörk Borg tables."""
        # Try Mörk Borg items and trinkets first
        trinkets = database_manager.get_table('items_trinkets', 'trinkets', self.language)
        items_prices = database_manager.get_table('items_prices', 'items', self.language)
        weapons_prices = database_manager.get_table('weapons_prices', 'weapons', self.language)
        
        # 50% chance for trinket, 30% chance for regular item, 20% chance for weapon
        loot_roll = random.randint(1, 100)
        
        if loot_roll <= 50 and trinkets:
            # Mörk Borg trinket
            loot_item = random.choice(trinkets)
            loot_type = "trinket"
            effect = "Mysterious properties"
        elif loot_roll <= 80 and items_prices:
            # Mörk Borg item
            item_data = random.choice(items_prices)
            loot_item = item_data.get('name', 'Unknown item')
            loot_type = "item"
            effect = item_data.get('notes', 'Mysterious properties')
        elif weapons_prices:
            # Mörk Borg weapon
            weapon_data = random.choice(weapons_prices)
            loot_item = f"{weapon_data.get('name', 'Unknown weapon')} ({weapon_data.get('damage', 'd4')})"
            loot_type = "weapon"
            effect = f"Damage: {weapon_data.get('damage', 'd4')}"
        else:
                # Fallback to old system
            if loot_roll <= 30:  # 30% weapons
                loot_item = random.choice(database_manager.get_table('enhanced_loot', 'weapon_loot', self.language) or ["Rusty sword"])
                loot_type = 'weapon'
            elif loot_roll <= 50:  # 20% armor
                loot_item = random.choice(database_manager.get_table('enhanced_loot', 'armor_loot', self.language) or ["Leather armor"])
                loot_type = 'armor'
            elif loot_roll <= 80:  # 30% valuable items
                loot_item = random.choice(database_manager.get_table('enhanced_loot', 'valuable_loot', self.language) or ["Silver coins"])
                loot_type = 'valuable'
            else:  # 20% utility items
                loot_item = random.choice(database_manager.get_table('enhanced_loot', 'utility_loot', self.language) or ["Rope"])
                loot_type = 'utility'
                effect = "Mysterious properties"
        
        return {
            'type': loot_type,
            'item': loot_item,
            'description': loot_item,
            'full_description': f"**{loot_item}**\n\n**Magical Effect:** {effect}"
        }
    
    def _generate_scroll(self) -> Optional[Dict[str, Any]]:
        """Generate ancient scroll/knowledge."""
        # Get scroll tables
        scroll_types = database_manager.get_table('scroll', 'scroll_types', self.language) or ["Ancient parchment"]
        scroll_content = database_manager.get_table('scroll', 'scroll_content', self.language) or ["forbidden knowledge"]
        scroll_effects = database_manager.get_table('scroll', 'scroll_effects', self.language) or ["causes nightmares when read"]
        
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
    
    def _get_translated_terrain_name(self, terrain: str) -> str:
        """Get terrain name in the current language."""
        terrain_names = {
            'en': {
                'mountain': 'Mountain',
                'forest': 'Forest', 
                'coast': 'Coast',
                'plains': 'Plains',
                'swamp': 'Swamp',
                'desert': 'Desert',
                'sea': 'Sea',
                'unknown': 'Unknown'
            },
            'pt': {
                'mountain': 'Montanha',
                'forest': 'Floresta',
                'coast': 'Costa', 
                'plains': 'Planícies',
                'swamp': 'Pântano',
                'desert': 'Deserto',
                'sea': 'Mar',
                'unknown': 'Desconhecido'
            }
        }
        
        return terrain_names.get(self.language, terrain_names['en']).get(terrain, terrain.title())

    def _generate_markdown_content(self, hex_data: Dict[str, Any]) -> str:
        """Generate markdown content for the hex."""
        lines = []
        
        # Title
        lines.append(f"# Hex {hex_data['hex_code']}")
        lines.append("")
        
        # Terrain - use translated name
        terrain_name = self._get_translated_terrain_name(hex_data['terrain'])
        lines.append(f"**Terrain:** {terrain_name}")
        lines.append("")
        
        # Encounter
        lines.append("## Encounter")
        encounter = hex_data['encounter']['raw'] if isinstance(hex_data.get('encounter'), dict) and 'raw' in hex_data['encounter'] else hex_data.get('encounter', '')
        lines.append(encounter)
        lines.append("")
        # Denizen
        lines.append("## Denizen")
        if isinstance(hex_data.get('denizen'), dict):
            lines.append(hex_data['denizen'].get('raw', ''))
            # Print subfields
            for k, v in hex_data['denizen'].get('fields', {}).items():
                if isinstance(v, list):
                    for item in v:
                        lines.append(f"**{k.replace('_', ' ').title()}:** {item}")
                else:
                    lines.append(f"**{k.replace('_', ' ').title()}:** {v}")
            # Print ASCII art
            for art in hex_data['denizen'].get('ascii_art', []):
                lines.append(art)
        else:
            lines.append(hex_data.get('denizen', ''))
        lines.append("")
        # Notable Feature
        lines.append("## Notable Feature")
        if isinstance(hex_data.get('notable_feature'), dict):
            lines.append(hex_data['notable_feature'].get('raw', ''))
            for k, v in hex_data['notable_feature'].get('fields', {}).items():
                if isinstance(v, list):
                    for item in v:
                        lines.append(f"**{k.replace('_', ' ').title()}:** {item}")
                else:
                    lines.append(f"**{k.replace('_', ' ').title()}:** {v}")
            for art in hex_data['notable_feature'].get('ascii_art', []):
                lines.append(art)
        else:
            lines.append(hex_data.get('notable_feature', ''))
        lines.append("")
        # Atmosphere
        lines.append("## Atmosphere")
        if isinstance(hex_data.get('atmosphere'), dict):
            lines.append(hex_data['atmosphere'].get('raw', ''))
            for k, v in hex_data['atmosphere'].get('fields', {}).items():
                if isinstance(v, list):
                    for item in v:
                        lines.append(f"**{k.replace('_', ' ').title()}:** {item}")
                else:
                    lines.append(f"**{k.replace('_', ' ').title()}:** {v}")
            for art in hex_data['atmosphere'].get('ascii_art', []):
                lines.append(art)
        else:
            lines.append(hex_data.get('atmosphere', ''))
        lines.append("")
        # Loot
        if hex_data.get('loot'):
            lines.append("## Loot Found")
            loot = hex_data['loot']
            if isinstance(loot, list):
                for item in loot:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"**{k.replace('_', ' ').title()}:** {v}")
                    else:
                        lines.append(str(item))
            elif isinstance(loot, dict):
                for k, v in loot.items():
                    lines.append(f"**{k.replace('_', ' ').title()}:** {v}")
            else:
                lines.append(str(loot))
            lines.append("")
        # Scroll/Ancient Knowledge
        if hex_data.get('scroll'):
            lines.append("## Ancient Knowledge")
            scroll = hex_data['scroll']
            if isinstance(scroll, dict):
                for k, v in scroll.items():
                    lines.append(f"**{k.replace('_', ' ').title()}:** {v}")
            else:
                lines.append(str(scroll))
            lines.append("")
        
        # Settlement-specific content
        if hex_data.get('is_settlement'):
            lines.append("**Local Tavern:** " + hex_data.get('local_tavern', 'Unknown'))
            lines.append("")
            lines.append("**Local Power:** " + hex_data.get('local_power', 'Unknown'))
            lines.append("")
            
            # Mörk Borg settlement details
            if hex_data.get('weather'):
                lines.append("**Weather:** " + hex_data.get('weather'))
                lines.append("")
            
            if hex_data.get('city_event'):
                lines.append("**City Event:** " + hex_data.get('city_event'))
                lines.append("")
            
            # Tavern details
            tavern_details = hex_data.get('tavern_details', {})
            if tavern_details:
                lines.append("## Tavern Details")
                if tavern_details.get('select_dish'):
                    lines.append(f"**Select Menu:** {tavern_details['select_dish']}")
                if tavern_details.get('budget_dish'):
                    lines.append(f"**Budget Menu:** {tavern_details['budget_dish']}")
                if tavern_details.get('innkeeper_quirk'):
                    lines.append(f"**Innkeeper:** {tavern_details['innkeeper_quirk']}")
                if tavern_details.get('patron_trait'):
                    lines.append(f"**Notable Patron:** {tavern_details['patron_trait']}")
                lines.append("")
            
            lines.append("## Settlement Layout")
            lines.append(hex_data.get('settlement_art', ''))
            lines.append("")
            
            if hex_data.get('loot'):
                lines.append("## Loot Found")
                lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
                lines.append("")
        
        # Dungeon-specific content
        if hex_data.get('is_dungeon'):
            lines.append("## Dungeon Details")
            lines.append(f"**Type:** {hex_data.get('dungeon_type', 'Unknown')}")
            lines.append(f"**Danger:** {hex_data.get('danger', 'Unknown')}")
            lines.append(f"**Treasure:** {hex_data.get('treasure', 'Unknown')}")
            lines.append("")
            
            # Mörk Borg trap details
            if hex_data.get('trap_section'):
                lines.append("## Trap")
                trap = hex_data['trap_section']
                if trap.get('description'):
                    lines.append(f"**Description:** {trap['description']}")
                if trap.get('effect'):
                    lines.append(f"**Effect:** {trap['effect']}")
                if trap.get('builder'):
                    lines.append(f"**Builder:** {trap['builder']}")
            lines.append("")
            
            if hex_data.get('loot'):
                lines.append("## Loot Found")
                lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
                lines.append("")
            
            if hex_data.get('scroll'):
                lines.append("## Ancient Knowledge")
                lines.append(hex_data['scroll'].get('full_description', hex_data['scroll'].get('description', 'Unknown knowledge')))
                lines.append("")
        
        # Beast-specific content
        if hex_data.get('is_beast'):
            lines.append("## Beast Details")
            lines.append(f"**Type:** {hex_data.get('beast_type', 'Unknown')}")
            lines.append(f"**Feature:** {hex_data.get('beast_feature', 'Unknown')}")
            lines.append(f"**Behavior:** {hex_data.get('beast_behavior', 'Unknown')}")
            lines.append("")
            
            # Add threat level and territory as separate sections
            if hex_data.get('threat_level'):
                lines.append("## Threat Level")
                lines.append(hex_data['threat_level'])
                lines.append("")
            
            if hex_data.get('territory'):
                lines.append("## Territory")
                lines.append(hex_data['territory'])
                lines.append("")
            
            if hex_data.get('loot'):
                lines.append("## Loot Found")
                lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
                lines.append("")
        
        # Sea-specific content
        if hex_data.get('is_sea_encounter'):
            lines.append("## Sea Encounter Details")
            lines.append(f"**Type:** {hex_data.get('encounter_type', 'Unknown')}")
            lines.append("")
            
            # Add threat level and territory as separate sections
            if hex_data.get('threat_level'):
                lines.append("## Threat Level")
                lines.append(hex_data['threat_level'])
                lines.append("")
            
            if hex_data.get('territory'):
                lines.append("## Territory")
                lines.append(hex_data['territory'])
                lines.append("")
            
            if hex_data.get('loot'):
                lines.append("## Loot Found")
                lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
                lines.append("")
        
        # NPC-specific content
        if hex_data.get('is_npc'):
            lines.append("## NPC Details")
            lines.append(f"**Name:** {hex_data.get('name', 'Unknown')}")
            lines.append(f"**Type:** {hex_data.get('denizen_type', 'Unknown')}")
            
            # Mörk Borg NPC details
            if hex_data.get('trait'):
                lines.append(f"**Trait:** {hex_data.get('trait')}")
            if hex_data.get('concern'):
                lines.append(f"**Concern:** {hex_data.get('concern')}")
            if hex_data.get('want'):
                lines.append(f"**Want:** {hex_data.get('want')}")
            if hex_data.get('apocalypse_attitude'):
                lines.append(f"**Apocalypse Attitude:** {hex_data.get('apocalypse_attitude')}")
            if hex_data.get('secret'):
                lines.append(f"**Secret:** {hex_data.get('secret')}")
            
            # Fallback to old fields if new ones not available
            if not hex_data.get('trait') and hex_data.get('motivation'):
                lines.append(f"**Motivation:** {hex_data.get('motivation')}")
            if not hex_data.get('concern') and hex_data.get('feature'):
                lines.append(f"**Feature:** {hex_data.get('feature')}")
            if not hex_data.get('want') and hex_data.get('demeanor'):
                lines.append(f"**Demeanor:** {hex_data.get('demeanor')}")
            
            lines.append("")
            
            if hex_data.get('loot'):
                lines.append("## Loot Found")
                lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
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
            self.content_tables = database_manager.load_tables(self.language)
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