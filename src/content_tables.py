#!/usr/bin/env python3
"""
Content Tables for Hexcrawl Generators
Modular table system for Mörk Borg-inspired content generation
"""

# ===== CORE TABLES =====
BASIC_TABLES = {
    'en': {
        'populations': ["20-50", "51-100", "101-500", "501-1000"],
        'buildings': ["Straw", "Cob", "Stone", "Logs", "Clay brick", "Lime mortar"],
        'sounds': ["Silence", "Bustle", "Fighting", "Laughter", "Screaming", "Chanting"],
    },
    'pt': {
        'populations': ["20-50", "51-100", "101-500", "501-1000"],
        'buildings': ["Palha", "Adobe", "Pedra", "Troncos", "Tijolo de barro", "Argamassa de cal"],
        'sounds': ["Silêncio", "Agitação", "Luta", "Risadas", "Gritos", "Cânticos"],
    }
}

# ===== NAMING TABLES =====
NAMING_TABLES = {
    'en': {
        'city_name_1': [
            "Sheep's Head", "Beggar's", "Schleger's", "Arkh's", "Shadow", "Damnation", 
            "Trollblood", "Verhu's", "Mournful", "Weeping", "Grave", "Boar's", "Broken", 
            "Black Moon's", "Shattered Stone", "Bloody Blade", "Omen's", "Resurrection", 
            "Witch's", "Serpent's"
        ],
        'city_name_2': [
            "Crossing", "Creek", "Grove", "Hollow", "Cove", "Alley", "Henge", "Common", 
            "Hill", "Forge", "Moor", "Plain", "Ford", "Pass", "End", "Horn", "Lake", 
            "Harbour", "Heart", "Lot"
        ],
        'tavern_name_1': [
            "The Ancient", "The Bloody", "The Angry", "The Slaughtered", "The Dead", 
            "The Hanged", "The Betrayed", "The Bloated", "The Haunted", "The Sneaky",
            "The Butchered", "The Gutted", "The Decapitated", "The Sleeping", "The Flayed", 
            "The Immortal", "The Buried", "The Putrid", "The Screaming", "The Rotting"
        ],
        'tavern_name_2': [
            "Queen", "Donkey", "Troll", "Wickhead", "Goblin", "Wyvern", "Basilisk", 
            "Prince", "Ram", "Priest", "Hermit", "Butcher", "Assassin", "Taxman", 
            "Lich", "Cannibal", "Blacksmith", "Jester", "Soothsayer", "Devil"
        ],
        'denizen_names_prefix': ['Brother', 'Sister', 'Father', 'Mother', 'Old', 'Young', 'Mad', 'Saint', 'Heretic', 'Lost'],
        'denizen_names_suffix': ['Bones', 'Ash', 'Crow', 'Thorn', 'Rust', 'Mold', 'Grime', 'Rot', 'Doom', 'Blight'],
    },
    'pt': {
        'city_name_1': [
            "Cabeça de Ovelha", "Do Mendigo", "De Schleger", "De Arkh", "Sombra", "Danação", 
            "Sangue de Troll", "De Verhu", "Lamentosa", "Chorosa", "Tumba", "Do Javali", 
            "Quebrada", "Lua Negra", "Pedra Estilhaçada", "Lâmina Sangrenta", "Do Presságio", 
            "Ressurreição", "Da Bruxa", "Da Serpente"
        ],
        'city_name_2': [
            "Cruzamento", "Riacho", "Bosque", "Oco", "Enseada", "Beco", "Pedras Eretas", 
            "Comuna", "Colina", "Forja", "Pântano", "Planície", "Vau", "Passagem", "Fim", 
            "Chifre", "Lago", "Porto", "Coração", "Lote"
        ],
        'tavern_name_1': [
            "O Antigo", "O Sangrento", "O Irado", "O Abatido", "O Morto", "O Enforcado", 
            "O Traído", "O Inchado", "O Assombrado", "O Sorrateiro", "O Açougueiro", 
            "O Destripado", "O Decapitado", "O Adormecido", "O Esfolado", "O Imortal", 
            "O Enterrado", "O Pútrido", "O Gritante", "O Apodrecido"
        ],
        'tavern_name_2': [
            "Rainha", "Burro", "Troll", "Cabeça Maluca", "Goblin", "Serpe", "Basilisco", 
            "Príncipe", "Carneiro", "Sacerdote", "Eremita", "Açougueiro", "Assassino", 
            "Cobrador", "Liche", "Canibal", "Ferreiro", "Bobo", "Adivinho", "Diabo"
        ],
        'denizen_names_prefix': ['Irmão', 'Irmã', 'Pai', 'Mãe', 'Velho', 'Jovem', 'Louco', 'Santo', 'Herege', 'Perdido'],
        'denizen_names_suffix': ['Ossos', 'Cinza', 'Corvo', 'Espinho', 'Ferrugem', 'Mofo', 'Sujeira', 'Podridão', 'Perdição', 'Praga'],
    }
}

# ===== TAVERN TABLES =====
TAVERN_TABLES = {
    'en': {
        'tavern_descriptions': ["Smokey", "Silent", "Filthy", "Dark", "Rowdy", "Smelly"],
        'tavern_special_1': ["Maggot", "Troll steak", "Monkey brain", "Goblin toe", "Long pig", "Bat liver"],
        'tavern_special_2': ["Mushroom", "Algae", "Cockroach", "Spider", "Eyeball", "Locust"],
    },
    'pt': {
        'tavern_descriptions': ["Fumacenta", "Silenciosa", "Imunda", "Escura", "Barulhenta", "Fedorenta"],
        'tavern_special_1': ["Larva", "Bife de troll", "Cérebro de macaco", "Dedo de goblin", "Carne longa", "Fígado de morcego"],
        'tavern_special_2': ["Cogumelo", "Alga", "Barata", "Aranha", "Globo ocular", "Gafanhoto"],
    }
}

# ===== DUNGEON TABLES =====
DUNGEON_TABLES = {
    'en': {
        'dungeon_types': [
            "Ancient tomb", "Ruined temple", "Collapsed mine", "Forgotten crypt", "Abandoned tower", 
            "Underground warren", "Sunken cathedral", "Twisted labyrinth", "Bone pit", "Plague house", 
            "Cursed cellar", "Sacrificial chamber"
        ],
        'dungeon_features': [
            "flooded with black water", "filled with poisonous gas", "haunted by restless spirits", 
            "overrun with vermin", "decorated with blasphemous murals", "littered with ancient bones", 
            "carved from living rock", "built on unholy ground", "twisted by dark magic", 
            "scarred by old battles", "abandoned in haste", "sealed for good reason"
        ],
        'dungeon_dangers': [
            "Collapsing ceiling", "Pit trap with spikes", "Poisonous gas leak", "Unstable floor", 
            "Cursed artifacts", "Territorial undead", "Aggressive scavengers", "Hidden blade traps", 
            "Magical wards", "Disease-ridden corpses", "Flooding chambers", "Structural decay", 
            "Ancient curses", "Toxic mold", "Predatory creatures"
        ],
        'dungeon_treasures': [
            "Silver coins scattered about", "A rusted but valuable weapon", "Ancient scrolls", 
            "Precious gemstones", "Religious artifacts", "Old maps and documents", "Jewelry from the dead", 
            "Rare herbs and components", "Forgotten tools", "Ornate containers", "Mysterious potions", 
            "Carved idols", "Rare metals", "Lost books"
        ],
        'dungeon_atmospheres': ['Oppressive silence', 'Echoing drips', 'Scratching sounds', 'Distant moaning', 'Unnatural cold'],
    },
    'pt': {
        'dungeon_types': [
            "Tumba antiga", "Templo em ruínas", "Mina desabada", "Cripta esquecida", "Torre abandonada", 
            "Toca subterrânea", "Catedral submersa", "Labirinto retorcido", "Poço de ossos", 
            "Casa da peste", "Porão amaldiçoado", "Câmara sacrificial"
        ],
        'dungeon_features': [
            "inundada com água negra", "cheia de gás venenoso", "assombrada por espíritos inquietos", 
            "infestada de pragas", "decorada com murais blasfemos", "coberta de ossos antigos", 
            "escavada na rocha viva", "construída em solo profano", "retorcida por magia sombria", 
            "marcada por batalhas antigas", "abandonada às pressas", "selada por boa razão"
        ],
        'dungeon_dangers': [
            "Teto desabando", "Armadilha com espinhos", "Vazamento de gás venenoso", "Piso instável", 
            "Artefatos amaldiçoados", "Mortos-vivos territoriais", "Carniceiros agressivos", 
            "Armadilhas de lâminas", "Proteções mágicas", "Cadáveres doentes", "Câmaras inundadas", 
            "Deterioração estrutural", "Maldições antigas", "Mofo tóxico", "Criaturas predadoras"
        ],
        'dungeon_treasures': [
            "Moedas de prata espalhadas", "Uma arma enferrujada mas valiosa", "Pergaminhos antigos", 
            "Pedras preciosas", "Artefatos religiosos", "Mapas e documentos antigos", "Joias dos mortos", 
            "Ervas e componentes raros", "Ferramentas esquecidas", "Recipientes ornamentados", 
            "Poções misteriosas", "Ídolos esculpidos", "Metais raros", "Livros perdidos"
        ],
        'dungeon_atmospheres': ['Silêncio opressivo', 'Pingar ecoante', 'Sons de arranhar', 'Gemidos distantes', 'Frio sobrenatural'],
    }
}

# ===== DENIZEN TABLES =====
DENIZEN_TABLES = {
    'en': {
        'denizen_types': [
            "Diseased beggar", "Mad hermit", "Wandering cultist", "Desperate bandit", "Plague doctor", 
            "Witch hunter", "Corrupted priest", "Feral child", "Broken soldier", "Death merchant", 
            "Bone collector", "Grave robber", "Cursed wanderer", "Zealot preacher", "Flesh trader", 
            "Scavenger lord", "Plague bearer", "Doom prophet"
        ],
        'denizen_motivations': [
            "seeks redemption for past sins", "hunts for forbidden knowledge", "flees from terrible pursuers",
            "searches for lost family", "collects trophies from the dead", "spreads word of the coming end",
            "guards ancient secrets", "trades in human misery", "seeks to break an ancient curse",
            "worships forgotten gods", "harvests organs for dark rituals", "prophesies doom and destruction"
        ],
        'denizen_features': [
            "Covered in ritual scars", "Missing several fingers", "Eyes clouded with cataracts", 
            "Speaks in whispers", "Constantly muttering prayers", "Smells of decay", "Wears tattered robes", 
            "Carries strange implements", "Bears holy symbols", "Has visible plague marks", 
            "Moves with unnatural stiffness", "Avoids eye contact", "Nervous tics and twitches", 
            "Unnaturally pale skin", "Teeth filed to points", "Burns easily in sunlight"
        ],
        'denizen_demeanors': ['Hostile', 'Suspicious', 'Desperate', 'Helpful', 'Indifferent', 'Cryptic'],
    },
    'pt': {
        'denizen_types': [
            "Mendigo doente", "Eremita louco", "Cultista errante", "Bandido desesperado", "Médico da peste", 
            "Caçador de bruxas", "Sacerdote corrompido", "Criança selvagem", "Soldado quebrado", 
            "Mercador da morte", "Coletor de ossos", "Saqueador de tumbas", "Andarilho amaldiçoado", 
            "Pregador fanático", "Comerciante de carne", "Senhor dos catadores", "Portador da peste", 
            "Profeta da perdição"
        ],
        'denizen_motivations': [
            "busca redenção pelos pecados passados", "caça conhecimento proibido", "foge de perseguidores terríveis",
            "procura família perdida", "coleta troféus dos mortos", "espalha a palavra do fim que se aproxima",
            "guarda segredos antigos", "comercia com miséria humana", "busca quebrar uma maldição antiga",
            "adora deuses esquecidos", "colhe órgãos para rituais sombrios", "profetiza perdição e destruição"
        ],
        'denizen_features': [
            "Coberto de cicatrizes rituais", "Perdeu vários dedos", "Olhos turvos com cataratas", 
            "Fala em sussurros", "Murmura orações constantemente", "Cheira a decomposição", 
            "Usa robes esfarrapados", "Carrega implementos estranhos", "Porta símbolos sagrados", 
            "Tem marcas visíveis da peste", "Move-se com rigidez sobrenatural", "Evita contato visual", 
            "Tiques nervosos e espasmos", "Pele anormalmente pálida", "Dentes afiados em pontas", 
            "Queima facilmente no sol"
        ],
        'denizen_demeanors': ['Hostil', 'Suspeito', 'Desesperado', 'Prestativo', 'Indiferente', 'Enigmático'],
    }
}

# ===== NEW: BESTIARY TABLES =====
BESTIARY_TABLES = {
    'en': {
        'beast_types': [
            "Plague rat", "Corpse crow", "Bone spider", "Blood leech", "Shadow wolf", "Carrion hound",
            "Sewer serpent", "Rust beetle", "Doom moth", "Acid toad", "Spine crawler", "Flesh wasp",
            "Grave worm", "Blight bat", "Void spider", "Death adder", "Scream bird", "Terror mole"
        ],
        'beast_features': [
            "glowing red eyes", "exposed ribs", "rotting flesh", "venomous bite", "acidic saliva",
            "razor-sharp claws", "diseased fur", "multiple heads", "wings of bone", "metallic scales",
            "constantly bleeding", "emits toxic fumes", "translucent skin", "backwards joints"
        ],
        'beast_behaviors': [
            "hunts in packs", "feeds on corpses", "burrows underground", "hangs from ceilings",
            "stalks silently", "ambushes from shadows", "screams before attacking", "plays dead",
            "spits acid", "drains blood", "spreads disease", "mimics voices", "phases through walls"
        ],
    },
    'pt': {
        'beast_types': [
            "Rato da peste", "Corvo cadavérico", "Aranha óssea", "Sanguessuga sangrenta", "Lobo sombrio", 
            "Cão carniceiro", "Serpente do esgoto", "Besouro enferrujado", "Mariposa da perdição", 
            "Sapo ácido", "Rastejante espinhoso", "Vespa da carne", "Verme sepulcral", "Morcego da praga", 
            "Aranha do vazio", "Víbora da morte", "Pássaro do grito", "Toupeira do terror"
        ],
        'beast_features': [
            "olhos vermelhos brilhantes", "costelas expostas", "carne apodrecida", "mordida venenosa", 
            "saliva ácida", "garras afiadas como navalhas", "pelo doente", "múltiplas cabeças", 
            "asas de osso", "escamas metálicas", "constantemente sangrando", "emite vapores tóxicos", 
            "pele translúcida", "articulações invertidas"
        ],
        'beast_behaviors': [
            "caça em matilhas", "alimenta-se de cadáveres", "escava no subsolo", "pende do teto",
            "espreita silenciosamente", "embosca das sombras", "grita antes de atacar", "finge-se de morto",
            "cospe ácido", "drena sangue", "espalha doenças", "imita vozes", "atravessa paredes"
        ],
    }
}

# ===== NEW: SCROLL TABLES =====
SCROLL_TABLES = {
    'en': {
        'scroll_types': [
            "Crumbling parchment", "Blood-stained vellum", "Bone tablets", "Metal scrolls", "Flesh pages",
            "Stone inscriptions", "Tree bark writings", "Skin manuscripts", "Clay fragments", "Wax tablets"
        ],
        'scroll_content': [
            "heretical prayers", "forbidden spells", "plague recipes", "death rituals", "curses and hexes",
            "prophecies of doom", "maps to lost places", "alchemical formulas", "summoning circles",
            "torture methods", "poison guides", "necromantic arts", "demonic contracts", "blasphemous hymns"
        ],
        'scroll_effects': [
            "causes nightmares when read", "burns the reader's hands", "whispers dark secrets",
            "ages the reader rapidly", "summons malevolent spirits", "inflicts temporary blindness",
            "drives reader temporarily mad", "reveals hidden truths", "grants dark knowledge",
            "curses the reader", "attracts undead", "causes uncontrollable fear"
        ],
    },
    'pt': {
        'scroll_types': [
            "Pergaminho esfarelando", "Velino manchado de sangue", "Tabletes de osso", "Pergaminhos de metal", 
            "Páginas de carne", "Inscrições em pedra", "Escritos em casca de árvore", "Manuscritos de pele", 
            "Fragmentos de argila", "Tabletes de cera"
        ],
        'scroll_content': [
            "orações heréticas", "feitiços proibidos", "receitas da peste", "rituais da morte", 
            "maldições e pragas", "profecias da perdição", "mapas para lugares perdidos", "fórmulas alquímicas", 
            "círculos de invocação", "métodos de tortura", "guias de venenos", "artes necromânticas", 
            "contratos demoníacos", "hinos blasfemos"
        ],
        'scroll_effects': [
            "causa pesadelos quando lido", "queima as mãos do leitor", "sussurra segredos sombrios",
            "envelhece o leitor rapidamente", "invoca espíritos malevolentes", "inflige cegueira temporária",
            "deixa o leitor temporariamente louco", "revela verdades ocultas", "concede conhecimento sombrio",
            "amaldiçoa o leitor", "atrai mortos-vivos", "causa medo incontrolável"
        ],
    }
}

# ===== NEW: LOOT TABLES =====
LOOT_TABLES = {
    'en': {
        'treasure_types': [
            "Cursed jewelry", "Tainted coins", "Bone ornaments", "Blood gems", "Skull chalices",
            "Ritual daggers", "Plague masks", "Death totems", "Forbidden books", "Soul stones",
            "Corpse candles", "Grave dirt", "Unholy relics", "Demon bottles", "Witch tools"
        ],
        'treasure_values': [
            "Worthless but cursed", "Few copper pieces", "Handful of silver", "Small fortune in gold",
            "Priceless but dangerous", "Valuable to cultists", "Sought by collectors", "Worth a life",
            "Magically valuable", "Historically significant", "Religiously important", "Extremely rare"
        ],
        'treasure_effects': [
            "brings bad luck", "attracts undead", "causes nightmares", "grants dark visions",
            "whispers constantly", "feels unnaturally cold", "pulses with evil energy", "corrupts nearby items",
            "reveals hidden passages", "allows communion with dead", "protects from holy symbols",
            "enhances dark magic", "marks bearer for death", "slowly drains life force"
        ],
    },
    'pt': {
        'treasure_types': [
            "Joias amaldiçoadas", "Moedas contaminadas", "Ornamentos de osso", "Gemas sangrentas", 
            "Cálices de caveira", "Punhais rituais", "Máscaras da peste", "Totens da morte", 
            "Livros proibidos", "Pedras da alma", "Velas de cadáver", "Terra de sepultura", 
            "Relíquias profanas", "Garrafas demoníacas", "Ferramentas de bruxa"
        ],
        'treasure_values': [
            "Sem valor mas amaldiçoado", "Algumas moedas de cobre", "Punhado de prata", 
            "Pequena fortuna em ouro", "Inestimável mas perigoso", "Valioso para cultistas", 
            "Procurado por colecionadores", "Vale uma vida", "Magicamente valioso", 
            "Historicamente significativo", "Religiosamente importante", "Extremamente raro"
        ],
        'treasure_effects': [
            "traz má sorte", "atrai mortos-vivos", "causa pesadelos", "concede visões sombrias",
            "sussurra constantemente", "sente-se anormalmente frio", "pulsa com energia maligna", 
            "corrompe itens próximos", "revela passagens ocultas", "permite comunhão com mortos", 
            "protege de símbolos sagrados", "intensifica magia sombria", "marca portador para morte", 
            "drena lentamente força vital"
        ],
    }
}

# ===== NEW: AFFILIATION TABLES =====
AFFILIATION_TABLES = {
    'en': {
        'monster_affiliations': [
            "Cult of the Dying God", "Brotherhood of Bones", "Circle of Carrion", "Order of the Black Sun",
            "Servants of the Void", "Children of Pestilence", "Followers of the Last Prophet", "Legion of the Damned",
            "Covenant of Shadows", "Disciples of Decay", "Heralds of the End", "Apostles of Agony"
        ],
        'npc_affiliations': [
            "Royal Guard remnants", "Merchant Guild outcasts", "Heretical clergy", "Plague survivors",
            "Bandit confederations", "Witch covens", "Grave robber crews", "Mercenary companies",
            "Cultist cells", "Refugee communities", "Scavenger gangs", "Death merchant cartels"
        ],
        'faction_affiliations': [
            "The Dying Church", "House of Broken Nobles", "Merchants of Misery", "The Bone Throne",
            "Plague Wardens", "Shadow Parliament", "Carrion Court", "The Last Kingdom",
            "Brotherhood of the Grave", "Order of Silent Bells", "Council of Worms", "Throne of Skulls"
        ],
        'affiliation_attitudes': [
            "Violently hostile", "Deeply suspicious", "Cautiously neutral", "Grudgingly helpful",
            "Opportunistically friendly", "Desperately seeking aid", "Fanatically devoted", "Secretly plotting",
            "Openly contemptuous", "Fearfully obedient", "Reluctantly cooperative", "Blindly loyal"
        ],
    },
    'pt': {
        'monster_affiliations': [
            "Culto do Deus Moribundo", "Irmandade dos Ossos", "Círculo da Carniça", "Ordem do Sol Negro",
            "Servos do Vazio", "Filhos da Pestilência", "Seguidores do Último Profeta", "Legião dos Danados",
            "Pacto das Sombras", "Discípulos da Decomposição", "Arautos do Fim", "Apóstolos da Agonia"
        ],
        'npc_affiliations': [
            "Remanescentes da Guarda Real", "Rejeitados da Guilda Mercante", "Clero herético", "Sobreviventes da peste",
            "Confederações de bandidos", "Covens de bruxas", "Equipes de saqueadores", "Companhias mercenárias",
            "Células cultistas", "Comunidades refugiadas", "Gangues de catadores", "Cartéis de mercadores da morte"
        ],
        'faction_affiliations': [
            "A Igreja Moribunda", "Casa dos Nobres Quebrados", "Mercadores da Miséria", "O Trono de Ossos",
            "Guardiões da Peste", "Parlamento das Sombras", "Corte da Carniça", "O Último Reino",
            "Irmandade da Sepultura", "Ordem dos Sinos Silenciosos", "Conselho dos Vermes", "Trono de Caveiras"
        ],
        'affiliation_attitudes': [
            "Violentamente hostil", "Profundamente suspeito", "Cautelosamente neutro", "Relutantemente prestativo",
            "Oportunisticamente amigável", "Desesperadamente buscando ajuda", "Fanaticamente devotado", "Secretamente conspiração",
            "Abertamente desdenhoso", "Medrosamente obediente", "Relutantemente cooperativo", "Cegamente leal"
        ],
    }
}

# ===== WILDERNESS TABLES =====
WILDERNESS_TABLES = {
    'en': {
        'wilderness_encounters': [
            "A circle of standing stones humming with power", "Abandoned cart with scattered belongings",
            "Fresh graves with disturbed earth", "Gallows tree with old rope", "Ruined watchtower on a hill",
            "Stream running red with unknown substance", "Crossroads with weathered signpost",
            "Burned farmhouse with blackened timbers", "Ancient cairn marking forgotten dead",
            "Ritual circle drawn in ash and bone", "Well with rope cut and bucket missing",
            "Trail of blood leading into darkness", "Shepherd's hut with door hanging open",
            "Stone bridge over rushing water", "Grove of dead trees in perfect circle",
            "Merchant's bones picked clean by crows", "Cave mouth sealed with heavy stones",
            "Battlefield littered with old weapons", "Shrine to forgotten deity", "Gibbet cage swaying empty"
        ],
        'random_events': [
            "A murder of crows follows the party ominously", "Strange lights dance in the distance",
            "The air grows thick and hard to breathe", "Distant screaming echoes across the land",
            "An unnatural fog rolls in quickly", "The ground trembles with unknown cause",
            "Dead animals litter the path ahead", "A cold wind brings whispers of the past",
            "The sky darkens despite the hour", "Flowers wilt as the party approaches",
            "A terrible stench fills the air", "Shadows move independently of their casters",
            "The temperature drops suddenly", "Strange symbols appear carved in trees",
            "A blood-red moon rises despite daylight", "The party feels watched by unseen eyes",
            "Time seems to slow and distort", "A child's laughter echoes from nowhere",
            "The dead rise from unmarked graves", "Holy symbols crack and tarnish"
        ],
    },
    'pt': {
        'wilderness_encounters': [
            "Um círculo de pedras eretas zunindo com poder", "Carroça abandonada com pertences espalhados",
            "Covas frescas com terra revirada", "Árvore da forca com corda velha", "Torre de vigia arruinada numa colina",
            "Riacho correndo vermelho com substância desconhecida", "Encruzilhada com placa gasta",
            "Casa de fazenda queimada com vigas carbonizadas", "Cairn antigo marcando mortos esquecidos",
            "Círculo ritual desenhado em cinza e osso", "Poço com corda cortada e balde perdido",
            "Trilha de sangue levando à escuridão", "Cabana de pastor com porta escancarada",
            "Ponte de pedra sobre água corrente", "Bosque de árvores mortas em círculo perfeito",
            "Ossos de mercador limpos por corvos", "Boca de caverna selada com pedras pesadas",
            "Campo de batalha coberto de armas velhas", "Santuário de divindade esquecida", "Gaiola de patíbulo balançando vazia"
        ],
        'random_events': [
            "Um bando de corvos segue o grupo sinistro", "Luzes estranhas dançam na distância",
            "O ar fica espesso e difícil de respirar", "Gritos distantes ecoam pela terra",
            "Uma névoa sobrenatural se aproxima rapidamente", "O chão treme com causa desconhecida",
            "Animais mortos cobrem o caminho à frente", "Um vento frio traz sussurros do passado",
            "O céu escurece apesar da hora", "Flores murcham quando o grupo se aproxima",
            "Um fedor terrível preenche o ar", "Sombras se movem independentes de seus criadores",
            "A temperatura cai repentinamente", "Símbolos estranhos aparecem esculpidos em árvores",
            "Uma lua vermelho-sangue nasce apesar da luz do dia", "O grupo se sente observado por olhos invisíveis",
            "O tempo parece desacelerar e se distorcer", "Risada de criança ecoa do nada",
            "Os mortos ressurgem de covas não marcadas", "Símbolos sagrados racham e escurecem"
        ],
    }
}

# ===== STATS TABLES =====
STATS_TABLES = {
    'en': {
        'creature_stats': {
            'weak': {'hp': '1d4', 'armor': '10', 'morale': '6', 'damage': '1d4'},
            'normal': {'hp': '1d6', 'armor': '12', 'morale': '7', 'damage': '1d6'},
            'strong': {'hp': '2d6', 'armor': '14', 'morale': '8', 'damage': '1d8'},
            'elite': {'hp': '3d6', 'armor': '16', 'morale': '9', 'damage': '1d10'},
            'boss': {'hp': '4d6+4', 'armor': '18', 'morale': '10', 'damage': '2d6'}
        },
        'npc_stats': {
            'peasant': {'hp': '1d4', 'armor': '10', 'morale': '5', 'damage': '1d3'},
            'soldier': {'hp': '1d6+1', 'armor': '14', 'morale': '7', 'damage': '1d6'},
            'veteran': {'hp': '2d6', 'armor': '16', 'morale': '8', 'damage': '1d8'},
            'leader': {'hp': '3d6', 'armor': '18', 'morale': '9', 'damage': '1d10'},
            'champion': {'hp': '4d6+2', 'armor': '20', 'morale': '10', 'damage': '2d6'}
        },
        'special_abilities': [
            "Regenerates 1 HP per round", "Immune to normal weapons", "Causes fear (morale -2)",
            "Poisonous attack (save or die)", "Invisible until attacks", "Flies at will",
            "Breathes fire (2d6 damage)", "Drains life force", "Splits when killed",
            "Phases through walls", "Summons reinforcements", "Reflects magic",
            "Berserker rage (+2 damage)", "Death curse on killer", "Explodes when killed"
        ],
        'weaknesses': [
            "Vulnerable to silver", "Harmed by holy symbols", "Fears bright light",
            "Cannot cross running water", "Repelled by garlic", "Weakened by iron",
            "Affected by salt circles", "Damaged by holy water", "Bound by true names",
            "Confused by mirrors", "Paralyzed by music", "Slowed by cold iron"
        ]
    },
    'pt': {
        'creature_stats': {
            'weak': {'hp': '1d4', 'armor': '10', 'morale': '6', 'damage': '1d4'},
            'normal': {'hp': '1d6', 'armor': '12', 'morale': '7', 'damage': '1d6'},
            'strong': {'hp': '2d6', 'armor': '14', 'morale': '8', 'damage': '1d8'},
            'elite': {'hp': '3d6', 'armor': '16', 'morale': '9', 'damage': '1d10'},
            'boss': {'hp': '4d6+4', 'armor': '18', 'morale': '10', 'damage': '2d6'}
        },
        'npc_stats': {
            'peasant': {'hp': '1d4', 'armor': '10', 'morale': '5', 'damage': '1d3'},
            'soldier': {'hp': '1d6+1', 'armor': '14', 'morale': '7', 'damage': '1d6'},
            'veteran': {'hp': '2d6', 'armor': '16', 'morale': '8', 'damage': '1d8'},
            'leader': {'hp': '3d6', 'armor': '18', 'morale': '9', 'damage': '1d10'},
            'champion': {'hp': '4d6+2', 'armor': '20', 'morale': '10', 'damage': '2d6'}
        },
        'special_abilities': [
            "Regenera 1 PV por turno", "Imune a armas normais", "Causa medo (moral -2)",
            "Ataque venenoso (save ou morre)", "Invisível até atacar", "Voa à vontade",
            "Sopra fogo (2d6 dano)", "Drena força vital", "Divide-se quando morto",
            "Atravessa paredes", "Convoca reforços", "Reflete magia",
            "Fúria berserker (+2 dano)", "Maldição da morte no assassino", "Explode quando morto"
        ],
        'weaknesses': [
            "Vulnerável à prata", "Ferido por símbolos sagrados", "Teme luz brilhante",
            "Não pode cruzar água corrente", "Repelido por alho", "Enfraquecido por ferro",
            "Afetado por círculos de sal", "Danificado por água benta", "Preso por nomes verdadeiros",
            "Confundido por espelhos", "Paralisado por música", "Retardado por ferro frio"
        ]
    }
}

# ===== ENHANCED LOOT TABLES =====
ENHANCED_LOOT_TABLES = {
    'en': {
        'weapon_loot': [
            "Rusted sword (+1 damage, breaks on 1)", "Bone dagger (1d4, +1 vs undead)",
            "Plague doctor's cane (1d6, causes disease)", "Executioner's axe (1d8, intimidating)",
            "Witch hunter's crossbow (1d6, +2 vs magic users)", "Grave robber's crowbar (1d4, useful tool)",
            "Cursed blade (1d8, hurts wielder on 1)", "Holy symbol mace (1d6, +1 vs undead)",
            "Poisoned stiletto (1d4, save or paralyzed)", "Broken knight's sword (1d6, once noble)"
        ],
        'armor_loot': [
            "Tattered leather armor (AC 12, smells awful)", "Plague doctor's robes (AC 11, disease immunity)",
            "Rusty chainmail (AC 14, noisy)", "Bone plate armor (AC 15, intimidating)",
            "Witch's cloak (AC 11, +1 vs magic)", "Grave dirt coating (AC 10, undead ignore you)",
            "Cursed helmet (AC +1, constant whispers)", "Holy vestments (AC 12, +1 vs evil)",
            "Thieves' leathers (AC 13, +1 stealth)", "Broken shield (AC +1, once magnificent)"
        ],
        'valuable_loot': [
            "Bag of silver teeth (50 coins)", "Cursed jewelry (100 coins, bad luck)",
            "Rare plague mask (200 coins to collectors)", "Ancient tome (300 coins, forbidden knowledge)",
            "Soul gem (500 coins, whispers constantly)", "Golden skull chalice (150 coins, unholy)",
            "Witch's grimoire (400 coins, dangerous spells)", "Noble's signet ring (80 coins, political value)",
            "Demon bottle (600 coins, contains something)", "Relic bone (250 coins, holy/unholy power)"
        ],
        'utility_loot': [
            "Thieves' tools (lockpicking kit)", "Healing potion (restore 1d6 HP)",
            "Rope (50 feet, sturdy)", "Lantern with oil (6 hours light)",
            "Grappling hook (climbing aid)", "Poison vial (coat weapon)",
            "Holy water (1d4 damage to undead)", "Smoke bomb (escape aid)",
            "Crowbar (useful tool)", "Manacles (restraint device)"
        ]
    },
    'pt': {
        'weapon_loot': [
            "Espada enferrujada (+1 dano, quebra em 1)", "Punhal de osso (1d4, +1 vs mortos-vivos)",
            "Bengala do médico da peste (1d6, causa doença)", "Machado do carrasco (1d8, intimidador)",
            "Besta do caçador de bruxas (1d6, +2 vs usuários de magia)", "Pé de cabra do saqueador (1d4, ferramenta útil)",
            "Lâmina amaldiçoada (1d8, fere portador em 1)", "Maça com símbolo sagrado (1d6, +1 vs mortos-vivos)",
            "Estilete envenenado (1d4, save ou paralisado)", "Espada quebrada do cavaleiro (1d6, outrora nobre)"
        ],
        'armor_loot': [
            "Armadura de couro esfarrapada (CA 12, cheira mal)", "Vestes do médico da peste (CA 11, imunidade à doença)",
            "Cota de malha enferrujada (CA 14, barulhenta)", "Armadura de placas de osso (CA 15, intimidadora)",
            "Manto da bruxa (CA 11, +1 vs magia)", "Revestimento de terra de sepultura (CA 10, mortos-vivos te ignoram)",
            "Elmo amaldiçoado (CA +1, sussurros constantes)", "Vestimentas sagradas (CA 12, +1 vs mal)",
            "Couro de ladrão (CA 13, +1 furtividade)", "Escudo quebrado (CA +1, outrora magnífico)"
        ],
        'valuable_loot': [
            "Saco de dentes de prata (50 moedas)", "Joias amaldiçoadas (100 moedas, má sorte)",
            "Máscara da peste rara (200 moedas para colecionadores)", "Tomo antigo (300 moedas, conhecimento proibido)",
            "Gema da alma (500 moedas, sussurra constantemente)", "Cálice de caveira dourada (150 moedas, profano)",
            "Grimório da bruxa (400 moedas, feitiços perigosos)", "Anel de selo nobre (80 moedas, valor político)",
            "Garrafa demoníaca (600 moedas, contém algo)", "Osso relíquia (250 moedas, poder sagrado/profano)"
        ],
        'utility_loot': [
            "Ferramentas de ladrão (kit de gazua)", "Poção de cura (restaura 1d6 PV)",
            "Corda (50 pés, resistente)", "Lanterna com óleo (6 horas de luz)",
            "Gancho de escalada (ajuda de escalada)", "Frasco de veneno (aplicar na arma)",
            "Água benta (1d4 dano em mortos-vivos)", "Bomba de fumaça (ajuda de fuga)",
            "Pé de cabra (ferramenta útil)", "Algemas (dispositivo de contenção)"
        ]
    }
}

# Update the table categories to include stats
def get_table(category, table_name, language='en'):
    """Get a specific table from a category."""
    table_categories = {
        'basic': BASIC_TABLES,
        'naming': NAMING_TABLES,
        'tavern': TAVERN_TABLES,
        'dungeon': DUNGEON_TABLES,
        'denizen': DENIZEN_TABLES,
        'bestiary': BESTIARY_TABLES,
        'scroll': SCROLL_TABLES,
        'loot': LOOT_TABLES,
        'affiliation': AFFILIATION_TABLES,
        'wilderness': WILDERNESS_TABLES,
        'stats': STATS_TABLES,
        'enhanced_loot': ENHANCED_LOOT_TABLES,
    }
    
    return table_categories.get(category, {}).get(language, {}).get(table_name, [])

def get_all_tables(language='en'):
    """Get all tables combined for backward compatibility."""
    all_tables = {}
    categories = [BASIC_TABLES, NAMING_TABLES, TAVERN_TABLES, DUNGEON_TABLES, 
                 DENIZEN_TABLES, BESTIARY_TABLES, SCROLL_TABLES, LOOT_TABLES, 
                 AFFILIATION_TABLES, WILDERNESS_TABLES, STATS_TABLES, ENHANCED_LOOT_TABLES]
    
    for category in categories:
        if language in category:
            all_tables.update(category[language])
    
    return all_tables

def list_categories():
    """List all available table categories."""
    return ['basic', 'naming', 'tavern', 'dungeon', 'denizen', 'bestiary', 'scroll', 'loot', 'affiliation', 'wilderness', 'stats', 'enhanced_loot']

def list_tables_in_category(category, language='en'):
    """List all tables in a specific category."""
    table_categories = {
        'basic': BASIC_TABLES,
        'naming': NAMING_TABLES,
        'tavern': TAVERN_TABLES,
        'dungeon': DUNGEON_TABLES,
        'denizen': DENIZEN_TABLES,
        'bestiary': BESTIARY_TABLES,
        'scroll': SCROLL_TABLES,
        'loot': LOOT_TABLES,
        'affiliation': AFFILIATION_TABLES,
        'wilderness': WILDERNESS_TABLES,
        'stats': STATS_TABLES,
        'enhanced_loot': ENHANCED_LOOT_TABLES,
    }
    
    category_tables = table_categories.get(category, {}).get(language, {})
    return list(category_tables.keys()) 