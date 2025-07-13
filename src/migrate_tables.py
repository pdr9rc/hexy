#!/usr/bin/env python3
"""
Migration Script for The Dying Lands Database Normalization
Extracts tables from content_tables.py and converts them to normalized JSON format.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

# Import the existing content tables
from content_tables import (
    BASIC_TABLES, NAMING_TABLES, TAVERN_TABLES, DUNGEON_TABLES, 
    DENIZEN_TABLES, BESTIARY_TABLES, SCROLL_TABLES, LOOT_TABLES, 
    AFFILIATION_TABLES, WILDERNESS_TABLES, STATS_TABLES, ENHANCED_LOOT_TABLES,
    TERRAIN_TABLES, CORE_TABLES
)

from database_manager import DatabaseManager

class TableMigrator:
    """Migrates tables from Python dictionaries to normalized JSON format."""
    
    def __init__(self, output_path: str = "databases"):
        self.output_path = output_path
        self.db_manager = DatabaseManager(output_path)
        self.schema_version = "1.0"
    
    def migrate_all_tables(self):
        """Migrate all tables from content_tables.py to normalized JSON format."""
        print("🔄 Starting table migration...")
        
        # Clear and recreate the databases directory
        if os.path.exists(self.output_path):
            import shutil
            shutil.rmtree(self.output_path)
        
        # Recreate the directory structure
        self.db_manager._ensure_directory_structure()
        
        # Migrate each table category
        migration_stats = {
            'total_tables': 0,
            'total_items': 0,
            'categories': 0,
            'languages': 0
        }
        
        # Map original table names to normalized structure
        table_mapping = {
            'BASIC_TABLES': self._migrate_basic_tables,
            'NAMING_TABLES': self._migrate_naming_tables,
            'TAVERN_TABLES': self._migrate_tavern_tables,
            'DUNGEON_TABLES': self._migrate_dungeon_tables,
            'DENIZEN_TABLES': self._migrate_denizen_tables,
            'BESTIARY_TABLES': self._migrate_bestiary_tables,
            'SCROLL_TABLES': self._migrate_scroll_tables,
            'LOOT_TABLES': self._migrate_loot_tables,
            'AFFILIATION_TABLES': self._migrate_affiliation_tables,
            'WILDERNESS_TABLES': self._migrate_wilderness_tables,
            'STATS_TABLES': self._migrate_stats_tables,
            'ENHANCED_LOOT_TABLES': self._migrate_enhanced_loot_tables,
            'TERRAIN_TABLES': self._migrate_terrain_tables,
            'CORE_TABLES': self._migrate_core_tables
        }
        
        # Execute migrations
        for table_name, migrate_func in table_mapping.items():
            print(f"📋 Migrating {table_name}...")
            stats = migrate_func()
            migration_stats['total_tables'] += stats['tables']
            migration_stats['total_items'] += stats['items']
            migration_stats['categories'] += 1
        
        # Count languages
        migration_stats['languages'] = len(['en', 'pt'])
        
        # Create migration report
        self._create_migration_report(migration_stats)
        
        print(f"\n✅ Migration complete!")
        print(f"📊 Statistics:")
        print(f"   - Categories: {migration_stats['categories']}")
        print(f"   - Tables: {migration_stats['total_tables']}")
        print(f"   - Items: {migration_stats['total_items']}")
        print(f"   - Languages: {migration_stats['languages']}")
        print(f"📁 Database created in '{self.output_path}/' directory")
    
    def _migrate_basic_tables(self) -> Dict[str, int]:
        """Migrate basic tables to core/basic.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in BASIC_TABLES:
                for table_name, table_data in BASIC_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "basic", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_naming_tables(self) -> Dict[str, int]:
        """Migrate naming tables to content/names.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in NAMING_TABLES:
                for table_name, table_data in NAMING_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_content_file("names", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_tavern_tables(self) -> Dict[str, int]:
        """Migrate tavern tables to languages/tavern.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in TAVERN_TABLES:
                for table_name, table_data in TAVERN_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "tavern", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_dungeon_tables(self) -> Dict[str, int]:
        """Migrate dungeon tables to languages/dungeon.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in DUNGEON_TABLES:
                for table_name, table_data in DUNGEON_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "dungeon", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_denizen_tables(self) -> Dict[str, int]:
        """Migrate denizen tables to core/denizens.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in DENIZEN_TABLES:
                for table_name, table_data in DENIZEN_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "denizen", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_bestiary_tables(self) -> Dict[str, int]:
        """Migrate bestiary tables to languages/bestiary.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in BESTIARY_TABLES:
                for table_name, table_data in BESTIARY_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "bestiary", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_scroll_tables(self) -> Dict[str, int]:
        """Migrate scroll tables to languages/scroll.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in SCROLL_TABLES:
                for table_name, table_data in SCROLL_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "scroll", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_loot_tables(self) -> Dict[str, int]:
        """Migrate loot tables to languages/loot.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in LOOT_TABLES:
                for table_name, table_data in LOOT_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "loot", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_affiliation_tables(self) -> Dict[str, int]:
        """Migrate affiliation tables to languages/affiliation.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in AFFILIATION_TABLES:
                for table_name, table_data in AFFILIATION_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "affiliation", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_wilderness_tables(self) -> Dict[str, int]:
        """Migrate wilderness tables to languages/wilderness.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in WILDERNESS_TABLES:
                for table_name, table_data in WILDERNESS_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "wilderness", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_stats_tables(self) -> Dict[str, int]:
        """Migrate stats tables to languages/stats.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in STATS_TABLES:
                for table_name, table_data in STATS_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "stats", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_enhanced_loot_tables(self) -> Dict[str, int]:
        """Migrate enhanced loot tables to languages/enhanced_loot.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in ENHANCED_LOOT_TABLES:
                for table_name, table_data in ENHANCED_LOOT_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "enhanced_loot", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_terrain_tables(self) -> Dict[str, int]:
        """Migrate terrain tables to core/terrain.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in TERRAIN_TABLES:
                for terrain_type, terrain_data in TERRAIN_TABLES[lang].items():
                    if terrain_type not in tables:
                        tables[terrain_type] = {}
                    tables[terrain_type][lang] = terrain_data
                    # Count items in all subtables
                    for subtable in terrain_data.values():
                        if isinstance(subtable, list):
                            item_count += len(subtable)
        
        self._write_multilang_file("core", "terrain", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _migrate_core_tables(self) -> Dict[str, int]:
        """Migrate core tables to languages/core.json."""
        tables = {}
        item_count = 0
        
        for lang in ['en', 'pt']:
            if lang in CORE_TABLES:
                for table_name, table_data in CORE_TABLES[lang].items():
                    if table_name not in tables:
                        tables[table_name] = {}
                    tables[table_name][lang] = table_data
                    item_count += len(table_data)
        
        self._write_multilang_file("languages", "core", tables)
        return {'tables': len(tables), 'items': item_count}
    
    def _write_multilang_file(self, directory: str, filename: str, tables: Dict[str, Dict[str, Any]]):
        """Write a multilingual file with language-specific data."""
        if directory == "languages":
            # Write separate files for each language
            for lang in ['en', 'pt']:
                lang_tables = {}
                for table_name, lang_data in tables.items():
                    if lang in lang_data:
                        lang_tables[table_name] = lang_data[lang]
                
                if lang_tables:
                    self._write_language_file(lang, filename, lang_tables)
        else:
            # Write to core directory with multilingual structure
            filepath = os.path.join(self.output_path, directory, f"{filename}.json")
            
            # Convert to normalized structure
            normalized_tables = {}
            for table_name, lang_data in tables.items():
                normalized_tables[table_name] = lang_data
            
            file_data = {
                "category": filename,
                "tables": normalized_tables,
                "metadata": {
                    "version": self.schema_version,
                    "last_updated": datetime.now().isoformat(),
                    "migrated_from": "content_tables.py"
                }
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)
    
    def _write_language_file(self, language: str, filename: str, tables: Dict[str, Any]):
        """Write a language-specific file."""
        filepath = os.path.join(self.output_path, "languages", language, f"{filename}.json")
        
        file_data = {
            "category": filename,
            "tables": tables,
            "metadata": {
                "version": self.schema_version,
                "language": language,
                "last_updated": datetime.now().isoformat(),
                "migrated_from": "content_tables.py"
            }
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
    
    def _write_content_file(self, filename: str, tables: Dict[str, Dict[str, Any]]):
        """Write a content file with multilingual structure."""
        filepath = os.path.join(self.output_path, "content", f"{filename}.json")
        
        # Convert to normalized multilingual structure
        languages = {}
        for lang in ['en', 'pt']:
            lang_tables = {}
            for table_name, lang_data in tables.items():
                if lang in lang_data:
                    lang_tables[table_name] = lang_data[lang]
            
            if lang_tables:
                languages[lang] = {"tables": lang_tables}
        
        file_data = {
            "category": filename,
            "languages": languages,
            "metadata": {
                "version": self.schema_version,
                "last_updated": datetime.now().isoformat(),
                "migrated_from": "content_tables.py"
            }
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
    
    def _create_migration_report(self, stats: Dict[str, int]):
        """Create a migration report."""
        report = {
            "migration_date": datetime.now().isoformat(),
            "migration_stats": stats,
            "database_structure": {
                "core": ["terrain.json"],
                "lore": [],
                "content": ["names.json"],
                "languages": {
                    "en": ["basic.json", "tavern.json", "dungeon.json", "denizen.json", "bestiary.json", "scroll.json", "loot.json", "affiliation.json", "wilderness.json", "stats.json", "enhanced_loot.json", "core.json"],
                    "pt": ["basic.json", "tavern.json", "dungeon.json", "denizen.json", "bestiary.json", "scroll.json", "loot.json", "affiliation.json", "wilderness.json", "stats.json", "enhanced_loot.json", "core.json"]
                }
            },
            "schema_version": self.schema_version
        }
        
        report_path = os.path.join(self.output_path, "migration_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Migration report created: {report_path}")


def main():
    """Main migration function."""
    print("🚀 Starting database migration...")
    
    migrator = TableMigrator()
    migrator.migrate_all_tables()
    
    # Validate the migrated database
    print("\n🔍 Validating migrated database...")
    validation_report = migrator.db_manager.validate_schema()
    
    if validation_report['valid']:
        print("✅ Database validation successful!")
        print(f"📊 Database statistics:")
        print(f"   - Files: {validation_report['statistics']['total_files']}")
        print(f"   - Tables: {validation_report['statistics']['total_tables']}")
        print(f"   - Languages: {validation_report['statistics']['languages']}")
    else:
        print("❌ Database validation failed!")
        for error in validation_report['errors']:
            print(f"   - {error}")
    
    if validation_report['warnings']:
        print("⚠️  Warnings:")
        for warning in validation_report['warnings']:
            print(f"   - {warning}")


if __name__ == "__main__":
    main()