#!/usr/bin/env python3

import re

def remove_hardcoded_fallbacks():
    """Remove all hardcoded fallbacks from city_overlay_analyzer.py"""
    
    with open('backend/city_overlay_analyzer.py', 'r') as f:
        content = f.read()
    
    # Remove hardcoded fallback patterns
    patterns_to_remove = [
        # Building encounters fallbacks
        (r'encounter = f"O prédio \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No building encounters available in database")'),
        
        # Building atmospheres fallbacks
        (r'atmosphere = f"O ar ao redor do prédio \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Street encounters fallbacks
        (r'encounter = f"A rua \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No street encounters available in database")'),
        
        # Street atmospheres fallbacks
        (r'atmosphere = f"Andar aqui \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Landmark encounters fallbacks
        (r'encounter = f"The landmark \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No landmark encounters available in database")'),
        
        # Landmark atmospheres fallbacks
        (r'atmosphere = f"The area around it \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Market encounters fallbacks
        (r'encounter = f"The market \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No market encounters available in database")'),
        
        # Market atmospheres fallbacks
        (r'atmosphere = f"The air \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Temple encounters fallbacks
        (r'encounter = f"The temple \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No temple encounters available in database")'),
        
        # Temple atmospheres fallbacks
        (r'atmosphere = f"The sacred space \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Tavern encounters fallbacks
        (r'encounter = f"The tavern \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No tavern encounters available in database")'),
        
        # Tavern descriptions fallbacks
        (r'description = f"A drinking establishment where \{random\.choice\(\[.*?\]\)\}\."', 'description = random.choice(database_manager.get_table("descriptions", "tavern_descriptions", self.language) or [])'),
        
        # Tavern NPCs fallbacks
        (r'random\.choice\(\["Grizzled barkeep", "Mysterious stranger", "Drunk prophet", "Scarred mercenary"\]\)', 'random.choice(database_manager.get_table("npc_names", "tavern_npcs", self.language) or [])'),
        (r'random\.choice\(\["Tavern wench", "Regular patron", "Traveling bard", "Local gossip"\]\)', 'random.choice(database_manager.get_table("npc_names", "tavern_customers", self.language) or [])'),
        
        # Guild encounters fallbacks
        (r'encounter = f"The guild \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No guild encounters available in database")'),
        
        # Guild atmospheres fallbacks
        (r'atmosphere = f"The guild hall \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Guild NPCs fallbacks
        (r'random\.choice\(\["Guild master", "Senior member", "Initiate", "Guild enforcer"\]\)', 'random.choice(database_manager.get_table("npc_names", "guild_members", self.language) or [])'),
        (r'random\.choice\(\["Client", "Rival guild member", "Informant", "Potential recruit"\]\)', 'random.choice(database_manager.get_table("npc_names", "guild_visitors", self.language) or [])'),
        
        # Residence encounters fallbacks
        (r'encounter = f"The residence \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No residence encounters available in database")'),
        
        # Residence atmospheres fallbacks
        (r'atmosphere = f"The home \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Residence treasures fallbacks
        (r'random\.choice\(\["Family heirloom", "Hidden vault", "Personal diary", "Secret passage"\]\)', 'random.choice(database_manager.get_table("loot", "residence_treasures", self.language) or [])'),
        
        # Ruins encounters fallbacks
        (r'encounter = f"The ruins \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No ruins encounters available in database")'),
        
        # Ruins atmospheres fallbacks
        (r'atmosphere = f"The broken stones \{random\.choice\(\[.*?\]\)\}\."', 'raise ValueError("No atmospheres available in database")'),
        
        # Ruins treasures fallbacks
        (r'random\.choice\(\["Ancient artifact", "Forgotten knowledge", "Hidden treasure", "Lost relic"\]\)', 'random.choice(database_manager.get_table("loot", "ruins_treasures", self.language) or [])'),
        (r'random\.choice\(\["Historical document", "Valuable material", "Cursed item", "Sacred object"\]\)', 'random.choice(database_manager.get_table("loot", "ruins_artifacts", self.language) or [])'),
        
        # Hardcoded treasure fallbacks
        (r'or \["Cofre escondido", "Passagem secreta", "Artefato amaldiçoado", "Tomo antigo"\]\)', 'or [])'),
        (r'or \["Prédios instáveis", "Gangues errantes", "Manifestações sobrenaturais", "Vapores venenosos"\]\)', 'or [])'),
        
        # Hardcoded conditions
        (r'conditions = \[.*?\]\s*\n\s*name = random\.choice\(streets\)\s*condition = random\.choice\(conditions\)', 'name = random.choice(streets)\n        condition = random.choice(database_manager.get_table("features", "street_features", self.language) or [])'),
        
        # Hardcoded landmarks
        (r'if not landmarks:\s*landmarks = \[.*?\]\s*\n\s*significances = \[.*?\]\s*\n\s*name = random\.choice\(landmarks\)\s*significance = random\.choice\(significances\)', 'name = random.choice(landmarks)\n        significance = random.choice(database_manager.get_table("features", "landmark_features", self.language) or [])'),
    ]
    
    for pattern, replacement in patterns_to_remove:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('backend/city_overlay_analyzer.py', 'w') as f:
        f.write(content)
    
    print("Hardcoded fallbacks removed from city_overlay_analyzer.py")

if __name__ == "__main__":
    remove_hardcoded_fallbacks()
