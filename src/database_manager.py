#!/usr/bin/env python3
"""
Database Manager for The Dying Lands
Centralized database management with normalized table structure, caching, and structured logging.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil

try:
    from .base_classes import BaseDatabaseManager, DatabaseError
except ImportError:
    from base_classes import BaseDatabaseManager, DatabaseError

class DatabaseManager(BaseDatabaseManager):
    """
    Centralized database management for normalized content tables.
    Inherits caching and logging from BaseDatabaseManager.
    """
    
    def __init__(self, database_path: str = "databases"):
        """Initialize the database manager."""
        super().__init__()
        self.database_path = database_path
        self.schema_version = "1.0"
        os.makedirs(database_path, exist_ok=True)
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self) -> None:
        """Ensure the normalized directory structure exists."""
        subdirs = [
            "core",
            "lore",
            "content",
            "languages/en",
            "languages/pt"
        ]
        for subdir in subdirs:
            os.makedirs(os.path.join(self.database_path, subdir), exist_ok=True)
    
    def load_tables(self, language: str = 'en') -> Dict[str, Any]:
        """Load all tables for a specific language, using cache if available."""
        cache_key = f"tables_{language}"
        cached = self.get_cached_data(cache_key)
        if cached:
            self.logger.info(f"Loaded tables for '{language}' from cache.")
            return cached
        tables: Dict[str, Any] = {}
        try:
            tables.update(self._load_core_tables())
            tables.update(self._load_language_tables(language))
            tables.update(self._load_lore_tables())
            tables.update(self._load_content_tables(language))
            self.set_cached_data(cache_key, tables)
            self.logger.info(f"Loaded tables for '{language}' from disk and cached.")
            return tables
        except Exception as e:
            self.logger.error(f"Failed to load tables for '{language}': {e}")
            raise DatabaseError(f"Failed to load tables for '{language}': {e}")
    
    def _load_core_tables(self) -> Dict[str, Any]:
        """Load core system tables."""
        core_files = [
            "terrain.json",
            "encounters.json",
            "denizens.json",
            "settlements.json"
        ]
        tables: Dict[str, Any] = {}
        for filename in core_files:
            filepath = os.path.join(self.database_path, "core", filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category = filename.replace('.json', '')
                    tables[f"{category}_tables"] = data.get('tables', {})
        return tables
    
    def _load_language_tables(self, language: str) -> Dict[str, Any]:
        """Load language-specific tables."""
        lang_dir = os.path.join(self.database_path, "languages", language)
        if not os.path.exists(lang_dir):
            return {}
        tables: Dict[str, Any] = {}
        for filename in os.listdir(lang_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(lang_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category = filename.replace('.json', '')
                    tables[f"{category}_tables"] = data.get('tables', {})
        return tables
    
    def _load_lore_tables(self) -> Dict[str, Any]:
        """Load lore tables."""
        lore_files = [
            "cities.json",
            "factions.json",
            "regions.json"
        ]
        tables: Dict[str, Any] = {}
        for filename in lore_files:
            filepath = os.path.join(self.database_path, "lore", filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category = filename.replace('.json', '')
                    tables[f"{category}_tables"] = data.get('tables', {})
        return tables
    
    def _load_content_tables(self, language: str) -> Dict[str, Any]:
        """Load content tables."""
        content_files = [
            "names.json",
            "descriptions.json",
            "features.json"
        ]
        tables: Dict[str, Any] = {}
        for filename in content_files:
            filepath = os.path.join(self.database_path, "content", filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang_data = data.get('languages', {}).get(language, {})
                    category = filename.replace('.json', '')
                    tables[f"{category}_tables"] = lang_data.get('tables', {})
        return tables
    
    def get_table(self, category: str, table_name: str, language: str = 'en') -> List[Any]:
        """Get a specific table from a category."""
        tables = self.load_tables(language)
        category_key = f"{category}_tables"
        if category_key in tables:
            return tables[category_key].get(table_name, [])
        for key, table_data in tables.items():
            if isinstance(table_data, dict) and table_name in table_data:
                return table_data[table_name]
        return []
    
    def add_custom_table(self, category: str, table_name: str, data: List[Any], language: str = 'en') -> None:
        """Add or update a custom table."""
        if category in ['terrain', 'encounters', 'denizens', 'settlements']:
            filepath = os.path.join(self.database_path, "core", f"{category}.json")
        elif category in ['cities', 'factions', 'regions']:
            filepath = os.path.join(self.database_path, "lore", f"{category}.json")
        elif category in ['names', 'descriptions', 'features']:
            filepath = os.path.join(self.database_path, "content", f"{category}.json")
        else:
            filepath = os.path.join(self.database_path, "languages", language, f"{category}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
        else:
            file_data = {
                "category": category,
                "metadata": {
                    "version": self.schema_version,
                    "language": language,
                    "last_updated": datetime.now().isoformat()
                }
            }
        if category in ['names', 'descriptions', 'features']:
            if 'languages' not in file_data:
                file_data['languages'] = {}
            if language not in file_data['languages']:
                file_data['languages'][language] = {'tables': {}}
            file_data['languages'][language]['tables'][table_name] = data
        else:
            if 'tables' not in file_data:
                file_data['tables'] = {}
            file_data['tables'][table_name] = data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        self.clear_cache()
        self.logger.info(f"Custom table '{table_name}' added/updated in category '{category}' for language '{language}'.")
    
    def clear_cache(self) -> None:
        """Clear all cached tables."""
        super().clear_cache()
        self.logger.info("DatabaseManager cache cleared.")

# Singleton instance for import compatibility

database_manager = DatabaseManager()