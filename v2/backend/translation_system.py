#!/usr/bin/env python3
"""
Unified Translation System for The Dying Lands
Handles all translation and localization functionality.
Loads translations from JSON files to maintain consistency.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from .config import get_config

class TranslationSystem:
    """Unified translation system for The Dying Lands."""
    
    def __init__(self, language: str = 'en', base_path: Optional[str] = None):
        self.language = language
        self.base_path = base_path or self._get_default_base_path()
        self.translations: Dict[str, Dict[str, Any]] = {}
        self._load_all_translations()
    
    def _get_default_base_path(self) -> str:
        """Get the default path to translation files."""
        cfg = get_config()
        return str(cfg.paths.database_path / "languages")
    
    def _load_all_translations(self) -> None:
        """Load all translation files for all supported languages."""
        for language_code in ['en', 'pt']:
            language_path = Path(self.base_path) / language_code
            if language_path.exists():
                self.translations[language_code] = self._load_language_files(language_path)
            else:
                print(f"⚠️  Warning: Language directory not found: {language_path}")
                self.translations[language_code] = {}
    
    def _load_language_files(self, language_path: Path) -> Dict[str, Any]:
        """Load all JSON files for a specific language."""
        combined_translations = {}
        
        # Load each JSON file in the language directory
        for json_file in language_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Extract category and tables/translations
                category = data.get('category', json_file.stem)
                
                # Handle different JSON structures
                if 'tables' in data:
                    # Database format with tables
                    for table_name, table_data in data['tables'].items():
                        key = f"{category}.{table_name}"
                        combined_translations[key] = table_data
                elif 'translations' in data:
                    # Translation format with translations object
                    for key, value in data['translations'].items():
                        combined_translations[f"{category}.{key}"] = value
                else:
                    # Direct key-value format or other structures
                    combined_translations[category] = data
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading translation file {json_file}: {e}")
        
        return combined_translations
    
    def t(self, key: str, language: Optional[str] = None, fallback: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key to the specified language with optional formatting.
        
        Args:
            key: Translation key (can be dotted path like 'ui.confirm_generate_all')
            language: Optional language override
            fallback: Fallback text if translation not found
            **kwargs: Variables for string formatting
        """
        target_language = language or self.language
        
        # Get translation from the appropriate language
        translation = self._get_translation(key, target_language)
        
        # Fall back to English if not found in target language
        if translation is None and target_language != 'en':
            translation = self._get_translation(key, 'en')
        
        # Use fallback or original key if no translation found
        if translation is None:
            translation = fallback or key
        
        # Apply formatting if kwargs provided
        if kwargs and isinstance(translation, str):
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return unformatted translation
                pass
        
        return str(translation)
    
    def _get_translation(self, key: str, language: str) -> Optional[Any]:
        """Get a translation for a specific key and language."""
        translations = self.translations.get(language, {})
        
        # Handle dotted key paths
        if '.' in key:
            parts = key.split('.')
            current = translations
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current
        else:
            return translations.get(key)
    
    def get_table(self, category: str, table_name: str, language: Optional[str] = None) -> List[Any]:
        """
        Get a table of data for random selection.
        
        Args:
            category: Category name (e.g., 'core', 'npc_traits')
            table_name: Table name (e.g., 'denizen_names_prefix')
            language: Optional language override
        """
        target_language = language or self.language
        key = f"{category}.{table_name}"
        result = self._get_translation(key, target_language)
        
        # Fall back to English if not found
        if result is None and target_language != 'en':
            result = self._get_translation(key, 'en')
        
        # Return as list if found, empty list otherwise
        return result if isinstance(result, list) else []
    
    def set_language(self, language: str) -> None:
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
    
    def has_translation(self, key: str, language: Optional[str] = None) -> bool:
        """Check if a translation key exists for the specified language."""
        target_language = language or self.language
        return self._get_translation(key, target_language) is not None
    
    def get_all_translations(self, key: str) -> Dict[str, Any]:
        """Get all translations for a key across all languages."""
        return {
            lang: self._get_translation(key, lang)
            for lang in self.translations.keys()
            if self._get_translation(key, lang) is not None
        }
    
    def get_ui_translations(self, language: Optional[str] = None) -> Dict[str, str]:
        """Get all UI translations for frontend consumption."""
        target_language = language or self.language
        ui_translations = {}
        
        # Extract UI-related translations
        for key, value in self.translations.get(target_language, {}).items():
            if key == 'ui' and isinstance(value, dict):
                # Get all translations from the ui category
                ui_translations.update(value)
            elif key.startswith('ui.') and isinstance(value, str):
                # Remove 'ui.' prefix for frontend
                ui_key = key[3:]
                ui_translations[ui_key] = value
            elif isinstance(value, str) and not key.endswith('.json'):
                # Include all direct string translations for backward compatibility
                ui_translations[key] = value
        
        return ui_translations
    
    def reload_translations(self) -> None:
        """Reload all translation files."""
        self._load_all_translations()

# Global translation system instance
translation_system = TranslationSystem() 