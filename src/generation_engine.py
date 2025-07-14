#!/usr/bin/env python3
"""
Generation Engine for The Dying Lands
Core generation algorithms with template-based content generation and unified reset/initialization.
Now includes integrated sandbox generation for enhanced world building.
"""

import random
import os
import shutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import database_manager
from terrain_system import terrain_system
from translation_system import translation_system
from mork_borg_lore_database import MorkBorgLoreDatabase

class GenerationEngine:
    """Core generation algorithms and template system with integrated sandbox generation."""
    
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
            'scroll_chance': 0.35,      # Increased from 0.30
            
            # Sandbox integration rules
            'sandbox_enabled': True,
            'faction_influence': True,
            'detailed_settlements': True,
            'castle_generation': True,
            'conflict_generation': True,
            'economic_modeling': True
        }
        
        # Content generators registry
        self.content_generators = self._register_content_generators()
        
        # Template variables
        self.template_vars = {}
        
        # Initialize sandbox systems
        self._initialize_sandbox_systems()
    
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
            """.strip(),
            
            'dungeon': """
{dungeon_type}, {feature}.

**Danger:** {danger}
**Atmosphere:** {atmosphere}
{treasure_section}
{scroll_section}
            """.strip(),
            
            'beast': """
A {beast_type} with {feature} that {behavior}.

**Territory:** This creature has claimed this area of {terrain} as its hunting ground.
**Threat Level:** High - approach with extreme caution.
            """.strip(),
            
            'npc': """
**{name}** - {denizen_type}

**Motivation:** {motivation}
**Feature:** {feature}
**Demeanor:** {demeanor}
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
        """Generate content using the template system with integrated sandbox elements."""
        if content_type not in self.content_generators:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Set template variables from context
        self.template_vars.update(context)
        
        # Generate base content using the appropriate generator
        generator = self.content_generators[content_type]
        content_data = generator(context)
        
        # Apply template if available
        if content_type in self.templates:
            content_data['formatted_content'] = self._apply_template(content_type, content_data)
        
        # Enhance with sandbox elements if enabled
        if self.default_rules.get('sandbox_enabled', True):
            content_data = self._enhance_with_sandbox_elements(content_data, context)
        
        return content_data
    
    def _enhance_with_sandbox_elements(self, content_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance base content with sandbox generation elements."""
        hex_code = context.get('hex_code', '0000')
        terrain = context.get('terrain', 'unknown')
        language = context.get('language', 'en')
        
        # Initialize sandbox data
        sandbox_data = {
            'factions': [],
            'settlements': [],
            'castles': [],
            'conflicts': [],
            'economic_data': {},
            'political_situation': {}
        }
        
        # Generate faction influence
        if self.default_rules.get('faction_influence', True):
            factions = self._generate_faction_influence(hex_code, terrain)
            sandbox_data['factions'] = factions
        
        # Enhance settlements with detailed information
        if content_data.get('type') == 'settlement' and self.default_rules.get('detailed_settlements', True):
            enhanced_settlement = self._enhance_settlement(content_data, terrain, factions)
            content_data.update(enhanced_settlement)
            sandbox_data['settlements'].append(enhanced_settlement)
        
        # Generate castles for appropriate terrain
        if self.default_rules.get('castle_generation', True):
            castles = self._generate_castles_for_hex(hex_code, terrain)
            sandbox_data['castles'] = castles
        
        # Generate conflicts
        if self.default_rules.get('conflict_generation', True):
            conflicts = self._generate_conflicts_for_hex(hex_code, terrain, factions)
            sandbox_data['conflicts'] = conflicts
        
        # Generate economic data
        if self.default_rules.get('economic_modeling', True):
            economic_data = self._generate_economic_data(hex_code, terrain, content_data)
            sandbox_data['economic_data'] = economic_data
        
        # Store the original content as base_content
        base_content = content_data.copy()
        
        # Create the final enhanced content structure
        enhanced_content = {
            'hex_code': hex_code,
            'terrain': terrain,
            'language': language,
            'content_type': content_data.get('type', 'unknown'),
            'base_content': base_content,  # Original content
            'sandbox_data': sandbox_data,  # Sandbox enhancements
            'enhanced_encounter': self._create_enhanced_encounter(content_data, sandbox_data)
        }
        
        # Add all the original content fields for backwards compatibility
        enhanced_content.update(content_data)
        
        # Ensure content_type is set correctly
        if 'content_type' not in enhanced_content or enhanced_content['content_type'] is None:
            enhanced_content['content_type'] = content_data.get('type', 'unknown')
        
        return enhanced_content
    
    def _generate_faction_influence(self, hex_code: str, terrain: str) -> List[Dict[str, Any]]:
        """Generate faction influence for a hex."""
        factions = []
        
        # Determine faction presence based on terrain and location
        faction_chance = self._get_faction_chance_by_terrain(terrain)
        
        if random.random() < faction_chance:
            faction_type = self._determine_faction_type(terrain)
            faction = {
                'name': self._generate_faction_name(faction_type),
                'type': faction_type,
                'influence_level': random.randint(1, 5),
                'goals': self._generate_faction_goals(faction_type),
                'resources': self._generate_faction_resources(faction_type, terrain)
            }
            factions.append(faction)
        
        return factions
    
    def _get_faction_chance_by_terrain(self, terrain: str) -> float:
        """Get faction presence chance based on terrain."""
        terrain_faction_chances = {
            'mountain': 0.4,  # High - mining, bandits, dwarves
            'forest': 0.3,    # Medium - druids, rangers, bandits
            'plains': 0.25,   # Medium - farmers, merchants, nobles
            'coast': 0.35,    # High - pirates, merchants, fishermen
            'swamp': 0.2,     # Low - hermits, cults
            'desert': 0.15,   # Low - nomads, bandits
            'unknown': 0.1    # Very low
        }
        return terrain_faction_chances.get(terrain, 0.2)
    
    def _determine_faction_type(self, terrain: str) -> str:
        """Determine faction type based on terrain."""
        terrain_faction_types = {
            'mountain': ['mining_guild', 'mountain_clan', 'bandit_gang', 'religious_order'],
            'forest': ['druid_circle', 'ranger_company', 'forest_bandits', 'nature_cult'],
            'plains': ['noble_house', 'merchant_company', 'farmer_cooperative', 'military_order'],
            'coast': ['pirate_crew', 'merchant_guild', 'fishing_cooperative', 'naval_order'],
            'swamp': ['hermit_cult', 'witch_coven', 'outlaw_band', 'death_cult'],
            'desert': ['nomad_tribe', 'desert_bandits', 'merchant_caravan', 'religious_sect']
        }
        
        faction_types = terrain_faction_types.get(terrain, ['local_group'])
        return random.choice(faction_types)
    
    def _generate_faction_name(self, faction_type: str) -> str:
        """Generate a faction name based on type."""
        faction_name_templates = {
            'mining_guild': ['Iron Brotherhood', 'Deep Delvers', 'Stone Seekers'],
            'mountain_clan': ['Thunder Peak Clan', 'Stone Fist Clan', 'High Ridge Clan'],
            'bandit_gang': ['Shadow Wolves', 'Rough Riders', 'Night Raiders'],
            'religious_order': ['Order of the Sacred Flame', 'Brotherhood of the Void', 'Temple of the End'],
            'druid_circle': ['Circle of the Ancient Oak', 'Grove of the Sacred Spring', 'Circle of the Wild'],
            'ranger_company': ['Forest Wardens', 'Wild Hunters', 'Border Rangers'],
            'noble_house': ['House of the Setting Sun', 'Noble House of the Golden Lion', 'House of the Silver Moon'],
            'merchant_company': ['Golden Road Traders', 'Silk Road Consortium', 'Emerald Merchants'],
            'pirate_crew': ['Sea Wolves', 'Crimson Tide', 'Storm Riders'],
            'hermit_cult': ['Cult of the Lonely Path', 'Sect of the Solitary', 'Brotherhood of the Isolated']
        }
        
        names = faction_name_templates.get(faction_type, ['Local Faction'])
        return random.choice(names)
    
    def _generate_faction_goals(self, faction_type: str) -> List[str]:
        """Generate faction goals based on type."""
        goal_templates = {
            'mining_guild': ['Expand mining operations', 'Secure rare mineral deposits', 'Establish trade routes'],
            'mountain_clan': ['Defend ancestral lands', 'Expand territory', 'Maintain traditions'],
            'bandit_gang': ['Control trade routes', 'Amass wealth', 'Establish hideouts'],
            'religious_order': ['Spread faith', 'Gather followers', 'Establish temples'],
            'druid_circle': ['Protect nature', 'Maintain balance', 'Preserve ancient knowledge'],
            'ranger_company': ['Protect borders', 'Maintain order', 'Guide travelers'],
            'noble_house': ['Expand influence', 'Secure alliances', 'Maintain status'],
            'merchant_company': ['Control trade', 'Establish markets', 'Build wealth'],
            'pirate_crew': ['Control sea lanes', 'Plunder wealth', 'Establish bases'],
            'hermit_cult': ['Seek isolation', 'Gather knowledge', 'Avoid contact']
        }
        
        goals = goal_templates.get(faction_type, ['Survive', 'Expand influence'])
        return random.sample(goals, min(2, len(goals)))
    
    def _generate_faction_resources(self, faction_type: str, terrain: str) -> Dict[str, Any]:
        """Generate faction resources based on type and terrain."""
        base_resources = {
            'wealth': random.randint(1, 10),
            'influence': random.randint(1, 10),
            'military': random.randint(1, 10),
            'knowledge': random.randint(1, 10)
        }
        
        # Modify based on faction type
        if 'merchant' in faction_type:
            base_resources['wealth'] += 3
        elif 'military' in faction_type or 'bandit' in faction_type:
            base_resources['military'] += 3
        elif 'religious' in faction_type or 'druid' in faction_type:
            base_resources['knowledge'] += 3
        elif 'noble' in faction_type:
            base_resources['influence'] += 3
        
        return base_resources
    
    def _enhance_settlement(self, settlement_data: Dict[str, Any], terrain: str, factions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance settlement with detailed sandbox information."""
        enhanced = settlement_data.copy()
        
        # Add government type
        enhanced['government'] = self._generate_government_type(terrain, factions)
        
        # Add economic data
        enhanced['economy'] = self._generate_settlement_economy(terrain, factions)
        
        # Add defenses
        enhanced['defenses'] = self._generate_settlement_defenses(terrain, factions)
        
        # Add notable locations
        enhanced['notable_locations'] = self._generate_notable_locations(terrain, enhanced.get('population', 'small'))
        
        # Add key NPCs
        enhanced['key_npcs'] = self._generate_key_npcs(terrain, enhanced.get('population', 'small'))
        
        # Add rumors
        enhanced['rumors'] = self._generate_settlement_rumors(terrain, factions)
        
        return enhanced
    
    def _generate_government_type(self, terrain: str, factions: List[Dict[str, Any]]) -> str:
        """Generate government type based on terrain and factions."""
        terrain_governments = {
            'mountain': ['Clan Council', 'Mining Guild Rule', 'Religious Theocracy', 'Bandit Chief'],
            'forest': ['Druid Circle', 'Ranger Council', 'Village Elder', 'Bandit King'],
            'plains': ['Noble Rule', 'Merchant Council', 'Farmer Assembly', 'Military Governor'],
            'coast': ['Merchant Prince', 'Pirate Captain', 'Fishing Council', 'Port Authority'],
            'swamp': ['Hermit Rule', 'Cult Leader', 'Outlaw Chief', 'Witch Queen'],
            'desert': ['Nomad Chief', 'Caravan Master', 'Desert King', 'Religious Leader']
        }
        
        governments = terrain_governments.get(terrain, ['Local Council'])
        return random.choice(governments)
    
    def _generate_settlement_economy(self, terrain: str, factions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate economic data for settlement."""
        economy = {
            'primary_industry': self._get_primary_industry(terrain),
            'trade_goods': self._get_trade_goods(terrain),
            'wealth_level': random.randint(1, 10),
            'trade_routes': random.randint(0, 3)
        }
        
        # Modify based on factions
        for faction in factions:
            if 'merchant' in faction.get('type', ''):
                economy['wealth_level'] += 2
                economy['trade_routes'] += 1
            elif 'mining' in faction.get('type', ''):
                economy['primary_industry'] = 'Mining'
                economy['trade_goods'].append('Precious metals')
        
        return economy
    
    def _get_primary_industry(self, terrain: str) -> str:
        """Get primary industry based on terrain."""
        terrain_industries = {
            'mountain': 'Mining',
            'forest': 'Logging',
            'plains': 'Farming',
            'coast': 'Fishing',
            'swamp': 'Herb Gathering',
            'desert': 'Nomadic Herding'
        }
        return terrain_industries.get(terrain, 'General Trade')
    
    def _get_trade_goods(self, terrain: str) -> List[str]:
        """Get trade goods based on terrain."""
        terrain_goods = {
            'mountain': ['Iron', 'Stone', 'Precious metals', 'Crafts'],
            'forest': ['Wood', 'Furs', 'Herbs', 'Honey'],
            'plains': ['Grain', 'Livestock', 'Textiles', 'Tools'],
            'coast': ['Fish', 'Salt', 'Shells', 'Boat parts'],
            'swamp': ['Herbs', 'Poisons', 'Rare plants', 'Mystical items'],
            'desert': ['Spices', 'Textiles', 'Precious stones', 'Exotic goods']
        }
        return terrain_goods.get(terrain, ['General goods'])
    
    def _generate_settlement_defenses(self, terrain: str, factions: List[Dict[str, Any]]) -> List[str]:
        """Generate settlement defenses."""
        base_defenses = []
        
        # Terrain-based defenses
        if terrain == 'mountain':
            base_defenses.extend(['Stone walls', 'Watchtowers', 'Natural cliffs'])
        elif terrain == 'forest':
            base_defenses.extend(['Palisade', 'Hidden paths', 'Natural camouflage'])
        elif terrain == 'plains':
            base_defenses.extend(['Earthen walls', 'Moat', 'Guard towers'])
        elif terrain == 'coast':
            base_defenses.extend(['Sea walls', 'Lighthouse', 'Harbor defenses'])
        
        # Faction-based defenses
        for faction in factions:
            if 'military' in faction.get('type', ''):
                base_defenses.extend(['Barracks', 'Training grounds', 'Armory'])
            elif 'religious' in faction.get('type', ''):
                base_defenses.extend(['Temple defenses', 'Sacred barriers', 'Religious guards'])
        
        return base_defenses[:3]  # Limit to 3 defenses
    
    def _generate_notable_locations(self, terrain: str, population: str) -> List[str]:
        """Generate notable locations in settlement."""
        locations = []
        
        # Population-based locations
        if 'large' in population or 'city' in population:
            locations.extend(['Market square', 'Temple district', 'Noble quarter'])
        elif 'medium' in population or 'town' in population:
            locations.extend(['Central plaza', 'Main temple', 'Merchant street'])
        else:
            locations.extend(['Village green', 'Local shrine', 'Trading post'])
        
        # Terrain-based locations
        terrain_locations = {
            'mountain': ['Mining office', 'Stone mason workshop'],
            'forest': ['Woodcutter lodge', 'Herbalist shop'],
            'plains': ['Grain mill', 'Livestock pens'],
            'coast': ['Fishing docks', 'Shipwright workshop'],
            'swamp': ['Herb gatherer hut', 'Poisoner workshop'],
            'desert': ['Caravanserai', 'Water well']
        }
        
        locations.extend(terrain_locations.get(terrain, []))
        return locations[:4]  # Limit to 4 locations
    
    def _generate_key_npcs(self, terrain: str, population: str) -> List[Dict[str, str]]:
        """Generate key NPCs for settlement."""
        npcs = []
        
        # Always have a leader
        npcs.append({
            'name': f"Local Leader",
            'role': 'Settlement leader',
            'description': 'The person in charge of this settlement'
        })
        
        # Add terrain-specific NPCs
        terrain_npcs = {
            'mountain': ['Mining overseer', 'Stone mason', 'Guard captain'],
            'forest': ['Woodcutter chief', 'Herbalist', 'Ranger scout'],
            'plains': ['Farmer elder', 'Merchant', 'Militia captain'],
            'coast': ['Fishing captain', 'Shipwright', 'Port master'],
            'swamp': ['Herb gatherer', 'Witch', 'Outlaw leader'],
            'desert': ['Caravan master', 'Water keeper', 'Desert guide']
        }
        
        npc_roles = terrain_npcs.get(terrain, ['Local expert'])
        for role in npc_roles[:2]:  # Add up to 2 terrain-specific NPCs
            npcs.append({
                'name': f"Local {role.lower()}",
                'role': role,
                'description': f'The {role.lower()} of this settlement'
            })
        
        return npcs
    
    def _generate_settlement_rumors(self, terrain: str, factions: List[Dict[str, Any]]) -> List[str]:
        """Generate rumors for settlement."""
        rumors = []
        
        # Terrain-based rumors
        terrain_rumors = {
            'mountain': [
                'Strange sounds from the deep mines',
                'Valuable ore discovered in nearby caves',
                'Mountain spirits are restless'
            ],
            'forest': [
                'Ancient trees whisper secrets',
                'Hidden paths lead to forgotten places',
                'Forest creatures are acting strangely'
            ],
            'plains': [
                'Strange lights in the distance',
                'Travelers bring news of distant lands',
                'The harvest this year will be bountiful'
            ],
            'coast': [
                'Strange ships on the horizon',
                'Treasure washed up on the beach',
                'Sea monsters spotted offshore'
            ],
            'swamp': [
                'Mysterious lights in the mist',
                'Ancient ruins discovered in the muck',
                'The swamp is expanding'
            ],
            'desert': [
                'Oasis discovered in the deep desert',
                'Ancient city ruins found',
                'Sandstorms bring strange artifacts'
            ]
        }
        
        rumors.extend(terrain_rumors.get(terrain, ['Local gossip', 'Traveler tales']))
        
        # Faction-based rumors
        for faction in factions:
            if 'bandit' in faction.get('type', ''):
                rumors.append(f'{faction["name"]} is planning a raid')
            elif 'religious' in faction.get('type', ''):
                rumors.append(f'{faction["name"]} seeks new converts')
            elif 'merchant' in faction.get('type', ''):
                rumors.append(f'{faction["name"]} has valuable goods')
        
        return random.sample(rumors, min(3, len(rumors)))
    
    def _generate_castles_for_hex(self, hex_code: str, terrain: str) -> List[Dict[str, Any]]:
        """Generate castles for a hex."""
        castles = []
        
        # Determine castle presence based on terrain and location
        castle_chance = self._get_castle_chance_by_terrain(terrain)
        
        if random.random() < castle_chance:
            castle = {
                'name': self._generate_castle_name(terrain),
                'type': random.choice(self.castle_generator['castle_types']),
                'condition': self._generate_castle_condition(),
                'defenses': self._generate_castle_defenses(),
                'garrison': self._generate_castle_garrison(),
                'lord': self._generate_castle_lord(),
                'treasury': self._generate_castle_treasury(),
                'strategic_value': random.randint(1, 10)
            }
            castles.append(castle)
        
        return castles
    
    def _get_castle_chance_by_terrain(self, terrain: str) -> float:
        """Get castle presence chance based on terrain."""
        terrain_castle_chances = {
            'mountain': 0.3,  # High - strategic locations
            'plains': 0.25,   # Medium - border defense
            'coast': 0.2,     # Medium - coastal defense
            'forest': 0.15,   # Low - hidden locations
            'swamp': 0.1,     # Very low - difficult terrain
            'desert': 0.1,    # Very low - harsh environment
            'unknown': 0.05   # Very low
        }
        return terrain_castle_chances.get(terrain, 0.1)
    
    def _generate_castle_name(self, terrain: str) -> str:
        """Generate castle name based on terrain."""
        terrain_castle_names = {
            'mountain': ['Thunder Peak Keep', 'Stone Fist Fortress', 'High Ridge Castle'],
            'plains': ['Golden Field Keep', 'Border Watch Castle', 'Plains Fortress'],
            'coast': ['Sea Watch Tower', 'Harbor Keep', 'Coastal Fortress'],
            'forest': ['Forest Edge Keep', 'Hidden Grove Castle', 'Woodland Fortress'],
            'swamp': ['Marsh Keep', 'Misty Tower', 'Swamp Fortress'],
            'desert': ['Desert Watch', 'Oasis Keep', 'Sand Castle']
        }
        
        names = terrain_castle_names.get(terrain, ['Local Keep'])
        return random.choice(names)
    
    def _generate_castle_condition(self) -> str:
        """Generate castle condition."""
        conditions = [
            'Pristine - Well maintained',
            'Good - Minor repairs needed',
            'Fair - Some structural damage',
            'Poor - Major repairs required',
            'Ruined - Partially collapsed',
            'Abandoned - Overgrown ruins'
        ]
        return random.choice(conditions)
    
    def _generate_castle_defenses(self) -> List[str]:
        """Generate castle defenses."""
        defenses = self.castle_generator['defensive_features']
        return random.sample(defenses, random.randint(2, 4))
    
    def _generate_castle_garrison(self) -> Dict[str, Any]:
        """Generate castle garrison."""
        size = random.choice(self.castle_generator['garrison_sizes'])
        garrison_sizes = {
            'small': {'total': 20, 'cavalry': 2, 'archers': 6, 'infantry': 12},
            'medium': {'total': 50, 'cavalry': 8, 'archers': 15, 'infantry': 27},
            'large': {'total': 100, 'cavalry': 15, 'archers': 30, 'infantry': 55}
        }
        return garrison_sizes.get(size, {'total': 20, 'cavalry': 2, 'archers': 6, 'infantry': 12})
    
    def _generate_castle_lord(self) -> str:
        """Generate castle lord name."""
        lord_names = [
            'Lord Blackwood', 'Lady Stormwind', 'Sir Ironheart',
            'Count Darkstone', 'Baron Frost', 'Duke Thunder',
            'Lord Shadow', 'Lady Moon', 'Sir Firebrand'
        ]
        return random.choice(lord_names)
    
    def _generate_castle_treasury(self) -> Dict[str, Any]:
        """Generate castle treasury."""
        return {
            'wealth': random.randint(100, 1000),
            'precious_items': random.randint(0, 5),
            'magical_items': random.randint(0, 3),
            'documents': random.randint(0, 10)
        }
    
    def _generate_conflicts_for_hex(self, hex_code: str, terrain: str, factions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate conflicts for a hex."""
        conflicts = []
        
        # Generate conflicts between factions
        if len(factions) >= 2:
            for i, faction_a in enumerate(factions):
                for faction_b in factions[i+1:]:
                    if random.random() < 0.3:  # 30% chance of conflict
                        conflict = {
                            'type': random.choice(self.conflict_generator['conflict_types']),
                            'factions': [faction_a['name'], faction_b['name']],
                            'intensity': random.choice(self.conflict_generator['intensity_levels']),
                            'description': self._generate_conflict_description(faction_a, faction_b),
                            'plot_hooks': self._generate_conflict_plot_hooks(faction_a, faction_b)
                        }
                        conflicts.append(conflict)
        
        # Generate terrain-based conflicts
        terrain_conflicts = self._generate_terrain_conflicts(terrain)
        conflicts.extend(terrain_conflicts)
        
        return conflicts[:3]  # Limit to 3 conflicts
    
    def _generate_conflict_description(self, faction_a: Dict[str, Any], faction_b: Dict[str, Any]) -> str:
        """Generate conflict description between two factions."""
        conflict_templates = [
            f"{faction_a['name']} and {faction_b['name']} are locked in a bitter rivalry over territory.",
            f"{faction_a['name']} seeks to expand their influence, threatening {faction_b['name']}'s interests.",
            f"Ancient grudges between {faction_a['name']} and {faction_b['name']} have flared up again.",
            f"{faction_a['name']} and {faction_b['name']} compete for the same limited resources.",
            f"Ideological differences between {faction_a['name']} and {faction_b['name']} have led to open hostility."
        ]
        return random.choice(conflict_templates)
    
    def _generate_conflict_plot_hooks(self, faction_a: Dict[str, Any], faction_b: Dict[str, Any]) -> List[str]:
        """Generate plot hooks for faction conflict."""
        plot_hooks = [
            f"Mediate between {faction_a['name']} and {faction_b['name']}",
            f"Choose sides in the conflict between {faction_a['name']} and {faction_b['name']}",
            f"Exploit the conflict for personal gain",
            f"Gather intelligence for one faction",
            f"Sabotage the other faction's operations"
        ]
        return random.sample(plot_hooks, 3)
    
    def _generate_terrain_conflicts(self, terrain: str) -> List[Dict[str, Any]]:
        """Generate terrain-based conflicts."""
        terrain_conflicts = {
            'mountain': [
                {'type': 'resource', 'description': 'Mining rights dispute over valuable ore deposits'},
                {'type': 'territory', 'description': 'Control of mountain passes and trade routes'}
            ],
            'forest': [
                {'type': 'ideological', 'description': 'Logging vs. forest preservation'},
                {'type': 'territory', 'description': 'Control of ancient forest paths'}
            ],
            'plains': [
                {'type': 'economic', 'description': 'Dispute over fertile farmland'},
                {'type': 'territory', 'description': 'Control of trade routes and markets'}
            ],
            'coast': [
                {'type': 'economic', 'description': 'Fishing rights and harbor control'},
                {'type': 'territory', 'description': 'Control of coastal trade routes'}
            ],
            'swamp': [
                {'type': 'resource', 'description': 'Rare herb gathering rights'},
                {'type': 'ideological', 'description': 'Control of mystical sites'}
            ],
            'desert': [
                {'type': 'resource', 'description': 'Control of water sources and oases'},
                {'type': 'territory', 'description': 'Control of caravan routes'}
            ]
        }
        
        conflicts = terrain_conflicts.get(terrain, [])
        return [{'type': c['type'], 'description': c['description'], 'intensity': random.randint(1, 5)} for c in conflicts]
    
    def _generate_economic_data(self, hex_code: str, terrain: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate economic data for a hex."""
        economy = {
            'trade_routes': random.randint(0, 2),
            'resources': self._get_hex_resources(terrain),
            'economic_activity': self._get_economic_activity(terrain),
            'wealth_level': random.randint(1, 10)
        }
        
        # Modify based on content type
        if content_data.get('type') == 'settlement':
            economy['trade_routes'] += 1
            economy['wealth_level'] += 2
        
        return economy
    
    def _get_hex_resources(self, terrain: str) -> List[str]:
        """Get resources available in hex based on terrain."""
        terrain_resources = {
            'mountain': ['Iron ore', 'Stone', 'Precious metals', 'Crystal deposits'],
            'forest': ['Timber', 'Herbs', 'Game', 'Honey'],
            'plains': ['Grain', 'Livestock', 'Fertile soil', 'Water'],
            'coast': ['Fish', 'Salt', 'Shells', 'Seaweed'],
            'swamp': ['Rare herbs', 'Poisons', 'Mystical plants', 'Peat'],
            'desert': ['Spices', 'Precious stones', 'Salt', 'Exotic materials']
        }
        return terrain_resources.get(terrain, ['General resources'])
    
    def _get_economic_activity(self, terrain: str) -> str:
        """Get primary economic activity for terrain."""
        activities = {
            'mountain': 'Mining and crafting',
            'forest': 'Logging and gathering',
            'plains': 'Farming and herding',
            'coast': 'Fishing and trade',
            'swamp': 'Herb gathering and mysticism',
            'desert': 'Nomadic trade and oasis farming'
        }
        return activities.get(terrain, 'General trade')
    
    def _create_enhanced_encounter(self, content_data: Dict[str, Any], sandbox_data: Dict[str, Any]) -> str:
        """Create enhanced encounter description with sandbox context."""
        encounter_parts = []
        
        # Start with base encounter
        if 'encounter' in content_data:
            encounter_parts.append(content_data['encounter'])
        
        # Add faction context
        if sandbox_data.get('factions'):
            faction = sandbox_data['factions'][0]
            encounter_parts.append(f"Under {faction['name']} influence")
        
        # Add conflict context
        if sandbox_data.get('conflicts'):
            conflict = sandbox_data['conflicts'][0]
            encounter_parts.append(f"Tension: {conflict['type']}")
        
        # Add economic context
        if sandbox_data.get('economic_data', {}).get('trade_routes', 0) > 0:
            encounter_parts.append("Trade route present")
        
        # Add castle context
        if sandbox_data.get('castles'):
            castle = sandbox_data['castles'][0]
            encounter_parts.append(f"Near {castle['name']}")
        
        return " | ".join(encounter_parts) if encounter_parts else content_data.get('encounter', 'Empty hex')
    
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
        """Generate settlement content."""
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
        
        return {
            'name': name,
            'population': population,
            'local_tavern': local_tavern,
            'local_power': local_power,
            'atmosphere': atmosphere,
            'notable_feature': notable_feature,
            'terrain': terrain,
            'type': 'settlement',
            'encounter': f"⌂ **{name}** - A {population} settlement"
        }
    
    def _generate_dungeon_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dungeon content."""
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
        
        if random.random() <= rules.get('loot_chance', 0.3):
            loot = self._generate_loot(language)
            if loot:
                treasure_section = f"\n**Treasure Found:** {loot['description']}"
        
        if random.random() <= rules.get('scroll_chance', 0.2):
            scroll = self._generate_scroll(language)
            if scroll:
                scroll_section = f"\n**Ancient Knowledge:** {scroll['description']}"
        
        return {
            'dungeon_type': dungeon_type,
            'feature': feature,
            'danger': danger,
            'atmosphere': atmosphere,
            'treasure_section': treasure_section,
            'scroll_section': scroll_section,
            'type': 'dungeon',
            'encounter': "▲ **Ancient Ruins**"
        }
    
    def _generate_beast_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate beast encounter content."""
        terrain = context.get('terrain', 'unknown')
        language = context.get('language', 'en')
        
        # Get bestiary tables
        beast_types = self.db_manager.get_table('bestiary', 'beast_types', language)
        beast_features = self.db_manager.get_table('bestiary', 'beast_features', language)
        beast_behaviors = self.db_manager.get_table('bestiary', 'beast_behaviors', language)
        
        # Generate elements
        beast_type = random.choice(beast_types) if beast_types else "Wild beast"
        feature = random.choice(beast_features) if beast_features else "unnatural appearance"
        behavior = random.choice(beast_behaviors) if beast_behaviors else "hunts in the area"
        
        return {
            'beast_type': beast_type,
            'feature': feature,
            'behavior': behavior,
            'terrain': terrain,
            'type': 'beast',
            'encounter': f"※ **Wild Beast Encounter**"
        }
    
    def _generate_npc_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NPC content."""
        terrain = context.get('terrain', 'unknown')
        language = context.get('language', 'en')
        hex_code = context.get('hex_code', '0000')
        
        # Get NPC tables
        tables = self.db_manager.load_tables(language)
        core_tables = tables.get('core_tables', {})
        terrain_tables = tables.get('terrain_tables', {})
        
        # Get terrain-specific denizen types
        terrain_data = terrain_tables.get(terrain, {})
        denizen_types = terrain_data.get('denizen_types', [])
        
        # Generate NPC elements
        name_prefixes = core_tables.get('denizen_names_prefix', [])
        name_suffixes = core_tables.get('denizen_names_suffix', [])
        motivations = core_tables.get('denizen_motivations', [])
        features = core_tables.get('denizen_features', [])
        demeanors = core_tables.get('denizen_demeanors', [])
        
        # Generate name
        if name_prefixes and name_suffixes:
            prefix = random.choice(name_prefixes)
            suffix = random.choice(name_suffixes)
            name = f"{prefix} {suffix}"
        else:
            name = f"Unknown Denizen of {hex_code}"
        
        # Generate other elements
        denizen_type = random.choice(denizen_types) if denizen_types else f"{terrain.title()} dweller"
        motivation = random.choice(motivations) if motivations else "seeks something unknown"
        feature = random.choice(features) if features else "Has an unsettling presence"
        demeanor = random.choice(demeanors) if demeanors else "Cryptic"
        
        return {
            'name': name,
            'denizen_type': denizen_type,
            'motivation': motivation,
            'feature': feature,
            'demeanor': demeanor,
            'terrain': terrain,
            'type': 'npc',
            'encounter': f"☉ **Wandering {denizen_type}**"
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
            notable_features = "\n\n**Notable Features:**\n" + "\n".join(f"- {feature}" for feature in features_list)
        
        # Format key NPCs
        key_npcs = ""
        npcs_list = hardcoded_data.get('key_npcs', [])
        if npcs_list:
            key_npcs = f"\n\n**Key NPCs:** {', '.join(npcs_list)}"
        
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
        """Generate treasure/loot."""
        loot_roll = random.randint(1, 100)
        
        if loot_roll <= 30:  # 30% weapons
            items = self.db_manager.get_table('enhanced_loot', 'weapon_loot', language) or ["Rusty sword"]
            loot_type = 'weapon'
        elif loot_roll <= 50:  # 20% armor
            items = self.db_manager.get_table('enhanced_loot', 'armor_loot', language) or ["Leather armor"]
            loot_type = 'armor'
        elif loot_roll <= 80:  # 30% valuable items
            items = self.db_manager.get_table('enhanced_loot', 'valuable_loot', language) or ["Silver coins"]
            loot_type = 'valuable'
        else:  # 20% utility items
            items = self.db_manager.get_table('enhanced_loot', 'utility_loot', language) or ["Rope"]
            loot_type = 'utility'
        
        loot_item = random.choice(items)
        
        # Generate magical effect
        effects = ["Glimmers with dark energy", "Whispers ancient secrets", "Pulses with unholy power", "Radiates cold"]
        effect = random.choice(effects)
        
        return {
            'type': loot_type,
            'item': loot_item,
            'description': loot_item,
            'full_description': f"**{loot_item}**\n\n**Magical Effect:** {effect}"
        }
    
    def _generate_scroll(self, language: str) -> Optional[Dict[str, Any]]:
        """Generate ancient scroll/knowledge."""
        scroll_types = self.db_manager.get_table('scroll', 'scroll_types', language) or ["Ancient parchment"]
        scroll_content = self.db_manager.get_table('scroll', 'scroll_content', language) or ["forbidden knowledge"]
        scroll_effects = self.db_manager.get_table('scroll', 'scroll_effects', language) or ["causes nightmares when read"]
        
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
    
    def apply_custom_rules(self, rules: Dict[str, Any]):
        """Apply custom generation rules."""
        self.default_rules.update(rules)
        print(f"✅ Custom rules applied: {list(rules.keys())}")
    
    def reset_all_data(self, output_directory: str = "dying_lands_output"):
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
            # Run migration script
            from migrate_tables import TableMigrator
            migrator = TableMigrator()
            migrator.migrate_all_tables()
        
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

    def _initialize_sandbox_systems(self):
        """Initialize sandbox generation systems."""
        # Import sandbox components
        try:
            from sandbox_generator import SandboxGenerator
            self.sandbox_generator = SandboxGenerator()
            print("✅ Sandbox generator initialized")
        except ImportError as e:
            print(f"⚠️  Sandbox generator not available: {e}")
            self.sandbox_generator = None
        
        # Initialize faction system
        self.faction_system = self._initialize_faction_system()
        
        # Initialize settlement enhancement system
        self.settlement_enhancer = self._initialize_settlement_enhancer()
        
        # Initialize castle generation system
        self.castle_generator = self._initialize_castle_generator()
        
        # Initialize conflict generation system
        self.conflict_generator = self._initialize_conflict_generator()
    
    def _initialize_faction_system(self):
        """Initialize the faction system."""
        return {
            'factions': {},
            'relationships': {},
            'territories': {}
        }
    
    def _initialize_settlement_enhancer(self):
        """Initialize settlement enhancement system."""
        return {
            'enhanced_features': True,
            'government_types': True,
            'economic_data': True,
            'defense_systems': True
        }
    
    def _initialize_castle_generator(self):
        """Initialize castle generation system."""
        return {
            'castle_types': ['fortress', 'keep', 'tower', 'palace', 'ruin'],
            'defensive_features': ['walls', 'moat', 'towers', 'gatehouse', 'murder_holes'],
            'garrison_sizes': ['small', 'medium', 'large']
        }
    
    def _initialize_conflict_generator(self):
        """Initialize conflict generation system."""
        return {
            'conflict_types': ['territory', 'resource', 'ideological', 'personal', 'economic', 'religious'],
            'intensity_levels': [1, 2, 3, 4, 5],
            'resolution_methods': ['diplomacy', 'war', 'alliance', 'neutrality', 'escalation']
        }


# Global generation engine instance
generation_engine = GenerationEngine()