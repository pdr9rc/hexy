# Hexy - Dying Lands Hexcrawl Generator

A streamlined hexcrawl generator for **The Dying Lands** campaign with web-based visualization and lore-accurate city placement.

## 🎯 Core Features

- **Complete 25×30 hex map** generation (750 hexes)
- **6 Major Mörk Borg cities** with canonical lore placement
- **Interactive web interface** for viewing and generating content
- **Bilingual support** (English/Portuguese)
- **Terrain-aware content** generation
- **Normalized database system** with JSON storage

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip3 install -r requirements.txt

# Clone repository
git clone <repo-url>
cd hexy
```

### Generate Complete Map
```bash
# Generate full 750-hex map in Portuguese
python3 src/main_map_generator.py --language pt

# Generate in English  
python3 src/main_map_generator.py --language en
```

### Launch Web Interface
```bash
# Start the web viewer
python3 src/ascii_map_viewer.py

# Visit http://localhost:5000
```

## 📁 Project Structure

```
hexy/
├── src/                              # Core system
│   ├── ascii_map_viewer.py          # 🌐 Web interface
│   ├── main_map_generator.py        # 🗺️ Complete map generation
│   ├── database_manager.py          # 📊 Database management
│   ├── mork_borg_lore_database.py   # 📚 Cities & lore placement
│   ├── generation_engine.py         # ⚙️ Content creation system
│   ├── sandbox_generator.py         # 🏘️ Sandbox generation
│   ├── terrain_system.py            # 🌍 Terrain management
│   ├── translation_system.py        # 🌐 Language support
│   └── migrate_tables.py            # 🔄 Database migration
├── databases/                        # Normalized content database
│   ├── core/                        # Core generation tables
│   ├── content/                     # Content-specific tables
│   ├── languages/                   # Language-specific content
│   └── sandbox/                     # Sandbox-specific content
├── data/                            # Campaign materials
│   └── TheDyingLands-Campaign Sheet.png
├── web/                             # Web interface assets
│   ├── static/                      # Static files
│   └── templates/                   # HTML templates
└── docs/                            # Documentation
```

## 🏰 Major Cities

All **6 canonical Mörk Borg cities** are automatically placed:

- **Galgenbeck** (1215) - Central urban hub, population 501-1000
- **Bergen Chrypt** (0805) - Northern mountain fortress, population 101-500
- **Sarkash Forest Settlement** (0508) - Northwest forest outpost, population 51-100
- **Tveland Outpost** (2012) - Eastern trading post, population 51-100
- **Kergus Plains Settlement** (1525) - Southern agriculture, population 101-500
- **Pyre-Chrypt** (0618) - Abandoned plague city, population 0

## 🌍 Terrain Distribution

**Optimized 25×30 Map:**
- 🌾 Plains: ~31% (Perfect for settlements)
- ⛰️ Mountains: ~27% (Eastern ranges) 
- 🌲 Forests: ~23% (Northern Sarkash region)
- 🐸 Swamps: ~14% (Southern wetlands)
- 🌊 Coast: ~5% (Western shoreline)

## 🎮 Usage

### Generate Individual Hexes
```bash
python3 src/main_map_generator.py --hex 0508
# Generates content for hex 0508 (Sarkash Forest area)
```

### Web Interface Features
- **Interactive ASCII map** with clickable hexes
- **Real-time hex generation** 
- **City information** and lore details
- **Terrain overview** with statistics
- **Search and navigation** tools

### API Endpoints
- `/api/hex/<hex_code>` - Get hex information
- `/api/generate-hex` - Generate single hex
- `/api/terrain-overview` - Map analysis

## 🌍 Language Support

```bash
# Portuguese generation (default for Mörk Borg atmosphere)
python3 src/main_map_generator.py --language pt

# English generation
python3 src/main_map_generator.py --language en
```

## 🔧 Advanced Usage

### Regenerate Existing Content
```bash
# Force regeneration of all hexes
python3 src/main_map_generator.py --regenerate --language pt
```

### Custom Content Generation
```python
# Generate specific terrain types
from src.main_map_generator import MainMapGenerator
generator = MainMapGenerator(language="pt")
hex_data = generator.generate_hex_content("0508", "forest")
```

## 🎯 Perfect For

- **Mörk Borg campaigns** with official lore integration
- **Hexcrawl adventures** with detailed terrain
- **Campaign preparation** with automated content
- **Web-based gaming** with interactive maps

## 📈 File Count

- **Core system**: 14 Python files (streamlined)
- **Normalized database**: JSON-based content management
- **Single web interface**: All viewing in one place
- **Clean architecture**: Separation of concerns

---

**🎲 Ready to explore The Dying Lands! Launch the web interface and start your hexcrawl.** 