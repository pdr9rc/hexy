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
from database_manager import database_manager
from terrain_system import terrain_system
from translation_system import translation_system
from mork_borg_lore_database import MorkBorgLoreDatabase
from generation_engine import GenerationEngine
import json

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
        
        # Initialize enhanced generation engine with sandbox integration
        self.generation_engine = GenerationEngine()
        
        # Load content tables
        self.content_tables = database_manager.load_tables(self.language)
        self.terrain_tables = self.content_tables.get('terrain_tables', {})
        self.core_tables = self.content_tables.get('core_tables', {})
        
        # Map configuration
        self.map_width, self.map_height = self.config.get('map_dimensions', terrain_system.get_map_dimensions())
        self.start_x, self.start_y = self.config.get('map_start', (1, 1))
        self.output_dir = self.config.get('output_directory', 'dying_lands_output')
        
        # Generation rules (now using enhanced engine rules)
        self.generation_rules = self.generation_engine.default_rules
        self.generation_rules.update(self.config.get('generation_rules', {}))
        
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
        
        # After generating all hexes, write unified all_hexes.json
        all_json_path = f"{self.output_dir}/all_hexes.json"
        with open(all_json_path, 'w', encoding='utf-8') as f:
            json.dump({h['hex_code']: h for h in all_hex_data}, f, ensure_ascii=False, indent=2)
        
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
        """Generate complete content for a hex using enhanced generation engine."""
        # Determine terrain if not provided
        if terrain is None:
            terrain = terrain_system.get_terrain_for_hex(hex_code, self.lore_db)
        
        # Check for hardcoded lore locations first
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('locked', False):
            return self._generate_lore_hex_content(hex_code, hardcoded)
        
        # Use enhanced generation engine with sandbox integration
        return self._generate_enhanced_hex_content(hex_code, terrain)
    
    def _generate_enhanced_hex_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate enhanced hex content using the generation engine with sandbox integration."""
        # Determine content type using enhanced engine
        content_type = self.generation_engine.determine_content_type(hex_code, terrain, self.generation_rules)
        
        # Generate content with sandbox enhancements
        context = {
            'hex_code': hex_code,
            'terrain': terrain,
            'language': self.language,
            'rules': self.generation_rules
        }
        
        enhanced_content = self.generation_engine.generate_content(content_type, context)
        
        # Add hex metadata
        enhanced_content['hex_code'] = hex_code
        enhanced_content['terrain'] = terrain
        enhanced_content['language'] = self.language
        
        return enhanced_content
    
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
        # Special handling for sea terrain
        if terrain == 'sea':
            return self._generate_sea_content(hex_code)
        
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
                    return self._generate_settlement_content(hex_code, terrain)
                elif kind == 'dungeon':
                    return self._generate_dungeon_content(hex_code, terrain)
                elif kind == 'beast':
                    return self._generate_beast_content(hex_code, terrain)
                elif kind == 'npc':
                    return self._generate_npc_content(hex_code, terrain, denizen_types)
            upto += weight
        # fallback (shouldn't happen)
        return self._generate_npc_content(hex_code, terrain, denizen_types)

    def _generate_sea_content(self, hex_code: str) -> Dict[str, Any]:
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
            'terrain': 'sea',
            'encounter': f"≈ **{encounter_type} Encounter**",
            'denizen': encounter_desc,
            'notable_feature': feature,
            'atmosphere': atmosphere,
            'threat_level': "Catastrophic - this entity represents an existential threat to all who encounter it.",
            'territory': f"This section of the sea has been claimed by the nightmare, its influence corrupting the very waters themselves.",
            'loot': loot,
            'is_sea_encounter': True,
            'encounter_type': encounter_type
        }
    
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
            'is_settlement': True
        }
    
    def _generate_dungeon_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate dungeon/ruins content."""
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
        """Generate NPC/denizen content."""
        # Get name tables from database
        name_prefixes = database_manager.get_table('content', 'denizen_names_prefix', self.language)
        name_suffixes = database_manager.get_table('content', 'denizen_names_suffix', self.language)
        

        
        # Get denizen detail tables
        motivations = database_manager.get_table('denizen', 'denizen_motivations', self.language)
        features = database_manager.get_table('denizen', 'denizen_features', self.language)
        demeanors = database_manager.get_table('denizen', 'denizen_demeanors', self.language)
        
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
        
        # Generate loot (NPCs might carry valuable items)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.6 else None
        
        # Build description
        description = f"**{name}** - {denizen_type}\n\n"
        description += f"**Motivation:** {motivation}\n"
        description += f"**Feature:** {feature}\n"
        description += f"**Demeanor:** {demeanor}\n"
        description += f"**Location:** Wandering the {terrain}\n"
        
        # Add loot if present
        if loot:
            description += f"\n**Carries:** {loot['description']}\n"
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"☉ **Wandering {denizen_type}**",
            'denizen': description,
            'notable_feature': f"NPC territory",
            'atmosphere': "Mysterious and unpredictable",
            'name': name,
            'denizen_type': denizen_type,
            'motivation': motivation,
            'feature': feature,
            'demeanor': demeanor,
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
    
    def _enrich_with_display_names(self, hex_data: Dict[str, Any]):
        """Enrich hex_data with human-readable names/descriptions for reference fields."""
        # Example for local_faction
        lore_db = getattr(self, 'lore_db', None)
        if not lore_db:
            return
        # Handle local_faction
        local_faction_key = hex_data.get('local_faction')
        if local_faction_key and hasattr(lore_db, 'factions'):
            faction_info = lore_db.factions.get(local_faction_key)
            if faction_info:
                hex_data['local_faction_name'] = faction_info.get('name')
                hex_data['local_faction_description'] = faction_info.get('description')
        # Handle sandbox_data factions
        sandbox = hex_data.get('sandbox_data', {})
        if 'factions' in sandbox and hasattr(lore_db, 'factions'):
            for faction in sandbox['factions']:
                key = faction.get('key') or faction.get('id') or faction.get('faction_key')
                if not key and 'name' in faction:
                    # Try to reverse lookup by name
                    for k, v in lore_db.factions.items():
                        if v.get('name') == faction['name']:
                            key = k
                            break
                if key and key in lore_db.factions:
                    faction_info = lore_db.factions[key]
                    faction['name'] = faction_info.get('name', faction.get('name', key))
                    faction['description'] = faction_info.get('description', '')
        # ... add similar enrichment for other reference fields as needed ...

    def _write_hex_file(self, hex_data: Dict[str, Any]):
        self._enrich_with_display_names(hex_data)
        # Ensure loot field is always present
        if 'loot' not in hex_data:
            hex_data['loot'] = None
        hex_code = hex_data.get('hex_code')
        if not hex_code:
            return
        # Write markdown as before (if needed)
        md_path = f"{self.output_dir}/hexes/hex_{hex_code}.md"
        md_content = self._generate_markdown_content(hex_data)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        # Write JSON file
        json_path = f"{self.output_dir}/hexes/hex_{hex_code}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(hex_data, f, ensure_ascii=False, indent=2)
    
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
        """Generate markdown content for the hex with enhanced data structure."""
        lines = []
        
        # Title
        lines.append(f"# Hex {hex_data['hex_code']}")
        lines.append("")
        
        # Terrain - use translated name
        terrain_name = self._get_translated_terrain_name(hex_data['terrain'])
        lines.append(f"**Terrain:** {terrain_name}")
        lines.append("")
        
        # Enhanced encounter description
        if 'enhanced_encounter' in hex_data:
            lines.append("## Encounter")
            lines.append(hex_data['enhanced_encounter'])
            lines.append("")
        elif 'encounter' in hex_data:
            lines.append("## Encounter")
            lines.append(hex_data['encounter'])
            lines.append("")
        
        # Base content from generation engine
        if 'base_content' in hex_data:
            base_content = hex_data['base_content']
            
            # Add base content fields if they exist
            if 'denizen' in base_content:
                lines.append("## Denizen")
                lines.append(base_content['denizen'])
                lines.append("")
            
            if 'notable_feature' in base_content:
                lines.append("## Notable Feature")
                lines.append(base_content['notable_feature'])
                lines.append("")
            
            if 'atmosphere' in base_content:
                lines.append("## Atmosphere")
                lines.append(base_content['atmosphere'])
                lines.append("")
            
            # Add formatted content if available
            if 'formatted_content' in base_content:
                lines.append("## Details")
                lines.append(base_content['formatted_content'])
                lines.append("")
        
        # Fallback for old data structure
        else:
            if 'denizen' in hex_data:
                lines.append("## Denizen")
                lines.append(hex_data['denizen'])
                lines.append("")
            
            if 'notable_feature' in hex_data:
                lines.append("## Notable Feature")
                lines.append(hex_data['notable_feature'])
                lines.append("")
            
            if 'atmosphere' in hex_data:
                lines.append("## Atmosphere")
                lines.append(hex_data['atmosphere'])
                lines.append("")
        
        # Content-specific sections based on content type
        content_type = hex_data.get('content_type', 'unknown')
        
        if content_type == 'settlement':
            # Settlement-specific content from base_content
            if 'base_content' in hex_data:
                base = hex_data['base_content']
                if 'local_tavern' in base:
                    lines.append("**Local Tavern:** " + base['local_tavern'])
                    lines.append("")
                if 'local_power' in base:
                    lines.append("**Local Power:** " + base['local_power'])
                    lines.append("")
                if 'population' in base:
                    lines.append("**Population:** " + base['population'])
                    lines.append("")
        
        elif content_type == 'dungeon':
            # Dungeon-specific content from base_content
            if 'base_content' in hex_data:
                base = hex_data['base_content']
                if 'dungeon_type' in base:
                    lines.append("**Dungeon Type:** " + base['dungeon_type'])
                    lines.append("")
                if 'danger' in base:
                    lines.append("**Danger:** " + base['danger'])
                    lines.append("")
        
        elif content_type == 'beast':
            # Beast-specific content from base_content
            if 'base_content' in hex_data:
                base = hex_data['base_content']
                if 'beast_type' in base:
                    lines.append("**Beast Type:** " + base['beast_type'])
                    lines.append("")
                if 'feature' in base:
                    lines.append("**Feature:** " + base['feature'])
                    lines.append("")
                if 'behavior' in base:
                    lines.append("**Behavior:** " + base['behavior'])
                    lines.append("")
        
        elif content_type == 'npc':
            # NPC-specific content from base_content
            if 'base_content' in hex_data:
                base = hex_data['base_content']
                if 'name' in base:
                    lines.append("**Name:** " + base['name'])
                    lines.append("")
                if 'denizen_type' in base:
                    lines.append("**Type:** " + base['denizen_type'])
                    lines.append("")
                if 'motivation' in base:
                    lines.append("**Motivation:** " + base['motivation'])
                    lines.append("")
        
        # Add loot information if present
        if 'base_content' in hex_data and 'loot' in hex_data['base_content']:
            loot = hex_data['base_content']['loot']
            lines.append("## Loot Found")
            lines.append(loot.get('full_description', loot.get('description', 'Unknown treasure')))
            lines.append("")
        
        # Add scroll information if present
        if 'base_content' in hex_data and 'scroll' in hex_data['base_content']:
            scroll = hex_data['base_content']['scroll']
            lines.append("## Ancient Knowledge")
            lines.append(scroll.get('full_description', scroll.get('description', 'Unknown knowledge')))
            lines.append("")
        
        # Fallback for old data structure
        else:
            # Settlement-specific content
            if hex_data.get('is_settlement'):
                lines.append("**Local Tavern:** " + hex_data.get('local_tavern', 'Unknown'))
                lines.append("")
                lines.append("**Local Power:** " + hex_data.get('local_power', 'Unknown'))
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
                lines.append(f"**Motivation:** {hex_data.get('motivation', 'Unknown')}")
                lines.append(f"**Feature:** {hex_data.get('feature', 'Unknown')}")
                lines.append(f"**Demeanor:** {hex_data.get('demeanor', 'Unknown')}")
                lines.append("")
                
                if hex_data.get('loot'):
                    lines.append("## Loot Found")
                    lines.append(hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure')))
                    lines.append("")
        
        # Add sandbox enhancements
        if 'sandbox_data' in hex_data:
            lines.extend(self._generate_sandbox_markdown(hex_data['sandbox_data']))
        
        return '\n'.join(lines)
    
    def _generate_sandbox_markdown(self, sandbox_data: Dict[str, Any]) -> List[str]:
        """Generate markdown for sandbox enhancements."""
        lines = []
        
        # Add factions section
        if sandbox_data.get('factions'):
            lines.append("## Factions")
            for faction in sandbox_data['factions']:
                lines.append(f"**{faction['name']}** ({faction['type']})")
                lines.append(f"- Influence Level: {faction['influence_level']}")
                lines.append(f"- Goals: {', '.join(faction['goals'])}")
                lines.append(f"- Resources: Wealth {faction['resources']['wealth']}, Military {faction['resources']['military']}, Knowledge {faction['resources']['knowledge']}")
                lines.append("")
        
        # Add enhanced settlement details
        if sandbox_data.get('settlements'):
            for settlement in sandbox_data['settlements']:
                if 'government' in settlement:
                    lines.append("## Government")
                    lines.append(f"**Type:** {settlement['government']}")
                    lines.append("")
                
                if 'economy' in settlement:
                    lines.append("## Economy")
                    lines.append(f"**Primary Industry:** {settlement['economy']['primary_industry']}")
                    lines.append(f"**Trade Goods:** {', '.join(settlement['economy']['trade_goods'])}")
                    lines.append(f"**Wealth Level:** {settlement['economy']['wealth_level']}/10")
                    lines.append(f"**Trade Routes:** {settlement['economy']['trade_routes']}")
                    lines.append("")
                
                if 'defenses' in settlement:
                    lines.append("## Defenses")
                    for defense in settlement['defenses']:
                        lines.append(f"- {defense}")
                    lines.append("")
                
                if 'notable_locations' in settlement:
                    lines.append("## Notable Locations")
                    for location in settlement['notable_locations']:
                        lines.append(f"- {location}")
                    lines.append("")
                
                if 'key_npcs' in settlement:
                    lines.append("## Key NPCs")
                    for npc in settlement['key_npcs']:
                        lines.append(f"**{npc['name']}** - {npc['role']}")
                        lines.append(f"*{npc['description']}*")
                        lines.append("")
                
                if 'rumors' in settlement:
                    lines.append("## Rumors")
                    for rumor in settlement['rumors']:
                        lines.append(f"- {rumor}")
                    lines.append("")
        
        # Add castles section
        if sandbox_data.get('castles'):
            lines.append("## Castles")
            for castle in sandbox_data['castles']:
                lines.append(f"**{castle['name']}** ({castle['type']})")
                lines.append(f"- Condition: {castle['condition']}")
                lines.append(f"- Lord: {castle['lord']}")
                lines.append(f"- Defenses: {', '.join(castle['defenses'])}")
                lines.append(f"- Garrison: {castle['garrison']['total']} troops")
                lines.append(f"- Strategic Value: {castle['strategic_value']}/10")
                lines.append("")
        
        # Add conflicts section
        if sandbox_data.get('conflicts'):
            lines.append("## Conflicts")
            for conflict in sandbox_data['conflicts']:
                lines.append(f"**{conflict['type'].title()} Conflict** (Intensity: {conflict['intensity']}/5)")
                if 'factions' in conflict:
                    lines.append(f"- Factions: {', '.join(conflict['factions'])}")
                lines.append(f"- Description: {conflict['description']}")
                if 'plot_hooks' in conflict:
                    lines.append("- Plot Hooks:")
                    for hook in conflict['plot_hooks']:
                        lines.append(f"  - {hook}")
                lines.append("")
        
        # Add economic data section
        if sandbox_data.get('economic_data'):
            economy = sandbox_data['economic_data']
            lines.append("## Economic Data")
            lines.append(f"**Trade Routes:** {economy.get('trade_routes', 0)}")
            lines.append(f"**Resources:** {', '.join(economy.get('resources', []))}")
            lines.append(f"**Economic Activity:** {economy.get('economic_activity', 'Unknown')}")
            lines.append(f"**Wealth Level:** {economy.get('wealth_level', 0)}/10")
            lines.append("")
        
        return lines
    
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