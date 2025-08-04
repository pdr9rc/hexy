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
                
                # Content Labels (for hex content formatting)
                'hex_number': 'HEX',
                'terrain_label': 'TERRAIN',
                'type_label': 'TYPE',
                'content_label': 'CONTENT',
                'district_label': 'DISTRICT',
                'position_label': 'POSITION',
                'description_label': 'DESCRIPTION',
                'atmosphere_label': 'ATMOSPHERE',
                'encounter_label': 'ENCOUNTER',
                'notable_features_label': 'NOTABLE FEATURES',
                'npc_information_label': 'NPC INFORMATION',
                'leadership_label': 'LEADERSHIP',
                'trade_opportunities_label': 'TRADE OPPORTUNITIES',
                'loot_found_label': 'LOOT FOUND',
                'denizen_type_label': 'DENIZEN TYPE',
                'beast_type_label': 'BEAST TYPE',
                'dungeon_type_label': 'DUNGEON TYPE',
                'encounter_type_label': 'ENCOUNTER TYPE',
                'behavior_label': 'BEHAVIOR',
                'danger_label': 'DANGER',
                'territory_label': 'TERRITORY',
                'threat_level_label': 'THREAT LEVEL',
                'treasure_found_label': 'TREASURE FOUND',
                'ancient_knowledge_label': 'ANCIENT KNOWLEDGE',
                'carries_label': 'CARRIES',
                'motivation_label': 'MOTIVATION',
                'demeanor_label': 'DEMEANOR',
                'name_label': 'NAME',
                'affiliation_label': 'AFFILIATION',
                'attitude_label': 'ATTITUDE',
                'trade_label': 'TRADE',
                'concern_label': 'CONCERN',
                'want_label': 'WANT',
                'secret_label': 'SECRET',
                'trait_label': 'TRAIT',
                
                # UI Action Labels
                'loading': 'Loading...',
                'loading_hex_details': 'Loading hex details...',
                'return_to_hex': 'RETURN TO HEX',
                'return_to_map': 'RETURN TO MAP',
                'edit': 'EDIT',
                'generate_all_content': 'GENERATE ALL CONTENT',
                'no_atmosphere_available': 'No atmosphere available.',
                
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
                'reset_continent': '🔄 RESET CONTINENT',
                'zoom_in': '🔍+',
                'zoom_out': '🔍-',
                'terrain_button': '🗺️ TERRAIN',
                'lore_button': '📜 LORE',
                
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
                'unknown': 'Unknown'
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
                
                # Content Labels (for hex content formatting)
                'hex_number': 'HEX',
                'terrain_label': 'TERRENO',
                'type_label': 'TIPO',
                'content_label': 'CONTEÚDO',
                'district_label': 'DISTRITO',
                'position_label': 'POSIÇÃO',
                'description_label': 'DESCRIÇÃO',
                'atmosphere_label': 'ATMOSFERA',
                'encounter_label': 'ENCONTRO',
                'notable_features_label': 'CARACTERÍSTICAS NOTÁVEIS',
                'npc_information_label': 'INFORMAÇÕES DO NPC',
                'leadership_label': 'LIDERANÇA',
                'trade_opportunities_label': 'OPORTUNIDADES DE COMÉRCIO',
                'loot_found_label': 'TESOURO ENCONTRADO',
                'denizen_type_label': 'TIPO DE HABITANTE',
                'beast_type_label': 'TIPO DE FERA',
                'dungeon_type_label': 'TIPO DE MASMORRA',
                'encounter_type_label': 'TIPO DE ENCONTRO',
                'behavior_label': 'COMPORTAMENTO',
                'danger_label': 'PERIGO',
                'territory_label': 'TERRITÓRIO',
                'threat_level_label': 'NÍVEL DE AMEAÇA',
                'treasure_found_label': 'TESOURO ENCONTRADO',
                'ancient_knowledge_label': 'CONHECIMENTO ANCESTRAL',
                'carries_label': 'CARREGA',
                'motivation_label': 'MOTIVAÇÃO',
                'demeanor_label': 'ATITUDE',
                'name_label': 'NOME',
                'affiliation_label': 'AFILIAÇÃO',
                'attitude_label': 'ATITUDE',
                'trade_label': 'COMÉRCIO',
                'concern_label': 'PREOCUPAÇÃO',
                'want_label': 'DESEJO',
                'secret_label': 'SEGREDO',
                'trait_label': 'CARACTERÍSTICA',
                
                # UI Action Labels
                'loading': 'Carregando...',
                'loading_hex_details': 'Carregando detalhes do hex...',
                'return_to_hex': 'VOLTAR AO HEX',
                'return_to_map': 'VOLTAR AO MAPA',
                'edit': 'EDITAR',
                'generate_all_content': 'GERAR TODO CONTEÚDO',
                'no_atmosphere_available': 'Nenhuma atmosfera disponível.',
                
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
                'reset_continent': '🔄 RESETAR CONTINENTE',
                'zoom_in': '🔍+',
                'zoom_out': '🔍-',
                'terrain_button': '🗺️ TERRENO',
                'lore_button': '📜 LORE',
                
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
                'unknown': 'Desconhecido'
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