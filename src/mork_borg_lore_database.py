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
                'description': 'City built upon ancient ruins and corpses',
                'description_pt': 'Cidade construída sobre ruínas antigas e cadáveres',
                'population': '501-1000',
                'terrain': 'plains',
                'region': 'central',
                'coordinates': (12, 15),  # Central location
                'notable_features': [
                    'Built on layers of previous cities',
                    'Ruled by mysterious council',
                    'Famous for its hanging gardens of corpses',
                    'Underground sewers with ancient horrors',
                    'Ministry of Wealth & Taxes extracting souls as currency',
                    'Guild of the Utmost Eager Day Laborers seeking any work',
                    'House of Binding Contracts where devils broker deals',
                    'Daily mandatory festivals causing economic standstill',
                    'Demon infestation in government buildings',
                    'Silver coin shortage due to ravenous taxation',
                    'Cult of the Golden Tongue corrupting merchants',
                    'Heptaliths - seven cursed standing stones in the city center'
                ],
                'key_npcs': ['Josilfa Migol', 'The Galgenbeck Council', 'Tax Collectors', 'Contract Devils', 'Eager Day Laborers'],
                'atmosphere': 'Urban decay and ancient evil mixed with bureaucratic horror'
            },
            
            'bergen_chrypt': {
                'name': 'Bergen Chrypt',
                'name_pt': 'Bergen Cripta',
                'description': 'Ancient fortress-city in the northern wastes',
                'description_pt': 'Antiga cidade-fortaleza nas terras devastadas do norte',
                'population': '101-500',
                'terrain': 'mountain',
                'region': 'north',
                'coordinates': (8, 5),  # Northern mountains
                'notable_features': [
                    'Fortress built into mountain',
                    'Crypts extend deep underground',
                    'Ruled by undead nobility',
                    'Gateway to the Sarkash Forest'
                ],
                'key_npcs': ['The Crypt Lords', 'Bergen Wardens'],
                'atmosphere': 'Ancient fortress and undead nobility'
            },
            
            'sarkash': {
                'name': 'Sarkash Forest Settlement',
                'name_pt': 'Povoado da Floresta Sarkash',
                'description': 'Hidden settlement within the cursed forest',
                'description_pt': 'Povoado escondido na floresta amaldiçoada',
                'population': '51-100',
                'terrain': 'forest',
                'region': 'northwest',
                'coordinates': (5, 8),  # Northwest forests
                'notable_features': [
                    'Built in treetops for safety',
                    'Surrounded by cursed woods',
                    'Home to forest witches',
                    'Protected by ancient ward stones'
                ],
                'key_npcs': ['Forest Witches', 'Tree Wardens'],
                'atmosphere': 'Dark forest magic and ancient curses'
            },
            
            'tveland': {
                'name': 'Tveland Outpost',
                'name_pt': 'Posto Avançado de Tveland',
                'description': 'Fortified outpost on the eastern steppes',
                'description_pt': 'Posto fortificado nas estepes orientais',
                'population': '51-100',
                'terrain': 'plains',
                'region': 'east',
                'coordinates': (20, 12),  # Eastern plains
                'notable_features': [
                    'Last outpost before the wastes',
                    'Trading post for nomads',
                    'Watchtowers scan the horizon',
                    'Stockpiles weapons and supplies'
                ],
                'key_npcs': ['Captain of the Watch', 'Nomad Traders'],
                'atmosphere': 'Frontier outpost and nomadic traders'
            },
            
            'kergus': {
                'name': 'Kergus Plains Settlement',
                'name_pt': 'Povoado das Planícies de Kergus',
                'description': 'Pastoral settlement on the southern plains',
                'description_pt': 'Povoado pastoral nas planícies do sul',
                'population': '101-500',
                'terrain': 'plains',
                'region': 'south',
                'coordinates': (15, 25),  # Southern plains
                'notable_features': [
                    'Agricultural community',
                    'Herds of strange cattle',
                    'Ancient stone circles',
                    'Plagued by weird weather'
                ],
                'key_npcs': ['Cattle Barons', 'Weather Seers'],
                'atmosphere': 'Pastoral horror and strange livestock'
            },
            
            # Additional settlements from supplements
            'pyre_chrypt': {
                'name': 'Pyre-Chrypt',
                'name_pt': 'Pira-Cripta',
                'description': 'Dead plague city, walled and abandoned',
                'description_pt': 'Cidade morta pela peste, murada e abandonada',
                'population': '0 (abandoned)',
                'terrain': 'plains',
                'region': 'west',
                'coordinates': (6, 18),  # Western area
                'notable_features': [
                    'Completely abandoned due to plague',
                    'Walls sealed from outside',
                    'Treasures locked within',
                    'Source of plague in iron ziggurat'
                ],
                'key_npcs': ['Plague Spirits', 'The Last Survivor'],
                'atmosphere': 'Abandoned plague city and locked secrets'
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
            
            # NEW: Forgotten Gods Cults (from Ikhon supplement)
            'bilkherd_cult': {
                'name': 'Servants of the Bilkherd',
                'name_pt': 'Servos do Bilkherd',
                'description': 'Cattle herders and farmers serving the forgotten god of livestock',
                'description_pt': 'Criadores de gado e fazendeiros servindo o deus esquecido do gado',
                'regions': ['south', 'central', 'plains'],
                'influence': 'agricultural',
                'goals': ['Increase livestock yields', 'Perform cattle sacrifices', 'Spread pastoral corruption']
            },
            
            'becklure_cult': {
                'name': 'Drowned Servants of the Becklure',
                'name_pt': 'Servos Afogados do Becklure',
                'description': 'Fishermen and coastal dwellers serving the water deity',
                'description_pt': 'Pescadores e moradores costeiros servindo a divindade da água',
                'regions': ['coast', 'swamp'],
                'influence': 'maritime',
                'goals': ['Control waterways', 'Drown the unfaithful', 'Seek sunken treasures']
            },
            
            'old_dead_cult': {
                'name': 'Whisperers to the Old Dead',
                'name_pt': 'Sussurradores aos Mortos Antigos',
                'description': 'Necromancers and grave-robbers serving ancient corpses',
                'description_pt': 'Necromantes e saqueadores de túmulos servindo cadáveres antigos',
                'regions': ['north', 'mountain', 'underground'],
                'influence': 'necromantic',
                'goals': ['Commune with ancient dead', 'Gather lost knowledge', 'Raise forgotten armies']
            },
            
            'silkfiend_cult': {
                'name': 'Bound by the Silkfiend',
                'name_pt': 'Presos pelo Demônio da Seda',
                'description': 'Artists and craftsmen enslaved by the spider deity',
                'description_pt': 'Artistas e artesãos escravizados pela divindade aranha',
                'regions': ['central', 'urban'],
                'influence': 'artistic',
                'goals': ['Create cursed artworks', 'Weave fate itself', 'Trap souls in silk']
            },
            
            # NEW: Recent supplement factions
            'golden_tongue_cult': {
                'name': 'Cult of the Golden Tongue',
                'name_pt': 'Culto da Língua Dourada',
                'description': 'Merchants and tax collectors serving greed incarnate',
                'description_pt': 'Mercadores e cobradores de impostos servindo a ganância encarnada',
                'regions': ['central', 'urban'],
                'influence': 'economic',
                'goals': ['Accumulate wealth', 'Corrupt through greed', 'Control commerce']
            },
            
            'eager_day_laborers': {
                'name': 'Guild of the Utmost Eager Day Laborers',
                'name_pt': 'Guilda dos Mais Ansiosos Trabalhadores Diários',
                'description': 'Desperate workers performing any task for coin',
                'description_pt': 'Trabalhadores desesperados realizando qualquer tarefa por moedas',
                'regions': ['central', 'urban'],
                'influence': 'labor',
                'goals': ['Find work at any cost', 'Serve highest bidder', 'Survive another day']
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
                'atmosphere': 'Ancient burial grounds and frozen peaks'
            },
            
            'central': {
                'themes': ['Urban decay', 'Political intrigue', 'Ancient ruins', 'Trade routes'],
                'common_encounters': ['Corrupt officials', 'Plague victims', 'Heretical priests'],
                'terrain_bias': {'plains': 0.7, 'forest': 0.2, 'mountain': 0.1},
                'atmosphere': 'Decaying civilization and political corruption'
            },
            
            'south': {
                'themes': ['Pastoral horror', 'Weird weather', 'Ancient stones', 'Diseased livestock'],
                'common_encounters': ['Mutant animals', 'Weather cults', 'Plague farmers'],
                'terrain_bias': {'plains': 0.6, 'swamp': 0.3, 'forest': 0.1},
                'atmosphere': 'Agricultural nightmare and weather madness'
            },
            
            'west': {
                'themes': ['Coastal storms', 'Plague cities', 'Trade collapse', 'Isolated settlements'],
                'common_encounters': ['Plague bearers', 'Storm cultists', 'Desperate survivors'],
                'terrain_bias': {'coast': 0.5, 'swamp': 0.3, 'plains': 0.2},
                'atmosphere': 'Coastal decay and plague-ridden ports'
            },
            
            'east': {
                'themes': ['Frontier outposts', 'Nomadic traders', 'Ancient mysteries', 'Wasteland'],
                'common_encounters': ['Nomad warriors', 'Desert spirits', 'Treasure hunters'],
                'terrain_bias': {'plains': 0.5, 'mountain': 0.3, 'forest': 0.2},
                'atmosphere': 'Frontier wilderness and nomadic culture'
            },
            
            'northwest': {
                'themes': ['Dark forests', 'Witch covens', 'Ancient magic', 'Cursed woods'],
                'common_encounters': ['Forest witches', 'Cursed animals', 'Tree spirits'],
                'terrain_bias': {'forest': 0.8, 'swamp': 0.1, 'mountain': 0.1},
                'atmosphere': 'Dark magic and primordial forests'
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
        hardcoded['1010'] = {
            'type': 'special_location',
            'name': 'The Bone Temple',
            'name_pt': 'O Templo dos Ossos',
            'terrain': 'mountain',
            'description': 'Ancient temple built from the bones of titans',
            'description_pt': 'Templo antigo construído com ossos de titãs',
            'atmosphere': 'Ancient worship and bone architecture',
            'locked': True
        }
        
        hardcoded['0615'] = {
            'type': 'special_location',
            'name': 'The Weeping Lake',
            'name_pt': 'O Lago Chorão',
            'terrain': 'swamp',
            'description': 'Cursed lake that weeps tears of the damned',
            'description_pt': 'Lago amaldiçoado que chora lágrimas dos condenados',
            'atmosphere': 'Cursed waters and eternal sorrow',
            'locked': True
        }
        
        # NEW: Additional special locations from research
        hardcoded['0812'] = {
            'type': 'special_location',
            'name': 'The Weeping Stones',
            'name_pt': 'As Pedras Chorosas',
            'terrain': 'plains',
            'description': 'Ancient standing stones that bleed tears of the innocent',
            'description_pt': 'Pedras eretas antigas que sangram lágrimas dos inocentes',
            'atmosphere': 'Ancient sorrow and mystical power',
            'notable_features': ['Healing tears', 'Attracts undead at night', 'Prophetic visions'],
            'factions': ['nechrubel_cult', 'shadow_king_followers'],
            'locked': True
        }
        
        hardcoded['1820'] = {
            'type': 'special_location',
            'name': 'Plague Ship Graveyard',
            'name_pt': 'Cemitério de Navios da Peste',
            'terrain': 'coast',
            'description': 'Dozens of diseased vessels run aground on cursed shores',
            'description_pt': 'Dezenas de navios doentes encalhados em costas amaldiçoadas',
            'atmosphere': 'Maritime decay and disease',
            'notable_features': ['Valuable cargo among the dead', 'Plague zombies crew the ships', 'Storm spirits guard the wrecks'],
            'factions': ['plague_bearers', 'becklure_cult'],
            'locked': True
        }
        
        hardcoded['0409'] = {
            'type': 'special_location',
            'name': 'The Carnival of Sorrows',
            'name_pt': 'O Carnaval das Tristezas',
            'terrain': 'plains',  # Mobile, but needs a starting terrain
            'description': 'Cursed traveling carnival that appears without warning',
            'description_pt': 'Carnaval amaldiçoado viajante que aparece sem aviso',
            'atmosphere': 'False joy masking eternal torment',
            'notable_features': ['Moves every 1d4 weeks', 'Soul gambling games', 'Demonic performers'],
            'factions': ['silkfiend_cult', 'eager_day_laborers'],
            'special_properties': ['mobile_location', 'changes_hex_randomly'],
            'locked': True
        }
        
        hardcoded['2205'] = {
            'type': 'special_location',
            'name': 'The Bone Crown Barrows',
            'name_pt': 'Os Túmulos da Coroa Óssea',
            'terrain': 'mountain',
            'description': 'Ancient burial mounds of forgotten kings',
            'description_pt': 'Montículos funerários antigos de reis esquecidos',
            'atmosphere': 'Royal death and ancient majesty',
            'notable_features': ['Crowned skeletons that still rule', 'Treasures beyond imagining', 'Curse upon grave robbers'],
            'factions': ['old_dead_cult', 'shadow_king_followers'],
            'locked': True
        }
        
        hardcoded['1618'] = {
            'type': 'special_location',
            'name': 'The Ministry of Wealth & Taxes',
            'name_pt': 'O Ministério da Riqueza e Impostos',
            'terrain': 'plains',
            'description': 'Demon-infested government building extracting wealth from souls',
            'description_pt': 'Prédio governamental infestado de demônios extraindo riqueza das almas',
            'atmosphere': 'Bureaucratic horror and financial damnation',
            'notable_features': ['Devils in fine suits', 'Contracts written in blood', 'Vault of stolen souls'],
            'factions': ['golden_tongue_cult', 'eager_day_laborers'],
            'locked': True
        }
        
        hardcoded['0722'] = {
            'type': 'special_location',
            'name': 'The Quarantine Islands',
            'name_pt': 'As Ilhas de Quarentena',
            'terrain': 'coast',
            'description': 'Isolated islands where plague victims are abandoned',
            'description_pt': 'Ilhas isoladas onde vítimas da peste são abandonadas',
            'atmosphere': 'Abandonment and slow death',
            'notable_features': ['Desperate survivors', 'Mutated plague strains', 'Hidden rebel camps'],
            'factions': ['plague_bearers'],
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
                # NEW: Enhanced with forgotten gods and new content
                'Bone Crown Archaeologist', 'Old Dead Necromancer', 'Bergen Chrypt Warden',
                'Ancient King\'s Spirit', 'Frozen Plague Doctor', 'Crypt Robber'
            ],
            'central': [
                'Corrupt Merchant', 'Heretical Priest', 'City Guard', 'Plague Doctor',
                # NEW: Enhanced with Galgenbeck and tax content
                'Desperate Tax Collector', 'Soul Contract Negotiator', 'Eager Day Laborer',
                'Golden Tongue Merchant', 'Ministry Demon', 'Carnival Performer'
            ],
            'south': [
                'Weather Seer', 'Cattle Baron', 'Plague Farmer', 'Stone Circle Keeper',
                # NEW: Enhanced with Bilkherd cult content
                'Bilkherd Cattle Cultist', 'Infected Livestock Herder', 'Milk Shrine Keeper',
                'Sacrificial Cowhand', 'Pastoral Horror Priest', 'Diseased Ranch Owner'
            ],
            'west': [
                'Storm Caller', 'Plague Bearer', 'Desperate Survivor', 'Coastal Raider',
                # NEW: Enhanced with Becklure and coastal content
                'Drowned Fisherman', 'Quarantine Warden', 'Becklure Water Cultist',
                'Plague Ship Captain', 'Lighthouse Keeper', 'Storm Cult Sailor'
            ],
            'east': [
                'Nomad Warrior', 'Caravan Master', 'Desert Oracle', 'Treasure Hunter',
                # NEW: Enhanced with frontier content
                'Trade Route Guardian', 'Portal Seeker', 'Calendar Scholar',
                'Faction Scout', 'Wasteland Guide', 'Resource Flow Merchant'
            ],
            'northwest': [
                'Forest Witch', 'Tree Warden', 'Cursed Druid', 'Beast Speaker',
                # NEW: Enhanced with Silkfiend and forest content
                'Silkfiend Artist', 'Web-wrapped Hermit', 'Fate Weaver',
                'Silk-bound Prisoner', 'Tree-silk Harvester', 'Pattern Reader'
            ]
        }
        return regional_npcs.get(region, ['Wandering Survivor', 'Lost Soul', 'Desperate Scavenger'])
    
    def get_regional_factions(self, region: str) -> List[str]:
        """Get factions active in a region."""
        region_factions = {
            'north': ['shadow_king_followers', 'heretical_priests', 'old_dead_cult'],
            'central': ['nechrubel_cult', 'heretical_priests', 'golden_tongue_cult', 'eager_day_laborers'],
            'south': ['plague_bearers', 'nechrubel_cult', 'bilkherd_cult'],
            'west': ['plague_bearers', 'becklure_cult'],
            'east': ['nechrubel_cult'],
            'northwest': ['forest_witches', 'silkfiend_cult']
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