#!/usr/bin/env python3
"""
Sandbox Generator by Atelier Clandestin Integration
Enhances hex generation with faction systems, detailed settlements, castles, and biome-aware content.
"""

import random
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from terrain_system import terrain_system, TerrainType
from database_manager import database_manager
from mork_borg_lore_database import MorkBorgLoreDatabase

class FactionType(Enum):
    """Faction types from Sandbox Generator."""
    NOBLE = "noble"
    RELIGIOUS = "religious"
    MERCANTILE = "mercantile"
    CRIMINAL = "criminal"
    MILITARY = "military"
    SCHOLARLY = "scholarly"
    NATURAL = "natural"

class SettlementType(Enum):
    """Settlement types from Sandbox Generator."""
    VILLAGE = "village"
    TOWN = "town"
    CITY = "city"
    CASTLE = "castle"
    FORTRESS = "fortress"
    MONASTERY = "monastery"
    TRADING_POST = "trading_post"
    MINING_CAMP = "mining_camp"
    FISHING_VILLAGE = "fishing_village"
    BANDIT_CAMP = "bandit_camp"

class SandboxGenerator:
    """Main sandbox generation engine integrating with existing terrain system."""
    
    def __init__(self, database_manager_instance=None):
        """Initialize the sandbox generator."""
        self.db_manager = database_manager_instance or database_manager
        self.lore_db = MorkBorgLoreDatabase()
        self.terrain_system = terrain_system
        
        # Load sandbox-specific tables
        self.sandbox_tables = self._load_sandbox_tables()
        
        # Biome modifiers for generation
        self.biome_modifiers = self._initialize_biome_modifiers()
        
        # Faction tracking
        self.active_factions = {}
        self.faction_relationships = {}
        
        # Generation rules
        self.generation_rules = {
            'faction_chance': 0.25,
            'settlement_chance': 0.20,
            'castle_chance': 0.08,
            'dungeon_connection_chance': 0.15,
            'conflict_chance': 0.30
        }
    
    def _load_sandbox_tables(self) -> Dict[str, Any]:
        """Load sandbox-specific generation tables."""
        tables = {}
        
        # Try to load from sandbox-specific JSON files
        sandbox_dir = os.path.join(os.path.dirname(__file__), '..', 'databases', 'sandbox')
        
        if os.path.exists(sandbox_dir):
            for filename in os.listdir(sandbox_dir):
                if filename.endswith('.json') and not filename.startswith('extracted_'):
                    table_name = filename.replace('.json', '')
                    try:
                        with open(os.path.join(sandbox_dir, filename), 'r', encoding='utf-8') as f:
                            tables[table_name] = json.load(f)
                    except Exception as e:
                        print(f"⚠️  Failed to load {filename}: {e}")
        
        # Fallback to existing tables if sandbox tables don't exist
        if not tables:
            print("ℹ️  Using existing database tables for sandbox generation")
            tables = self._create_fallback_tables()
        
        return tables
    
    def _create_fallback_tables(self) -> Dict[str, Any]:
        """Create fallback tables using existing database content."""
        return {
            'factions': {
                'noble': [
                    'Local Baron seeking expansion',
                    'Exiled noble planning return',
                    'Knight-Commander of military order',
                    'Merchant prince with political ambitions'
                ],
                'religious': [
                    'Orthodox temple maintaining tradition',
                    'Heretical cult spreading influence',
                    'Monastic order preserving knowledge',
                    'Death cult preparing for apocalypse'
                ],
                'criminal': [
                    'Thieves guild controlling trade routes',
                    'Bandit clan raiding settlements',
                    'Smugglers moving contraband',
                    'Assassins guild accepting contracts'
                ]
            },
            'settlements': {
                'village': ['Farming village', 'Mining village', 'Fishing village'],
                'town': ['Market town', 'Trading post', 'Military outpost'],
                'city': ['Port city', 'Capital city', 'University city']
            },
            'castles': {
                'conditions': [
                    'Pristine - Well maintained',
                    'Good - Minor repairs needed',
                    'Fair - Some structural damage',
                    'Poor - Major repairs required',
                    'Ruined - Partially collapsed',
                    'Abandoned - Overgrown ruins'
                ],
                'defenses': [
                    'High stone walls with towers',
                    'Deep moat with drawbridge',
                    'Murder holes and portcullis',
                    'Concentric wall design',
                    'Natural cliff protection',
                    'Magical ward stones'
                ]
            }
        }
    
    def _initialize_biome_modifiers(self) -> Dict[str, Dict[str, int]]:
        """Initialize biome-specific modifiers for generation."""
        return {
            'mountain': {
                'fortress_chance': +2,
                'mining_settlement': +3,
                'population_modifier': -1,
                'faction_types': ['military', 'noble'],
                'settlement_types': ['mining_camp', 'fortress', 'monastery']
            },
            'forest': {
                'druid_grove': +2,
                'logging_camp': +3,
                'ranger_outpost': +2,
                'faction_types': ['natural', 'religious'],
                'settlement_types': ['logging_camp', 'ranger_outpost', 'monastery']
            },
            'swamp': {
                'hermit_chance': +3,
                'witch_hut': +2,
                'population_modifier': -2,
                'faction_types': ['religious', 'criminal'],
                'settlement_types': ['village', 'bandit_camp']
            },
            'coast': {
                'port_town': +4,
                'fishing_village': +3,
                'lighthouse': +2,
                'faction_types': ['mercantile', 'military'],
                'settlement_types': ['fishing_village', 'port_town', 'trading_post']
            },
            'plains': {
                'farming_settlement': +3,
                'trade_route': +2,
                'population_modifier': +1,
                'faction_types': ['noble', 'mercantile'],
                'settlement_types': ['village', 'town', 'city']
            },
            'desert': {
                'oasis_settlement': +4,
                'nomad_camp': +3,
                'population_modifier': -2,
                'faction_types': ['religious', 'military'],
                'settlement_types': ['trading_post', 'fortress']
            }
        }
    
    def generate_enhanced_hex_content(self, hex_code: str, terrain_type: str, language: str = 'en') -> Dict[str, Any]:
        """Generate enhanced hex content using Sandbox Generator methods."""
        # Get base terrain information
        terrain_info = self._get_terrain_info(hex_code, terrain_type)
        
        # Generate sandbox elements
        sandbox_data = {
            'factions': self._generate_local_factions(hex_code, terrain_type),
            'settlements': self._generate_detailed_settlements(hex_code, terrain_type),
            'castles': self._generate_castles(hex_code, terrain_type),
            'conflicts': self._generate_faction_conflicts(hex_code),
            'economic_data': self._generate_economic_data(hex_code, terrain_type),
            'plot_hooks': self._generate_plot_hooks(hex_code, terrain_type),
            'terrain_features': self._generate_terrain_features(hex_code, terrain_type)
        }
        
        # Combine with existing content
        enhanced_content = {
            'hex_code': hex_code,
            'terrain': terrain_type,
            'terrain_info': terrain_info,
            'sandbox_data': sandbox_data,
            'language': language
        }
        
        return enhanced_content
    
    def _get_terrain_info(self, hex_code: str, terrain_type: str) -> Dict[str, Any]:
        """Get detailed terrain information."""
        return {
            'type': terrain_type,
            'symbol': self.terrain_system.get_terrain_symbol(terrain_type),
            'color': self.terrain_system.get_terrain_color(terrain_type),
            'description': self.terrain_system.get_terrain_description(terrain_type, 'en'),
            'biome_modifiers': self.biome_modifiers.get(terrain_type, {}),
            'region_analysis': self.terrain_system.analyze_region(hex_code, 3)
        }
    
    def _generate_local_factions(self, hex_code: str, terrain_type: str) -> List[Dict[str, Any]]:
        """Generate factions present in the hex."""
        factions = []
        
        # Check if there are active factions in the region
        region_factions = self._get_factions_in_region(hex_code, radius=3)
        
        # Generate new faction if needed
        if random.random() <= self.generation_rules['faction_chance']:
            new_faction = self._create_faction(hex_code, terrain_type)
            if new_faction:
                factions.append(new_faction)
                self.active_factions[new_faction['id']] = new_faction
        
        # Add existing factions that have influence here
        for faction in region_factions:
            if self._faction_has_influence(faction, hex_code):
                factions.append(faction)
        
        return factions
    
    def _create_faction(self, hex_code: str, terrain_type: str) -> Optional[Dict[str, Any]]:
        """Create a new faction based on terrain and context."""
        faction_types = self.biome_modifiers.get(terrain_type, {}).get('faction_types', ['noble'])
        faction_type = random.choice(faction_types)
        
        # Get faction names from tables
        faction_names = self.sandbox_tables.get('factions', {}).get(faction_type, [])
        if not faction_names:
            faction_names = [f"{faction_type.title()} Faction"]
        
        faction_name = random.choice(faction_names)
        
        faction = {
            'id': f"faction_{len(self.active_factions) + 1}",
            'name': faction_name,
            'type': faction_type,
            'territory': [hex_code],
            'power_level': random.randint(1, 5),
            'goals': self._generate_faction_goals(faction_type),
            'resources': self._generate_faction_resources(faction_type, terrain_type),
            'relationships': {},
            'headquarters': hex_code
        }
        
        return faction
    
    def _generate_faction_goals(self, faction_type: str) -> List[str]:
        """Generate faction goals based on type."""
        goals_map = {
            'noble': ['Expand territory', 'Maintain power', 'Secure alliances'],
            'religious': ['Spread faith', 'Gather followers', 'Protect sacred sites'],
            'mercantile': ['Control trade routes', 'Increase wealth', 'Establish markets'],
            'criminal': ['Expand operations', 'Eliminate rivals', 'Control territory'],
            'military': ['Defend borders', 'Train forces', 'Conquer territory'],
            'scholarly': ['Gather knowledge', 'Preserve artifacts', 'Study ancient texts'],
            'natural': ['Protect nature', 'Maintain balance', 'Drive out civilization']
        }
        
        return random.sample(goals_map.get(faction_type, ['Survive', 'Grow']), 
                           min(2, len(goals_map.get(faction_type, ['Survive']))))
    
    def _generate_faction_resources(self, faction_type: str, terrain_type: str) -> Dict[str, Any]:
        """Generate faction resources based on type and terrain."""
        base_resources = {
            'wealth': random.randint(1, 10),
            'influence': random.randint(1, 10),
            'military': random.randint(1, 10),
            'information': random.randint(1, 10)
        }
        
        # Apply terrain modifiers
        terrain_bonus = self.biome_modifiers.get(terrain_type, {}).get('population_modifier', 0)
        base_resources['influence'] = max(1, base_resources['influence'] + terrain_bonus)
        
        return base_resources
    
    def _generate_detailed_settlements(self, hex_code: str, terrain_type: str) -> List[Dict[str, Any]]:
        """Generate detailed settlements using Sandbox Generator methods."""
        settlements = []
        
        if random.random() <= self.generation_rules['settlement_chance']:
            settlement = self._create_detailed_settlement(hex_code, terrain_type)
            if settlement:
                settlements.append(settlement)
        
        return settlements
    
    def _create_detailed_settlement(self, hex_code: str, terrain_type: str) -> Optional[Dict[str, Any]]:
        """Create a detailed settlement."""
        # Determine settlement type based on terrain
        settlement_types = self.biome_modifiers.get(terrain_type, {}).get('settlement_types', ['village'])
        settlement_type = random.choice(settlement_types)
        
        # Get settlement data from tables
        settlement_names = self.sandbox_tables.get('settlements', {}).get(settlement_type, [])
        if not settlement_names:
            settlement_names = [f"{settlement_type.title()} {hex_code}"]
        
        settlement_name = random.choice(settlement_names)
        
        settlement = {
            'hex_code': hex_code,
            'name': settlement_name,
            'type': settlement_type,
            'population': self._calculate_population(settlement_type, terrain_type),
            'government': self._determine_government(settlement_type),
            'defenses': self._generate_defenses(settlement_type, terrain_type),
            'economy': self._generate_economy(settlement_type, terrain_type),
            'notable_locations': self._generate_notable_locations(settlement_type, terrain_type),
            'key_npcs': self._generate_key_npcs(settlement_type),
            'faction_influence': self._get_faction_influence(hex_code)
        }
        
        return settlement
    
    def _calculate_population(self, settlement_type: str, terrain_type: str) -> int:
        """Calculate settlement population."""
        base_population = {
            'village': random.randint(50, 200),
            'town': random.randint(200, 1000),
            'city': random.randint(1000, 5000),
            'castle': random.randint(20, 100),
            'fortress': random.randint(50, 200),
            'monastery': random.randint(10, 50),
            'trading_post': random.randint(30, 150),
            'mining_camp': random.randint(20, 100),
            'fishing_village': random.randint(100, 300),
            'bandit_camp': random.randint(10, 50)
        }
        
        population = base_population.get(settlement_type, 100)
        
        # Apply terrain modifier
        terrain_modifier = self.biome_modifiers.get(terrain_type, {}).get('population_modifier', 0)
        population = max(10, population + (population * terrain_modifier // 10))
        
        return population
    
    def _determine_government(self, settlement_type: str) -> str:
        """Determine settlement government type."""
        governments = {
            'village': ['Elder council', 'Village head', 'Family patriarch'],
            'town': ['Mayor', 'Merchant council', 'Guild masters'],
            'city': ['City council', 'Noble ruler', 'Merchant prince'],
            'castle': ['Noble lord', 'Knight commander', 'Castellan'],
            'fortress': ['Military commander', 'Garrison captain', 'Warlord'],
            'monastery': ['Abbot', 'Prior', 'Monastic council'],
            'trading_post': ['Factor', 'Merchant master', 'Trade captain'],
            'mining_camp': ['Foreman', 'Mine owner', 'Guild master'],
            'fishing_village': ['Harbor master', 'Fishing captain', 'Village elder'],
            'bandit_camp': ['Bandit chief', 'Gang leader', 'Outlaw king']
        }
        
        return random.choice(governments.get(settlement_type, ['Leader']))
    
    def _generate_defenses(self, settlement_type: str, terrain_type: str) -> List[str]:
        """Generate settlement defenses."""
        base_defenses = {
            'village': ['Wooden palisade', 'Watch tower'],
            'town': ['Stone walls', 'Gatehouse', 'Watch towers'],
            'city': ['High walls', 'Multiple gates', 'Towers', 'Barracks'],
            'castle': ['Stone walls', 'Towers', 'Gatehouse', 'Moats'],
            'fortress': ['Thick walls', 'Battlements', 'Archer positions', 'Siege defenses'],
            'monastery': ['Stone walls', 'Gatehouse', 'Defensive towers'],
            'trading_post': ['Wooden walls', 'Watch tower', 'Armed guards'],
            'mining_camp': ['Wooden palisade', 'Guard posts'],
            'fishing_village': ['Harbor defenses', 'Watch tower'],
            'bandit_camp': ['Hidden location', 'Scout network', 'Escape routes']
        }
        
        defenses = base_defenses.get(settlement_type, [])
        
        # Add terrain-specific defenses
        if terrain_type == 'mountain':
            defenses.extend(['Natural cliffs', 'Narrow passes'])
        elif terrain_type == 'forest':
            defenses.extend(['Dense trees', 'Hidden paths'])
        elif terrain_type == 'swamp':
            defenses.extend(['Difficult terrain', 'Hidden paths'])
        
        return defenses
    
    def _generate_economy(self, settlement_type: str, terrain_type: str) -> Dict[str, Any]:
        """Generate settlement economy."""
        economy = {
            'primary_industry': self._get_primary_industry(settlement_type, terrain_type),
            'trade_goods': self._get_trade_goods(terrain_type),
            'wealth_level': random.randint(1, 5),
            'market_days': random.randint(1, 7)
        }
        
        return economy
    
    def _get_primary_industry(self, settlement_type: str, terrain_type: str) -> str:
        """Get primary industry based on settlement type and terrain."""
        industries = {
            'mountain': ['Mining', 'Stone quarrying', 'Metalworking'],
            'forest': ['Logging', 'Hunting', 'Herb gathering'],
            'coast': ['Fishing', 'Shipbuilding', 'Trade'],
            'plains': ['Farming', 'Herding', 'Trade'],
            'swamp': ['Fishing', 'Herb gathering', 'Hunting'],
            'desert': ['Trade', 'Mining', 'Herding']
        }
        
        settlement_industries = {
            'mining_camp': ['Mining', 'Metalworking'],
            'fishing_village': ['Fishing', 'Shipbuilding'],
            'trading_post': ['Trade', 'Crafting'],
            'monastery': ['Farming', 'Crafting', 'Scholarship']
        }
        
        if settlement_type in settlement_industries:
            return random.choice(settlement_industries[settlement_type])
        else:
            return random.choice(industries.get(terrain_type, ['Farming']))
    
    def _get_trade_goods(self, terrain_type: str) -> List[str]:
        """Get trade goods based on terrain."""
        # Try to get from enhanced economics table
        if 'economics' in self.sandbox_tables:
            terrain_goods_key = f"{terrain_type}_goods"
            if terrain_goods_key in self.sandbox_tables['economics']['trade_goods']:
                goods = self.sandbox_tables['economics']['trade_goods'][terrain_goods_key]
                return random.sample(goods, min(3, len(goods)))
        
        # Fallback to basic goods
        goods = {
            'mountain': ['Iron ore', 'Precious metals', 'Stone', 'Gems'],
            'forest': ['Timber', 'Furs', 'Herbs', 'Honey'],
            'coast': ['Fish', 'Salt', 'Shells', 'Seaweed'],
            'plains': ['Grain', 'Livestock', 'Wool', 'Leather'],
            'swamp': ['Herbs', 'Fish', 'Reeds', 'Bog iron'],
            'desert': ['Spices', 'Precious stones', 'Salt', 'Textiles']
        }
        
        return random.sample(goods.get(terrain_type, ['General goods']), 
                           min(3, len(goods.get(terrain_type, ['General goods']))))
    
    def _generate_notable_locations(self, settlement_type: str, terrain_type: str) -> List[str]:
        """Generate notable locations in the settlement."""
        locations = []
        
        # Base locations by settlement type
        base_locations = {
            'village': ['Tavern', 'Market square', 'Well'],
            'town': ['Tavern', 'Market', 'Temple', 'Guild hall'],
            'city': ['Multiple taverns', 'Grand market', 'Temple district', 'Noble quarter'],
            'castle': ['Great hall', 'Chapel', 'Armory', 'Kitchen'],
            'fortress': ['Command center', 'Barracks', 'Armory', 'Training grounds'],
            'monastery': ['Chapel', 'Library', 'Scriptorium', 'Refectory'],
            'trading_post': ['Warehouse', 'Stables', 'Guest house', 'Market'],
            'mining_camp': ['Mine entrance', 'Ore processing', 'Barracks', 'Mess hall'],
            'fishing_village': ['Harbor', 'Fish market', 'Boat builder', 'Net maker'],
            'bandit_camp': ['Hidden cave', 'Stash location', 'Training area', 'Meeting hall']
        }
        
        locations.extend(base_locations.get(settlement_type, ['Main building']))
        
        # Add terrain-specific locations
        if terrain_type == 'mountain':
            locations.extend(['Mine entrance', 'Lookout post'])
        elif terrain_type == 'forest':
            locations.extend(['Sacred grove', 'Hunting lodge'])
        elif terrain_type == 'coast':
            locations.extend(['Lighthouse', 'Shipyard'])
        
        return locations
    
    def _generate_key_npcs(self, settlement_type: str) -> List[Dict[str, str]]:
        """Generate key NPCs for the settlement."""
        npcs = []
        
        # Get NPC data from existing database
        try:
            npc_types = self.db_manager.get_table('denizen', 'denizen_types', 'en')
            npc_features = self.db_manager.get_table('denizen', 'denizen_features', 'en')
            npc_motivations = self.db_manager.get_table('denizen', 'denizen_motivations', 'en')
        except:
            npc_types = ['Leader', 'Merchant', 'Guard', 'Priest']
            npc_features = ['Scarred', 'Wise', 'Strong', 'Charismatic']
            npc_motivations = ['Power', 'Wealth', 'Knowledge', 'Protection']
        
        # Generate 2-4 key NPCs
        num_npcs = random.randint(2, 4)
        for i in range(num_npcs):
            npc = {
                'name': f"NPC {i+1}",
                'role': random.choice(npc_types),
                'feature': random.choice(npc_features),
                'motivation': random.choice(npc_motivations)
            }
            npcs.append(npc)
        
        return npcs
    
    def _get_faction_influence(self, hex_code: str) -> Dict[str, Any]:
        """Get faction influence in the hex."""
        local_factions = self._get_factions_in_region(hex_code, radius=1)
        
        influence = {}
        for faction in local_factions:
            influence[faction['name']] = {
                'type': faction['type'],
                'power_level': faction['power_level'],
                'goals': faction['goals']
            }
        
        return influence
    
    def _generate_castles(self, hex_code: str, terrain_type: str) -> List[Dict[str, Any]]:
        """Generate castles and fortifications."""
        castles = []
        
        if random.random() <= self.generation_rules['castle_chance']:
            castle = self._create_castle(hex_code, terrain_type)
            if castle:
                castles.append(castle)
        
        return castles
    
    def _create_castle(self, hex_code: str, terrain_type: str) -> Optional[Dict[str, Any]]:
        """Create a castle using Sandbox Generator methods."""
        castle_tables = self.sandbox_tables.get('castles', {})
        
        conditions = castle_tables.get('conditions', ['Good condition'])
        defenses = castle_tables.get('defenses', ['Stone walls'])
        
        castle = {
            'hex_code': hex_code,
            'name': self._generate_castle_name(terrain_type),
            'condition': random.choice(conditions),
            'defenses': random.sample(defenses, min(3, len(defenses))),
            'garrison': self._generate_garrison(terrain_type),
            'lord': self._generate_castle_lord(),
            'treasury': self._generate_treasury(),
            'special_features': self._generate_castle_features(terrain_type),
            'strategic_importance': random.randint(1, 5)
        }
        
        return castle
    
    def _generate_castle_name(self, terrain_type: str) -> str:
        """Generate castle name based on terrain."""
        prefixes = {
            'mountain': ['Stone', 'Iron', 'Granite', 'Peak'],
            'forest': ['Wood', 'Oak', 'Pine', 'Green'],
            'coast': ['Sea', 'Wave', 'Harbor', 'Cliff'],
            'plains': ['Field', 'Meadow', 'Golden', 'Wind'],
            'swamp': ['Marsh', 'Bog', 'Mire', 'Fen'],
            'desert': ['Sand', 'Dune', 'Oasis', 'Sun']
        }
        
        suffixes = ['Keep', 'Castle', 'Fortress', 'Tower', 'Hold']
        
        prefix = random.choice(prefixes.get(terrain_type, ['Old']))
        suffix = random.choice(suffixes)
        
        return f"{prefix} {suffix}"
    
    def _generate_garrison(self, terrain_type: str) -> Dict[str, int]:
        """Generate castle garrison."""
        base_size = random.randint(20, 100)
        
        garrison = {
            'total': base_size,
            'cavalry': base_size // 5,
            'archers': base_size // 3,
            'infantry': base_size - (base_size // 5) - (base_size // 3)
        }
        
        return garrison
    
    def _generate_castle_lord(self) -> Dict[str, str]:
        """Generate castle lord."""
        titles = ['Lord', 'Baron', 'Count', 'Knight', 'Commander']
        names = ['Aldric', 'Baldric', 'Cedric', 'Derek', 'Erik']
        
        return {
            'name': random.choice(names),
            'title': random.choice(titles),
            'reputation': random.choice(['Feared', 'Respected', 'Loved', 'Hated'])
        }
    
    def _generate_treasury(self) -> Dict[str, Any]:
        """Generate castle treasury."""
        return {
            'gold': random.randint(100, 1000),
            'gems': random.randint(0, 10),
            'artifacts': random.randint(0, 3),
            'documents': random.randint(0, 5)
        }
    
    def _generate_castle_features(self, terrain_type: str) -> List[str]:
        """Generate special castle features."""
        features = ['Secret passages', 'Hidden vault', 'Ancient library']
        
        if terrain_type == 'mountain':
            features.extend(['Mountain spring', 'Mine entrance'])
        elif terrain_type == 'forest':
            features.extend(['Hunting grounds', 'Sacred grove'])
        elif terrain_type == 'coast':
            features.extend(['Harbor access', 'Lighthouse'])
        
        return random.sample(features, min(2, len(features)))
    
    def _generate_faction_conflicts(self, hex_code: str) -> List[Dict[str, Any]]:
        """Generate faction conflicts in the region."""
        conflicts = []
        local_factions = self._get_factions_in_region(hex_code, radius=3)
        
        for i, faction_a in enumerate(local_factions):
            for faction_b in local_factions[i+1:]:
                if random.random() <= self.generation_rules['conflict_chance']:
                    conflict = self._create_conflict(faction_a, faction_b)
                    if conflict:
                        conflicts.append(conflict)
        
        return conflicts
    
    def _create_conflict(self, faction_a: Dict[str, Any], faction_b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a conflict between two factions."""
        conflict_types = [
            'Territory Dispute',
            'Resource Competition',
            'Ideological Opposition',
            'Personal Vendetta',
            'Economic Rivalry',
            'Religious Schism'
        ]
        
        conflict_type = random.choice(conflict_types)
        intensity = random.randint(1, 5)
        
        return {
            'type': conflict_type,
            'factions': [faction_a['name'], faction_b['name']],
            'intensity': intensity,
            'description': f"{faction_a['name']} and {faction_b['name']} are in conflict over {conflict_type.lower()}",
            'plot_hooks': self._generate_conflict_plot_hooks(conflict_type, faction_a, faction_b),
            'potential_outcomes': self._generate_potential_outcomes(conflict_type, intensity)
        }
    
    def _generate_conflict_plot_hooks(self, conflict_type: str, faction_a: Dict[str, Any], faction_b: Dict[str, Any]) -> List[str]:
        """Generate plot hooks from faction conflicts."""
        hooks = [
            f"Help {faction_a['name']} gain advantage in the {conflict_type.lower()}",
            f"Mediate between {faction_a['name']} and {faction_b['name']}",
            f"Exploit the conflict for personal gain",
            f"Investigate the root cause of the {conflict_type.lower()}"
        ]
        
        return random.sample(hooks, min(2, len(hooks)))
    
    def _generate_potential_outcomes(self, conflict_type: str, intensity: int) -> List[str]:
        """Generate potential outcomes for conflicts."""
        outcomes = [
            'Peaceful resolution',
            'One faction gains dominance',
            'Escalation to open warfare',
            'Third party intervention',
            'Economic sanctions',
            'Territorial division'
        ]
        
        return random.sample(outcomes, min(3, len(outcomes)))
    
    def _generate_economic_data(self, hex_code: str, terrain_type: str) -> Dict[str, Any]:
        """Generate economic data for the hex."""
        economic_data = {
            'trade_routes': self._generate_trade_routes(hex_code),
            'resources': self._get_trade_goods(terrain_type),
            'economic_activity': random.choice(['High', 'Medium', 'Low']),
            'market_influence': random.randint(1, 5)
        }
        
        # Add enhanced economic data if available
        if 'economics' in self.sandbox_tables:
            # Add market type
            market_types = self.sandbox_tables['economics'].get('market_types', [])
            if market_types:
                economic_data['market_type'] = random.choice(market_types)
            
            # Add economic events
            economic_events = self.sandbox_tables['economics'].get('economic_events', [])
            if economic_events:
                economic_data['recent_events'] = random.sample(economic_events, min(2, len(economic_events)))
        
        return economic_data
    
    def _generate_trade_routes(self, hex_code: str) -> List[str]:
        """Generate trade routes passing through the hex."""
        routes = []
        
        # Simple trade route generation
        directions = ['North-South', 'East-West', 'Coastal', 'Mountain pass']
        route_types = ['Major', 'Minor', 'Local']
        
        if random.random() <= 0.3:  # 30% chance of trade route
            direction = random.choice(directions)
            route_type = random.choice(route_types)
            routes.append(f"{route_type} {direction} route")
        
        return routes
    
    def _generate_plot_hooks(self, hex_code: str, terrain_type: str) -> List[str]:
        """Generate plot hooks for the hex."""
        hooks = []
        
        # Try to get from enhanced rumors table
        if 'rumors' in self.sandbox_tables:
            # Get terrain-specific rumors
            if terrain_type in ['mountain', 'forest', 'coast', 'plains', 'swamp', 'desert']:
                terrain_rumors = self.sandbox_tables['rumors'].get(f'{terrain_type}_rumors', [])
                if terrain_rumors:
                    hooks.extend(random.sample(terrain_rumors, min(2, len(terrain_rumors))))
            
            # Get general rumors
            general_rumors = self.sandbox_tables['rumors'].get('general_rumors', [])
            if general_rumors:
                hooks.extend(random.sample(general_rumors, min(1, len(general_rumors))))
        
        # Fallback to basic terrain hooks
        terrain_hooks = {
            'mountain': [
                'Ancient dwarven ruins discovered',
                'Mining accident reveals hidden chamber',
                'Mountain pass blocked by avalanche'
            ],
            'forest': [
                'Sacred grove threatened by loggers',
                'Ancient tree shows signs of corruption',
                'Forest spirits demand tribute'
            ],
            'coast': [
                'Shipwreck reveals ancient treasure',
                'Pirates establish hidden base',
                'Sea monster sightings increase'
            ],
            'plains': [
                'Crop blight threatens famine',
                'Nomadic raiders approach',
                'Ancient burial mound discovered'
            ],
            'swamp': [
                'Witch coven discovered',
                'Ancient temple emerges from muck',
                'Disease spreads from swamp'
            ],
            'desert': [
                'Oasis dries up mysteriously',
                'Ancient city uncovered by sandstorm',
                'Nomad tribe seeks refuge'
            ]
        }
        
        hooks.extend(terrain_hooks.get(terrain_type, ['Mysterious events occur']))
        
        # Add general hooks
        general_hooks = [
            'Strange lights seen at night',
            'Travelers report unusual encounters',
            'Local legends speak of hidden treasure',
            'Recent events suggest ancient evil awakening'
        ]
        
        hooks.extend(random.sample(general_hooks, min(2, len(general_hooks))))
        
        return hooks
    
    def _generate_terrain_features(self, hex_code: str, terrain_type: str) -> List[str]:
        """Generate terrain-specific features for the hex."""
        features = []
        
        # Try to get from enhanced terrain features table
        if 'terrain_features' in self.sandbox_tables:
            terrain_features_key = f"{terrain_type}_features"
            if terrain_features_key in self.sandbox_tables['terrain_features']:
                available_features = self.sandbox_tables['terrain_features'][terrain_features_key]
                # Generate 1-3 terrain features
                num_features = random.randint(1, min(3, len(available_features)))
                features = random.sample(available_features, num_features)
        
        # Fallback to basic features
        if not features:
            basic_features = {
                'mountain': ['Rocky terrain', 'Steep slopes', 'Mountain pass'],
                'forest': ['Dense trees', 'Wildlife', 'Forest path'],
                'coast': ['Sandy beach', 'Rocky shore', 'Coastal cliffs'],
                'plains': ['Open grassland', 'Fertile soil', 'Wide horizon'],
                'swamp': ['Muddy ground', 'Stagnant water', 'Dense vegetation'],
                'desert': ['Sand dunes', 'Rocky outcrops', 'Oasis']
            }
            features = basic_features.get(terrain_type, ['Natural feature'])
        
        return features
    
    def _get_factions_in_region(self, hex_code: str, radius: int = 3) -> List[Dict[str, Any]]:
        """Get factions active in a region around the hex."""
        try:
            center_x, center_y = int(hex_code[:2]), int(hex_code[2:])
        except (ValueError, IndexError):
            return []
        
        region_factions = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                if 1 <= x <= 25 and 1 <= y <= 30:
                    check_hex = f"{x:02d}{y:02d}"
                    for faction in self.active_factions.values():
                        if check_hex in faction.get('territory', []):
                            region_factions.append(faction)
        
        return region_factions
    
    def _faction_has_influence(self, faction: Dict[str, Any], hex_code: str) -> bool:
        """Check if a faction has influence in a hex."""
        return hex_code in faction.get('territory', [])
    
    def generate_region(self, center_hex: str, radius: int = 9) -> Dict[str, Any]:
        """Generate a complete sandbox region around a center hex."""
        region_hexes = self._get_region_hexes(center_hex, radius)
        
        region_data = {
            'center_hex': center_hex,
            'radius': radius,
            'hexes': region_hexes,
            'factions': [],
            'settlements': [],
            'castles': [],
            'conflicts': [],
            'terrain_distribution': {},
            'economic_network': {}
        }
        
        # Generate content for each hex in the region
        for hex_code in region_hexes:
            terrain = self.terrain_system.get_terrain_for_hex(hex_code)
            hex_content = self.generate_enhanced_hex_content(hex_code, terrain)
            
            # Aggregate region data
            region_data['factions'].extend(hex_content['sandbox_data']['factions'])
            region_data['settlements'].extend(hex_content['sandbox_data']['settlements'])
            region_data['castles'].extend(hex_content['sandbox_data']['castles'])
            region_data['conflicts'].extend(hex_content['sandbox_data']['conflicts'])
            
            # Track terrain distribution
            terrain_type = hex_content['terrain']
            region_data['terrain_distribution'][terrain_type] = region_data['terrain_distribution'].get(terrain_type, 0) + 1
        
        # Remove duplicates
        region_data['factions'] = list({f['id']: f for f in region_data['factions']}.values())
        region_data['conflicts'] = list({c['type'] + str(c['factions']): c for c in region_data['conflicts']}.values())
        
        return region_data
    
    def _get_region_hexes(self, center_hex: str, radius: int) -> List[str]:
        """Get all hex codes in a region around a center hex."""
        try:
            center_x, center_y = int(center_hex[:2]), int(center_hex[2:])
        except (ValueError, IndexError):
            return []
        
        hexes = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                if 1 <= x <= 25 and 1 <= y <= 30:
                    hex_code = f"{x:02d}{y:02d}"
                    hexes.append(hex_code)
        
        return hexes

# Create global instance
sandbox_generator = SandboxGenerator() 