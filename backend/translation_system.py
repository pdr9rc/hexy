#!/usr/bin/env python3
"""
Unified Translation System for The Dying Lands
Handles all translation and localization functionality.
"""

from typing import Dict, Any, Optional, List

class TranslationSystem:
    """Unified translation system for The Dying Lands."""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translation data."""
        return {
            'en': {
                # UI Elements
                'hex_prompt': 'Enter hex code (XXYY format, e.g., 0601) or range (0601-0610): ',
                'terrain_prompt': 'Terrain type for this hex (mountain/forest/coast/plains/swamp): ',
                'invalid_hex': 'Invalid hex format. Using default range.',
                'files_generated': 'Files generated in \'dying_lands_output/\' directory:',
                'hex_files': 'hex files in hexes/',
                'overland_hex_map': 'The Dying Lands Hex Map',
                'hex_descriptions': 'Hex Descriptions',
                
                # Content Types
                'terrain': 'Terrain',
                'encounter': 'Encounter',
                'denizen': 'Denizen',
                'location': 'Location',
                'notable_feature': 'Notable Feature',
                'atmosphere': 'Atmosphere',
                'motivation': 'Motivation',
                'demeanor': 'Demeanor',
                
                # Generation Messages
                'generating_full_map': 'Generating Full Map',
                'map_size': 'Map Size',
                'language': 'Language',
                'generation_complete': 'Generation Complete',
                'creating_ascii_map': 'Creating ASCII Map',
                'generating_hex': 'Generating hex',
                'skipping_existing': 'Skipping existing hex',
                
                # Error Messages
                'error_loading_hex': 'ERROR LOADING HEX',
                'error_loading_city': 'ERROR LOADING CITY DETAILS',
                'error_loading_settlement': 'ERROR LOADING SETTLEMENT DETAILS',
                'error_generating_hex': 'ERROR GENERATING HEX CONTENT',
                'error_generating_map': 'ERROR GENERATING FULL MAP',
                'error_resetting_continent': 'ERROR RESETTING CONTINENT',
                
                # Success Messages
                'generated_hexes': 'Generated {count} hexes!',
                'continent_reset': 'Continent reset! Generated {count} fresh hexes',
                'hex_generated': 'Generated content for hex {hex_code}',
                
                # Confirmation Messages
                'confirm_generate_all': 'GENERATE CONTENT FOR THE ENTIRE MAP? THIS MAY TAKE A WHILE...',
                'confirm_reset_continent': '🚨 RESET ENTIRE CONTINENT? 🚨\n\nTHIS WILL DELETE ALL GENERATED CONTENT AND CREATE A COMPLETELY FRESH MAP.\n\nTHIS ACTION CANNOT BE UNDONE!',
                
                # Status Messages
                'generating_map': '⏳ Generating Map...',
                'resetting_generating': '🔄 Resetting & Generating...',
                'clearing_content': '🗑️ Clearing old content and generating fresh map...',
                'generating_hex_content': '⏳ Generating hex content...',
                'resetting_continent': '🔄 Resetting continent...',
                
                # Map Elements
                'major_cities': 'MAJOR CITIES',
                'settlements': 'SETTLEMENTS',
                'terrain_legend': 'TERRAIN:',
                'locations_legend': 'LOCATIONS:',
                'has_content': 'BOLD = HAS CONTENT',
                
                # Modal Titles
                'hex_details': 'HEX DETAILS',
                'city_details': 'CITY DETAILS',
                'settlement_details': 'SETTLEMENT DETAILS',
                'terrain_overview': '🗺️ TERRAIN OVERVIEW',
                'lore_overview': '📜 MÖRK BORG LORE',
                
                # Button Labels
                'close': 'CLOSE',
                'generate_content': 'GENERATE CONTENT',
                'generate_all': '⚡ GENERATE ALL',
                'reset_continent': '🩸 RESET CONTINENT',
                'zoom_in': '🔍+',
                'zoom_out': '🔍-',
                'terrain_button': '🗺️ TERRAIN',
                'lore_button': '🍄 LORE',
                
                # Map Information
                'click_hexes': 'CLICK HEXES TO VIEW/GENERATE CONTENT',
                'major_city_symbol': '◆ = MAJOR CITIES',
                'settlement_symbol': '⌂ = SETTLEMENTS',
                
                # Terrain Names
                'mountain': 'Mountain',
                'forest': 'Forest', 
                'coast': 'Coast',
                'plains': 'Plains',
                'swamp': 'Swamp',
                'desert': 'Desert',
                'unknown': 'Unknown',
                
                # NPC Field Labels
                'npc_trait': 'Trait',
                'npc_concern': 'Concern',
                'npc_want': 'Want',
                'npc_apocalypse_attitude': 'Apocalypse Attitude',
                'npc_secret': 'Secret',
                'npc_location': 'Location',
                'npc_carries': 'Carries',
                
                # Content Field Labels
                'territory': 'Territory',
                'threat_level': 'Threat Level',
                'treasure_found': 'Treasure Found',
                'loot_found': 'Loot Found',
                'type': 'Type',
                'item': 'Item',
                'description': 'Description',
                'full_description': 'Full Description',
                'name': 'Name',
                'behavior': 'Behavior',
                'feature': 'Feature',
                'danger': 'Danger',
                'atmosphere': 'Atmosphere',
                'motivation': 'Motivation',
                'demeanor': 'Demeanor',
                'origin': 'Origin',
                'weather': 'Weather',
                'innkeeper': 'Innkeeper',
                'effect': 'Effect',
                'builder': 'Builder',
                'age': 'Age',
                'population': 'Population',
                'trend': 'Trend',
                'government': 'Government',
                
                # Settlement Field Labels
                'local_tavern': 'Local Tavern',
                'local_power': 'Local Power',
                'city_event': 'City Event',
                'settlement_layout': 'Settlement Layout',
                'key_npcs': 'Key NPCs',
                
                # City Overlay Field Labels
                'district': 'District',
                'position': 'Position',
                'random_encounters': 'Random Encounters',
                'notable_features': 'Notable Features',
                'encounter': 'Encounter'
            },
            'pt': {
                # UI Elements
                'hex_prompt': 'Digite o código do hex (formato XXYY, ex: 0601) ou intervalo (0601-0610): ',
                'terrain_prompt': 'Tipo de terreno para este hex (montanha/floresta/costa/planicie/pantano): ',
                'invalid_hex': 'Formato de hex inválido. Usando intervalo padrão.',
                'files_generated': 'Arquivos gerados no diretório \'dying_lands_output/\':',
                'hex_files': 'arquivos de hex em hexes/',
                'overland_hex_map': 'Mapa Hexagonal das Terras Moribundas',
                'hex_descriptions': 'Descrições dos Hexágonos',
                
                # Content Types
                'terrain': 'Terreno',
                'encounter': 'Encontro',
                'denizen': 'Habitante',
                'location': 'Localização',
                'notable_feature': 'Característica Notável',
                'atmosphere': 'Atmosfera',
                'motivation': 'Motivação',
                'demeanor': 'Comportamento',
                
                # Generation Messages
                'generating_full_map': 'Gerando Mapa Completo',
                'map_size': 'Tamanho do Mapa',
                'language': 'Idioma',
                'generation_complete': 'Geração Completa',
                'creating_ascii_map': 'Criando Mapa ASCII',
                'generating_hex': 'Gerando hex',
                'skipping_existing': 'Pulando hex existente',
                
                # Error Messages
                'error_loading_hex': 'ERRO AO CARREGAR HEX',
                'error_loading_city': 'ERRO AO CARREGAR DETALHES DA CIDADE',
                'error_loading_settlement': 'ERRO AO CARREGAR DETALHES DO ASSENTAMENTO',
                'error_generating_hex': 'ERRO AO GERAR CONTEÚDO DO HEX',
                'error_generating_map': 'ERRO AO GERAR MAPA COMPLETO',
                'error_resetting_continent': 'ERRO AO RESETAR CONTINENTE',
                
                # Success Messages
                'generated_hexes': 'Gerados {count} hexes!',
                'continent_reset': 'Continente resetado! Gerados {count} hexes frescos',
                'hex_generated': 'Conteúdo gerado para hex {hex_code}',
                
                # Confirmation Messages
                'confirm_generate_all': 'GERAR CONTEÚDO PARA TODO O MAPA? ISSO PODE DEMORAR...',
                'confirm_reset_continent': '🚨 RESETAR CONTINENTE INTEIRO? 🚨\n\nISSO IRÁ DELETAR TODO O CONTEÚDO GERADO E CRIAR UM MAPA COMPLETAMENTE NOVO.\n\nESTA AÇÃO NÃO PODE SER DESFEITA!',
                
                # Status Messages
                'generating_map': '⏳ Gerando Mapa...',
                'resetting_generating': '🔄 Resetando & Gerando...',
                'clearing_content': '🗑️ Limpando conteúdo antigo e gerando mapa fresco...',
                'generating_hex_content': '⏳ Gerando conteúdo do hex...',
                'resetting_continent': '🔄 Resetando continente...',
                
                # Map Elements
                'major_cities': 'CIDADES PRINCIPAIS',
                'settlements': 'ASSENTAMENTOS',
                'terrain_legend': 'TERRENO:',
                'locations_legend': 'LOCALIZAÇÕES:',
                'has_content': 'NEGRITO = TEM CONTEÚDO',
                
                # Modal Titles
                'hex_details': 'DETALHES DO HEX',
                'city_details': 'DETALHES DA CIDADE',
                'settlement_details': 'DETALHES DO ASSENTAMENTO',
                'terrain_overview': '🗺️ VISÃO GERAL DO TERRENO',
                'lore_overview': '📜 LORE DO MÖRK BORG',
                
                # Button Labels
                'close': 'FECHAR',
                'generate_content': 'GERAR CONTEÚDO',
                'generate_all': '⚡ GERAR TUDO',
                'reset_continent': '🩸 RESETAR CONTINENTE',
                'zoom_in': '🔍+',
                'zoom_out': '🔍-',
                'terrain_button': '🗺️ TERRENO',
                'lore_button': '🍄 LORE',
                
                # Map Information
                'click_hexes': 'CLIQUE NOS HEXES PARA VER/GERAR CONTEÚDO',
                'major_city_symbol': '◆ = CIDADES PRINCIPAIS',
                'settlement_symbol': '⌂ = ASSENTAMENTOS',
                
                # Terrain Names
                'mountain': 'Montanha',
                'forest': 'Floresta',
                'coast': 'Costa',
                'plains': 'Planície',
                'swamp': 'Pântano',
                'desert': 'Deserto',
                'unknown': 'Desconhecido',
                
                # NPC Field Labels
                'npc_trait': 'Característica',
                'npc_concern': 'Preocupação',
                'npc_want': 'Desejo',
                'npc_apocalypse_attitude': 'Atitude do Apocalipse',
                'npc_secret': 'Segredo',
                'npc_location': 'Localização',
                'npc_carries': 'Carrega',
                
                # Content Field Labels
                'territory': 'Território',
                'threat_level': 'Nível de Ameaça',
                'treasure_found': 'Tesouro Encontrado',
                'loot_found': 'Saque Encontrado',
                'type': 'Tipo',
                'item': 'Item',
                'description': 'Descrição',
                'full_description': 'Descrição Completa',
                'name': 'Nome',
                'behavior': 'Comportamento',
                'feature': 'Característica',
                'danger': 'Perigo',
                'atmosphere': 'Atmosfera',
                'motivation': 'Motivação',
                'demeanor': 'Comportamento',
                'origin': 'Origem',
                'weather': 'Clima',
                'innkeeper': 'Taverneiro',
                'effect': 'Efeito',
                'builder': 'Construtor',
                'age': 'Idade',
                'population': 'População',
                'trend': 'Tendência',
                'government': 'Governo',
                
                # Settlement Field Labels
                'local_tavern': 'Taberna Local',
                'local_power': 'Poder Local',
                'city_event': 'Evento da Cidade',
                'settlement_layout': 'Layout do Assentamento',
                'key_npcs': 'NPCs Principais',
                
                # City Overlay Field Labels
                'district': 'Distrito',
                'position': 'Posição',
                'random_encounters': 'Encontros Aleatórios',
                'notable_features': 'Características Notáveis',
                'encounter': 'Encontro'
            }
        }
    
    def t(self, key: str, **kwargs) -> str:
        """Translate a key to the current language with optional formatting."""
        translation = self.translations.get(self.language, {}).get(key, key)
        
        # Apply formatting if kwargs provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return the key
                return key
        
        return translation
    
    def set_language(self, language: str):
        """Set the current language."""
        if language in self.translations:
            self.language = language
        else:
            print(f"⚠️  Language '{language}' not supported, using 'en'")
            self.language = 'en'
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.translations.keys())
    
    def get_current_language(self) -> str:
        """Get the current language."""
        return self.language
    
    def has_translation(self, key: str) -> bool:
        """Check if a translation key exists for the current language."""
        return key in self.translations.get(self.language, {})
    
    def get_all_translations(self, key: str) -> Dict[str, str]:
        """Get all translations for a key across all languages."""
        return {
            lang: translations.get(key, key)
            for lang, translations in self.translations.items()
        }

# Global translation system instance
translation_system = TranslationSystem() 