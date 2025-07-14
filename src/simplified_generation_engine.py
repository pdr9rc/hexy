#!/usr/bin/env python3
"""
Simplified Generation Engine for The Dying Lands
Streamlined generation algorithms with simplified rules and cleaner code structure.
"""

import random
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from database_manager import database_manager
from terrain_system import terrain_system
from translation_system import translation_system
from mork_borg_lore_database import MorkBorgLoreDatabase
from datetime import datetime

class SimplifiedGenerationEngine:
    """Simplified generation engine with cleaner structure and consolidated methods."""
    
    def __init__(self, language: str = 'en'):
        """Initialize the simplified generation engine."""
        self.language = language
        self.db_manager = database_manager
        self.lore_db = MorkBorgLoreDatabase()
        self.translation_system = translation_system
        self.translation_system.set_language(language)
        
        # Load content tables
        self.content_tables = self.db_manager.load_tables(language)
        
        # Simplified generation rules
        self.rules = {
            'settlement_chance': 0.15,
            'dungeon_chance': 0.40,
            'beast_chance': 0.45,
            'npc_chance': 0.35,
            'loot_chance': 0.55,
            'encounter_chance': 0.70,
            'max_encounters_per_hex': 3,
            'max_npcs_per_hex': 2
        }
        
        # Cache for generated content
        self._content_cache = {}
    
    def generate_hex_content(self, hex_code: str, terrain_type: str) -> Dict[str, Any]:
        """Generate complete content for a hex."""
        # Check cache first
        if hex_code in self._content_cache:
            return self._content_cache[hex_code]
        
        content = {
            'hex_code': hex_code,
            'terrain_type': terrain_type,
            'exists': True,
            'weather': self._generate_weather(),
            'difficulty': self._generate_difficulty(),
            'encounters': self._generate_encounters(terrain_type),
            'npcs': self._generate_npcs(terrain_type),
            'settlements': self._generate_settlements(terrain_type),
            'loot': self._generate_loot(terrain_type),
            'description': self._generate_description(terrain_type)
        }
        
        # Cache the content
        self._content_cache[hex_code] = content
        return content
    
    def _generate_weather(self) -> str:
        """Generate weather conditions."""
        weather_table = self.content_tables.get('core_tables', {}).get('weather', [])
        if not weather_table:
            return "Clear skies"
        return random.choice(weather_table)
    
    def _generate_difficulty(self) -> str:
        """Generate difficulty level."""
        difficulties = ['Easy', 'Normal', 'Hard', 'Extreme']
        weights = [0.2, 0.5, 0.25, 0.05]
        return random.choices(difficulties, weights=weights)[0]
    
    def _generate_encounters(self, terrain_type: str) -> List[str]:
        """Generate encounters for the hex."""
        if random.random() > self.rules['encounter_chance']:
            return []
        
        encounters = []
        terrain_tables = self.content_tables.get('terrain_tables', {})
        encounter_table = terrain_tables.get(f'{terrain_type}_encounters', [])
        
        if not encounter_table:
            # Fall back to generic encounters
            encounter_table = self.content_tables.get('core_tables', {}).get('generic_encounters', [])
        
        if encounter_table:
            num_encounters = random.randint(1, min(len(encounter_table), self.rules['max_encounters_per_hex']))
            encounters = random.sample(encounter_table, num_encounters)
        
        return encounters
    
    def _generate_npcs(self, terrain_type: str) -> List[str]:
        """Generate NPCs for the hex."""
        if random.random() > self.rules['npc_chance']:
            return []
        
        npcs = []
        npc_table = self.content_tables.get('core_tables', {}).get('npcs', [])
        
        if npc_table:
            num_npcs = random.randint(1, self.rules['max_npcs_per_hex'])
            npcs = random.sample(npc_table, min(num_npcs, len(npc_table)))
        
        return npcs
    
    def _generate_settlements(self, terrain_type: str) -> List[str]:
        """Generate settlements for the hex."""
        if random.random() > self.rules['settlement_chance']:
            return []
        
        settlements = []
        settlement_table = self.content_tables.get('core_tables', {}).get('settlements', [])
        
        if settlement_table:
            settlements = [random.choice(settlement_table)]
        
        return settlements
    
    def _generate_loot(self, terrain_type: str) -> List[str]:
        """Generate loot for the hex."""
        if random.random() > self.rules['loot_chance']:
            return []
        
        loot = []
        loot_table = self.content_tables.get('core_tables', {}).get('loot', [])
        
        if loot_table:
            num_items = random.randint(1, 3)
            loot = random.choices(loot_table, k=num_items)
        
        return loot
    
    def _generate_description(self, terrain_type: str) -> str:
        """Generate a description for the hex."""
        terrain_tables = self.content_tables.get('terrain_tables', {})
        description_table = terrain_tables.get(f'{terrain_type}_descriptions', [])
        
        if not description_table:
            return f"A {terrain_type} hex in the dying lands."
        
        return random.choice(description_table)
    
    def generate_city_content(self, hex_code: str, city_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced city content."""
        enhanced_city = city_data.copy()
        
        # Add regional NPCs
        regional_npcs = self._generate_regional_npcs()
        
        # Add faction influence
        factions = self._generate_factions()
        
        return {
            'city': enhanced_city,
            'regional_npcs': regional_npcs,
            'factions': factions,
            'success': True
        }
    
    def _generate_regional_npcs(self) -> List[str]:
        """Generate regional NPCs."""
        npc_table = self.content_tables.get('core_tables', {}).get('regional_npcs', [])
        if not npc_table:
            return []
        
        num_npcs = random.randint(2, 5)
        return random.sample(npc_table, min(num_npcs, len(npc_table)))
    
    def _generate_factions(self) -> List[Dict[str, str]]:
        """Generate active factions."""
        faction_table = self.content_tables.get('core_tables', {}).get('factions', [])
        if not faction_table:
            return []
        
        factions = []
        num_factions = random.randint(1, 3)
        
        for _ in range(num_factions):
            faction_name = random.choice(faction_table)
            influence = random.choice(['Low', 'Medium', 'High'])
            description = self._generate_faction_description(faction_name)
            
            factions.append({
                'name': faction_name,
                'influence': influence,
                'description': description
            })
        
        return factions
    
    def _generate_faction_description(self, faction_name: str) -> str:
        """Generate faction description."""
        descriptions = [
            f"The {faction_name} seeks to expand their influence in the region.",
            f"Members of {faction_name} are known for their secretive nature.",
            f"The {faction_name} controls important trade routes.",
            f"Local citizens fear the growing power of {faction_name}.",
            f"The {faction_name} offers protection for a price."
        ]
        return random.choice(descriptions)
    
    def bulk_generate(self, hex_codes: List[str], terrain_map: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Generate content for multiple hexes efficiently."""
        results = {}
        
        for hex_code in hex_codes:
            terrain_type = terrain_map.get(hex_code, 'plains')
            results[hex_code] = self.generate_hex_content(hex_code, terrain_type)
        
        return results
    
    def clear_cache(self):
        """Clear the content cache."""
        self._content_cache.clear()
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about generated content."""
        total_hexes = len(self._content_cache)
        
        stats = {
            'total_hexes': total_hexes,
            'cached_hexes': total_hexes,
            'rules': self.rules.copy(),
            'language': self.language
        }
        
        if total_hexes > 0:
            # Calculate averages
            total_encounters = sum(len(content.get('encounters', [])) for content in self._content_cache.values())
            total_npcs = sum(len(content.get('npcs', [])) for content in self._content_cache.values())
            total_settlements = sum(len(content.get('settlements', [])) for content in self._content_cache.values())
            
            stats.update({
                'avg_encounters_per_hex': round(total_encounters / total_hexes, 2),
                'avg_npcs_per_hex': round(total_npcs / total_hexes, 2),
                'avg_settlements_per_hex': round(total_settlements / total_hexes, 2)
            })
        
        return stats
    
    def export_content(self, output_path: str):
        """Export generated content to JSON file."""
        import json
        
        export_data = {
            'metadata': {
                'language': self.language,
                'generation_rules': self.rules,
                'total_hexes': len(self._content_cache),
                'export_timestamp': str(datetime.now())
            },
            'content': self._content_cache
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def import_content(self, input_path: str):
        """Import previously generated content from JSON file."""
        import json
        
        with open(input_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        if 'content' in import_data:
            self._content_cache.update(import_data['content'])
        
        if 'metadata' in import_data and 'generation_rules' in import_data['metadata']:
            self.rules.update(import_data['metadata']['generation_rules'])


# Global instance for easy access
simplified_generation_engine = SimplifiedGenerationEngine()