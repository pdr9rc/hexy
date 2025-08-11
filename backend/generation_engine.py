#!/usr/bin/env python3
"""
Generation Engine for The Dying Lands
Core generation algorithms with template-based content generation and unified reset/initialization.
"""

import random
import os
import shutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from backend.database_manager import database_manager
from backend.utils.loot_generator import LootGenerator
from backend.utils.settlement_generator import generate_settlement_atmosphere, generate_settlement_feature
from backend.utils.beast_generator import generate_beast_encounter
from backend.utils.tavern_generator import generate_tavern_details, generate_weather, generate_city_event
from backend.utils.npc_generator import generate_npc_encounter
from backend.terrain_system import terrain_system
from backend.translation_system import translation_system
from backend.mork_borg_lore_database import MorkBorgLoreDatabase

class GenerationEngine:
    """Core generation algorithms and template system."""
    
    def __init__(self, database_manager_instance=None):
        """Initialize the generation engine."""
        self.db_manager = database_manager_instance or database_manager
        self.lore_db = MorkBorgLoreDatabase()
        self.translation_system = translation_system
        
        # Generation templates
        self.templates = self._initialize_templates()
        
        # Generation rules (can be overridden)
        self.default_rules = {
            'settlement_chance': 0.15,  # Reduced to make room for more dungeons/beasts
            'dungeon_chance': 0.45,     # Increased from 0.30 - more dungeons!
            'beast_chance': 0.50,       # Increased from 0.35 - more beasts!
            'npc_chance': 0.40,         # Reduced to make room for more dungeons/beasts
            'loot_chance': 0.60,        # Increased from 0.50 - more loot!
            'scroll_chance': 0.35       # Increased from 0.30
        }
        
        # Content generators registry
        self.content_generators = self._register_content_generators()
        
        # Template variables
        self.template_vars = {}
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize content generation templates."""
        return {
            'settlement': """
**{name}** - Settlement

A {population} settlement in the {terrain}.

**Local Tavern:** {local_tavern}
**Local Power:** {local_power}
**Atmosphere:** {atmosphere}
**Notable Feature:** {notable_feature}

**Weather:** {weather}
**City Event:** {city_event}

**Tavern Details:**
- Select Menu (4s): {select_dish}
- Budget Menu (2s): {budget_dish}
- Innkeeper: {innkeeper_quirk}
- Notable Patron: {patron_trait}
            """.strip(),
            
            'dungeon': """
{dungeon_type}, {feature}.

**Danger:** {danger}
**Atmosphere:** {atmosphere}
{treasure_section}
{scroll_section}
{trap_section}
            """.strip(),
            
            'beast': """
{beast_type}, {feature}, {behavior}.

**Territory:** This creature has claimed this area of {terrain} as its hunting ground.
**Threat Level:** High - approach with extreme caution.
            """.strip(),
            
            'npc': """
**{name}** - {denizen_type}

**Trait:** {trait}
**Concern:** {concern}
**Want:** {want}
**Apocalypse Attitude:** {apocalypse_attitude}
**Secret:** {secret}
**Location:** Wandering the {terrain}
            """.strip(),
            
            'lore_location': """
**{name}** - {location_type}

{description}
{notable_features}
{key_npcs}
            """.strip()
        }
    
    def _register_content_generators(self) -> Dict[str, Callable]:
        """Register content generation functions."""
        return {
            'settlement': self._generate_settlement_content,
            'dungeon': self._generate_dungeon_content,
            'beast': self._generate_beast_content,
            'npc': self._generate_npc_content,
            'lore_location': self._generate_lore_content
        }
    
    def generate_content(self, content_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using the template system."""
        if content_type not in self.content_generators:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Set template variables from context
        self.template_vars.update(context)
        
        # Generate content using the appropriate generator
        generator = self.content_generators[content_type]
        content_data = generator(context)
        
        # Apply template if available
        if content_type in self.templates:
            content_data['formatted_content'] = self._apply_template(content_type, content_data)
        
        return content_data
    
    def _apply_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Apply a template to generate formatted content."""
        template = self.templates[template_name]
        
        try:
            return template.format(**data)
        except KeyError as e:
            # Handle missing template variables gracefully
            print(f"⚠️  Missing template variable {e} for {template_name}")
            return template
    
    def determine_content_type(self, hex_code: str, terrain: str, rules: Optional[Dict[str, Any]] = None) -> str:
        """Determine what type of content to generate for a hex."""
        if rules is None:
            rules = self.default_rules
        
        # Check for hardcoded lore locations first
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('locked', False):
            return 'lore_location'
        
        # Use probability rules to determine content type
        content_roll = random.random()
        
        if content_roll <= rules['settlement_chance']:
            return 'settlement'
        elif content_roll <= rules['settlement_chance'] + rules['dungeon_chance']:
            return 'dungeon'
        elif content_roll <= rules['settlement_chance'] + rules['dungeon_chance'] + rules['beast_chance']:
            return 'beast'
        else:
            return 'npc'
    
    def _generate_settlement_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate settlement content with Mörk Borg tavern details."""
        terrain = context.get('terrain', 'unknown')
        language = context.get('language', 'en')
        
        # Generate settlement elements
        settlement_names = self._get_settlement_names(language)
        name = random.choice(settlement_names) if settlement_names else f"Settlement {context.get('hex_code', '0000')}"
        
        population = self._generate_population(language)
        local_tavern = self._generate_local_tavern(language)
        local_power = self._generate_local_power(language)
        atmosphere = self._generate_settlement_atmosphere(terrain)
        notable_feature = self._generate_settlement_feature(terrain)
        
        # Generate Mörk Borg tavern details
        tavern_details = self._generate_tavern_details(language)
        weather = self._generate_weather(language)
        city_event = self._generate_city_event(language)
        
        return {
            'name': name,
            'population': population,
            'local_tavern': local_tavern,
            'local_power': local_power,
            'atmosphere': atmosphere,
            'notable_feature': notable_feature,
            'select_dish': tavern_details['select_dish']['name'],
            'budget_dish': tavern_details['budget_dish']['name'],
            'innkeeper_quirk': tavern_details['innkeeper_quirk'],
            'patron_trait': tavern_details['patron_trait'],
            'weather': weather,
            'city_event': city_event,
            'terrain': terrain,
            'type': 'settlement',
            'encounter': f"⌂ **{name}** - A {population} settlement"
        }
    
    def _generate_dungeon_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dungeon content with Mörk Borg traps."""
        language = context.get('language', 'en')
        rules = context.get('rules', self.default_rules)
        
        # Get dungeon tables
        dungeon_types = self.db_manager.get_table('dungeon', 'dungeon_types', language)
        dungeon_features = self.db_manager.get_table('dungeon', 'dungeon_features', language)
        dungeon_dangers = self.db_manager.get_table('dungeon', 'dungeon_dangers', language)
        dungeon_atmospheres = self.db_manager.get_table('dungeon', 'dungeon_atmospheres', language)
        
        # Generate elements
        dungeon_type = random.choice(dungeon_types) if dungeon_types else "Ancient ruins"
        feature = random.choice(dungeon_features) if dungeon_features else "filled with mystery"
        danger = random.choice(dungeon_dangers) if dungeon_dangers else "Unknown dangers"
        atmosphere = random.choice(dungeon_atmospheres) if dungeon_atmospheres else "Oppressive silence"
        
        # Generate optional treasure and scroll
        treasure_section = ""
        scroll_section = ""
        trap_section = ""
        
        if random.random() <= rules.get('loot_chance', 0.3):
            loot = self._generate_loot(language)
            if loot:
                treasure_section = f"\n**Treasure Found:** {loot['description']}"
        
        if random.random() <= rules.get('scroll_chance', 0.2):
            scroll = self._generate_scroll(language)
            if scroll:
                scroll_section = f"\n**Ancient Knowledge:** {scroll['description']}"
        
        # Generate trap (30% chance)
        if random.random() <= 0.3:
            trap = self._generate_trap(language)
            if trap:
                trap_section = f"\n**Trap:** {trap['description']}\n**Effect:** {trap['effect']}\n**Builder:** {trap['builder']}"
        
        return {
            'dungeon_type': dungeon_type,
            'feature': feature,
            'danger': danger,
            'atmosphere': atmosphere,
            'treasure_section': treasure_section,
            'scroll_section': scroll_section,
            'trap_section': trap_section,
            'type': 'dungeon',
            'encounter': "▲ **Ancient Ruins**"
        }
    
    def _generate_beast_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate beast encounter content using centralized utility."""
        terrain = context.get('terrain', 'unknown')
        language = context.get('language', 'en')
        
        # Use centralized beast generator
        beast_data = generate_beast_encounter(self.db_manager, language)
        beast_type = beast_data['beast_type']
        feature = beast_data['beast_feature']
        behavior = beast_data['beast_behavior']
        
        return {
            'beast_type': beast_type,
            'feature': feature,
            'behavior': behavior,
            'terrain': terrain,
            'type': 'beast',
            'encounter': f"※ **Wild Beast Encounter**"
        }
    
    def _generate_npc_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NPC content using centralized utility."""
        terrain = context.get('terrain', 'unknown')
        language = context.get('language', 'en')
        hex_code = context.get('hex_code', '0000')
        
        # Use centralized NPC generator
        npc_data = generate_npc_encounter(self.db_manager, language)
        name = npc_data['name']
        trait = npc_data['trait']
        trade = npc_data['trade']
        concern = npc_data['concern']
        want = npc_data['want']
        apocalypse_attitude = npc_data['apocalypse_attitude']
        secret = npc_data['secret']
        
        # Get terrain-specific denizen types for fallback
        tables = self.db_manager.load_tables(language)
        core_tables = tables.get('core_tables', {})
        terrain_tables = tables.get('terrain_tables', {})
        terrain_data = terrain_tables.get(terrain, {})
        denizen_types = terrain_data.get('denizen_types', [])
        
        # Use trade as denizen type, fallback to terrain dweller
        denizen_type = trade if trade else f"{terrain.title()} dweller"
        
        return {
            'name': name,
            'denizen_type': denizen_type,
            'trait': trait,
            'concern': concern,
            'want': want,
            'apocalypse_attitude': apocalypse_attitude,
            'secret': secret,
            'terrain': terrain,
            'type': 'npc',
            'encounter': f"☉ **{name} - {denizen_type}**"
        }
    
    def _generate_lore_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lore location content."""
        hex_code = context.get('hex_code', '0000')
        hardcoded_data = self.lore_db.get_hardcoded_hex(hex_code) or {}
        
        location_type = hardcoded_data.get('type', 'special_location')
        name = hardcoded_data.get('name', f'Unknown Location {hex_code}')
        description = hardcoded_data.get('description', 'A mysterious location of unknown origin.')
        
        # Format notable features
        notable_features = ""
        features_list = hardcoded_data.get('notable_features', [])
        if features_list:
            # Use translation system if available
            try:
                from backend.translation_system import translation_system
                notable_label = translation_system.t('notable_features')
            except ImportError:
                notable_label = 'Notable Features'
            notable_features = f"\n\n**{notable_label}:**\n" + "\n".join(f"- {feature}" for feature in features_list)
        
        # Format key NPCs
        key_npcs = ""
        npcs_list = hardcoded_data.get('key_npcs', [])
        if npcs_list:
            # Use translation system if available
            try:
                from backend.translation_system import translation_system
                npcs_label = translation_system.t('key_npcs')
            except ImportError:
                npcs_label = 'Key NPCs'
            key_npcs = f"\n\n**{npcs_label}:** {', '.join(npcs_list)}"
        
        return {
            'name': name,
            'location_type': location_type.replace('_', ' ').title(),
            'description': description,
            'notable_features': notable_features,
            'key_npcs': key_npcs,
            'type': 'lore_location',
            'encounter': f"Major Location: {name}"
        }
    
    def _get_settlement_names(self, language: str) -> List[str]:
        """Generate settlement names."""
        city_name_1 = self.db_manager.get_table('names', 'city_name_1', language) or ["Shadow", "Grave", "Bloody"]
        city_name_2 = self.db_manager.get_table('names', 'city_name_2', language) or ["Hill", "Grove", "Creek"]
        
        names = []
        for base in city_name_1[:10]:  # Limit for performance
            for suffix in city_name_2[:10]:
                names.append(f"{base} {suffix}")
        
        return names
    
    def _generate_population(self, language: str) -> str:
        """Generate population range."""
        populations = self.db_manager.get_table('basic', 'populations', language) or ["20-50", "51-100", "101-500", "501-1000"]
        return random.choice(populations)
    
    def _generate_local_tavern(self, language: str) -> str:
        """Generate local tavern name."""
        tavern_1 = self.db_manager.get_table('names', 'tavern_name_1', language) or ["The Ancient", "The Bloody"]
        tavern_2 = self.db_manager.get_table('names', 'tavern_name_2', language) or ["Queen", "Donkey"]
        
        if tavern_1 and tavern_2:
            return f"{random.choice(tavern_1)} {random.choice(tavern_2)}"
        else:
            return "The Local Tavern"
    
    def _generate_local_power(self, language: str) -> str:
        """Generate local power description."""
        powers = ["Corrupt mayor", "Mysterious hermit", "Witch coven", "Bandit chief", 
                 "Religious fanatic", "Undead noble", "Cult leader", "Mad prophet"]
        return random.choice(powers)
    
    def _generate_settlement_atmosphere(self, terrain: str) -> str:
        """Generate settlement atmosphere using centralized utility."""
        return generate_settlement_atmosphere(terrain)
    
    def _generate_settlement_feature(self, terrain: str) -> str:
        """Generate notable feature for settlement."""
        features = {
            'mountain': 'Ancient stone circle',
            'forest': 'Twisted tree grove',
            'coast': 'Old lighthouse',
            'plains': 'Ancient standing stones',
            'swamp': 'Witch\'s hut on stilts',
            'desert': 'Oasis with strange water'
        }
        return features.get(terrain, 'Mysterious landmark')
    
    def _generate_loot(self, language: str) -> Optional[Dict[str, Any]]:
        """Generate treasure/loot using centralized loot generator."""
        loot_generator = LootGenerator(self.db_manager)
        return loot_generator.generate_loot(language)
    
    def _generate_scroll(self, language: str) -> Optional[Dict[str, Any]]:
        """Generate ancient scroll/knowledge using centralized loot generator."""
        loot_generator = LootGenerator(self.db_manager)
        return loot_generator.generate_scroll(language)
    
    def _generate_tavern_details(self, language: str) -> Dict[str, Any]:
        """Generate Mörk Borg tavern details using centralized utility."""
        return generate_tavern_details(self.db_manager, language)
    
    def _generate_weather(self, language: str) -> str:
        """Generate Mörk Borg weather conditions."""
        weather_conditions = self.db_manager.get_table('weather', 'weather_conditions', language) or []
        return random.choice(weather_conditions) if weather_conditions else "Lifeless grey"
    
    def _generate_city_event(self, language: str) -> str:
        """Generate Mörk Borg city events."""
        city_events = self.db_manager.get_table('city_events', 'city_events', language) or []
        return random.choice(city_events) if city_events else "Something mysterious happens in the streets"
    
    def _generate_trap(self, language: str) -> Optional[Dict[str, Any]]:
        """Generate Mörk Borg trap."""
        # Get trap tables
        trap_triggers = self.db_manager.get_table('traps_triggers', 'trap_triggers', language) or []
        trap_builders = self.db_manager.get_table('traps_builders', 'trap_builders', language) or []
        trap_effects = self.db_manager.get_table('traps_effects', 'trap_effects', language) or []
        
        if not trap_triggers or not trap_builders or not trap_effects:
            return None
        
        trigger = random.choice(trap_triggers)
        builder = random.choice(trap_builders)
        effect_data = random.choice(trap_effects)
        
        return {
            'trigger': trigger,
            'builder': builder,
            'description': effect_data.get('description', 'Unknown trap'),
            'effect': effect_data.get('effect', 'Unknown effect')
        }
    
    def apply_custom_rules(self, rules: Dict[str, Any]):
        """Apply custom generation rules."""
        self.default_rules.update(rules)
        print(f"✅ Custom rules applied: {list(rules.keys())}")
    
    def reset_all_data(self, output_directory: str = None):
        if output_directory is None:
            hexy_output_env = os.getenv('HEXY_OUTPUT_DIR')
            hexy_app_dir = os.getenv('HEXY_APP_DIR')
            if hexy_output_env:
                output_directory = hexy_output_env
            elif hexy_app_dir:
                output_directory = os.path.join(hexy_app_dir, 'dying_lands_output')
            else:
                output_directory = 'dying_lands_output'
        """Reset all generated data and clear caches."""
        print("🔄 Resetting all data...")
        
        # Clear terrain cache
        terrain_system.clear_cache()
        
        # Clear database cache
        self.db_manager.clear_cache()
        
        # Remove output directory
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
            print(f"🗑️  Removed output directory: {output_directory}")
        
        # Clear template variables
        self.template_vars.clear()
        
        print("✅ Reset complete")
    
    def initialize_database(self, force_migration: bool = False):
        """Initialize or re-initialize the database."""
        print("🔄 Initializing database...")
        
        if force_migration:
            # Migration is handled by database_manager
            print("⚠️  Migration is now handled by DatabaseManager")
            self.db_manager.initialize_database()
        
        # Validate database
        validation_report = self.db_manager.validate_schema()
        
        if validation_report['valid']:
            print("✅ Database initialization complete")
            print(f"📊 Database statistics:")
            print(f"   - Files: {validation_report['statistics']['total_files']}")
            print(f"   - Tables: {validation_report['statistics']['total_tables']}")
            print(f"   - Languages: {validation_report['statistics']['languages']}")
        else:
            print("❌ Database initialization failed!")
            for error in validation_report['errors']:
                print(f"   - {error}")
            raise RuntimeError("Database initialization failed")
    
    def add_custom_template(self, template_name: str, template_content: str):
        """Add a custom content generation template."""
        self.templates[template_name] = template_content
        print(f"✅ Custom template '{template_name}' added")
    
    def add_custom_generator(self, content_type: str, generator_func: Callable):
        """Add a custom content generator function."""
        self.content_generators[content_type] = generator_func
        print(f"✅ Custom generator '{content_type}' registered")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about the generation system."""
        tables = self.db_manager.load_tables('en')
        
        stats = {
            'total_table_categories': len(tables),
            'content_generators': list(self.content_generators.keys()),
            'templates': list(self.templates.keys()),
            'default_rules': self.default_rules,
            'database_path': self.db_manager.database_path
        }
        
        return stats


# Global generation engine instance
generation_engine = GenerationEngine()