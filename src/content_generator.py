#!/usr/bin/env python3
"""
Content Generator Classes
Modular generator system for Mörk Borg-inspired content
"""

import random
from content_tables import get_table, get_all_tables

class ContentGenerator:
    """Main content generator with modular table system."""
    
    def __init__(self, language='en'):
        self.language = language
        self.tables = get_all_tables(language)
    
    def roll(self, table_or_list):
        """Roll on a table (list) or get from table system."""
        if isinstance(table_or_list, str):
            # Try to get from modular tables first
            for category in ['basic', 'naming', 'tavern', 'dungeon', 'denizen', 
                           'bestiary', 'scroll', 'loot', 'affiliation', 'wilderness']:
                table = get_table(category, table_or_list, self.language)
                if table:
                    return random.choice(table)
            # Fallback to combined tables
            return random.choice(self.tables.get(table_or_list, ['Unknown']))
        else:
            return random.choice(table_or_list)
    
    def set_language(self, language):
        """Change the generator language."""
        self.language = language
        self.tables = get_all_tables(language)

class TownGenerator(ContentGenerator):
    """Specialized generator for towns and cities."""
    
    def generate_affiliation(self, affiliation_type=None):
        """Generate an affiliation (monster, npc, or faction)."""
        if not affiliation_type:
            affiliation_type = self.roll(['monster', 'npc', 'faction'])
        
        if affiliation_type == 'monster':
            name = self.roll('monster_affiliations')
        elif affiliation_type == 'npc':
            name = self.roll('npc_affiliations')
        else:  # faction
            name = self.roll('faction_affiliations')
        
        attitude = self.roll('affiliation_attitudes')
        
        return {
            'type': affiliation_type,
            'name': name,
            'attitude': attitude,
            'description': f"{name} ({attitude})"
        }
    
    def generate_town(self):
        """Generate a complete town with all features."""
        name = f"{self.roll('city_name_1')} {self.roll('city_name_2')}"
        population = self.roll('populations')
        building = self.roll('buildings')
        sound = self.roll('sounds')
        
        tavern_name = f"{self.roll('tavern_name_1')} {self.roll('tavern_name_2')}"
        tavern_desc = f"{self.roll('tavern_descriptions')}, {self.roll('tavern_descriptions')}"
        tavern_special = f"{self.roll('tavern_special_1')} & {self.roll('tavern_special_2')}"
        
        # Generate affiliation for the town
        affiliation = self.generate_affiliation()
        
        return {
            "name": name,
            "population": population,
            "building": building,
            "sound": sound,
            "tavern_name": tavern_name,
            "tavern_desc": tavern_desc,
            "tavern_special": tavern_special,
            "affiliation": affiliation
        }

class DungeonGenerator(ContentGenerator):
    """Specialized generator for dungeons."""
    
    def generate_affiliation(self, affiliation_type=None):
        """Generate an affiliation (monster, npc, or faction)."""
        if not affiliation_type:
            affiliation_type = self.roll(['monster', 'npc', 'faction'])
        
        if affiliation_type == 'monster':
            name = self.roll('monster_affiliations')
        elif affiliation_type == 'npc':
            name = self.roll('npc_affiliations')
        else:  # faction
            name = self.roll('faction_affiliations')
        
        attitude = self.roll('affiliation_attitudes')
        
        return {
            'type': affiliation_type,
            'name': name,
            'attitude': attitude,
            'description': f"{name} ({attitude})"
        }
    
    def generate_loot(self):
        """Generate treasure/loot."""
        import random
        from content_tables import get_table
        
        # Roll for loot type
        loot_roll = random.randint(1, 100)
        
        if loot_roll <= 30:  # 30% weapons
            loot_item = self.roll(get_table('enhanced_loot', 'weapon_loot', self.language))
            loot_type = 'weapon'
        elif loot_roll <= 50:  # 20% armor
            loot_item = self.roll(get_table('enhanced_loot', 'armor_loot', self.language))
            loot_type = 'armor'
        elif loot_roll <= 80:  # 30% valuable items
            loot_item = self.roll(get_table('enhanced_loot', 'valuable_loot', self.language))
            loot_type = 'valuable'
        else:  # 20% utility items
            loot_item = self.roll(get_table('enhanced_loot', 'utility_loot', self.language))
            loot_type = 'utility'
        
        # Also add cursed/magical effect
        effect = self.roll('treasure_effects')
        
        return {
            'type': loot_type,
            'item': loot_item,
            'effect': effect,
            'description': loot_item,
            'full_description': f"**{loot_item}**\n\n**Magical Effect:** {effect}"
        }
    
    def generate_scroll(self):
        """Generate a mysterious scroll."""
        scroll_type = self.roll('scroll_types')
        content = self.roll('scroll_content')
        effect = self.roll('scroll_effects')
        
        description = f"{scroll_type} containing {content}"
        
        return {
            'type': scroll_type,
            'content': content,
            'effect': effect,
            'description': description,
            'full_description': f"**{scroll_type}**\n*Contains {content}*\n\n**Effect:** {effect}"
        }
    
    def generate_dungeon(self):
        """Generate a complete dungeon description."""
        dungeon_type = self.roll('dungeon_types')
        feature = self.roll('dungeon_features')
        danger = self.roll('dungeon_dangers')
        treasure = self.roll('dungeon_treasures')
        atmosphere = self.roll('dungeon_atmospheres')
        
        # Generate loot and scrolls
        loot = self.generate_loot()
        scroll = self.generate_scroll()
        
        description = f"{dungeon_type.capitalize()}, {feature}.\n\n"
        description += f"**Primary Danger:** {danger}\n"
        description += f"**Notable Feature:** {treasure}\n"
        description += f"**Atmosphere:** {atmosphere}\n\n"
        
        # Add some procedural rooms
        num_rooms = random.randint(3, 7)
        description += f"**Layout:** {num_rooms} connected chambers\n\n"
        
        # Add loot and scroll if present
        if loot:
            description += f"**Treasure Found:** {loot['description']}\n"
        if scroll:
            description += f"**Ancient Scroll:** {scroll['description']}\n"
        
        return {
            'description': description,
            'loot': loot,
            'scroll': scroll,
            'affiliation': self.generate_affiliation()
        }

class DenizenGenerator(ContentGenerator):
    """Specialized generator for NPCs and denizens."""
    
    def generate_affiliation(self, affiliation_type=None):
        """Generate an affiliation (monster, npc, or faction)."""
        if not affiliation_type:
            affiliation_type = self.roll(['monster', 'npc', 'faction'])
        
        if affiliation_type == 'monster':
            name = self.roll('monster_affiliations')
        elif affiliation_type == 'npc':
            name = self.roll('npc_affiliations')
        else:  # faction
            name = self.roll('faction_affiliations')
        
        attitude = self.roll('affiliation_attitudes')
        
        return {
            'type': affiliation_type,
            'name': name,
            'attitude': attitude,
            'description': f"{name} ({attitude})"
        }
    
    def generate_denizen(self):
        """Generate a complete NPC/denizen."""
        denizen_type = self.roll('denizen_types')
        motivation = self.roll('denizen_motivations')
        feature = self.roll('denizen_features')
        demeanor = self.roll('denizen_demeanors')
        
        name_prefix = self.roll('denizen_names_prefix')
        name_suffix = self.roll('denizen_names_suffix')
        name = f"{name_prefix} {name_suffix}"
        
        # Generate affiliation
        affiliation = self.generate_affiliation()
        
        # Generate stats based on denizen type
        from content_tables import get_table
        npc_stats = get_table('stats', 'npc_stats', self.language)
        
        # Map denizen types to stat categories
        stat_type = 'peasant'  # default
        if any(word in denizen_type.lower() for word in ['soldier', 'guard', 'warrior']):
            stat_type = 'soldier'
        elif any(word in denizen_type.lower() for word in ['veteran', 'captain', 'sergeant']):
            stat_type = 'veteran'
        elif any(word in denizen_type.lower() for word in ['leader', 'noble', 'lord', 'chief']):
            stat_type = 'leader'
        elif any(word in denizen_type.lower() for word in ['champion', 'hero', 'knight']):
            stat_type = 'champion'
        
        stats = npc_stats.get(stat_type, npc_stats.get('peasant', {}))
        
        # Generate equipment/loot
        equipment = []
        if stat_type in ['soldier', 'veteran', 'leader', 'champion']:
            from content_tables import get_table
            weapon = self.roll(get_table('enhanced_loot', 'weapon_loot', self.language))
            armor = self.roll(get_table('enhanced_loot', 'armor_loot', self.language))
            equipment = [weapon, armor]
        
        description = f"**{name}** - {denizen_type}\n"
        description += f"*{feature}*\n\n"
        description += f"**HP:** {stats.get('hp', '1d4')} **AC:** {stats.get('armor', '10')} **Morale:** {stats.get('morale', '5')}\n"
        description += f"**Damage:** {stats.get('damage', '1d3')}\n\n"
        description += f"**Motivation:** {motivation}\n"
        description += f"**Demeanor:** {demeanor}\n"
        description += f"**Affiliation:** {affiliation['name']}\n"
        description += f"**Attitude:** {affiliation['attitude']}"
        
        if equipment:
            description += f"\n\n**Equipment:**\n"
            for item in equipment:
                description += f"- {item}\n"
        
        return {
            'name': name,
            'type': denizen_type,
            'description': description,
            'motivation': motivation,
            'demeanor': demeanor,
            'feature': feature,
            'affiliation': affiliation,
            'stats': stats,
            'equipment': equipment
        }

class BestiaryGenerator(ContentGenerator):
    """Specialized generator for creatures and beasts."""
    
    def generate_affiliation(self, affiliation_type=None):
        """Generate an affiliation (monster, npc, or faction)."""
        if not affiliation_type:
            affiliation_type = self.roll(['monster', 'npc', 'faction'])
        
        if affiliation_type == 'monster':
            name = self.roll('monster_affiliations')
        elif affiliation_type == 'npc':
            name = self.roll('npc_affiliations')
        else:  # faction
            name = self.roll('faction_affiliations')
        
        attitude = self.roll('affiliation_attitudes')
        
        return {
            'type': affiliation_type,
            'name': name,
            'attitude': attitude,
            'description': f"{name} ({attitude})"
        }
    
    def generate_beast(self):
        """Generate a creature for the bestiary."""
        beast_type = self.roll('beast_types')
        feature = self.roll('beast_features')
        behavior = self.roll('beast_behaviors')
        
        # Generate affiliation (usually monster-based)
        affiliation = self.generate_affiliation('monster')
        
        threat_level = self.roll(['Low', 'Medium', 'High', 'Extreme'])
        
        # Generate stats based on threat level
        from content_tables import get_table
        stats_map = {'Low': 'weak', 'Medium': 'normal', 'High': 'strong', 'Extreme': 'elite'}
        stat_type = stats_map.get(threat_level, 'normal')
        creature_stats = get_table('stats', 'creature_stats', self.language)
        stats = creature_stats.get(stat_type, creature_stats.get('normal', {}))
        
        # Add special abilities/weaknesses
        special_ability = None
        weakness = None
        if threat_level in ['High', 'Extreme']:
            special_ability = self.roll(get_table('stats', 'special_abilities', self.language))
        if threat_level in ['Medium', 'High', 'Extreme']:
            weakness = self.roll(get_table('stats', 'weaknesses', self.language))
        
        description = f"**{beast_type.title()}**\n"
        description += f"*{feature}*\n\n"
        description += f"**HP:** {stats.get('hp', '1d6')} **AC:** {stats.get('armor', '12')} **Morale:** {stats.get('morale', '7')}\n"
        description += f"**Damage:** {stats.get('damage', '1d6')}\n\n"
        description += f"**Behavior:** {behavior}\n"
        description += f"**Affiliation:** {affiliation['name']}\n"
        description += f"**Threat Level:** {threat_level}"
        
        if special_ability:
            description += f"\n**Special:** {special_ability}"
        if weakness:
            description += f"\n**Weakness:** {weakness}"
        
        return {
            'name': beast_type,
            'description': description,
            'feature': feature,
            'behavior': behavior,
            'affiliation': affiliation,
            'stats': stats,
            'threat_level': threat_level,
            'special_ability': special_ability,
            'weakness': weakness
        }

class ScrollGenerator(ContentGenerator):
    """Specialized generator for scrolls and documents."""
    
    def generate_scroll(self):
        """Generate a mysterious scroll."""
        scroll_type = self.roll('scroll_types')
        content = self.roll('scroll_content')
        effect = self.roll('scroll_effects')
        
        description = f"{scroll_type} containing {content}"
        
        return {
            'type': scroll_type,
            'content': content,
            'effect': effect,
            'description': description,
            'full_description': f"**{scroll_type}**\n*Contains {content}*\n\n**Effect:** {effect}"
        }

class LootGenerator(ContentGenerator):
    """Specialized generator for treasure and loot."""
    
    def generate_loot(self):
        """Generate treasure/loot."""
        treasure_type = self.roll('treasure_types')
        value = self.roll('treasure_values')
        effect = self.roll('treasure_effects')
        
        description = f"{treasure_type} - {value}"
        
        return {
            'type': treasure_type,
            'value': value,
            'effect': effect,
            'description': description,
            'full_description': f"**{treasure_type}**\n*{value}*\n\n**Magical Effect:** {effect}"
        }

class AffiliationGenerator(ContentGenerator):
    """Specialized generator for affiliations and factions."""
    
    def generate_affiliation(self, affiliation_type=None):
        """Generate an affiliation (monster, npc, or faction)."""
        if not affiliation_type:
            affiliation_type = self.roll(['monster', 'npc', 'faction'])
        
        if affiliation_type == 'monster':
            name = self.roll('monster_affiliations')
        elif affiliation_type == 'npc':
            name = self.roll('npc_affiliations')
        else:  # faction
            name = self.roll('faction_affiliations')
        
        attitude = self.roll('affiliation_attitudes')
        
        return {
            'type': affiliation_type,
            'name': name,
            'attitude': attitude,
            'description': f"{name} ({attitude})"
        }

class WildernessGenerator(ContentGenerator):
    """Specialized generator for wilderness encounters."""
    
    def generate_affiliation(self, affiliation_type=None):
        """Generate an affiliation (monster, npc, or faction)."""
        if not affiliation_type:
            affiliation_type = self.roll(['monster', 'npc', 'faction'])
        
        if affiliation_type == 'monster':
            name = self.roll('monster_affiliations')
        elif affiliation_type == 'npc':
            name = self.roll('npc_affiliations')
        else:  # faction
            name = self.roll('faction_affiliations')
        
        attitude = self.roll('affiliation_attitudes')
        
        return {
            'type': affiliation_type,
            'name': name,
            'attitude': attitude,
            'description': f"{name} ({attitude})"
        }
    
    def generate_wilderness_encounter(self):
        """Generate a wilderness encounter with all features."""
        encounter = self.roll('wilderness_encounters')
        event = self.roll('random_events')
        
        # Chance for additional content
        has_beast = random.random() < 0.3  # 30% chance
        has_loot = random.random() < 0.2   # 20% chance
        has_scroll = random.random() < 0.1  # 10% chance
        
        result = {
            'encounter': encounter,
            'event': event,
            'description': f"{encounter}. {event}.",
            'affiliation': self.generate_affiliation()
        }
        
        if has_beast:
            beast_gen = BestiaryGenerator(self.language)
            result['beast'] = beast_gen.generate_beast()
        
        if has_loot:
            loot_gen = LootGenerator(self.language)
            result['loot'] = loot_gen.generate_loot()
        
        if has_scroll:
            scroll_gen = ScrollGenerator(self.language)
            result['scroll'] = scroll_gen.generate_scroll()
        
        return result

class HexGenerator(ContentGenerator):
    """Main hex content generator that combines all systems."""
    
    def __init__(self, language='en'):
        super().__init__(language)
        self.town_gen = TownGenerator(language)
        self.dungeon_gen = DungeonGenerator(language)
        self.denizen_gen = DenizenGenerator(language)
        self.bestiary_gen = BestiaryGenerator(language)
        self.scroll_gen = ScrollGenerator(language)
        self.loot_gen = LootGenerator(language)
        self.affiliation_gen = AffiliationGenerator(language)
        self.wilderness_gen = WildernessGenerator(language)
    
    def set_language(self, language):
        """Update language for all generators."""
        super().set_language(language)
        self.town_gen.set_language(language)
        self.dungeon_gen.set_language(language)
        self.denizen_gen.set_language(language)
        self.bestiary_gen.set_language(language)
        self.scroll_gen.set_language(language)
        self.loot_gen.set_language(language)
        self.affiliation_gen.set_language(language)
        self.wilderness_gen.set_language(language)
    
    def generate_complete_hex(self, hex_type='random'):
        """Generate a complete hex with all possible content."""
        if hex_type == 'random':
            hex_type = self.roll(['town', 'wilderness', 'dungeon'])
        
        base_content = {
            'type': hex_type,
            'affiliation': self.affiliation_gen.generate_affiliation(),
            'denizen': self.denizen_gen.generate_denizen()
        }
        
        if hex_type == 'town':
            base_content['town'] = self.town_gen.generate_town()
            base_content['dungeon'] = self.dungeon_gen.generate_dungeon()
        elif hex_type == 'wilderness':
            base_content['wilderness'] = self.wilderness_gen.generate_wilderness_encounter()
        elif hex_type == 'dungeon':
            base_content['dungeon'] = self.dungeon_gen.generate_dungeon()
            base_content['wilderness'] = self.wilderness_gen.generate_wilderness_encounter()
        
        # Random additional content
        if random.random() < 0.4:  # 40% chance
            base_content['beast'] = self.bestiary_gen.generate_beast()
        
        if random.random() < 0.3:  # 30% chance
            base_content['loot'] = self.loot_gen.generate_loot()
        
        if random.random() < 0.2:  # 20% chance
            base_content['scroll'] = self.scroll_gen.generate_scroll()
        
        return base_content

# ===== TRANSLATION FUNCTIONS =====
TRANSLATIONS = {
    'en': {
        'bestiary': 'Bestiary', 'scroll': 'Scroll', 'loot': 'Loot', 'affiliation': 'Affiliation',
        'beast': 'Beast', 'treasure': 'Treasure', 'faction': 'Faction', 'attitude': 'Attitude',
        'threat_level': 'Threat Level', 'effect': 'Effect', 'behavior': 'Behavior',
        'motivation': 'Motivation', 'demeanor': 'Demeanor', 'type': 'Type'
    },
    'pt': {
        'bestiary': 'Bestiário', 'scroll': 'Pergaminho', 'loot': 'Tesouro', 'affiliation': 'Afiliação',
        'beast': 'Fera', 'treasure': 'Tesouro', 'faction': 'Facção', 'attitude': 'Atitude',
        'threat_level': 'Nível de Ameaça', 'effect': 'Efeito', 'behavior': 'Comportamento',
        'motivation': 'Motivação', 'demeanor': 'Comportamento', 'type': 'Tipo'
    }
}

def t(key, language='en'):
    """Translate a key to the specified language."""
    return TRANSLATIONS.get(language, {}).get(key, key) 