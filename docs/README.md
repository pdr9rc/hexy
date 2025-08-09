# Hexy - Technical Documentation

Technical documentation for the Hexy hexcrawl generator system.

## 🏗️ System Architecture

### Backend Architecture (Flask)

The backend is built with Flask using a modular architecture:

```
backend/
├── __init__.py              # Flask app factory
├── app.py                   # Main application entry point
├── routes.py                # API endpoints and web routes
├── config.py                # Configuration management
├── hex_service.py           # Hex data management service
├── generation_engine.py     # Content generation engine
├── city_overlay_analyzer.py # City overlay system
├── mork_borg_lore_database.py # Lore integration
├── database_manager.py      # Database access layer
├── translation_system.py    # Internationalization
├── terrain_system.py        # Terrain analysis
├── hex_model.py             # Hex data models
├── models.py                # Database models
├── utils.py                 # Utility functions
├── image_analyzer.py        # Image processing
├── ascii_map_viewer.py     # ASCII map generation
└── web/                     # Frontend assets
    ├── static/              # JavaScript, CSS, images
    └── templates/           # HTML templates
```

### Frontend Architecture (Vanilla JS/TypeScript)

The frontend uses vanilla JavaScript with TypeScript for development:

```
backend/web/static/
├── main.js                  # Main application logic
├── hexViewer.js             # Hex visualization
├── api.js                   # API communication
├── translations.js          # Internationalization
├── controls.js              # UI controls
├── mapRenderer.js           # Map rendering
├── uiUtils.js               # UI utilities
├── cityOverlays.js          # City overlay handling
├── cityOverlay.js           # Individual city overlays
├── utils/                   # Utility modules
│   ├── apiUtils.js          # API utilities
│   └── colorUtils.js        # Color utilities
└── icons/                   # Application icons
```

## 🔧 Configuration System

### Environment Variables

The application uses environment variables for configuration:

```bash
# Application paths
HEXY_APP_DIR=/path/to/app          # Application directory
HEXY_OUTPUT_DIR=/path/to/output     # Output directory

# Server configuration
HEXY_PORT=7777                      # Server port (default: 6660)
HEXY_IDLE_TIMEOUT=1800              # Idle timeout in seconds

# Browser configuration
HEXY_BROWSER=chromium               # Preferred browser
```

### Configuration Classes

```python
@dataclass
class AppConfig:
    language: str = 'pt'
    debug: bool = True
    host: str = '127.0.0.1'
    port: int = int(os.getenv('HEXY_PORT', '6660'))
    
    # Map configuration
    map: MapConfig = field(default_factory=MapConfig)
    
    # Generation configuration
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    
    # Path configuration
    paths: PathConfig = field(default_factory=PathConfig)
```

## 🗄️ Database System

### SQLite Databases

Content is stored in SQLite databases in the `databases/` directory:

```
databases/
├── encounters.db            # Random encounters
├── npcs.db                 # NPC data
├── loot.db                 # Treasure tables
├── descriptions.db          # Location descriptions
├── atmospheres.db          # Atmospheric details
└── translations.db         # Translation data
```

### Database Manager

The `database_manager.py` provides a unified interface:

```python
class DatabaseManager:
    def get_table(self, table_type: str, table_name: str, language: str) -> List[str]
    def get_random_entry(self, table_type: str, table_name: str, language: str) -> str
    def get_all_tables(self, table_type: str, language: str) -> Dict[str, List[str]]
```

## 🎮 API Reference

### Core Endpoints

#### Health & Status
- `GET /api/health` - Health check
- `GET /api/debug-paths` - Debug path configuration
- `POST /api/heartbeat` - Client heartbeat

#### Hex Management
- `GET /api/hex/<hex_code>` - Get hex information
- `PUT /api/hex/<hex_code>` - Update hex content
- `POST /api/generate-hex` - Generate single hex
- `POST /api/reset-continent` - Regenerate entire continent

#### City Overlays
- `GET /api/city-overlays` - List available city overlays
- `GET /api/city-overlay/<name>` - Get city overlay data
- `GET /api/city-overlay/<name>/ascii` - Get ASCII representation
- `GET /api/city-overlay/<name>/hex/<hex_id>` - Get specific hex in overlay

#### Language & Configuration
- `POST /api/set-language` - Change language (en/pt)
- `GET /api/lore-overview` - Get lore overview

### Response Formats

#### Hex Data
```json
{
  "hex_code": "1113",
  "terrain": "forest",
  "hex_type": "dungeon",
  "is_dungeon": true,
  "encounter": "▲ **Bone pit**",
  "denizen": "Bone pit, built on unholy ground.",
  "danger": "Cursed artifacts",
  "atmosphere": "Scratching sounds",
  "raw_markdown": "# Hex 1113\n\n**Terrain:** Forest...",
  "exists": true
}
```

#### Reset Response
```json
{
  "success": true,
  "generated_count": 1800,
  "message": "Continent reset complete. Generated 1800 hexes."
}
```

## 🔄 Content Generation

### Generation Engine

The `generation_engine.py` handles content generation:

```python
class GenerationEngine:
    def generate_hex(self, hex_code: str) -> Dict[str, Any]
    def generate_settlement(self, hex_code: str) -> Dict[str, Any]
    def generate_dungeon(self, hex_code: str) -> Dict[str, Any]
    def generate_beast(self, hex_code: str) -> Dict[str, Any]
    def generate_npc(self, hex_code: str) -> Dict[str, Any]
```

### Content Types

1. **Settlements** (⌂) - Villages, towns, cities
2. **Dungeons** (▲) - Ruins, tombs, lairs
3. **Beasts** (※) - Monsters and creatures
4. **NPCs** (☉) - Wandering characters
5. **Sea Encounters** (≈) - Coastal events
6. **Basic Hexes** - Terrain descriptions

### Terrain System

The `terrain_system.py` provides terrain analysis:

```python
class TerrainSystem:
    def get_terrain_for_hex(self, hex_code: str) -> str
    def get_terrain_symbol(self, terrain: str) -> str
    def analyze_terrain_distribution(self) -> Dict[str, int]
```

## 🌍 Internationalization

### Translation System

The `translation_system.py` handles multiple languages:

```python
class TranslationSystem:
    def translate(self, key: str, language: str) -> str
    def get_available_languages(self) -> List[str]
    def set_language(self, language: str) -> None
```

### Supported Languages
- **Portuguese (pt)** - Default for Mörk Borg atmosphere
- **English (en)** - Alternative language

## 🏙️ City Overlay System

### City Overlay Analyzer

The `city_overlay_analyzer.py` generates detailed city content:

```python
class CityOverlayAnalyzer:
    def generate_city_overlay(self, city_name: str) -> Dict[str, Any]
    def get_district_details(self, city_name: str, district: str) -> Dict[str, Any]
    def generate_random_table(self, city_name: str, district: str) -> List[str]
```

### Available Cities
- **Galgenbeck** - Central urban hub
- **Bergen Chrypt** - Northern mountain fortress
- **Sarkash Forest Settlement** - Northwest forest outpost
- **Tveland Outpost** - Eastern trading post
- **Kergus Plains Settlement** - Southern agriculture
- **Pyre-Chrypt** - Abandoned plague city

## 🚀 Deployment

### Desktop Launcher

The launcher system provides easy desktop integration:

```bash
# Install launcher
./scripts/install-launcher.sh

# Launcher files
~/.local/share/hexy/hexy-run      # Main launcher script
~/.local/share/hexy/hexy-backend  # Backend service script
~/.local/share/applications/hexy.desktop  # Desktop entry
```

### Systemd Service

Optional systemd service for auto-start:

```ini
[Unit]
Description=Hexy Backend
After=network.target

[Service]
Type=simple
Environment=HEXY_PORT=6660
ExecStart=~/.local/share/hexy/hexy-backend
Restart=on-failure

[Install]
WantedBy=default.target
```

### Production Deployment

1. **WSGI Server**: Use Gunicorn or uWSGI
2. **Reverse Proxy**: Nginx or Apache
3. **SSL**: Configure HTTPS certificates
4. **Environment**: Set production environment variables

## 🧪 Testing

### Test Structure
```
backend/tests/
├── test_hex_service.py      # Hex service tests
├── test_generation_engine.py # Generation tests
├── test_api.py              # API endpoint tests
└── test_integration.py      # Integration tests
```

### Running Tests
```bash
# Run all tests
python -m pytest backend/tests/

# Run specific test file
python -m pytest backend/tests/test_hex_service.py

# Run with coverage
python -m pytest --cov=backend backend/tests/
```

## 🔍 Debugging

### Debug Endpoints
- `GET /api/debug-paths` - Show current path configuration
- `GET /api/health` - Health check with status
- `POST /api/heartbeat` - Client connectivity test

### Log Files
- `/tmp/hexy-launcher.log` - Launcher activity
- `/tmp/hexy-backend.log` - Backend server logs

### Common Debug Commands
```bash
# Check backend status
curl http://127.0.0.1:7777/api/health

# View debug paths
curl http://127.0.0.1:7777/api/debug-paths

# Reset continent
curl -X POST http://127.0.0.1:7777/api/reset-continent

# Check launcher logs
tail -f /tmp/hexy-launcher.log
```

## 📊 Performance

### Optimization Strategies
1. **Hex Service Caching** - In-memory hex data cache
2. **Database Indexing** - Optimized SQLite queries
3. **Static Asset Caching** - Browser caching for static files
4. **Lazy Loading** - Load hex data on demand

### Monitoring
- **Memory Usage**: Monitor hex service cache size
- **Response Times**: API endpoint performance
- **Database Queries**: SQLite query optimization
- **Frontend Performance**: JavaScript execution time

---

**For user documentation, see the main README.md file.** 