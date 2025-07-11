import argparse
import random
import os
import re

# ===== TRANSLATION SYSTEM (same as before) =====
TRANSLATIONS = {
    'en': {
        'hex_prompt': 'Enter hex code (XXYY format, e.g., 0601) or range (0601-0610): ',
        'terrain_prompt': 'Terrain type for this hex (mountain/forest/coast/plains/swamp): ',
        'invalid_hex': 'Invalid hex format. Using default range.',
        'files_generated': 'Files generated in \'dying_lands_output/\' directory:',
        'hex_files': 'hex files in hexes/',
        'overland_hex_map': 'The Dying Lands Hex Map',
        'hex_descriptions': 'Hex Descriptions',
        'terrain': 'Terrain',
        'encounter': 'Encounter',
        'denizen': 'Denizen',
        'location': 'Location',
        'notable_feature': 'Notable Feature',
        'atmosphere': 'Atmosphere',
        'motivation': 'Motivation',
        'demeanor': 'Demeanor',
    },
    'pt': {
        'hex_prompt': 'Digite o código do hex (formato XXYY, ex: 0601) ou intervalo (0601-0610): ',
        'terrain_prompt': 'Tipo de terreno para este hex (montanha/floresta/costa/planicie/pantano): ',
        'invalid_hex': 'Formato de hex inválido. Usando intervalo padrão.',
        'files_generated': 'Arquivos gerados no diretório \'dying_lands_output/\':',
        'hex_files': 'arquivos de hex em hexes/',
        'overland_hex_map': 'Mapa Hexagonal das Terras Moribundas',
        'hex_descriptions': 'Descrições dos Hexágonos',
        'terrain': 'Terreno',
        'encounter': 'Encontro',
        'denizen': 'Habitante',
        'location': 'Localização',
        'notable_feature': 'Característica Notável',
        'atmosphere': 'Atmosfera',
        'motivation': 'Motivação',
        'demeanor': 'Comportamento',
    }
}

# ===== TERRAIN-SPECIFIC TABLES =====
TERRAIN_TABLES = {
    'en': {
        'mountain': {
            'encounters': [
                "Ancient stone circle on peak", "Collapsed mine entrance", "Eagle's nest with strange eggs",
                "Frozen waterfall hiding cave", "Monastery ruins on cliff", "Giant skeleton embedded in rock",
                "Avalanche-blocked pass", "Hermit's cave dwelling", "Dragon bones scattered about",
                "Sacred burial cairns", "Wind-carved stone faces", "Hidden valley below"
            ],
            'denizen_types': ["Mountain hermit", "Stone giant", "Highland bandit", "Cave troll", "Wind spirit"],
            'features': ["Treacherous cliffs", "Hidden passes", "Ancient carved steps", "Sacred peaks", "Deep chasms"]
        },
        'forest': {
            'encounters': [
                "Circle of twisted trees", "Abandoned woodcutter's camp", "Shrine overgrown with vines",
                "Pack of dire wolves", "Fairy ring of mushrooms", "Hanging corpses in trees",
                "Druid's sacred grove", "Hunting lodge in ruins", "Ancient tree with hollow trunk",
                "Stream of black water", "Spider webs everywhere", "Will-o'-wisps dancing"
            ],
            'denizen_types': ["Wild druid", "Forest witch", "Bandit chief", "Tree shepherd", "Beast hunter"],
            'features': ["Dense undergrowth", "Ancient oaks", "Hidden clearings", "Overgrown paths", "Babbling brooks"]
        },
        'coast': {
            'encounters': [
                "Shipwreck on rocky shore", "Tide pools with strange creatures", "Lighthouse abandoned",
                "Sea cave with echoing depths", "Driftwood shrine", "Beached whale carcass",
                "Fishing village ruins", "Smuggler's hidden cove", "Siren's rocky perch",
                "Message in bottle", "Seaweed-wrapped bones", "Storm approaching fast"
            ],
            'denizen_types': ["Shipwreck survivor", "Sea witch", "Smuggler", "Lighthouse keeper", "Siren"],
            'features': ["Rocky cliffs", "Sandy beaches", "Hidden coves", "Tidal caves", "Salt marshes"]
        },
        'plains': {
            'encounters': [
                "Merchant caravan under attack", "Circle of standing stones", "Abandoned farmstead",
                "Wild horse herd", "Battlefield with old bones", "Windmill with broken sails",
                "Crossroads with gibbet", "Traveling circus camp", "Nomad tent circle",
                "Ancient road marker", "Grazing land turned sour", "Dust devil approaching"
            ],
            'denizen_types': ["Wandering merchant", "Plains rider", "Shepherd", "Road warden", "Nomad chief"],
            'features': ["Rolling hills", "Tall grass", "Ancient roads", "Scattered farms", "Open sky"]
        },
        'swamp': {
            'encounters': [
                "Witch's hut on stilts", "Swamp gas bubbling up", "Corpse hanging from tree",
                "Bog with floating bodies", "Fireflies leading astray", "Alligator nest",
                "Sunken temple ruins", "Will-o'-wisp trail", "Plague victim camp",
                "Quicksand pit hidden", "Frog chorus deafening", "Mist obscuring vision"
            ],
            'denizen_types': ["Swamp witch", "Bog lurker", "Disease bearer", "Marsh hunter", "Lost soul"],
            'features': ["Stagnant pools", "Twisted cypresses", "Floating islands", "Thick mist", "Sucking mud"]
        }
    },
    'pt': {
        'mountain': {
            'encounters': [
                "Círculo de pedras antigas no pico", "Entrada de mina desabada", "Ninho de águia com ovos estranhos",
                "Cachoeira congelada escondendo caverna", "Ruínas de mosteiro no penhasco", "Esqueleto gigante incrustado na rocha",
                "Passagem bloqueada por avalanche", "Caverna habitada por eremita", "Ossos de dragão espalhados",
                "Cairns sagrados de sepultura", "Faces esculpidas pelo vento na pedra", "Vale escondido abaixo"
            ],
            'denizen_types': ["Eremita da montanha", "Gigante de pedra", "Bandido das terras altas", "Troll das cavernas", "Espírito do vento"],
            'features': ["Penhascos traiçoeiros", "Passagens escondidas", "Degraus antigos esculpidos", "Picos sagrados", "Abismos profundos"]
        },
        'forest': {
            'encounters': [
                "Círculo de árvores retorcidas", "Acampamento abandonado de lenhador", "Santuário coberto por vinhas",
                "Matilha de lobos terríveis", "Círculo de fadas com cogumelos", "Cadáveres pendurados em árvores",
                "Bosque sagrado do druida", "Cabana de caça em ruínas", "Árvore antiga com tronco oco",
                "Riacho de água negra", "Teias de aranha por toda parte", "Fogos-fátuos dançando"
            ],
            'denizen_types': ["Druida selvagem", "Bruxa da floresta", "Chefe de bandidos", "Pastor de árvores", "Caçador de feras"],
            'features': ["Vegetação densa", "Carvalhos antigos", "Clareiras escondidas", "Trilhas cobertas", "Riachos murmurantes"]
        },
        'coast': {
            'encounters': [
                "Naufrágio na costa rochosa", "Poças de maré com criaturas estranhas", "Farol abandonado",
                "Caverna marinha com profundezas ecoantes", "Santuário de madeira flutuante", "Carcaça de baleia encalhada",
                "Ruínas de vila de pescadores", "Enseada escondida de contrabandistas", "Poleiro rochoso da sereia",
                "Mensagem na garrafa", "Ossos envoltos em algas", "Tempestade se aproximando rapidamente"
            ],
            'denizen_types': ["Sobrevivente de naufrágio", "Bruxa do mar", "Contrabandista", "Faroleiro", "Sereia"],
            'features': ["Penhascos rochosos", "Praias arenosas", "Enseadas escondidas", "Cavernas de maré", "Pântanos salgados"]
        },
        'plains': {
            'encounters': [
                "Caravana de mercadores sob ataque", "Círculo de pedras eretas", "Fazenda abandonada",
                "Manada de cavalos selvagens", "Campo de batalha com ossos velhos", "Moinho com velas quebradas",
                "Encruzilhada com patíbulo", "Acampamento de circo viajante", "Círculo de tendas nômades",
                "Marco antigo da estrada", "Terra de pastagem azedada", "Redemoinho de poeira se aproximando"
            ],
            'denizen_types': ["Mercador andarilho", "Cavaleiro das planícies", "Pastor", "Guarda da estrada", "Chefe nômade"],
            'features': ["Colinas ondulantes", "Grama alta", "Estradas antigas", "Fazendas espalhadas", "Céu aberto"]
        },
        'swamp': {
            'encounters': [
                "Cabana de bruxa sobre palafitas", "Gás do pântano borbulhando", "Cadáver pendurado em árvore",
                "Lama com corpos flutuando", "Vaga-lumes desviando o caminho", "Ninho de jacaré",
                "Ruínas de templo submerso", "Trilha de fogo-fátuo", "Acampamento de vítimas da peste",
                "Poço de areia movediça escondido", "Coro de sapos ensurdecedor", "Névoa obscurecendo a visão"
            ],
            'denizen_types': ["Bruxa do pântano", "Espreitador do brejo", "Portador de doença", "Caçador do charco", "Alma perdida"],
            'features': ["Poças estagnadas", "Ciprestes retorcidos", "Ilhas flutuantes", "Névoa espessa", "Lama sugadora"]
        }
    }
}

# ===== CORE TABLES (abbreviated for space) =====
TABLES = {
    'en': {
        'denizen_names_prefix': ['Brother', 'Sister', 'Father', 'Mother', 'Old', 'Young', 'Mad', 'Saint', 'Heretic', 'Lost'],
        'denizen_names_suffix': ['Bones', 'Ash', 'Crow', 'Thorn', 'Rust', 'Mold', 'Grime', 'Rot', 'Doom', 'Blight'],
        'denizen_motivations': [
            "seeks redemption for past sins", "hunts for forbidden knowledge", "flees from terrible pursuers",
            "searches for lost family", "guards ancient secrets", "trades in human misery"
        ],
        'denizen_features': [
            "Covered in ritual scars", "Missing several fingers", "Eyes clouded with cataracts",
            "Constantly muttering prayers", "Smells of decay", "Wears tattered robes"
        ],
        'denizen_demeanors': ['Hostile', 'Suspicious', 'Desperate', 'Helpful', 'Indifferent', 'Cryptic'],
        'atmospheres': ['Oppressive silence', 'Echoing sounds', 'Unnatural cold', 'Thick mist', 'Strange lights']
    },
    'pt': {
        'denizen_names_prefix': ['Irmão', 'Irmã', 'Pai', 'Mãe', 'Velho', 'Jovem', 'Louco', 'Santo', 'Herege', 'Perdido'],
        'denizen_names_suffix': ['Ossos', 'Cinza', 'Corvo', 'Espinho', 'Ferrugem', 'Mofo', 'Sujeira', 'Podridão', 'Perdição', 'Praga'],
        'denizen_motivations': [
            "busca redenção pelos pecados passados", "caça conhecimento proibido", "foge de perseguidores terríveis",
            "procura família perdida", "guarda segredos antigos", "comercia com miséria humana"
        ],
        'denizen_features': [
            "Coberto de cicatrizes rituais", "Perdeu vários dedos", "Olhos turvos com cataratas",
            "Murmura orações constantemente", "Cheira a decomposição", "Usa robes esfarrapados"
        ],
        'denizen_demeanors': ['Hostil', 'Suspeito', 'Desesperado', 'Prestativo', 'Indiferente', 'Enigmático'],
        'atmospheres': ['Silêncio opressivo', 'Sons ecoantes', 'Frio sobrenatural', 'Névoa espessa', 'Luzes estranhas']
    }
}

# Global language setting
CURRENT_LANG = 'en'

def t(key):
    """Translate a key to the current language."""
    return TRANSLATIONS.get(CURRENT_LANG, {}).get(key, key)

def get_table(table_name):
    """Get a table in the current language."""
    return TABLES.get(CURRENT_LANG, {}).get(table_name, [])

def get_terrain_table(terrain, table_type):
    """Get a terrain-specific table in the current language."""
    return TERRAIN_TABLES.get(CURRENT_LANG, {}).get(terrain, {}).get(table_type, [])

def roll(table):
    return random.choice(table)

def parse_hex_range(hex_input):
    """Parse hex input (single hex or range)."""
    if '-' in hex_input:
        start, end = hex_input.split('-')
        start_x, start_y = int(start[:2]), int(start[2:])
        end_x, end_y = int(end[:2]), int(end[2:])
        hexes = []
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                hexes.append(f"{x:02d}{y:02d}")
        return hexes
    else:
        return [hex_input]

def detect_terrain_from_hex(hex_code):
    """Basic terrain detection based on hex position (can be enhanced)."""
    x, y = int(hex_code[:2]), int(hex_code[2:])
    
    # Simple heuristics based on the map image
    if x <= 3:  # Western edge
        return 'coast'
    elif x >= 14:  # Eastern edge  
        return 'mountain'
    elif y >= 15:  # Southern swamps
        return 'swamp'
    elif 8 <= x <= 12 and 4 <= y <= 10:  # Central forests
        return 'forest'
    else:
        return 'plains'

def generate_hex_content(hex_code, terrain=None):
    """Generate content for a specific hex using the full content generation system."""
    if not terrain:
        terrain = detect_terrain_from_hex(hex_code)
    
    # Import the content generators
    from content_generator import HexGenerator, TownGenerator, DungeonGenerator, BestiaryGenerator, DenizenGenerator
    
    # Create generators
    hex_gen = HexGenerator(CURRENT_LANG)
    town_gen = TownGenerator(CURRENT_LANG)
    dungeon_gen = DungeonGenerator(CURRENT_LANG)
    beast_gen = BestiaryGenerator(CURRENT_LANG)
    denizen_gen = DenizenGenerator(CURRENT_LANG)
    
    # Determine what type of content to generate based on hex position and terrain
    x, y = int(hex_code[:2]), int(hex_code[2:])
    
    # Calculate probability of different content types
    content_roll = random.randint(1, 100)
    
    # Base content with ASCII terrain markers
    notable_feature = roll(get_terrain_table(terrain, 'features') or ["Unremarkable terrain"])
    atmosphere = roll(get_table('atmospheres') or ["Quiet and still"])
    
    # Determine primary content type with ASCII art markers
    if content_roll <= 15:  # 15% chance of settlement
        town_data = town_gen.generate_town()
        encounter = f"⌂ **{town_data['name']}** - A {town_data['population']} settlement"
        
        # ASCII settlement layout
        settlement_art = '''
    [===]  [===]  [===]
    | T |  | H |  | S |
    [===]  [===]  [===]
        '''
        
        denizen_desc = f"Built from {town_data['building'].lower()}, filled with {town_data['sound'].lower()}.\n\n"
        denizen_desc += f"```{settlement_art}```\n"
        denizen_desc += f"T=Tavern, H=Houses, S=Shops\n\n"
        denizen_desc += f"**Local Tavern:** {town_data['tavern_name']}\n"
        denizen_desc += f"*{town_data['tavern_desc']}*\n"
        denizen_desc += f"**Today's Special:** {town_data['tavern_special']}\n\n"
        denizen_desc += f"**Local Power:** {town_data['affiliation']['description']}"
        
    elif content_roll <= 35:  # 20% chance of dungeon/ruins
        dungeon_data = dungeon_gen.generate_dungeon()
        encounter = "▲ **Ancient Ruins**"
        
        # ASCII ruins layout
        ruins_art = '''
      /\\  /\\  /\\
     /  \\/  \\/  \\
    [    ][    ]
    | ?? || ?? |
    [____][____]
        '''
        
        denizen_desc = dungeon_data['description']
        denizen_desc += f"\n\n```{ruins_art}```\n"
        if dungeon_data.get('loot'):
            denizen_desc += f"\n**Hidden Treasure:** {dungeon_data['loot']['description']}"
        if dungeon_data.get('scroll'):
            denizen_desc += f"\n**Ancient Knowledge:** {dungeon_data['scroll']['description']}"
            
    elif content_roll <= 55:  # 20% chance of beast encounter
        beast_data = beast_gen.generate_beast()
        encounter = f"※ **Wild Beast Encounter**"
        
        # ASCII beast tracks
        beast_art = '''
     o   o   o   o
    / \\ / \\ / \\ / \\
        '''
        
        denizen_desc = beast_data['description']
        denizen_desc += f"\n\n```{beast_art}```\n"
        denizen_desc += f"Fresh tracks lead into the {terrain}..."
            
    else:  # 45% chance of NPCs/denizens
        denizen_data = denizen_gen.generate_denizen()
        encounter = f"☉ **Wandering {denizen_data['type']}**"
        
        # ASCII figure
        figure_art = '''
        O
       /|\\
       / \\
        '''
        
        denizen_desc = denizen_data['description']
        denizen_desc += f"\n\n```{figure_art}```\n"
    
    return {
        'hex_code': hex_code,
        'terrain': terrain,
        'encounter': encounter,
        'denizen': denizen_desc,
        'notable_feature': notable_feature,
        'atmosphere': atmosphere
    }

def create_output_dirs():
    """Create the output directory structure."""
    dirs = [
        'dying_lands_output',
        'dying_lands_output/hexes',
        'dying_lands_output/npcs'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def write_hex_file(hex_data):
    """Write a single hex file."""
    filename = f"dying_lands_output/hexes/hex_{hex_data['hex_code']}.md"
    
    # Safe translation function that falls back to English key
    def safe_t(key):
        try:
            return t(key)
        except:
            # Fallback to English translations
            return TRANSLATIONS.get('en', {}).get(key, key.title())
    
    # ASCII art headers based on terrain
    terrain_headers = {
        'mountain': '''
    /\\   /\\   /\\
   /  \\_/  \\_/  \\
  /            \\
 /              \\
''',
        'forest': '''
      /\\      /\\
     /  \\    /  \\
    /____\\  /____\\
      ||      ||
''',
        'coast': '''
   ~   ~   ~   ~
 ~   ~   ~   ~
   ~   ~   ~   ~
''',
        'plains': '''
  .  .  .  .  .
 .  .  .  .  .
  .  .  .  .  .
''',
        'swamp': '''
  # # # # # #
 # # # # # # #
  # # # # # #
''',
        'desert': '''
  ~~~~~~~~~~~
 ~~~~~.~~~~~
  ~~~~~~~~~~~
'''
    }
    
    terrain_art = terrain_headers.get(hex_data['terrain'], '')
    
    content = f"# Hex {hex_data['hex_code']} - {hex_data['terrain'].title()}\n"
    content += f"```{terrain_art}```\n\n"
    content += f"## Encounter\n\n"
    content += f"{hex_data['encounter']}\n\n"
    content += f"## Notable Feature\n\n"
    content += f"{hex_data['notable_feature']}\n\n"
    content += f"## Atmosphere\n\n"
    content += f"{hex_data['atmosphere']}\n\n"
    content += f"## Denizen\n\n"
    content += f"{hex_data['denizen']}\n\n"
    content += f"**Location:** Hex {hex_data['hex_code']} ({hex_data['terrain']})\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def write_summary_file(all_hex_data):
    """Write a summary file with all hexes."""
    filename = "dying_lands_output/dying_lands_summary.md"
    
    # Safe translation function that falls back to English key
    def safe_t(key):
        try:
            return t(key)
        except:
            # Fallback to English translations
            return TRANSLATIONS.get('en', {}).get(key, key.title())
    
    content = f"# {safe_t('overland_hex_map')}\n\n"
    content += f"## {safe_t('hex_descriptions')}\n\n"
    
    for hex_data in all_hex_data:
        content += f"### Hex {hex_data['hex_code']} - {hex_data['terrain'].title()}\n"
        content += f"- **{safe_t('terrain')}:** {hex_data['terrain']}\n"
        content += f"- **{safe_t('encounter')}:** {hex_data['encounter']}\n"
        content += f"- **{safe_t('notable_feature')}:** {hex_data['notable_feature']}\n\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Generate content for The Dying Lands hex map.")
    parser.add_argument('--hex', type=str, help='Hex code (XXYY) or range (XXYY-XXYY)')
    parser.add_argument('--terrain', choices=['mountain', 'forest', 'coast', 'plains', 'swamp'], help='Override terrain type')
    parser.add_argument('--language', choices=['en', 'pt'], default='en', help='Output language')
    args = parser.parse_args()
    
    global CURRENT_LANG
    CURRENT_LANG = args.language
    
    # Get hex range
    if args.hex:
        try:
            hex_list = parse_hex_range(args.hex)
        except:
            print(t('invalid_hex'))
            hex_list = ['0601', '0602', '0603']
    else:
        hex_input = input(t('hex_prompt'))
        try:
            hex_list = parse_hex_range(hex_input)
        except:
            print(t('invalid_hex'))
            hex_list = ['0601', '0602', '0603']
    
    # Generate content
    create_output_dirs()
    all_hex_data = []
    
    for hex_code in hex_list:
        terrain = args.terrain if args.terrain else None
        hex_data = generate_hex_content(hex_code, terrain)
        write_hex_file(hex_data)
        all_hex_data.append(hex_data)
    
    write_summary_file(all_hex_data)
    
    print(f"\n{t('files_generated')}")
    print(f"- dying_lands_summary.md")
    print(f"- {len(all_hex_data)} {t('hex_files')}")
    
    # Display summary
    print(f"\n## Generated Hexes\n")
    for hex_data in all_hex_data:
        print(f"**{hex_data['hex_code']}** ({hex_data['terrain']}) - {hex_data['encounter'][:50]}...")

if __name__ == "__main__":
    main() 