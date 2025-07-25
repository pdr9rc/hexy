# Hexy - Dying Lands Hexcrawl Generator

A streamlined hexcrawl generator for **The Dying Lands** campaign with web-based visualization and lore-accurate city placement.

## 🎯 Core Features

- **Complete 25×30 hex map** generation (750 hexes)
- **6 Major Mörk Borg cities** with canonical lore placement
- **Interactive web interface** for viewing and generating content
- **Bilingual support** (English/Portuguese)
- **Terrain-aware content** generation

## 🚀 Quick Start

### Installation
```bash
# Install Flask for web interface
pip3 install flask

# Clone repository
git clone <repo-url>
cd hexy
```

### Generate Complete Map
```bash
# Generate full 750-hex map in Portuguese
cd src && python3 main_map_generator.py --language pt

# Generate in English  
cd src && python3 main_map_generator.py --language en
```

### Launch Web Interface
```bash
# Start the web viewer (only interface needed)
cd src && python3 ascii_map_viewer.py

# Visit http://localhost:5000
```

## 📁 Project Structure

```
hexy/
├── src/                              # Core system (10 files)
│   ├── ascii_map_viewer.py          # 🌐 Web interface (ONLY viewer needed)
│   ├── main_map_generator.py        # 🗺️ Complete map generation
│   ├── generation_engine.py         # ⚙️ Content creation system
│   ├── mork_borg_lore_database.py   # 📚 Cities & lore placement
│   ├── database_manager.py          # 🗄️ Database management
│   ├── terrain_system.py            # 🗺️ Terrain analysis
│   ├── translation_system.py        # 🌍 Translation support
│   ├── city_overlay_analyzer.py     # 🏙️ City overlay system
│   └── image_analyzer.py            # 🖼️ Image processing
├── dying_lands_output/               # Generated content
│   ├── hexes/ (750 files)           # Individual hex descriptions
│   ├── npcs/                        # Generated NPCs
│   ├── dying_lands_summary.md       # Complete campaign summary
│   └── ascii_map.txt                # Simple ASCII overview
├── data/                             # Campaign materials
│   └── TheDyingLands-Campaign Sheet.png
└── docs/                             # Documentation
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
cd src && python3 main_map_generator.py --hex 0508
# Generate specific hex: 0508 (Sarkash Forest area)
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
cd src && python3 main_map_generator.py --language pt

# English generation
cd src && python3 main_map_generator.py --language en
```

## 📊 Web Interface Only

This system is designed around the **single web interface**. No other viewers are needed:

- ✅ **Interactive map visualization**
- ✅ **Real-time content generation** 
- ✅ **City and lore information**
- ✅ **Mobile-friendly responsive design**
- ✅ **All features integrated** in one interface

## 🔧 Advanced Usage

### Regenerate Existing Content
```bash
# Force regeneration of all hexes
cd src && python3 main_map_generator.py --reset --language pt
```

### Custom Content Generation
```python
# Generate specific terrain types
from src.main_map_generator import MainMapGenerator
generator = MainMapGenerator({'language': 'en'})
hex_data = generator.generate_hex("0508")
```

## 🎯 Perfect For

- **Mörk Borg campaigns** with official lore integration
- **Hexcrawl adventures** with detailed terrain
- **Campaign preparation** with automated content
- **Web-based gaming** with interactive maps

## 📈 File Count

- **Core system**: 10 Python files (streamlined)
- **Generated content**: 750+ hex files + cities
- **Single web interface**: All viewing in one place
- **No redundant viewers**: Clean, focused system

---

**🎲 Ready to explore The Dying Lands! Launch the web interface and start your hexcrawl.** 