#!/usr/bin/env python3
"""
Database Manager for The Dying Lands
Centralized database management with normalized table structure and easy customization.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil
from .utils.database_categories import get_all_categories, get_core_categories, get_lore_categories
from .config import get_config

class DatabaseManager:
    """Centralized database management for normalized content tables."""
    
    def __init__(self, database_path: Optional[str] = None):
        """Initialize the database manager."""
        cfg = get_config()
        resolved = Path(database_path) if database_path else cfg.paths.database_path
        self.database_path = str(resolved)
        self.tables_cache = {}
        self.schema_version = "1.0"
        
        # Ensure database directory exists
        os.makedirs(self.database_path, exist_ok=True)
        
        # Initialize directory structure
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self):
        """Ensure the unified directory structure exists."""
        # Use centralized category definitions
        categories = get_all_categories()
        
        # Create unified structure directories
        for category in categories:
            for lang in ['en', 'pt']:
                os.makedirs(os.path.join(self.database_path, category, lang), exist_ok=True)
    
    def load_tables(self, language: str = 'en') -> Dict[str, Any]:
        """Load all tables for a specific language."""
        if language in self.tables_cache:
            return self.tables_cache[language]
        
        # Load unified structure tables
        tables = self._load_unified_tables(language)
        
        # Cache the results
        self.tables_cache[language] = tables
        
        return tables
    
    def _load_core_tables(self) -> Dict[str, Any]:
        """Load core system tables - now handled by unified structure."""
        # Core tables are now loaded through the unified structure
        # This method is kept for backward compatibility but no longer loads files
        return {}
    
    def _load_language_tables(self, language: str) -> Dict[str, Any]:
        """Load language-specific tables."""
        lang_dir = os.path.join(self.database_path, "languages", language)
        if not os.path.exists(lang_dir):
            return {}
        
        tables = {}
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
            # Legacy lore files - now handled by unified structure
        ]
        
        tables = {}
        for filename in lore_files:
            filepath = os.path.join(self.database_path, "lore", filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category = filename.replace('.json', '')
                    tables[f"{category}_tables"] = data.get('tables', {})
        
        return tables
    
    def _load_content_tables(self, language: str) -> Dict[str, Any]:
        """Load content tables - now handled by unified structure."""
        # Content tables are now loaded through the unified structure
        # This method is kept for backward compatibility but no longer loads files
        return {}
    
    def _load_unified_tables(self, language: str) -> Dict[str, Any]:
        """Load tables from the new unified structure."""
        tables = {}
        
        # Scan for category directories with language subdirectories
        for item in os.listdir(self.database_path):
            category_path = os.path.join(self.database_path, item)
            if os.path.isdir(category_path):
                lang_path = os.path.join(category_path, language)
                if os.path.exists(lang_path) and os.path.isdir(lang_path):
                    # Look for the JSON file in the language directory
                    json_file = os.path.join(lang_path, f"{item}.json")
                    if os.path.exists(json_file):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                tables[f"{item}_tables"] = data.get('tables', {})
                        except (json.JSONDecodeError, FileNotFoundError):
                            continue
        
        return tables
    
    def get_table(self, category: str, table_name: str, language: str = 'en') -> List[Any]:
        """Get a specific table from a category."""
        tables = self.load_tables(language)
        
        # Look in the appropriate category
        category_key = f"{category}_tables"
        if category_key in tables:
            table = tables[category_key].get(table_name)
            if table is not None:
                return table
        
        # Fallback: search all tables
        for key, table_data in tables.items():
            if isinstance(table_data, dict) and table_name in table_data:
                return table_data[table_name]

        # Fallback: direct file lookup when unified naming is not used
        direct = Path(self.database_path) / category / language / f"{table_name}.json"
        if direct.exists():
            try:
                with open(direct, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "tables" in data:
                        return data["tables"].get(table_name, [])
                    if isinstance(data, dict) and "table" in data:
                        return data["table"]
                    if isinstance(data, list):
                        return data
            except Exception:
                return []
        
        return []
    
    def add_custom_table(self, category: str, table_name: str, data: List[Any], language: str = 'en'):
        """Add or update a custom table."""
        # Use new unified structure
        filepath = os.path.join(self.database_path, category, language, f"{category}.json")
        
        # Load existing data or create new
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
        
        # Update the table - unified structure uses simple tables structure
            if 'tables' not in file_data:
                file_data['tables'] = {}
            file_data['tables'][table_name] = data
        
        # Update metadata
        file_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        
        # Clear cache to force reload
        self.tables_cache.clear()
        
        print(f"✅ Custom table '{table_name}' added to category '{category}'")
    
    def export_tables(self, format: str = 'json', output_path: Optional[str] = None) -> str:
        """Export tables to various formats."""
        if format not in ['json', 'yaml', 'csv']:
            raise ValueError(f"Unsupported format: {format}")
        
        if output_path is None:
            output_path = f"exported_tables.{format}"
        
        if format == 'json':
            # Export all tables as a single JSON file
            all_data = {}
            for lang in ['en', 'pt']:
                all_data[lang] = self.load_tables(lang)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'yaml':
            import yaml
            all_data = {}
            for lang in ['en', 'pt']:
                all_data[lang] = self.load_tables(lang)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(all_data, f, default_flow_style=False, allow_unicode=True)
        
        elif format == 'csv':
            import csv
            # CSV export for individual tables
            os.makedirs(output_path, exist_ok=True)
            
            for lang in ['en', 'pt']:
                tables = self.load_tables(lang)
                lang_dir = os.path.join(output_path, lang)
                os.makedirs(lang_dir, exist_ok=True)
                
                for table_key, table_data in tables.items():
                    if isinstance(table_data, dict):
                        for subtable_name, subtable_data in table_data.items():
                            if isinstance(subtable_data, list):
                                csv_path = os.path.join(lang_dir, f"{table_key}_{subtable_name}.csv")
                                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    writer.writerow(['item'])
                                    for item in subtable_data:
                                        writer.writerow([item])
        
        print(f"✅ Tables exported to {output_path}")
        return output_path
    
    def import_tables(self, file_path: str):
        """Import tables from a JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Import file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            imported_data = json.load(f)
        
        # Process the imported data
        for lang, tables in imported_data.items():
            for table_key, table_data in tables.items():
                if isinstance(table_data, dict):
                    # Extract category from table_key
                    category = table_key.replace('_tables', '')
                    
                    for subtable_name, subtable_data in table_data.items():
                        if isinstance(subtable_data, list):
                            self.add_custom_table(category, subtable_name, subtable_data, lang)
        
        print(f"✅ Tables imported from {file_path}")
    
    def list_categories(self) -> List[str]:
        """List all available table categories."""
        categories = set()
        
        # Scan all directories
        for root, dirs, files in os.walk(self.database_path):
            for file in files:
                if file.endswith('.json'):
                    category = file.replace('.json', '')
                    categories.add(category)
        
        return sorted(list(categories))
    
    def list_tables_in_category(self, category: str, language: str = 'en') -> List[str]:
        """List all tables in a specific category."""
        tables = self.load_tables(language)
        category_key = f"{category}_tables"
        
        if category_key in tables and isinstance(tables[category_key], dict):
            return list(tables[category_key].keys())
        
        return []
    
    def get_table_info(self, category: str, table_name: str, language: str = 'en') -> Dict[str, Any]:
        """Get information about a specific table."""
        table_data = self.get_table(category, table_name, language)
        
        return {
            'category': category,
            'table_name': table_name,
            'language': language,
            'item_count': len(table_data),
            'sample_items': table_data[:3] if table_data else [],
            'data_type': type(table_data[0]).__name__ if table_data else 'empty'
        }
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate the database schema and return a report."""
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {
                'total_files': 0,
                'total_tables': 0,
                'languages': []
            }
        }
        
        # Check directory structure
        # Use centralized category definitions for validation
        categories = get_all_categories()
        
        for category in categories:
            for lang in ['en', 'pt']:
                dir_path = f"{category}/{lang}"
            full_path = os.path.join(self.database_path, dir_path)
            if not os.path.exists(full_path):
                    report['warnings'].append(f"Missing directory: {dir_path}")
                    # Don't mark as invalid since some categories might not exist
        
        # Validate JSON files
        for root, dirs, files in os.walk(self.database_path):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    report['statistics']['total_files'] += 1
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Check for required fields
                        if 'metadata' not in data:
                            report['warnings'].append(f"Missing metadata in {filepath}")
                        
                        # Count tables
                        if 'tables' in data:
                            report['statistics']['total_tables'] += len(data['tables'])
                        if 'languages' in data:
                            for lang_data in data['languages'].values():
                                if 'tables' in lang_data:
                                    report['statistics']['total_tables'] += len(lang_data['tables'])
                        
                    except json.JSONDecodeError as e:
                        report['errors'].append(f"Invalid JSON in {filepath}: {e}")
                        report['valid'] = False
        
        # Check for supported languages
        # Look for language directories in any category
        languages = set()
        for root, dirs, files in os.walk(self.database_path):
            for dir_name in dirs:
                if dir_name in ['en', 'pt']:
                    languages.add(dir_name)
        report['statistics']['languages'] = list(languages)
        
        return report
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the entire database."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"database_backup_{timestamp}"
        
        # Create backup
        shutil.copytree(self.database_path, backup_path)
        
        print(f"✅ Database backed up to {backup_path}")
        return backup_path
    
    def clear_cache(self):
        """Clear the tables cache."""
        self.tables_cache.clear()
        print("✅ Database cache cleared")


# Global database manager instance
import os
_database_path = str(get_config().paths.database_path)
database_manager = DatabaseManager(_database_path)