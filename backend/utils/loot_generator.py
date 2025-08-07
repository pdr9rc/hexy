"""
Loot generation utilities for Mörk Borg style treasure generation.
"""
import random
from typing import Dict, Any, List, Optional


class LootGenerator:
    """Centralized loot generation for Mörk Borg style content."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def generate_loot(self, language: str = 'en') -> Dict[str, Any]:
        """
        Generate Mörk Borg style loot with proper distribution.
        
        Args:
            language: Language for content ('en' or 'pt')
            
        Returns:
            Dictionary containing loot data
        """
        # Get loot tables from database
        trinkets = self.db_manager.get_table('items_trinkets', 'trinkets', language) or []
        items_prices = self.db_manager.get_table('items_prices', 'items', language) or []
        weapons_prices = self.db_manager.get_table('weapons_prices', 'weapons', language) or []
        
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
                loot_item = random.choice([
                    "Espada enferrujada", "Machado de batalha", "Adaga envenenada",
                    "Martelo de guerra", "Lança quebrada", "Arco curvo"
                ])
                loot_type = "weapon"
                effect = "Weapon damage"
            elif loot_roll <= 60:  # 30% armor
                loot_item = random.choice([
                    "Armadura de couro", "Escudo de madeira", "Elmo enferrujado",
                    "Botas de couro", "Luvas de couro", "Cinto de couro"
                ])
                loot_type = "armor"
                effect = "Protection"
            else:  # 40% miscellaneous
                loot_item = random.choice([
                    "Pergaminho antigo", "Poção misteriosa", "Anel estranho",
                    "Moeda antiga", "Pedaço de cristal", "Fragmento de metal"
                ])
                loot_type = "misc"
                effect = "Unknown properties"
        
        return {
            'type': loot_type,
            'item': loot_item,
            'description': f"A {loot_type} with {effect}.",
            'full_description': f"A mysterious {loot_type} that {effect}. Its origins are unknown."
        }
    
    def generate_enhanced_loot(self, language: str = 'en') -> Dict[str, Any]:
        """
        Generate enhanced loot with additional Mörk Borg elements.
        
        Args:
            language: Language for content ('en' or 'pt')
            
        Returns:
            Dictionary containing enhanced loot data
        """
        base_loot = self.generate_loot(language)
        
        # Add Mörk Borg specific enhancements
        enhancements = [
            "pulsa com energia escura",
            "sussurra segredos esquecidos",
            "atrai criaturas estranhas",
            "muda de cor ao toque",
            "esquenta ao contato com sangue",
            "fria como gelo"
        ]
        
        base_loot['enhancement'] = random.choice(enhancements)
        base_loot['full_description'] += f" The item {base_loot['enhancement']}."
        
        return base_loot
    
    def generate_scroll(self, language: str = 'en') -> Dict[str, Any]:
        """
        Generate a Mörk Borg scroll.
        
        Args:
            language: Language for content ('en' or 'pt')
            
        Returns:
            Dictionary containing scroll data
        """
        scroll_types = self.db_manager.get_table('scroll', 'scroll_types', language) or ["pergaminho antigo"]
        scroll_content = self.db_manager.get_table('scroll', 'scroll_content', language) or ["texto ilegível"]
        scroll_effects = self.db_manager.get_table('scroll', 'scroll_effects', language) or ["causa pesadelos quando lido"]
        
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