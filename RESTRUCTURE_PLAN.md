# 🔧 Content Generation Restructure Plan

## 📋 Current Issues Identified

### 1. **Scattered Map Generation Logic**
- Multiple map-related files: `map_generator.py`, `hex_generator.py`, `ascii_map_viewer.py`
- No single entry point for map generation
- Redundant functionality across files

### 2. **Non-normalized Database Structure**
- `content_tables.py` (748 lines) - massive dictionary with mixed content types
- `mork_borg_lore_database.py` (408 lines) - hardcoded city/lore data
- Tables split by language rather than logical grouping
- Difficult to customize or extend

### 3. **Dispersed Generation/Reset Logic**
- Reset functions scattered across files
- No centralized database management
- Generation logic mixed with presentation logic

## 🎯 Restructure Goals

### Primary Objectives:
1. **Single Main Map File** - Consolidate all map generation into one primary entry point
2. **Normalized Database** - Restructure tables for easy customization
3. **Centralized Generation Logic** - Condense all generation/reset/database logic

## 🏗️ Proposed Structure

### Phase 1: Create Unified Main Map Generator

**New File: `src/main_map_generator.py`**
- Single entry point for all map generation
- Consolidate functionality from `map_generator.py` and `hex_generator.py`
- Clean API for generation, reset, and customization

```python
class MainMapGenerator:
    def __init__(self, config: dict = None)
    def generate_full_map(self, options: dict = None)
    def generate_single_hex(self, hex_code: str)
    def reset_continent(self)
    def customize_generation(self, custom_tables: dict)
```

### Phase 2: Normalize Database Structure

**New File: `src/database_manager.py`**
- Centralized database management
- Normalized table structure
- Easy customization interface

```python
class DatabaseManager:
    def __init__(self)
    def load_tables(self, language: str)
    def get_table(self, category: str, table_name: str)
    def add_custom_table(self, category: str, table_name: str, data: dict)
    def export_tables(self, format: str = 'json')
    def import_tables(self, file_path: str)
```

**Restructured Table Organization:**
```
databases/
├── core/
│   ├── terrain.json
│   ├── encounters.json
│   ├── denizens.json
│   └── settlements.json
├── lore/
│   ├── cities.json
│   ├── factions.json
│   └── regions.json
├── content/
│   ├── names.json
│   ├── descriptions.json
│   └── features.json
└── languages/
    ├── en/
    └── pt/
```

### Phase 3: Centralized Generation Logic

**New File: `src/generation_engine.py`**
- Core generation algorithms
- Unified reset/initialization
- Template-based content generation

```python
class GenerationEngine:
    def __init__(self, database_manager: DatabaseManager)
    def generate_content(self, type: str, context: dict)
    def reset_all_data(self)
    def initialize_database(self)
    def apply_custom_rules(self, rules: dict)
```

## 📝 Implementation Plan

### Step 1: Database Normalization (Priority: HIGH)
1. **Extract and normalize tables** from `content_tables.py`
2. **Create JSON schema** for table structure
3. **Implement DatabaseManager** class
4. **Create migration script** to convert existing data

### Step 2: Main Map Consolidation (Priority: HIGH)
1. **Create MainMapGenerator** class
2. **Merge functionality** from existing generators
3. **Implement clean API** for external use
4. **Add configuration system** for customization

### Step 3: Generation Engine (Priority: MEDIUM)
1. **Create GenerationEngine** class
2. **Centralize all generation logic**
3. **Implement template system** for content
4. **Add reset/initialization methods**

### Step 4: Legacy Code Cleanup (Priority: LOW)
1. **Remove redundant files**
2. **Update imports** across codebase
3. **Update documentation**
4. **Add migration guide**

## 🔧 Technical Specifications

### Database Schema Structure:
```json
{
  "category": "terrain",
  "tables": {
    "mountain": {
      "encounters": ["...", "..."],
      "features": ["...", "..."],
      "descriptions": ["...", "..."]
    }
  },
  "metadata": {
    "version": "1.0",
    "language": "en",
    "last_updated": "2024-01-01"
  }
}
```

### Configuration System:
```python
# config.py
DEFAULT_CONFIG = {
    'map_dimensions': (30, 25),
    'language': 'en',
    'generation_rules': {
        'city_density': 0.1,
        'encounter_rate': 0.3,
        'settlement_chance': 0.2
    },
    'output_formats': ['markdown', 'json', 'ascii']
}
```

## 🎯 Benefits of This Restructure

### For Users:
- **Single entry point** - one file to rule them all
- **Easy customization** - modify JSON files instead of code
- **Better performance** - optimized database queries
- **Extensible** - add new content types easily

### For Developers:
- **Clean architecture** - separation of concerns
- **Maintainable code** - less duplication
- **Testable** - isolated components
- **Scalable** - easy to add new features

## 📊 Implementation Timeline

### Week 1: Database Normalization
- [x] Extract tables from existing files
- [x] Create JSON schemas
- [x] Implement DatabaseManager
- [x] Create migration scripts

### Week 2: Main Map Generator
- [x] Create MainMapGenerator class
- [x] Merge existing functionality
- [x] Implement configuration system
- [x] Integrate with normalized DatabaseManager
- [x] Add comprehensive testing

### Week 3: Generation Engine
- [x] Create GenerationEngine class
- [x] Centralize generation logic
- [x] Implement template system
- [x] Add reset/initialization

### Week 4: Cleanup & Documentation
- [x] Remove legacy files
- [x] Update documentation
- [x] Performance optimization
- [x] Final testing

## 🧪 Testing Strategy

### Unit Tests:
- Database operations
- Generation algorithms
- Configuration handling
- Content validation

### Integration Tests:
- End-to-end map generation
- Multi-language support
- Custom content loading
- Performance benchmarks

### Migration Tests:
- Data integrity verification
- Backward compatibility
- Error handling
- Rollback procedures

## 📚 Documentation Updates

### User Documentation:
- Quick start guide
- Configuration reference
- Customization tutorial
- API documentation

### Developer Documentation:
- Architecture overview
- Database schema
- Extension guidelines
- Contributing guide

---

**Next Steps**: Start with Phase 1 (Database Normalization) as it's the foundation for all other improvements.