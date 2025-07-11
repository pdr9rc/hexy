# 🗺️ Hexcrawl Generator Suite

A comprehensive set of tools for generating Mörk Borg-inspired hexcrawl content with multilingual support and interactive viewers.

## 🎲 Features

### Content Generators
- **Hexcrawl Generator**: Procedural towns, dungeons, NPCs, and wilderness encounters
- **The Dying Lands Generator**: Terrain-aware content for existing hex maps
- **Multilingual Support**: English and Portuguese translations
- **Rich Content**: Atmospheric Mörk Borg-style descriptions

### Interactive Viewers
- **Terminal Viewer**: Curses-based interface with keyboard navigation
- **Web Viewer**: Modern browser-based interface with search functionality
- **Launcher**: Easy selection between viewer types

## 📁 Project Structure

```
hexy/
├── hexcrawl_generator.py      # Main hexcrawl generator
├── dying_lands_generator.py   # Terrain-aware hex generator
├── hex_viewer.py             # Terminal-based viewer
├── hex_web_viewer.py         # Web-based viewer
├── launch_viewer.py          # Viewer launcher
├── hexcrawl_output/          # Generated hexcrawl content
├── dying_lands_output/       # Generated Dying Lands content
├── templates/                # Web viewer HTML templates
└── static/                   # Web viewer CSS/JS assets
```

## 🚀 Quick Start

### 1. Generate Content

**Standard Hexcrawl:**
```bash
python3 hexcrawl_generator.py --towns 5 --language en --format markdown
```

**The Dying Lands (for existing hex maps):**
```bash
python3 dying_lands_generator.py --hex 0601-0610 --language pt
```

### 2. View Content

**Easy Launch:**
```bash
python3 launch_viewer.py
```

**Direct Launch:**
```bash
# Terminal viewer
python3 hex_viewer.py

# Web viewer
python3 hex_web_viewer.py
# Then open http://localhost:5000
```

## 🎯 Content Generators

### Hexcrawl Generator

Generates complete hexcrawls with towns, dungeons, NPCs, and encounters.

**Options:**
- `--towns N`: Number of towns to generate (default: 5)
- `--language {en,pt}`: Output language (default: en)
- `--format {markdown,plain}`: Output format (default: markdown)

**Example Output:**
```markdown
# C1(3,6) - Verhu's Henge

## City Overview
- **Population:** 101-500
- **Buildings:** Stone
- **Sounds:** Chanting

## Tavern: The Screaming Soothsayer
- **Description:** Smokey, Smelly
- **Daily Special:** Long pig & Algae

## Dungeon
Abandoned tower, overrun with vermin.
**Primary Danger:** Cursed artifacts
**Notable Feature:** Precious gemstones
```

### The Dying Lands Generator

Terrain-aware content generation for existing hex maps using 4-digit hex codes.

**Options:**
- `--hex XXYY`: Single hex or range (e.g., 0601-0610)
- `--terrain {mountain,forest,coast,plains,swamp}`: Override terrain detection
- `--language {en,pt}`: Output language

**Example Output:**
```markdown
# Hex 0201 - Coast

## Encounter
Beached whale carcass

## Notable Feature
Sandy beaches

## Denizen
**Sister Ash** - Lighthouse keeper
*Smells of decay*
**Motivation:** trades in human misery
**Demeanor:** Hostile
```

## 📺 Interactive Viewers

### Terminal Viewer (hex_viewer.py)

Curses-based terminal interface with keyboard navigation.

**Controls:**
- `↑↓` or `k/j`: Navigate files
- `←→` or `h/l`: Switch content types
- `1-9`: Switch directories
- `q` or `ESC`: Quit
- `?` or `h`: Help

**Features:**
- Syntax highlighting for markdown
- Sidebar navigation
- File browser
- Cross-platform (Unix/Linux/macOS)

### Web Viewer (hex_web_viewer.py)

Modern browser-based interface with rich features.

**Features:**
- **Responsive Design**: Works on desktop and mobile
- **Search Functionality**: Full-text search across all content
- **Syntax Highlighting**: Beautiful markdown rendering
- **Navigation**: Easy switching between directories and content types
- **Raw View**: Toggle between formatted and raw markdown

**Routes:**
- `/`: Main interface
- `/directory/<name>`: View specific directory
- `/directory/<name>/<type>`: View specific content type
- `/api/file/<path>`: Get file content (JSON)
- `/api/search?q=<query>`: Search content (JSON)

### Launcher (launch_viewer.py)

Intelligent launcher that detects available content and dependencies.

**Features:**
- Content detection
- Dependency checking
- User-friendly error messages
- Choice between viewer types

## 🌍 Multilingual Support

Both generators support English and Portuguese with full translations:

**English Features:**
- Complete town names: "Shadow Hill", "Bloody Blade Crossing"
- Atmospheric descriptions: "Ancient tomb, haunted by restless spirits"
- Rich NPC details: "Brother Crow - Plague doctor, seeks forbidden knowledge"

**Portuguese Features:**
- Translated names: "Sombra Colina", "Cruzamento da Lâmina Sangrenta"
- Atmospheric descriptions: "Tumba antiga, assombrada por espíritos inquietos"
- Rich NPC details: "Irmão Corvo - Médico da peste, caça conhecimento proibido"

## 🎨 Generated Content Types

### Towns/Cities
- Procedural names with Mörk Borg atmosphere
- Population and building materials
- Ambient sounds and atmosphere
- Detailed taverns with specialties
- Local hex maps with encounters
- Generated dungeons

### Wilderness Hexes
- Terrain-specific encounters
- Environmental features
- Random events
- Atmospheric descriptions

### NPCs/Denizens
- Unique names and professions
- Physical descriptions
- Motivations and demeanor
- Role-playing hooks

### Dungeons
- Multi-layered descriptions
- Dangers and treasures
- Atmospheric details
- Room layouts

## 🛠️ Installation

### Requirements
- Python 3.6+
- `curses` (for terminal viewer, usually pre-installed on Unix systems)
- `flask` and `markdown` (for web viewer)

### Install Dependencies

**System packages (recommended):**
```bash
sudo apt install python3-flask python3-markdown
```

**Or with pip (in virtual environment):**
```bash
pip install flask markdown
```

### Clone and Run
```bash
git clone <repository>
cd hexy
python3 hexcrawl_generator.py --towns 3
python3 launch_viewer.py
```

## 📊 File Output Structure

### Hexcrawl Output
```
hexcrawl_output/
├── overland_map.md           # Complete overland map
├── cities/                   # Individual city files
│   ├── C1_Shadow_Hill.md
│   └── C2_Beggar_Creek.md
└── npcs/                     # NPC cards
    ├── overland_npcs/        # Wilderness encounters
    └── city_npcs/            # City inhabitants
```

### The Dying Lands Output
```
dying_lands_output/
├── dying_lands_summary.md    # Overview of all hexes
├── hexes/                    # Individual hex files
│   ├── hex_0601.md
│   └── hex_0602.md
└── npcs/                     # Generated NPCs (if applicable)
```

## 🎮 Example Workflow

1. **Generate a hexcrawl:**
   ```bash
   python3 hexcrawl_generator.py --towns 5 --language en
   ```

2. **Generate specific hex content:**
   ```bash
   python3 dying_lands_generator.py --hex 0601-0605 --language pt
   ```

3. **View content interactively:**
   ```bash
   python3 launch_viewer.py
   # Choose option 2 for web viewer
   # Open http://localhost:5000 in browser
   ```

4. **Search and explore:**
   - Use the web interface to search for "tavern", "witch", or "mountain"
   - Navigate between different content types
   - Toggle between formatted and raw views

## 🧙‍♂️ Tips & Tricks

### Generating Large Campaigns
```bash
# Generate a large hexcrawl
python3 hexcrawl_generator.py --towns 20 --language en

# Fill in specific hex ranges
python3 dying_lands_generator.py --hex 0601-0650 --language en
python3 dying_lands_generator.py --hex 0701-0750 --language en
```

### Multilingual Campaigns
```bash
# Generate in both languages for comparison
python3 hexcrawl_generator.py --towns 5 --language en
python3 hexcrawl_generator.py --towns 5 --language pt
```

### Custom Terrain Generation
```bash
# Force specific terrain types
python3 dying_lands_generator.py --hex 1501-1505 --terrain mountain
python3 dying_lands_generator.py --hex 0201-0205 --terrain coast
```

## 🐛 Troubleshooting

**"No content found" error:**
- Run a generator first to create content

**Terminal viewer doesn't work:**
- Ensure you're on a Unix-like system with curses support
- Try the web viewer instead

**Web viewer won't start:**
- Install Flask and Markdown: `sudo apt install python3-flask python3-markdown`
- Check if port 5000 is available

**Permission errors:**
- Make scripts executable: `chmod +x *.py`

## 🎲 Advanced Features

### Terrain Detection Algorithm
The Dying Lands generator uses intelligent terrain detection based on hex coordinates:
- Western edge (x ≤ 3): Coast
- Eastern edge (x ≥ 14): Mountain  
- Southern regions (y ≥ 15): Swamp
- Central areas (8 ≤ x ≤ 12, 4 ≤ y ≤ 10): Forest
- Default: Plains

### Content Caching
Both viewers implement content caching for improved performance when browsing large campaigns.

### Extensible Table System
Easy to add new languages or content types by extending the `TRANSLATIONS` and `TABLES` dictionaries.

## 🤝 Contributing

Feel free to extend the generators with:
- New language translations
- Additional terrain types
- More encounter tables
- Different output formats
- Enhanced viewer features

## 📜 License

This project is designed for tabletop RPG enthusiasts and Mörk Borg fans. Use responsibly and have fun exploring the dying lands!

---

**Happy hexcrawling!** 🗺️⚔️🏰 