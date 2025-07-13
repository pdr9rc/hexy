#!/usr/bin/env python3
"""
Legacy Code Cleanup Script for The Dying Lands
Safely removes redundant files and updates remaining dependencies.
"""

import os
import shutil
from datetime import datetime
from typing import List, Dict

class LegacyCleanup:
    """Handles cleanup of legacy files and dependency updates."""
    
    def __init__(self, backup_dir: str = "legacy_backup"):
        self.backup_dir = backup_dir
        self.legacy_files = [
            "src/hex_generator.py",      # Superseded by main_map_generator.py + generation_engine.py
            "src/map_generator.py",      # Superseded by main_map_generator.py
            "src/content_tables.py"      # Superseded by normalized database system
        ]
        
        self.files_to_update = [
            "src/ascii_map_viewer.py",
            "src/test_generation.py"
        ]
        
        self.cleanup_report = {
            'backed_up': [],
            'removed': [],
            'updated': [],
            'errors': []
        }
    
    def run_cleanup(self, create_backup: bool = True, remove_files: bool = False):
        """Run the complete cleanup process."""
        print("🧹 Starting legacy code cleanup...")
        
        if create_backup:
            self._create_backup()
        
        self._update_dependencies()
        
        if remove_files:
            self._remove_legacy_files()
        else:
            print("ℹ️  Legacy files preserved (use --remove-files to delete)")
        
        self._generate_cleanup_report()
        
        print("✅ Legacy cleanup complete!")
    
    def _create_backup(self):
        """Create backup of legacy files."""
        print("📦 Creating backup of legacy files...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.backup_dir}_{timestamp}"
        
        os.makedirs(backup_path, exist_ok=True)
        
        for file_path in self.legacy_files:
            if os.path.exists(file_path):
                backup_file = os.path.join(backup_path, os.path.basename(file_path))
                shutil.copy2(file_path, backup_file)
                self.cleanup_report['backed_up'].append(file_path)
                print(f"📦 Backed up: {file_path}")
        
        print(f"✅ Backup created: {backup_path}")
    
    def _update_dependencies(self):
        """Update remaining files to use new system."""
        print("🔄 Updating dependencies in remaining files...")
        
        # Update ascii_map_viewer.py
        self._update_ascii_map_viewer()
        
        # Update test_generation.py  
        self._update_test_generation()
        
        print("✅ Dependencies updated")
    
    def _update_ascii_map_viewer(self):
        """Update ascii_map_viewer.py to use new system."""
        file_path = "src/ascii_map_viewer.py"
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already updated
            if 'from database_manager import database_manager' in content:
                print(f"ℹ️  {file_path} already updated")
                return
            
            # Update imports
            old_imports = [
                'from content_tables import get_all_tables, get_table',
                'from hex_generator import HexGenerator',
                'from map_generator import MapGenerator'
            ]
            
            new_imports = [
                'from database_manager import database_manager',
                'from main_map_generator import MainMapGenerator',
                'from generation_engine import generation_engine'
            ]
            
            updated_content = content
            
            # Replace imports
            for old_import in old_imports:
                if old_import in updated_content:
                    updated_content = updated_content.replace(old_import, new_imports[0], 1)
                    break
            
            # Replace class instantiations
            replacements = {
                'MapGenerator()': 'MainMapGenerator()',
                'HexGenerator(': 'MainMapGenerator(',
                'get_all_tables(': 'database_manager.load_tables(',
                'get_table(': 'database_manager.get_table('
            }
            
            for old, new in replacements.items():
                updated_content = updated_content.replace(old, new)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.cleanup_report['updated'].append(file_path)
            print(f"✅ Updated: {file_path}")
            
        except Exception as e:
            error_msg = f"Error updating {file_path}: {e}"
            self.cleanup_report['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def _update_test_generation(self):
        """Update test_generation.py to use new system."""
        file_path = "src/test_generation.py"
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already updated
            if 'from database_manager import database_manager' in content:
                print(f"ℹ️  {file_path} already updated")
                return
            
            # Update imports
            updated_content = content.replace(
                'from content_tables import get_all_tables, get_table',
                'from database_manager import database_manager'
            ).replace(
                'from hex_generator import HexGenerator',
                'from main_map_generator import MainMapGenerator'
            ).replace(
                'from map_generator import MapGenerator',
                'from main_map_generator import MainMapGenerator'
            )
            
            # Update function calls
            replacements = {
                'get_all_tables(': 'database_manager.load_tables(',
                'get_table(': 'database_manager.get_table(',
                'HexGenerator()': 'MainMapGenerator()',
                'MapGenerator()': 'MainMapGenerator()'
            }
            
            for old, new in replacements.items():
                updated_content = updated_content.replace(old, new)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.cleanup_report['updated'].append(file_path)
            print(f"✅ Updated: {file_path}")
            
        except Exception as e:
            error_msg = f"Error updating {file_path}: {e}"
            self.cleanup_report['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def _remove_legacy_files(self):
        """Remove legacy files (after backup)."""
        print("🗑️  Removing legacy files...")
        
        for file_path in self.legacy_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.cleanup_report['removed'].append(file_path)
                    print(f"🗑️  Removed: {file_path}")
                except Exception as e:
                    error_msg = f"Error removing {file_path}: {e}"
                    self.cleanup_report['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
            else:
                print(f"ℹ️  File not found: {file_path}")
    
    def _generate_cleanup_report(self):
        """Generate cleanup report."""
        report_path = "CLEANUP_REPORT.md"
        
        report_content = f"""# Legacy Cleanup Report

## Cleanup Date
{datetime.now().isoformat()}

## Files Backed Up
{self._format_file_list(self.cleanup_report['backed_up'])}

## Files Removed
{self._format_file_list(self.cleanup_report['removed'])}

## Files Updated
{self._format_file_list(self.cleanup_report['updated'])}

## Errors
{self._format_error_list(self.cleanup_report['errors'])}

## Summary
- **Backed up:** {len(self.cleanup_report['backed_up'])} files
- **Removed:** {len(self.cleanup_report['removed'])} files  
- **Updated:** {len(self.cleanup_report['updated'])} files
- **Errors:** {len(self.cleanup_report['errors'])} errors

## New System Structure

### Core Files (Keep)
- `src/main_map_generator.py` - Unified entry point
- `src/generation_engine.py` - Core generation algorithms
- `src/database_manager.py` - Database management
- `databases/` - Normalized JSON tables

### Supporting Files (Keep)
- `src/ascii_map_viewer.py` - Web interface
- `src/mork_borg_lore_database.py` - Lore database
- `src/terrain_system.py` - Terrain detection
- `src/translation_system.py` - Translation system

### Utility Files (Keep)
- `src/migrate_tables.py` - Migration script
- `src/test_generation.py` - Testing utilities

### Legacy Files (Removed/Backed Up)
- `src/hex_generator.py` - Superseded by main_map_generator.py + generation_engine.py
- `src/map_generator.py` - Superseded by main_map_generator.py
- `src/content_tables.py` - Superseded by normalized database system

## Usage After Cleanup

### Primary Usage
```bash
# Generate content
python3 src/main_map_generator.py --hex 0101

# Generate with configuration
python3 src/main_map_generator.py --config config.json

# Reset continent
python3 src/main_map_generator.py --reset
```

### Programmatic Usage
```python
from src.main_map_generator import MainMapGenerator
from src.generation_engine import generation_engine
from src.database_manager import database_manager

# Generate content
generator = MainMapGenerator()
result = generator.generate_single_hex('0101')

# Use generation engine directly
content = generation_engine.generate_content('settlement', {{'hex_code': '0101', 'terrain': 'forest', 'language': 'en'}})

# Access database
tables = database_manager.load_tables('en')
data = database_manager.get_table('basic', 'populations', 'en')
```
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Cleanup report created: {report_path}")
    
    def _format_file_list(self, files: List[str]) -> str:
        """Format list of files for report."""
        if not files:
            return "- None"
        return '\n'.join(f"- {file}" for file in files)
    
    def _format_error_list(self, errors: List[str]) -> str:
        """Format list of errors for report."""
        if not errors:
            return "- None"
        return '\n'.join(f"- {error}" for error in errors)


def main():
    """Main cleanup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up legacy code files')
    parser.add_argument('--backup', action='store_true', default=True,
                       help='Create backup of legacy files (default: True)')
    parser.add_argument('--remove-files', action='store_true',
                       help='Remove legacy files after backup (default: False)')
    parser.add_argument('--backup-dir', default='legacy_backup',
                       help='Backup directory name (default: legacy_backup)')
    
    args = parser.parse_args()
    
    cleanup = LegacyCleanup(args.backup_dir)
    cleanup.run_cleanup(
        create_backup=args.backup,
        remove_files=args.remove_files
    )


if __name__ == "__main__":
    main()