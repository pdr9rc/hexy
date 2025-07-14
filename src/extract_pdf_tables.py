#!/usr/bin/env python3
"""
PDF Table Extraction Script
Extracts tables and content from the Sandbox Generator PDF for conversion to JSON.
"""

import PyPDF2
import json
import re
import os
from typing import Dict, List, Any

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def identify_tables(text: str) -> Dict[str, List[str]]:
    """Identify potential tables in the PDF text."""
    tables = {}
    
    # Common table patterns
    patterns = {
        'settlement_types': r'(?:settlement|village|town|city).*?(?:\n|$)',
        'faction_types': r'(?:faction|noble|religious|merchant|criminal).*?(?:\n|$)',
        'dungeon_types': r'(?:dungeon|ruin|temple|mine|cave).*?(?:\n|$)',
        'castle_types': r'(?:castle|fortress|keep|tower).*?(?:\n|$)',
        'terrain_features': r'(?:mountain|forest|coast|plains|swamp|desert).*?(?:\n|$)',
        'npc_types': r'(?:npc|character|person).*?(?:\n|$)',
        'treasure_types': r'(?:treasure|loot|gold|gem|artifact).*?(?:\n|$)',
        'conflict_types': r'(?:conflict|war|dispute|rivalry).*?(?:\n|$)',
        'rumor_types': r'(?:rumor|gossip|hearsay|tale).*?(?:\n|$)',
        'event_types': r'(?:event|happening|occurrence|incident).*?(?:\n|$)'
    }
    
    for table_name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            tables[table_name] = [match.strip() for match in matches if len(match.strip()) > 5]
    
    return tables

def extract_structured_content(text: str) -> Dict[str, Any]:
    """Extract structured content from PDF text."""
    content = {}
    
    # Split text into sections
    sections = text.split('\n\n')
    
    for section in sections:
        section = section.strip()
        if len(section) < 10:
            continue
            
        # Look for numbered lists or bullet points
        if re.match(r'^\d+\.', section):
            # Numbered list
            items = re.split(r'\n\d+\.', section)
            if len(items) > 1:
                content['numbered_list'] = [item.strip() for item in items[1:] if item.strip()]
        
        # Look for bullet points
        elif re.match(r'^[•\-\*]', section):
            # Bullet list
            items = re.split(r'\n[•\-\*]', section)
            if len(items) > 1:
                content['bullet_list'] = [item.strip() for item in items[1:] if item.strip()]
        
        # Look for table-like content
        elif '|' in section:
            # Table format
            rows = section.split('\n')
            table_data = []
            for row in rows:
                if '|' in row:
                    cells = [cell.strip() for cell in row.split('|')]
                    table_data.append(cells)
            if table_data:
                content['table_data'] = table_data
    
    return content

def create_enhanced_tables() -> Dict[str, Any]:
    """Create enhanced tables based on common sandbox generator content."""
    enhanced_tables = {
        "rumors": {
            "settlement_rumors": [
                "The mayor is secretly a werewolf",
                "A hidden treasure is buried under the town square",
                "The local priest is actually a cult leader",
                "Merchants are smuggling contraband through the town",
                "A ghost haunts the old inn",
                "The well water is poisoned",
                "Bandits are planning to raid the town",
                "A mysterious stranger has been asking questions",
                "The crops are failing due to a curse",
                "A dragon has been spotted in the nearby mountains"
            ],
            "faction_rumors": [
                "The noble house is plotting against the king",
                "The merchant guild is involved in illegal trade",
                "The religious order is hiding ancient artifacts",
                "The thieves guild has infiltrated the government",
                "The military is preparing for war",
                "The scholars have discovered forbidden knowledge",
                "The druids are protecting a sacred site",
                "The cult is planning a ritual sacrifice",
                "The bandits have a secret hideout",
                "The wizards are experimenting with dangerous magic"
            ],
            "dungeon_rumors": [
                "Ancient treasure lies in the depths",
                "A powerful monster guards the entrance",
                "The dungeon is cursed and drives people mad",
                "Secret passages lead to other locations",
                "The dungeon was built by an ancient civilization",
                "A magical portal exists somewhere inside",
                "The dungeon is actually alive",
                "Time flows differently inside",
                "The dungeon is connected to the underworld",
                "A powerful artifact is hidden within"
            ]
        },
        "events": {
            "settlement_events": [
                "Festival celebrating the harvest",
                "Arrival of a traveling merchant caravan",
                "Wedding of two prominent families",
                "Funeral of a respected elder",
                "Market day with exotic goods",
                "Religious ceremony or ritual",
                "Military parade or training exercise",
                "Arrival of foreign dignitaries",
                "Natural disaster (flood, fire, storm)",
                "Outbreak of disease or plague"
            ],
            "wilderness_events": [
                "Mysterious lights in the distance",
                "Strange animal behavior",
                "Unusual weather patterns",
                "Discovery of ancient ruins",
                "Encounter with nomadic travelers",
                "Natural phenomenon (aurora, eclipse)",
                "Wild animal migration",
                "Forest fire or natural disaster",
                "Mysterious disappearances",
                "Signs of ancient magic"
            ],
            "faction_events": [
                "Diplomatic meeting between factions",
                "Trade agreement or dispute",
                "Military conflict or skirmish",
                "Religious ceremony or ritual",
                "Criminal activity or investigation",
                "Political intrigue or conspiracy",
                "Alliance formation or betrayal",
                "Resource competition or conflict",
                "Cultural exchange or festival",
                "Espionage or sabotage"
            ]
        },
        "npcs": {
            "noble_npcs": [
                "Ambitious young lord seeking power",
                "Wise old noble advising the ruler",
                "Corrupt official abusing authority",
                "Exiled noble plotting return",
                "Noble scholar studying ancient texts",
                "Military noble leading troops",
                "Merchant noble controlling trade",
                "Religious noble serving the faith",
                "Noble adventurer seeking glory",
                "Noble diplomat negotiating peace"
            ],
            "merchant_npcs": [
                "Wealthy merchant controlling trade routes",
                "Crafty trader dealing in exotic goods",
                "Banker with political influence",
                "Smuggler avoiding taxes and laws",
                "Guild master protecting trade secrets",
                "Caravan master leading expeditions",
                "Market master regulating commerce",
                "Merchant spy gathering information",
                "Merchant prince with noble ambitions",
                "Merchant scholar studying economics"
            ],
            "religious_npcs": [
                "Orthodox priest maintaining tradition",
                "Heretical cult leader spreading influence",
                "Monastic scholar preserving knowledge",
                "Religious zealot enforcing doctrine",
                "Charitable cleric helping the poor",
                "Militant paladin fighting evil",
                "Mystical druid protecting nature",
                "Religious diplomat negotiating peace",
                "Prophet predicting the future",
                "Religious spy gathering intelligence"
            ],
            "criminal_npcs": [
                "Thieves guild master controlling crime",
                "Bandit chief leading raids",
                "Assassin accepting contracts",
                "Smuggler moving contraband",
                "Fence handling stolen goods",
                "Pirate captain terrorizing coasts",
                "Corrupt official abusing power",
                "Gang leader warring for territory",
                "Criminal informant selling secrets",
                "Criminal mastermind plotting schemes"
            ]
        },
        "treasures": {
            "magical_items": [
                "Sword that glows in the presence of evil",
                "Ring that grants invisibility",
                "Amulet that protects from magic",
                "Staff that can control weather",
                "Crystal ball that shows the future",
                "Boots that allow flight",
                "Cloak that makes the wearer silent",
                "Gloves that enhance strength",
                "Helmet that grants wisdom",
                "Shield that reflects spells"
            ],
            "artifacts": [
                "Ancient crown of a lost kingdom",
                "Sacred relic of a forgotten god",
                "Map to a hidden treasure",
                "Key to an ancient vault",
                "Scroll containing forbidden knowledge",
                "Crystal that stores memories",
                "Mirror that shows other worlds",
                "Book that contains all knowledge",
                "Sword that can slay any creature",
                "Crown that controls the weather"
            ],
            "valuables": [
                "Pouch of rare gemstones",
                "Chest of ancient gold coins",
                "Jeweled crown or tiara",
                "Golden statue or figurine",
                "Precious metal ingots",
                "Rare artwork or painting",
                "Exotic spices or perfumes",
                "Fine silk or velvet",
                "Rare books or scrolls",
                "Ancient pottery or ceramics"
            ]
        },
        "conflicts": {
            "territorial_disputes": [
                "Border conflict between nations",
                "Land dispute between nobles",
                "Resource competition in wilderness",
                "Trade route control dispute",
                "Fishing rights conflict",
                "Mining rights dispute",
                "Forest logging conflict",
                "Water rights dispute",
                "Hunting ground conflict",
                "Settlement expansion dispute"
            ],
            "ideological_conflicts": [
                "Religious schism or heresy",
                "Political ideology clash",
                "Cultural tradition dispute",
                "Philosophical disagreement",
                "Moral or ethical conflict",
                "Social class struggle",
                "Educational method dispute",
                "Artistic style conflict",
                "Scientific theory debate",
                "Legal interpretation dispute"
            ],
            "economic_conflicts": [
                "Trade monopoly dispute",
                "Taxation and tariff conflict",
                "Labor and wage dispute",
                "Resource distribution conflict",
                "Market control competition",
                "Currency or banking dispute",
                "Property ownership conflict",
                "Investment or loan dispute",
                "Price fixing or competition",
                "Economic policy disagreement"
            ]
        }
    }
    
    return enhanced_tables

def main():
    """Main function to extract and process PDF content."""
    pdf_path = "pdfcoffee.com_atelier-clandestin-sandbox-generator-pdf-free.pdf"
    
    print("🔍 Extracting content from Sandbox Generator PDF...")
    
    # Extract text from PDF
    text = extract_pdf_text(pdf_path)
    
    if not text:
        print("❌ Could not extract text from PDF")
        return
    
    print(f"✅ Extracted {len(text)} characters from PDF")
    
    # Identify tables
    tables = identify_tables(text)
    print(f"📊 Identified {len(tables)} potential table sections")
    
    # Extract structured content
    structured_content = extract_structured_content(text)
    print(f"📋 Extracted {len(structured_content)} structured content sections")
    
    # Create enhanced tables
    enhanced_tables = create_enhanced_tables()
    
    # Save extracted content
    output_dir = "databases/sandbox"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save identified tables
    if tables:
        with open(f"{output_dir}/extracted_tables.json", 'w', encoding='utf-8') as f:
            json.dump(tables, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved extracted tables to {output_dir}/extracted_tables.json")
    
    # Save structured content
    if structured_content:
        with open(f"{output_dir}/structured_content.json", 'w', encoding='utf-8') as f:
            json.dump(structured_content, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved structured content to {output_dir}/structured_content.json")
    
    # Save enhanced tables
    for table_name, table_data in enhanced_tables.items():
        with open(f"{output_dir}/{table_name}.json", 'w', encoding='utf-8') as f:
            json.dump(table_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {table_name} table to {output_dir}/{table_name}.json")
    
    print("\n🎯 Enhanced tables created:")
    for table_name in enhanced_tables.keys():
        print(f"  - {table_name}.json")
    
    print("\n✅ PDF extraction and table creation completed!")

if __name__ == "__main__":
    main() 