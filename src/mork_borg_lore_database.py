#!/usr/bin/env python3
"""
Mörk Borg Lore Database
Comprehensive database of canon locations, NPCs, factions, and lore for accurate map placement.
"""

from typing import Dict, List, Tuple, Optional

class MorkBorgLoreDatabase:
    """Database of canonical Mörk Borg lore for accurate map placement."""
    
    def __init__(self):
        self.major_cities = self._init_major_cities()
        self.factions = self._init_factions()
        self.notable_npcs = self._init_notable_npcs()
        self.regional_lore = self._init_regional_lore()
        self.hardcoded_hexes = self._init_hardcoded_hexes()
    
    def _init_major_cities(self) -> Dict:
        """Initialize major cities from Mörk Borg lore."""
        return {
            'galgenbeck': {
                'name': 'Galgenbeck',
                'name_pt': 'Galgenbeck',
                'description': 'A sprawling metropolis built atop the bones of countless civilizations. Its infamous Hanging Gardens sway with the corpses of the condemned, and the air is thick with the scent of rot and incense. The city is ruled by a secretive council, and its labyrinthine sewers are said to house ancient, unspeakable horrors.',
                'description_pt': 'Uma metrópole vasta construída sobre os ossos de civilizações esquecidas. Os infames Jardins dos Enforcados balançam com os corpos dos condenados, e o ar é denso com cheiro de podridão e incenso. A cidade é governada por um conselho secreto, e seus esgotos labirínticos abrigam horrores antigos e indizíveis.',
                'population': '1000+',
                'terrain': 'plains',
                'region': 'central',
                'coordinates': (15, 13),
                'notable_features': [
                    'Hanging Gardens of Corpses',
                    'Secretive ruling council',
                    'Labyrinthine sewers',
                    'Ancient, forbidden catacombs',
                    'Schleswig district with demon infestation',
                    'Ministry of Wealth & Taxes extracting souls as currency',
                    'Office of the Holy Inquisition (ruined)',
                    'Cursed Heptaliths throughout the city',
                    'City (Bone) Mill grinding bones to flour'
                ],
                'notable_features_pt': [
                    'Jardins dos Enforcados',
                    'Conselho governante secreto',
                    'Esgotos labirínticos',
                    'Catacumbas antigas e proibidas',
                    'Distrito de Schleswig com infestação demoníaca',
                    'Ministério da Riqueza e Impostos extraindo almas como moeda',
                    'Escritório da Santa Inquisição (em ruínas)',
                    'Heptalitos Amaldiçoados por toda a cidade',
                    'Moinho da Cidade (de Ossos) moendo ossos em farinha'
                ],
                'key_npcs': ['Josilfa Migol', 'The Galgenbeck Council'],
                'atmosphere': 'Urban decay, perpetual twilight, and the ever-present threat of betrayal.',
                'atmosphere_pt': 'Decadência urbana, crepúsculo perpétuo e a ameaça constante de traição.'
            },
            'allians': {
                'name': 'Allians',
                'name_pt': 'Allians',
                'description': 'An isolated city of scholars and mystics, Allians is built around a crumbling library said to contain the last true histories of the world. The city is shrouded in secrecy, and its towers are lit by ghostly blue flames.',
                'description_pt': 'Uma cidade isolada de eruditos e mistérios, Allians é construída em torno de uma biblioteca ruína dizendo conter as verdadeiras histórias finais do mundo. A cidade está envolta em segredo, e seus torres são iluminados por chamas azuis fantasmas.',
                'population': '500',
                'terrain': 'plains',
                'region': 'east',
                'coordinates': (5, 7),
                'notable_features': [
                    'Crumbling library of forbidden knowledge',
                    'Blue-flamed towers',
                    'Secretive scholar-council',
                    'Occult rituals at midnight'
                ],
                'notable_features_pt': [
                    'Biblioteca ruína de conhecimento proibido',
                    'Torres de chamas azuis',
                    'Conselho secreto de eruditos',
                    'Ritos ocultos à meia-noite'
                ],
                'key_npcs': ['The Archivist', 'Mistress of Tomes'],
                'atmosphere': 'Scholarly, secretive, and haunted by knowledge.',
                'atmosphere_pt': 'Erudito, secreto e assombrado pelo conhecimento.'
            },
            'kergus': {
                'name': 'Kergus',
                'name_pt': 'Kergus',
                'description': 'A farming community plagued by unnatural weather and stranger livestock. Stone circles dot the fields, and the locals speak of things that move beneath the earth.',
                'description_pt': 'Uma comunidade agrícola atormentada por tempo e animais estranhos. Círculos de pedra adornam os campos, e os locais falam de coisas que se movem sob a terra.',
                'population': '800',
                'terrain': 'plains',
                'region': 'south',
                'coordinates': (7, 8),
                'notable_features': [
                    'Twisted livestock',
                    'Stone circles',
                    'Weather-warped fields',
                    'Subterranean rumblings'
                ],
                'notable_features_pt': [
                    'Livestock torto',
                    'Círculos de pedra',
                    'Campos distorcidos pelo tempo',
                    'Rumores subterrâneos'
                ],
                'key_npcs': ['Cattle Baron', 'Weather Seer'],
                'atmosphere': 'Bleak, windswept, and tinged with dread.',
                'atmosphere_pt': 'Desolado, ventoso e tingido com medo.'
            },
            'sarkash': {
                'name': 'Sarkash Forest Settlement',
                'name_pt': 'Sarkash Assentamento Florestal',
                'description': 'Hidden high in the ancient trees, this settlement is protected by powerful ward stones and the enigmatic Forest Witches. The woods below are thick with curses, and the wind carries whispers of old magic.',
                'description_pt': 'Oculto em cima das árvores antigas, este assentamento é protegido por pedras de guarda poderosas e as Bruxas da Floresta enigmáticas. Os bosques abaixo estão cheios de maldições, e o vento carrega susurros de antigas magias.',
                'population': '120',
                'terrain': 'forest',
                'region': 'northwest',
                'coordinates': (9, 8),
                'notable_features': [
                    'Ward stones',
                    'Forest Witch coven',
                    'Cursed glades',
                    'Living trees'
                ],
                'notable_features_pt': [
                    'Pedras de guarda',
                    'Covens de Bruxa da Floresta',
                    'Glades amaldiçoadas',
                    'Árvores vivas'
                ],
                'key_npcs': ['Forest Witch', 'Tree Warden'],
                'atmosphere': 'Gloomy, tangled, and alive with secrets.',
                'atmosphere_pt': 'Sombrio, confuso e repleto de segredos.'
            },
            'graven_tosk': {
                'name': 'Graven-Tosk',
                'name_pt': 'Graven-Tosk',
                'description': 'A city of graveyards and necromancers, Graven-Tosk is a place where the living and the dead intermingle. Bone fields stretch to the horizon, and the air is thick with the scent of incense and decay.',
                'description_pt': 'Uma cidade de cemitérios e necromantes, Graven-Tosk é um lugar onde os vivos e os mortos se misturam. Campos de ossos se extendem até o horizonte, e o ar é denso com cheiro de incenso e podridão.',
                'population': '300',
                'terrain': 'swamp',
                'region': 'west',
                'coordinates': (19, 8),
                'notable_features': [
                    'Endless graveyards',
                    'Necromancer guilds',
                    'Bone fields',
                    'Funeral processions at all hours'
                ],
                'notable_features_pt': [
                    'Cemitérios infinitos',
                    'Guildas de Necromante',
                    'Campos de ossos',
                    'Processões funerárias 24 horas'
                ],
                'key_npcs': ['Bone Priest', 'Gravekeeper'],
                'atmosphere': 'Somber, funereal, and thick with the presence of the dead.',
                'atmosphere_pt': 'Sombrio, funerário e repleto da presença dos mortos.'
            },
            'tveland': {
                'name': 'Tveland Outpost',
                'name_pt': 'Faro de Tveland',
                'description': 'A battered outpost on the edge of the known world, Tveland is a haven for exiles, traders, and those fleeing darker things. Its watchtowers are always manned, and the horizon is a line of perpetual storms.',
                'description_pt': 'Um farol abandonado na beira do mundo conhecido, Tveland é um refúgio para exilados, comerciantes e aqueles que fogem coisas mais sombrias. Suas torres de vigia estão sempre patrulhadas, e o horizonte é uma linha de tempestades eternas.',
                'population': '200',
                'terrain': 'plains',
                'region': 'east',
                'coordinates': (21, 7),
                'notable_features': [
                    'Storm-wracked horizon',
                    'Nomad trading post',
                    'Exile camps',
                    'Perpetual watchtowers'
                ],
                'notable_features_pt': [
                    'Horizonte furibundo',
                    'Posto de comércio de nômades',
                    'Acampamentos de exilados',
                    'Torres de vigia perpétuas'
                ],
                'key_npcs': ['Captain of the Watch', 'Nomad Trader'],
                'atmosphere': 'Windswept, tense, and haunted by the unknown.',
                'atmosphere_pt': 'Ventoso, tenso e assombrado pelo desconhecido.'
            },
            'grift': {
                'name': 'Grift',
                'name_pt': 'Grift',
                'description': 'A city of pilgrimage and ruins, Grift is known for its crumbling temples and the endless procession of the faithful seeking absolution. The city is a crossroads for all manner of travelers.',
                'description_pt': 'Uma cidade de peregrinação e ruínas, Grift é conhecida por seus templos ruídos e a procissão interminável dos fiéis buscando absolvição. A cidade é um cruzamento para todos os tipos de viajantes.',
                'population': '600',
                'terrain': 'plains',
                'region': 'south',
                'coordinates': (23, 13),
                'notable_features': [
                    'Crumbling temples',
                    'Pilgrim camps',
                    'Sacred crossroads',
                    'Relic markets'
                ],
                'notable_features_pt': [
                    'Templos ruídos',
                    'Acampamentos de peregrinos',
                    'Cruzamento sagrado',
                    'Mercados de relicas'
                ],
                'key_npcs': ['High Pilgrim', 'Relic Seller'],
                'atmosphere': 'Sacred, bustling, and filled with desperate hope.',
                'atmosphere_pt': 'Sagrado, agitado e repleto de esperança desesperada.'
            },
            'schleswig': {
                'name': 'Schleswig',
                'name_pt': 'Schleswig',
                'description': 'A battered fishing town on the storm-lashed coast. Schleswig is isolated, its people hard and suspicious. The sea brings both bounty and terror.',
                'description_pt': 'Uma cidade de pescaria atormentada pelas tempestades, Schleswig é isolada, seus habitantes são duros e suspeitos. O mar traz tanto abundância quanto terror.',
                'population': '350',
                'terrain': 'coast',
                'region': 'west',
                'coordinates': (10, 17),
                'notable_features': [
                    'Storm-battered docks',
                    'Salt-stained houses',
                    'Sea-worn shrines',
                    'Fishermen who never speak'
                ],
                'notable_features_pt': [
                    'Doca furibunda',
                    'Casas manchadas de sal',
                    'Símbolos marinhos desgastados',
                    'Pescadores que nunca falam'
                ],
                'key_npcs': ['Harbormaster', 'Old Fisher'],
                'atmosphere': 'Salt-stained, ruined, and desperate.',
                'atmosphere_pt': 'Manchado de sal, ruído e desesperado.'
            },
            'wastland': {
                'name': 'Wästland',
                'name_pt': 'Wästland',
                'description': 'A ruined city in the endless desert, Wästland is a place of scavengers and lost secrets. Sand-choked streets hide treasures and dangers in equal measure.',
                'description_pt': 'Uma cidade ruína no deserto interminável, Wästland é um lugar de esmagadores e segredos perdidos. Ruas encharcadas de areia escondem tesouros e perigos em igual medida.',
                'population': '100',
                'terrain': 'desert',
                'region': 'east',
                'coordinates': (12, 21),
                'notable_features': [
                    'Sand-choked ruins',
                    'Scavenger camps',
                    'Ancient obelisks',
                    'Mirage-haunted streets'
                ],
                'notable_features_pt': [
                    'Ruas encharcadas de areia',
                    'Acampamentos de esmagadores',
                    'Obeliscos antigos',
                    'Ruas fantasmadas pelo mirage'
                ],
                'key_npcs': ['Sand Prophet', 'Scavenger King'],
                'atmosphere': 'Harsh, windswept, and mysterious.',
                'atmosphere_pt': 'Severo, ventoso e misterioso.'
            },
            'bergen_chrypt': {
                'name': 'Bergen Chrypt',
                'name_pt': 'Bergen Chrypt',
                'description': 'Carved into the heart of a glacier, Bergen Chrypt is a fortress-city where the living and the dead walk side by side. The crypts beneath the city stretch for miles, and the nobility are rumored to be centuries old.',
                'description_pt': 'Gravado no coração de um glaciar, Bergen Chrypt é uma cidade-fortaleza onde os vivos e os mortos andam lado a lado. Os cripts sob a cidade se extendem por milhas, e a nobreza é rumada como sendo séculos de idade.',
                'population': '400',
                'terrain': 'mountain',
                'region': 'north',
                'coordinates': (15, 7),
                'notable_features': [
                    'Glacier-carved fortress',
                    'Endless crypts',
                    'Undead nobility',
                    'Frozen battlements'
                ],
                'notable_features_pt': [
                    'Fortaleza esculpida em gelo',
                    'Cripts infinitos',
                    'Nobreza inumana',
                    'Batalhões congelados'
                ],
                'key_npcs': ['Crypt Lord', 'Bergen Warden'],
                'atmosphere': 'Bitter cold, echoing silence, and the oppressive weight of the past.',
                'atmosphere_pt': 'Frio amargo, silêncio ecoante e o peso opressor do passado.'
            },
            'valley_of_unfortunate_undead': {
                'name': 'Valley of Unfortunate Undead',
                'name_pt': 'Vale dos Mortos Infelizes',
                'description': 'A vast valley filled with mass graves and restless spirits. The ground is always soft, and the air is thick with the moans of the dead.',
                'description_pt': 'Um vale vasto preenchido com túmulos de massa e espíritos inquietos. O chão é sempre mole, e o ar é denso com os gemidos dos mortos.',
                'population': '0',
                'terrain': 'plains',
                'region': 'central',
                'coordinates': (8, 14),
                'notable_features': [
                    'Mass graves',
                    'Restless spirits',
                    'Bone-choked river',
                    'Eternal fog'
                ],
                'notable_features_pt': [
                    'Túmulos de massa',
                    'Espíritos inquietos',
                    'Rio encharcado de ossos',
                    'Névoa eterna'
                ],
                'key_npcs': ['The Mourner', 'Bone Whisperer'],
                'atmosphere': 'Sorrowful, mist-shrouded, and haunted.',
                'atmosphere_pt': 'Sorroso, nublado e assombrado.'
            },
            'ucalegon': {
                'name': 'Ucalegon',
                'name_pt': 'Ucalegon',
                'description': 'The Lost Kingdom of Ucalegon. Placeholder description.',
                'description_pt': 'O Reino Perdido de Ucalegon. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'mountain',
                'region': 'southwest',
                'coordinates': (4, 23),
                'notable_features': ['Ruins', 'Black salt peaks'],
                'notable_features_pt': ['Ruínas', 'Picos de sal preto'],
                'key_npcs': [],
                'atmosphere': 'Ruined, lost, and mysterious.',
                'atmosphere_pt': 'Ruína, perdida e misteriosa.'
            },
            'sanalassio': {
                'name': 'Sanalassio',
                'name_pt': 'Sanalassio',
                'description': 'The Ruins of Sanalassio. Placeholder description.',
                'description_pt': 'As Ruínas de Sanalassio. Descrição de placeholder.',
                'population': '0',
                'terrain': 'mountain',
                'region': 'southwest',
                'coordinates': (7, 22),
                'notable_features': ['Ruins'],
                'notable_features_pt': ['Ruínas'],
                'key_npcs': [],
                'atmosphere': 'Ruined and ancient.',
                'atmosphere_pt': 'Ruína e antiga.'
            },
            'ligure': {
                'name': 'Ligure',
                'name_pt': 'Ligure',
                'description': 'The Ruins of Ligure. Placeholder description.',
                'description_pt': 'As Ruínas de Ligure. Descrição de placeholder.',
                'population': '0',
                'terrain': 'island',
                'region': 'southwest',
                'coordinates': (2, 23),
                'notable_features': ['Island of Sages'],
                'notable_features_pt': ['Ilha dos Sagos'],
                'key_npcs': [],
                'atmosphere': 'Isolated and wise.',
                'atmosphere_pt': 'Isolado e sábio.'
            },
            'aurilliac': {
                'name': 'Aurilliac',
                'name_pt': 'Aurilliac',
                'description': 'Aurilliac. Placeholder description.',
                'description_pt': 'Aurilliac. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'northwest',
                'coordinates': (8, 7),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'brackenfurt': {
                'name': 'Brackenfurt',
                'name_pt': 'Brackenfurt',
                'description': 'Brackenfurt. Placeholder description.',
                'description_pt': 'Brackenfurt. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'north',
                'coordinates': (15, 7),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'norvarad': {
                'name': 'Norvarad',
                'name_pt': 'Norvarad',
                'description': 'The Ruins of Norvarad. Placeholder description.',
                'description_pt': 'As Ruínas de Norvarad. Descrição de placeholder.',
                'population': '0',
                'terrain': 'ruins',
                'region': 'northeast',
                'coordinates': (23, 7),
                'notable_features': ['Ruins'],
                'notable_features_pt': ['Ruínas'],
                'key_npcs': [],
                'atmosphere': 'Ruined and ancient.',
                'atmosphere_pt': 'Ruína e antiga.'
            },
            'jericho_asylum': {
                'name': 'Jericho Asylum',
                'name_pt': 'Asilo de Jericho',
                'description': 'Jericho Asylum. Placeholder description.',
                'description_pt': 'Asilo de Jericho. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'asylum',
                'region': 'east',
                'coordinates': (25, 10),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Madness and isolation.',
                'atmosphere_pt': 'Loucura e isolamento.'
            },
            'verisaille': {
                'name': 'Verisaille',
                'name_pt': 'Verisaille',
                'description': 'Verisaille. Placeholder description.',
                'description_pt': 'Verisaille. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'southeast',
                'coordinates': (25, 17),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'merodville': {
                'name': 'Merodville',
                'name_pt': 'Merodville',
                'description': 'The Eastern Kingdom of Merodville. Placeholder description.',
                'description_pt': 'O Reino Oriental de Merodville. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'southeast',
                'coordinates': (23, 21),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'severing': {
                'name': 'Severing',
                'name_pt': 'Severing',
                'description': 'The Barony of Severing. Placeholder description.',
                'description_pt': 'A Baronia de Severing. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'south',
                'coordinates': (18, 23),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'ferrox': {
                'name': 'Ferrox',
                'name_pt': 'Ferrox',
                'description': 'Ferrox. Placeholder description.',
                'description_pt': 'Ferrox. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'south',
                'coordinates': (24, 23),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'issiore': {
                'name': 'Issiore',
                'name_pt': 'Issiore',
                'description': 'Issiore. Placeholder description.',
                'description_pt': 'Issiore. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'west',
                'coordinates': (7, 13),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'lanciano': {
                'name': 'Lanciano',
                'name_pt': 'Lanciano',
                'description': 'Lanciano. Placeholder description.',
                'description_pt': 'Lanciano. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'plains',
                'region': 'west',
                'coordinates': (4, 15),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'saltcrest_hills': {
                'name': 'Saltcrest Hills',
                'name_pt': 'Colinas de Salcrest',
                'description': 'Saltcrest Hills. Placeholder description.',
                'description_pt': 'Colinas de Salcrest. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'hills',
                'region': 'east',
                'coordinates': (20, 14),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'borrow_hills': {
                'name': 'Borrow Hills',
                'name_pt': 'Colinas de Empréstimo',
                'description': 'Borrow Hills. Placeholder description.',
                'description_pt': 'Colinas de Empréstimo. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'hills',
                'region': 'east',
                'coordinates': (22, 16),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            },
            'dalmore_mountains': {
                'name': 'Dalmore Mountains',
                'name_pt': 'Montanhas de Dalmore',
                'description': 'Dalmore Mountains. Placeholder description.',
                'description_pt': 'Montanhas de Dalmore. Descrição de placeholder.',
                'population': 'unknown',
                'terrain': 'mountain',
                'region': 'east',
                'coordinates': (24, 13),
                'notable_features': [],
                'notable_features_pt': [],
                'key_npcs': [],
                'atmosphere': 'Unknown.',
                'atmosphere_pt': 'Desconhecido.'
            }
        }
    
    def _init_factions(self) -> Dict:
        """Initialize major factions from Mörk Borg lore."""
        return {
            'heretical_priests': {
                'name': 'Heretical Priests',
                'name_pt': 'Sacerdotes Heréticos',
                'description': 'Corrupt clergy serving dark gods',
                'description_pt': 'Clero corrupto servindo deuses sombrios',
                'regions': ['central', 'north'],
                'influence': 'religious',
                'goals': ['Spread corruption', 'Serve Nechrubel', 'Corrupt the faithful']
            },
            
            'nechrubel_cult': {
                'name': 'Cult of Nechrubel',
                'name_pt': 'Culto de Nechrubel',
                'description': 'Apocalyptic cult serving the Doomsday deity',
                'description_pt': 'Culto apocalíptico servindo a divindade do Fim dos Tempos',
                'regions': ['all'],
                'influence': 'apocalyptic',
                'goals': ['Hasten the apocalypse', 'Sacrifice the innocent', 'Spread doom']
            },
            
            'shadow_king_followers': {
                'name': 'Followers of the Shadow King',
                'name_pt': 'Seguidores do Rei das Sombras',
                'description': 'Servants of the mysterious Shadow King',
                'description_pt': 'Servos do misterioso Rei das Sombras',
                'regions': ['north', 'underground'],
                'influence': 'political',
                'goals': ['Restore the Shadow King', 'Control from shadows', 'Ancient knowledge']
            },
            
            'plague_bearers': {
                'name': 'Plague Bearers',
                'name_pt': 'Portadores da Peste',
                'description': 'Diseased cultists spreading contagion',
                'description_pt': 'Cultistas doentes espalhando contágio',
                'regions': ['west', 'swamp'],
                'influence': 'biological',
                'goals': ['Spread disease', 'Corrupt the living', 'Serve decay']
            },
            
            'forest_witches': {
                'name': 'Forest Witches of Sarkash',
                'name_pt': 'Bruxas da Floresta de Sarkash',
                'description': 'Ancient witches maintaining forest magic',
                'description_pt': 'Bruxas antigas mantendo a magia da floresta',
                'regions': ['northwest', 'forest'],
                'influence': 'magical',
                'goals': ['Protect ancient secrets', 'Maintain balance', 'Forest preservation']
            },
            
            # From Christian's "Death and Taxes"
            'eager_day_laborers': {
                'name': 'Guild of the Utmost Eager Day Laborers',
                'name_pt': 'Guilda dos Trabalhadores Diários Extremamente Ansiosos',
                'description': 'Desperate workers seeking any employment in Galgenbeck',
                'description_pt': 'Trabalhadores desesperados procurando qualquer emprego em Galgenbeck',
                'regions': ['central'],
                'influence': 'economic',
                'goals': ['Find work', 'Survive poverty', 'Serve the wealthy']
            },
            
            'binding_contracts': {
                'name': 'House of Binding Contracts',
                'name_pt': 'Casa dos Contratos Vinculativos',
                'description': 'Soul traders and contract devils operating in Galgenbeck',
                'description_pt': 'Comerciantes de almas e demônios contratantes operando em Galgenbeck',
                'regions': ['central'],
                'influence': 'infernal',
                'goals': ['Acquire souls', 'Enforce contracts', 'Spread corruption']
            },
            
            'golden_tongue': {
                'name': 'Cult of the Golden Tongue',
                'name_pt': 'Culto da Língua Dourada',
                'description': 'Secret cult obsessed with wealth and golden words',
                'description_pt': 'Culto secreto obcecado com riqueza e palavras douradas',
                'regions': ['central'],
                'influence': 'religious',
                'goals': ['Hoard gold', 'Speak persuasively', 'Corrupt through greed']
            },
            
            # From Christian's "Bergen Chrypt: Archfrost"
            'corpse_golem_cults': {
                'name': 'Corpse Golem Cults',
                'name_pt': 'Cultos dos Golems de Cadáver',
                'description': 'Necromantic cults creating undead servants in the mountains',
                'description_pt': 'Cultos necromânticos criando servos mortos-vivos nas montanhas',
                'regions': ['north', 'northwest'],
                'influence': 'necromantic',
                'goals': ['Raise corpse golems', 'Seek immortality', 'Control the dead']
            }
        }
    
    def _init_notable_npcs(self) -> Dict:
        """Initialize notable NPCs from Mörk Borg lore."""
        return {
            'josilfa_migol': {
                'name': 'Josilfa Migol',
                'name_pt': 'Josilfa Migol',
                'title': 'The Harvester of Galgenbeck',
                'title_pt': 'A Ceifadora de Galgenbeck',
                'location': 'galgenbeck',
                'description': 'Mysterious figure harvesting citizens for sacrifice',
                'description_pt': 'Figura misteriosa ceifando cidadãos para sacrifício',
                'faction': 'nechrubel_cult',
                'threat_level': 'extreme',
                'abilities': ['Memory erasure', 'Ritual sacrifice', 'Comet summoning']
            },
            
            'shadow_king': {
                'name': 'The Shadow King',
                'name_pt': 'O Rei das Sombras',
                'title': 'Ruler of Hidden Realms',
                'title_pt': 'Governante dos Reinos Ocultos',
                'location': 'unknown',
                'description': 'Ancient ruler seeking return to power',
                'description_pt': 'Governante antigo buscando retornar ao poder',
                'faction': 'shadow_king_followers',
                'threat_level': 'legendary',
                'abilities': ['Shadow manipulation', 'Ancient knowledge', 'Undead command']
            },
            
            'nechrubel': {
                'name': 'Nechrubel',
                'name_pt': 'Nechrubel',
                'title': 'The Destroyer',
                'title_pt': 'O Destruidor',
                'location': 'celestial',
                'description': 'Apocalyptic deity bringing the end times',
                'description_pt': 'Divindade apocalíptica trazendo o fim dos tempos',
                'faction': 'nechrubel_cult',
                'threat_level': 'divine',
                'abilities': ['World destruction', 'Plague creation', 'Time manipulation']
            }
        }
    
    def _init_regional_lore(self) -> Dict:
        """Initialize regional lore and biases."""
        return {
            'north': {
                'themes': ['Ancient tombs', 'Undead nobility', 'Frozen wastes', 'Mountain fortresses'],
                'common_encounters': ['Undead warriors', 'Ice wraiths', 'Ancient spirits'],
                'terrain_bias': {'mountain': 0.6, 'forest': 0.2, 'plains': 0.2},
                'atmosphere': 'Ancient burial grounds and frozen peaks',
                'atmosphere_pt': 'Sepulturas antigas e picos congelados'
            },
            
            'central': {
                'themes': ['Urban decay', 'Political intrigue', 'Ancient ruins', 'Trade routes'],
                'common_encounters': ['Corrupt officials', 'Plague victims', 'Heretical priests'],
                'terrain_bias': {'plains': 0.7, 'forest': 0.2, 'mountain': 0.1},
                'atmosphere': 'Decaying civilization and political corruption',
                'atmosphere_pt': 'Civilização decadente e corrupção política'
            },
            
            'south': {
                'themes': ['Pastoral horror', 'Weird weather', 'Ancient stones', 'Diseased livestock'],
                'common_encounters': ['Mutant animals', 'Weather cults', 'Plague farmers'],
                'terrain_bias': {'plains': 0.6, 'swamp': 0.3, 'forest': 0.1},
                'atmosphere': 'Agricultural nightmare and weather madness',
                'atmosphere_pt': 'Pesadelo agrícola e loucura do tempo'
            },
            
            'west': {
                'themes': ['Coastal storms', 'Plague cities', 'Trade collapse', 'Isolated settlements'],
                'common_encounters': ['Plague bearers', 'Storm cultists', 'Desperate survivors'],
                'terrain_bias': {'coast': 0.5, 'swamp': 0.3, 'plains': 0.2},
                'atmosphere': 'Coastal decay and plague-ridden ports',
                'atmosphere_pt': 'Decadência costeira e portos atormentados pela peste'
            },
            
            'east': {
                'themes': ['Frontier outposts', 'Nomadic traders', 'Ancient mysteries', 'Wasteland'],
                'common_encounters': ['Nomad warriors', 'Desert spirits', 'Treasure hunters'],
                'terrain_bias': {'plains': 0.5, 'mountain': 0.3, 'forest': 0.2},
                'atmosphere': 'Frontier wilderness and nomadic culture',
                'atmosphere_pt': 'Floresta fronteiriça e cultura nômade'
            },
            
            'northwest': {
                'themes': ['Dark forests', 'Witch covens', 'Ancient magic', 'Cursed woods'],
                'common_encounters': ['Forest witches', 'Cursed animals', 'Tree spirits'],
                'terrain_bias': {'forest': 0.8, 'swamp': 0.1, 'mountain': 0.1},
                'atmosphere': 'Dark magic and primordial forests',
                'atmosphere_pt': 'Magia escura e florestas primitivas'
            }
        }
    
    def _init_hardcoded_hexes(self) -> Dict:
        """Initialize specific hex locations that should be hardcoded."""
        hardcoded = {}
        
        # Place major cities
        for city_key, city_data in self.major_cities.items():
            x, y = city_data['coordinates']
            hex_code = f"{x:02d}{y:02d}"
            
            hardcoded[hex_code] = {
                'type': 'major_city',
                'city_key': city_key,
                'terrain': city_data['terrain'],
                'name': city_data['name'],
                'description': city_data['description'],
                'population': city_data['population'],
                'notable_features': city_data['notable_features'],
                'key_npcs': city_data['key_npcs'],
                'atmosphere': city_data['atmosphere'],
                'locked': True  # Cannot be overridden by random generation
            }
        
        # Add special locations
        hardcoded['1012'] = {
            'type': 'special_location',
            'name': 'The Bone Temple',
            'name_pt': 'O Templo dos Ossos',
            'terrain': 'mountain',
            'description': 'Ancient temple built from the bones of titans',
            'description_pt': 'Templo antigo construído com ossos de titãs',
            'atmosphere': 'Ancient worship and bone architecture',
            'locked': True
        }
        
        hardcoded['0614'] = {
            'type': 'special_location',
            'name': 'The Weeping Lake',
            'name_pt': 'O Lago Chorão',
            'terrain': 'swamp',
            'description': 'Cursed lake that weeps tears of the damned',
            'description_pt': 'Lago amaldiçoado que chora lágrimas dos condenados',
            'atmosphere': 'Cursed waters and eternal sorrow',
            'locked': True
        }
        
        # Add Bergen Chrypt from Christian's supplement
        hardcoded['0408'] = {
            'type': 'special_location',
            'name': 'Bergen Chrypt',
            'name_pt': 'Bergen Chrypt',
            'terrain': 'mountain',
            'description': 'The most haunted mountain range of the dying lands',
            'description_pt': 'A cordilheira mais assombrada das terras moribundas',
            'atmosphere': 'Dark desolation, rifts of unknown make, occult channelers',
            'features': [
                'Corpse golem cults',
                'Unctuous secrets buried in ice',
                'Rifts of unknown origin',
                'Occult channelers seeking the Elixir of Life',
                'Infectious rash upon the skin of the earth'
            ],
            'locked': True
        }
        
        return hardcoded
    
    def get_regional_bias(self, x: int, y: int) -> str:
        """Get regional classification for coordinates."""
        # Determine region based on coordinates
        if y <= 10:  # Northern regions
            if x <= 10:
                return 'northwest'
            else:
                return 'north'
        elif y >= 20:  # Southern regions
            return 'south'
        elif x <= 8:  # Western regions
            return 'west'
        elif x >= 18:  # Eastern regions
            return 'east'
        else:  # Central regions
            return 'central'
    
    def get_hardcoded_hex(self, hex_code: str) -> Optional[Dict]:
        """Get hardcoded information for a specific hex."""
        return self.hardcoded_hexes.get(hex_code)
    
    def get_city_by_location(self, x: int, y: int) -> Optional[Dict]:
        """Get city information by coordinates."""
        hex_code = f"{x:02d}{y:02d}"
        hardcoded = self.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('type') == 'major_city':
            city_key = hardcoded['city_key']
            return self.major_cities[city_key]
        return None
    
    def get_regional_npcs(self, region: str) -> List[str]:
        """Get NPCs commonly found in a region."""
        regional_npcs = {
            'north': [
                'Undead Knight', 'Ice Witch', 'Frost Giant', 'Tomb Guardian',
                # From Christian's supplements
                'Corpse Golem Cultist', 'Occult Channeler', 'Bergen Chrypt Explorer'
            ],
            'central': [
                'Corrupt Merchant', 'Heretical Priest', 'City Guard', 'Plague Doctor', 
                # From Christian's supplements
                'Desperate Tax Collector', 'Eager Day Laborer', 'Soul Contract Negotiator',
                'Sacrifice Heretic', 'Golden Tongue Preacher', 'Memory Eraser', 'Bone Mill Worker'
            ],
            'south': [
                'Weather Seer', 'Cattle Baron', 'Plague Farmer', 'Stone Circle Keeper',
                # From Christian's supplements
                'Traveling Tax Collector', 'Contract Devil'
            ],
            'west': [
                'Storm Caller', 'Plague Bearer', 'Desperate Survivor', 'Coastal Raider',
                # From Christian's supplements
                'Sea Demon', 'Drowned Soul Trader'
            ],
            'east': [
                'Nomad Warrior', 'Caravan Master', 'Desert Oracle', 'Treasure Hunter',
                # From Christian's supplements
                'Corpse Golem Hunter', 'Occult Artifact Seeker'
            ],
            'northwest': [
                'Forest Witch', 'Tree Warden', 'Cursed Druid', 'Beast Speaker',
                # From Christian's supplements
                'Corpse Golem Cultist', 'Mountain Occult Channeler'
            ]
        }
        return regional_npcs.get(region, ['Wandering Scavenger', 'Plague Victim', 'Mad Hermit'])
    
    def get_regional_factions(self, region: str) -> List[str]:
        """Get factions active in a region."""
        region_factions = {
            'north': ['shadow_king_followers', 'heretical_priests'],
            'central': ['nechrubel_cult', 'heretical_priests'],
            'south': ['plague_bearers', 'nechrubel_cult'],
            'west': ['plague_bearers'],
            'east': ['nechrubel_cult'],
            'northwest': ['forest_witches']
        }
        return region_factions.get(region, ['nechrubel_cult'])

def main():
    """Test the lore database."""
    lore_db = MorkBorgLoreDatabase()
    
    print("🏰 MÖRK BORG LORE DATABASE")
    print("=" * 40)
    
    print(f"\n📍 Major Cities: {len(lore_db.major_cities)}")
    for city_key, city in lore_db.major_cities.items():
        x, y = city['coordinates']
        print(f"  {city['name']} ({x:02d},{y:02d}) - {city['terrain']}")
    
    print(f"\n⚔️ Factions: {len(lore_db.factions)}")
    for faction_key, faction in lore_db.factions.items():
        print(f"  {faction['name']} - {faction['influence']}")
    
    print(f"\n🌍 Regional Biases:")
    for region, data in lore_db.regional_lore.items():
        print(f"  {region}: {data['themes'][:2]}...")

if __name__ == "__main__":
    main() 