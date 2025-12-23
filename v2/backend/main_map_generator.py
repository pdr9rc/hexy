#!/usr/bin/env python3
"""
Main Map Generator for The Dying Lands
Single entry point for all map generation functionality.
Consolidates MapGenerator and HexGenerator into one unified system.
"""

import os
import time
import random
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from .database_manager import database_manager
from .utils.loot_generator import LootGenerator
from .utils.settlement_generator import generate_settlement_atmosphere, generate_settlement_feature
from .utils.beast_generator import generate_beast_encounter
from .utils.tavern_generator import generate_tavern_details, generate_weather, generate_city_event
from .utils.npc_generator import generate_npc_encounter
from .utils.markdown_formatter import format_beast_details, format_sea_encounter_details, format_npc_details
from .terrain_system import TerrainSystem
from .translation_system import translation_system
from .lore_database import LoreDatabase
from .config import get_config
from .road_generator import generate_roads

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
        self.lore_db = LoreDatabase()
        
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
        app_cfg = get_config()
        hexy_output_env = os.getenv('HEXY_OUTPUT_DIR')
        default_out = hexy_output_env or str(app_cfg.paths.output_path)
        map_image_path = str(app_cfg.paths.map_image)

        # Resolve output directory: if configuration provides a value, honor
        # absolute paths; if it's a relative placeholder like 'dying_lands_output',
        # use the environment-driven default directory instead to avoid nesting.
        cfg_out = self.config.get('output_directory')
        if cfg_out is None or cfg_out == '' or cfg_out == 'dying_lands_output' or cfg_out == '.':
            self.output_dir = default_out
        else:
            self.output_dir = cfg_out if os.path.isabs(cfg_out) else os.path.join(default_out, cfg_out)
        
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
        # If image is provided, TerrainSystem will auto-calculate dimensions from image
        global terrain_system
        from .terrain_system import TerrainSystem
        terrain_system = TerrainSystem(
            map_width=self.map_width,
            map_height=self.map_height,
            image_path=map_image_path,
            mapping_mode="letterbox",
            debug=False,
            auto_size_from_image=True  # Enable dynamic grid sizing from image
        )
        # Update our dimensions to match what TerrainSystem calculated (in case image auto-sizing occurred)
        self.map_width, self.map_height = terrain_system.get_map_dimensions()
    
    def _load_config(self, config: Dict) -> Dict:
        """Load and validate configuration."""
        default_config = {
            'language': 'en',
            'map_dimensions': (30, 60),
            'map_start': (1, 1),
            # Do not force an output_directory here; let environment decide.
            # When not specified, the generator will use HEXY_OUTPUT_DIR or
            # fallback to APP_DIR/dying_lands_output.
            'output_directory': None,
            'generation_rules': {
                'settlement_chance': 0.15,  # Reduced to make room for more dungeons/beasts
                'dungeon_chance': 0.45,     # Increased from 0.30 - more dungeons!
                'beast_chance': 0.50,       # Increased from 0.35 - more beasts!
                'npc_chance': 0.40,         # Reduced to make room for more dungeons/beasts
                'loot_chance': 0.60,        # Increased from 0.50 - more loot!
                'scroll_chance': 0.35       # Increased from 0.30
            },
            'output_formats': ['markdown', 'ascii'],
            'skip_existing': False,
            'create_summary': True,
            'create_ascii_map': True,
            'generate_roads': True
        }
        
        if config:
            default_config.update(config)
        
        return default_config
    
    # ===== MAIN GENERATION METHODS =====
    
    def generate_full_map(self, options: Optional[Dict] = None) -> Dict:
        """Generate content for the entire map."""
        print(f"🗺️ {self.translation_system.t('ui.generating_full_map', fallback='Generating Full Map')}...")
        print(f"📍 {self.translation_system.t('ui.map_size', fallback='Map Size')}: {self.map_width}x{self.map_height} hexes")
        print(f"🎯 {self.translation_system.t('ui.language', fallback='Language')}: {self.language}")
        
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
                
                #print(f"🎲 {self.translation_system.t('generating_hex')} {hex_code}...")
                
                # Generate hex content
                hex_data = self.generate_hex_content(hex_code)
                all_hex_data.append(hex_data)
                
                # Write hex file
                self._write_hex_file(hex_data)
                generated_count += 1
        
        # Generate roads connecting all settlements and cities
        if self.config.get('generate_roads', True):
            print(f"🛣️  {self.translation_system.t('ui.generating_roads', fallback='Generating road network')}...")
            road_hexes = generate_roads(all_hex_data)
            
            # Mark hexes with roads
            for hex_data in all_hex_data:
                if hex_data['hex_code'] in road_hexes:
                    hex_data['has_road'] = True
            
            # Write roads to JSON file for API consumption
            import json
            roads_file = f"{self.output_dir}/roads.json"
            with open(roads_file, 'w', encoding='utf-8') as f:
                json.dump(list(road_hexes), f, indent=2)
            
            print(f"🛣️  Generated {len(road_hexes)} road hexes")
        
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
        # Determine terrain if not provided - this is the source of truth
        if terrain is None:
            terrain = terrain_system.get_terrain_for_hex(hex_code, self.lore_db)
        
        # Check for hardcoded lore locations first
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('locked', False):
            return self._generate_lore_hex_content(hex_code, hardcoded, terrain)
        
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
    
    def _generate_lore_hex_content(self, hex_code: str, hardcoded_data: Dict, terrain: str) -> Dict[str, Any]:
        """Generate content for lore-specific hexes (cities, special locations)."""
        location_type = hardcoded_data.get('type', 'special_location')
        name = hardcoded_data.get('name', f'Unknown Location {hex_code}')
        description = hardcoded_data.get('description', 'An unknown location of unclear origin.')
               # Set terrain to match TERRAIN_MAP types for special locations (Only exception)
        if location_type in ['major_city', 'minor_city']:
            terrain = 'city'
        elif location_type == 'settlement':
            terrain = 'settlement'
        features = hardcoded_data.get('notable_features') or hardcoded_data.get('features', [])
        key_npcs = hardcoded_data.get('key_npcs', [])
        atmosphere = hardcoded_data.get('atmosphere', 'Ancient and unknown')
        
        hex_data = {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"Major Location: {name}",
            'denizen': f"**{name}** - {location_type.replace('_', ' ').title()}\n\n{description}",
            'notable_feature': '\n'.join(features) if features else 'Ancient site of unclear purpose',
            'atmosphere': atmosphere,
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
            'location_type': location_type,
            'key_npcs': key_npcs,
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
        # Exclude settlements and dungeons from rivers and bridges
        weights = [
            ('settlement', self.generation_rules['settlement_chance']) if terrain not in ('river', 'bridge') else None,
            ('dungeon', self.generation_rules['dungeon_chance']) if terrain not in ('river', 'bridge') else None,
            ('beast', self.generation_rules['beast_chance']),
            ('npc', self.generation_rules['npc_chance']),
        ]
        weights = [w for w in weights if w is not None]
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
                
                return hex_data
            upto += weight
        # fallback (shouldn't happen)
        hex_data = self._generate_npc_content(hex_code, terrain, denizen_types)
        
        return hex_data

    def _generate_sea_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate sea encounter content with Tephrotic nightmares and oceanic horrors."""
        # Get sea content from database
        sea_encounters = database_manager.get_table('beasts', 'sea_encounters', self.language)
        if not sea_encounters:
            raise ValueError("No sea encounters available in database")
        
        sea_descriptions = database_manager.get_table('beasts', 'sea_descriptions', self.language)
        if not sea_descriptions:
            raise ValueError("No sea descriptions available in database")
        
        sea_atmospheres = database_manager.get_table('beasts', 'sea_atmospheres', self.language)
        if not sea_atmospheres:
            raise ValueError("No sea atmospheres available in database")
        
        sea_features = database_manager.get_table('beasts', 'sea_features', self.language)
        if not sea_features:
            raise ValueError("No sea features available in database")
        
        # Generate encounter
        encounter_type = random.choice(sea_encounters)
        description = random.choice(sea_descriptions)
        atmosphere = random.choice(sea_atmospheres)
        feature = random.choice(sea_features)
        # Generate loot (sea encounters might have sunken treasure)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.8 else None
        # Build the encounter description
        encounter_desc = f"**{encounter_type}**\n\n"
        encounter_desc += f"{description}.\n\n"
        encounter_desc += f"**{self.translation_system.t('origin')}:** This entity emerged from the depths when the world began to die. "
        encounter_desc += f"It is said to be one of the Tephrotic nightmares that plague the dying lands.\n\n"
        # Get behaviors from database
        behaviors = database_manager.get_table('beasts', 'sea_behaviors', self.language)
        if not behaviors:
            raise ValueError("No sea behaviors available in database")
        purposes = database_manager.get_table('beasts', 'sea_purposes', self.language)
        if not purposes:
            raise ValueError("No sea purposes available in database")
        
        encounter_desc += f"**{self.translation_system.t('behavior')}:** The creature {random.choice(behaviors)} "
        encounter_desc += f"this area of the sea, {random.choice(purposes)}.\n\n"
        encounter_desc += f"**Threat Level:** Catastrophic - this entity represents an existential threat to all who encounter it.\n\n"
        encounter_desc += f"**{self.translation_system.t('territory')}:** This section of the sea has been claimed by the nightmare, "
        encounter_desc += f"its influence corrupting the very waters themselves."
        # Add loot if present
        if loot:
            encounter_desc += f"\n\n**Sunken Treasure:** {loot['description']} (lost to the depths)"
        return {
            'hex_code': hex_code,
            'terrain': "sea", 
            'encounter': f"≈ **{encounter_type} Encounter**",
            'denizen': encounter_desc,
            'notable_feature': feature,
            'atmosphere': atmosphere,
            'threat_level': "Catastrophic - this entity represents an existential threat to all who encounter it.",
            'territory': f"This section of the sea has been claimed by the nightmare, its influence corrupting the very waters themselves.",
            'loot': loot,
            'is_sea_encounter': True,
            'encounter_type': encounter_type,
            'content_type': 'sea_encounter',
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
        government = random.choice(database_manager.get_table('settlements', 'settlement_governments', self.language) or ["Local council"])
        trend = random.choice(database_manager.get_table('settlements', 'settlement_trends', self.language) or ["Stable"])
        
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
            'terrain': "settlement",  # Set terrain to 'settlement' to match ASCII map symbol
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
            'government': government,
            'trend': trend,
            'faction_attitude': local_power.get('attitude') if isinstance(local_power, dict) else None,
            'faction_influence': local_power.get('influence') if isinstance(local_power, dict) else None,
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
        ruins_histories = database_manager.get_table('descriptions', 'ruins_histories', self.language)
        
        # Generate dungeon elements
        dungeon_type = random.choice(dungeon_types) if dungeon_types else "Ancient ruins"
        feature = random.choice(dungeon_features) if dungeon_features else "filled with mystery"
        danger = random.choice(dungeon_dangers) if dungeon_dangers else "Unknown dangers"
        treasure = random.choice(dungeon_treasures) if dungeon_treasures else "Hidden treasures"
        atmosphere = random.choice(dungeon_atmospheres) if dungeon_atmospheres else "Oppressive silence"
        history = random.choice(ruins_histories) if ruins_histories else None
        
        # Generate Mörk Borg trap (30% chance)
        trap_section = None
        if random.random() <= 0.3:
            trap_section = self._generate_trap()
        
        # Generate loot and scroll
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] else None
        scroll = self._generate_scroll() if random.random() <= self.generation_rules['scroll_chance'] else None
        
        # Build description
        description = f"{dungeon_type.capitalize()}, {feature}.\n\n"
        if history:
            description += f"**History:** {history}\n"
        description += f"**{self.translation_system.t('danger')}:** {danger}\n"
        description += f"**{self.translation_system.t('atmosphere')}:** {atmosphere}\n\n"
        
        # Add loot and scroll if present
        if loot:
            description += f"**Treasure Found:** {loot['description']}\n"
        if scroll:
            description += f"**Ancient Knowledge:** {scroll['description']}\n"
        
        # Generate ASCII dungeon art
        dungeon_art = self._generate_dungeon_art(dungeon_type)
        description += f"\n{dungeon_art}\n"
        
        return {
            'hex_code': hex_code,
            'terrain': "dungeon", 
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
            'history': history,
            'is_dungeon': True,
        }
    
    def _generate_beast_content(self, hex_code: str, terrain: str) -> Dict[str, Any]:
        """Generate beast encounter content."""
        # Get bestiary tables
        # Use centralized beast generator
        beast_data = generate_beast_encounter(database_manager, self.language)
        beast_type = beast_data['beast_type']
        feature = beast_data['beast_feature']
        behavior = beast_data['beast_behavior']
        
        # Generate loot (beasts might have treasure from their victims)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.7 else None
        
        # Build description
        description = f"{beast_type},{feature}, {behavior}.\n\n"
        description += f"**{self.translation_system.t('territory')}:** This creature has claimed this area of {terrain} as its hunting ground.\n"
        description += f"**{self.translation_system.t('threat_level')}:** High - approach with extreme caution.\n"
        
        # Add loot if present
        if loot:
            description += f"\n**{self.translation_system.t('treasure_found')}:** {loot['description']} (remains of previous victims)\n"
        
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
            'is_beast': True,
        }
    
    def _generate_npc_content(self, hex_code: str, terrain: str, denizen_types: List[str]) -> Dict[str, Any]:
        """Generate NPC/denizen content using centralized utility."""
        # Use centralized NPC generator
        npc_data = generate_npc_encounter(database_manager, self.language)
        name = npc_data['name']
        trait = npc_data['trait']
        trade = npc_data['trade']
        concern = npc_data['concern']
        want = npc_data['want']
        apocalypse_attitude = npc_data['apocalypse_attitude']
        secret = npc_data['secret']
        
        # Use trade as denizen type, fallback to terrain dweller
        if not trade or trade == "wanderer":
            trade = f"{terrain.title()} dweller"
        
        # Generate loot (NPCs might carry valuable items)
        loot = self._generate_loot() if random.random() <= self.generation_rules['loot_chance'] * 0.6 else None
        
        # Build description with Mörk Borg format using translated labels
        description = f"**{name}** - {trade}\n\n"
        description += f"**{self.translation_system.t('npc_trait')}:** {trait}\n"
        description += f"**{self.translation_system.t('npc_concern')}:** {concern}\n"
        description += f"**{self.translation_system.t('npc_want')}:** {want}\n"
        description += f"**{self.translation_system.t('npc_apocalypse_attitude')}:** {apocalypse_attitude}\n"
        description += f"**{self.translation_system.t('npc_secret')}:** {secret}\n"
        description += f"**{self.translation_system.t('npc_location')}:** Wandering the {terrain}\n"
        
        # Add loot if present
        if loot:
            description += f"\n**{self.translation_system.t('npc_carries')}:** {loot['description']}\n"
        
        return {
            'hex_code': hex_code,
            'terrain': terrain,
            'encounter': f"☉ **{name} - {trade}**",
            'denizen': description,
            'notable_feature': f"NPC territory",
            'atmosphere': "Tense and unpredictable",
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
        # Prefer settlement-specific base/suffix tables
        base_names = database_manager.get_table('settlements', 'settlement_base_names', self.language) or []
        suffixes = database_manager.get_table('settlements', 'settlement_suffixes', self.language) or []
        names: List[str] = []
        if base_names and suffixes:
            for base in base_names[:20]:
                for suffix in suffixes[:20]:
                    names.append(f"{base} {suffix}")
            if names:
                return names
        # Fallback to legacy city name parts
        city_name_1 = database_manager.get_table('names', 'city_name_1', self.language)
        city_name_2 = database_manager.get_table('names', 'city_name_2', self.language)
        if city_name_1 and city_name_2:
            for base in city_name_1[:10]:
                for suffix in city_name_2[:10]:
                    names.append(f"{base} {suffix}")
        return names or [f"Settlement"]
    
    def _generate_population(self) -> str:
        """Generate a population range."""
        populations = database_manager.get_table('settlements', 'settlement_populations', self.language) \
            or database_manager.get_table('basic', 'populations', self.language)
        if not populations:
            raise ValueError("No populations available in database")
        return random.choice(populations)
    
    def _generate_settlement_atmosphere(self, terrain: str) -> str:
        """Generate settlement atmosphere using centralized utility."""
        return generate_settlement_atmosphere(terrain, db_manager=database_manager, language=self.language)
    
    def _generate_settlement_feature(self, terrain: str) -> str:
        """Generate a notable feature for the settlement."""
        return generate_settlement_feature(terrain, db_manager=database_manager, language=self.language)
    
    def _generate_local_tavern(self) -> str:
        """Generate a local tavern description."""
        tavern_1 = database_manager.get_table('names', 'tavern_name_1', self.language)
        if not tavern_1:
            raise ValueError("No tavern name part 1 available in database")
        tavern_2 = database_manager.get_table('names', 'tavern_name_2', self.language)
        if not tavern_2:
            raise ValueError("No tavern name part 2 available in database")
        
        return f"{random.choice(tavern_1)} {random.choice(tavern_2)}"
    
    def _generate_local_power(self) -> Dict[str, Any]:
        """Generate a local power description using faction data when available."""
        factions = database_manager.get_table('factions', 'local_factions', self.language) or []
        major_factions = database_manager.get_table('factions', 'major_factions', self.language) or []
        pool = factions + major_factions
        if pool:
            entry = random.choice(pool)
            return {
                'name': entry.get('name', 'Unknown power'),
                'description': entry.get('description'),
                'leader': entry.get('leader'),
                'headquarters': entry.get('headquarters'),
                'influence': entry.get('influence'),
                'attitude': entry.get('attitude'),
                'activities': entry.get('activities', [])
            }
        # Fallback to legacy strings
        powers = database_manager.get_table('basic', 'local_powers', self.language)
        if not powers:
            raise ValueError("No local powers available in database")
        return {'name': random.choice(powers)}
    
    def _generate_tavern_details(self) -> Dict[str, Any]:
        """Generate Mörk Borg tavern details."""
        # Get tavern tables
        # Use centralized tavern generator
        return generate_tavern_details(database_manager, self.language)
    
    def _generate_weather(self) -> str:
        """Generate Mörk Borg weather conditions."""
        weather_conditions = database_manager.get_table('weather', 'weather_conditions', self.language)
        if not weather_conditions:
            raise ValueError("No weather conditions available in database")
        return random.choice(weather_conditions)
    
    def _generate_city_event(self) -> str:
        """Generate Mörk Borg city events."""
        city_events = database_manager.get_table('city_events', 'city_events', self.language)
        if not city_events:
            raise ValueError("No city events available in database")
        return random.choice(city_events)
    
    def _generate_trap(self) -> Dict[str, Any]:
        """Generate a trap from Mörk Borg tables."""
        trap_triggers = database_manager.get_table('traps_triggers', 'trap_triggers', self.language)
        trap_effects = database_manager.get_table('traps_effects', 'trap_effects', self.language)
        trap_builders = database_manager.get_table('traps_builders', 'trap_builders', self.language)
        
        if not trap_triggers:
            raise ValueError("No trap triggers available in database")
        if not trap_effects:
            raise ValueError("No trap effects available in database")
        if not trap_builders:
            raise ValueError("No trap builders available in database")
        
        trigger = random.choice(trap_triggers)
        effect_data = random.choice(trap_effects)
        builder = random.choice(trap_builders)
        
        # Handle case where effect_data is a string instead of a dictionary
        if isinstance(effect_data, dict):
            effect = effect_data.get('effect', 'Unknown damage')
        else:
            effect = effect_data
        
        return {
            'description': trigger,
            'effect': effect,
            'builder': builder
        }
    
    def _generate_settlement_art(self, name: str, terrain: str) -> str:
        """Generate ASCII art for the settlement using random layout patterns."""
        # Load settlement layouts from database
        layouts = database_manager.get_table('settlements', 'settlement_layouts', self.language)
        
        if layouts and len(layouts) > 0:
            # Pick a random layout
            layout_pattern = random.choice(layouts)
            layout_lines = layout_pattern.get('lines', [])
            layout_name = layout_pattern.get('name', name.upper())
        else:
            # Fallback to default layout if none found
            layout_lines = [
                "H H H",
                "H T S H",
                "H G H",
                "W"
            ]
            layout_name = name.upper()
        
        # Format the layout with legend
        layout_text = "\n".join(layout_lines)
        layout = f"""T=Tavern  H=House  S=Shrine  G=Gate  W=Well

{name.upper()}
{'=' * len(name)}

{layout_text}"""
        return layout
    
    def _generate_dungeon_art(self, name: str) -> str:
        """Generate ASCII art for the dungeon using random layout patterns."""
        # Load dungeon layouts from database
        layouts = database_manager.get_table('dungeon', 'dungeon_layouts', self.language)
        
        if layouts and len(layouts) > 0:
            # Pick a random layout
            layout_pattern = random.choice(layouts)
            layout_lines = layout_pattern.get('lines', [])
        else:
            # Fallback to default layout if none found
            layout_lines = [
                "      /\\  /\\",
                "     /  \\/  \\",
                "    [    ][    ]",
                "    | ?? || ?? |",
                "    [____][____]"
            ]
        
        # Format the layout
        layout_text = "\n".join(layout_lines)
        return layout_text
    
    def _generate_loot(self) -> Optional[Dict[str, Any]]:
        """Generate treasure/loot using centralized loot generator."""
        loot_generator = LootGenerator(database_manager)
        return loot_generator.generate_loot(self.language)
    
    def _generate_scroll(self) -> Optional[Dict[str, Any]]:
        """Generate ancient scroll/knowledge using centralized loot generator."""
        loot_generator = LootGenerator(database_manager)
        return loot_generator.generate_scroll(self.language)
    
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
                desc = loot.get('full_description') or loot.get('description')
                if desc:
                    lines.append(desc)
                if loot.get('treasure_type'):
                    lines.append(f"**Type:** {loot['treasure_type']}")
                if loot.get('value'):
                    lines.append(f"**Value:** {loot['value']}")
                for k, v in loot.items():
                    if k in ('full_description', 'description', 'treasure_type', 'value'):
                        continue
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
            lines.append(f"**{self.translation_system.t('local_tavern')}:** " + hex_data.get('local_tavern', 'Unknown'))
            lines.append("")
            local_power = hex_data.get('local_power')
            if isinstance(local_power, dict):
                lp_name = local_power.get('name', 'Unknown')
                lp_desc = local_power.get('description')
                lp_leader = local_power.get('leader')
                lp_hq = local_power.get('headquarters')
                lp_influence = local_power.get('influence')
                lp_attitude = local_power.get('attitude')
                lp_activities = local_power.get('activities', [])
                lines.append(f"**{self.translation_system.t('local_power')}:** {lp_name}")
                if lp_desc:
                    lines.append(lp_desc)
                if lp_leader:
                    lines.append(f"- Leader: {lp_leader}")
                if lp_hq:
                    lines.append(f"- HQ: {lp_hq}")
                if lp_influence:
                    lines.append(f"- Influence: {lp_influence}")
                if lp_attitude:
                    lines.append(f"- Attitude: {lp_attitude}")
                if lp_activities:
                    lines.append(f"- Activities: {', '.join(lp_activities)}")
                lines.append("")
            else:
                lines.append(f"**{self.translation_system.t('local_power')}:** " + str(local_power or 'Unknown'))
            lines.append("")
            
            # Mörk Borg settlement details
            if hex_data.get('weather'):
                lines.append(f"**{self.translation_system.t('weather')}:** " + hex_data.get('weather'))
                lines.append("")
            
            if hex_data.get('city_event'):
                lines.append(f"**{self.translation_system.t('city_event')}:** " + hex_data.get('city_event'))
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
                    lines.append(f"**{self.translation_system.t('innkeeper')}:** {tavern_details['innkeeper_quirk']}")
                if tavern_details.get('patron_trait'):
                    lines.append(f"**Notable Patron:** {tavern_details['patron_trait']}")
                if tavern_details.get('tavern_description'):
                    lines.append(f"**Description:** {tavern_details['tavern_description']}")
                lines.append("")
            
            lines.append(f"## {self.translation_system.t('settlement_layout')}")
            lines.append(hex_data.get('settlement_art', ''))
            lines.append("")
            if hex_data.get('government'):
                lines.append(f"**{self.translation_system.t('government') if hasattr(self.translation_system, 't') else 'Government'}:** {hex_data['government']}")
            if hex_data.get('trend'):
                lines.append(f"**{self.translation_system.t('trend') if hasattr(self.translation_system, 't') else 'Trend'}:** {hex_data['trend']}")
            lp = hex_data.get('local_power')
            if isinstance(lp, dict):
                lines.append("## Local Power")
                lines.append(f"**Name:** {lp.get('name', 'Unknown')}")
                if lp.get('description'):
                    lines.append(lp['description'])
                if lp.get('leader'):
                    lines.append(f"**Leader:** {lp['leader']}")
                if lp.get('headquarters'):
                    lines.append(f"**HQ:** {lp['headquarters']}")
                if lp.get('influence'):
                    lines.append(f"**Influence:** {lp['influence']}")
                if lp.get('attitude'):
                    lines.append(f"**Attitude:** {lp['attitude']}")
                if lp.get('activities'):
                    lines.append(f"**Activities:** {', '.join(lp['activities'])}")
            lines.append("")
            
            if hex_data.get('loot'):
                lines.append("## Loot Found")
                loot_block = hex_data['loot'].get('full_description', hex_data['loot'].get('description', 'Unknown treasure'))
                lines.append(loot_block)
                if hex_data['loot'].get('treasure_type'):
                    lines.append(f"**Type:** {hex_data['loot']['treasure_type']}")
                if hex_data['loot'].get('value'):
                    lines.append(f"**Value:** {hex_data['loot']['value']}")
                lines.append("")
        
        # Dungeon-specific content
        if hex_data.get('is_dungeon'):
            lines.append("## Dungeon Details")
            lines.append(f"**{self.translation_system.t('type')}:** {hex_data.get('dungeon_type', 'Unknown')}")
            if hex_data.get('history'):
                lines.append(f"**History:** {hex_data['history']}")
            lines.append(f"**{self.translation_system.t('danger')}:** {hex_data.get('danger', 'Unknown')}")
            lines.append(f"**{self.translation_system.t('treasure_found')}:** {hex_data.get('treasure', 'Unknown')}")
            lines.append("")
            
            # Mörk Borg trap details
            if hex_data.get('trap_section'):
                lines.append("## Trap")
                trap = hex_data['trap_section']
                if trap.get('description'):
                    lines.append(f"**{self.translation_system.t('description')}:** {trap['description']}")
                if trap.get('effect'):
                    lines.append(f"**{self.translation_system.t('effect')}:** {trap['effect']}")
                if trap.get('builder'):
                    lines.append(f"**{self.translation_system.t('builder')}:** {trap['builder']}")
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
            lines.extend(format_beast_details(hex_data, self.translation_system))
        
        # Sea-specific content
        if hex_data.get('is_sea_encounter'):
            lines.extend(format_sea_encounter_details(hex_data, self.translation_system))
        
        # NPC-specific content
        if hex_data.get('is_npc'):
            lines.extend(format_npc_details(hex_data, self.translation_system))
        
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