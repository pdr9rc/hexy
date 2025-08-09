# Hexy - The Dying Lands Hexcrawl Generator

A modern web-based hexcrawl generator for **The Dying Lands** campaign with interactive visualization and lore-accurate content generation.

## 🎯 Features

- **Interactive web interface** with real-time hex generation
- **Complete 30×60 hex map** (1800 hexes) with Mörk Borg lore integration
- **6 Major cities** with canonical placement and detailed overlays
- **Bilingual support** (English/Portuguese)
- **Desktop launcher** for easy access
- **Progressive Web App** with offline capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for development)
- Modern web browser

### Installation

#### Option 1: Desktop Launcher (Recommended)
```bash
# Clone the repository
git clone <repo-url>
cd hexy

# Install the desktop launcher
./scripts/install-launcher.sh

# Launch from your applications menu: "Hexy - The Dying Lands"
```

#### Option 2: Development Setup
```bash
# Clone the repository
git clone <repo-url>
cd hexy

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for development)
npm install

# Start the backend
npm run start:backend

# Or start everything (backend + frontend build)
npm run start:all
```

### Usage

#### Desktop Launcher
1. Launch "Hexy - The Dying Lands" from your applications menu
2. The app will open in your browser at `http://127.0.0.1:7777`
3. Click on hexes to view content or generate new hexes
4. Use the reset button to regenerate the entire continent

#### Development Mode
1. Start the backend: `npm run start:backend`
2. Open `http://127.0.0.1:6660` in your browser
3. The frontend will auto-rebuild when you make changes

## 🏗️ Architecture

### Backend (Flask)
- **`backend/`** - Core application
  - `app.py` - Main application entry point
  - `routes.py` - API endpoints and web routes
  - `hex_service.py` - Hex data management
  - `generation_engine.py` - Content generation
  - `city_overlay_analyzer.py` - City overlay system
  - `mork_borg_lore_database.py` - Lore integration
  - `config.py` - Configuration management

### Frontend (Vanilla JS/TypeScript)
- **`backend/web/static/`** - Frontend assets
  - `main.js` - Main application logic
  - `hexViewer.js` - Hex visualization
  - `api.js` - API communication
  - `translations.js` - Internationalization

### Scripts
- **`scripts/`** - Installation and deployment
  - `install-launcher.sh` - Desktop launcher installation
  - `hexy-backend.sh` - Backend service script
  - `hexy-launcher.sh` - Desktop launcher script

## 🎮 API Reference

### Core Endpoints
- `GET /` - Main application interface
- `GET /api/health` - Health check
- `GET /api/hex/<hex_code>` - Get hex information
- `POST /api/reset-continent` - Regenerate entire continent
- `GET /api/city-overlays` - List available city overlays
- `GET /api/city-overlay/<name>` - Get city overlay data

### Configuration
- `GET /api/debug-paths` - Debug path configuration
- `POST /api/set-language` - Change language (en/pt)

## 🏙️ Major Cities

All cities are placed according to Mörk Borg lore:

- **Galgenbeck** (1215) - Central urban hub
- **Bergen Chrypt** (0805) - Northern mountain fortress  
- **Sarkash Forest Settlement** (0508) - Northwest forest outpost
- **Tveland Outpost** (2012) - Eastern trading post
- **Kergus Plains Settlement** (1525) - Southern agriculture
- **Pyre-Chrypt** (0618) - Abandoned plague city

## 🌍 Terrain System

The map features diverse terrain types:
- **Plains** (~31%) - Perfect for settlements
- **Mountains** (~27%) - Eastern ranges
- **Forests** (~23%) - Northern Sarkash region
- **Swamps** (~14%) - Southern wetlands
- **Coast** (~5%) - Western shoreline

## 🔧 Development

### Project Structure
```
hexy/
├── backend/                    # Flask backend
│   ├── web/static/            # Frontend assets
│   ├── routes.py              # API endpoints
│   ├── hex_service.py         # Hex data management
│   └── generation_engine.py   # Content generation
├── scripts/                   # Installation scripts
├── data/                      # Campaign materials
├── dying_lands_output/        # Generated content
└── docs/                      # Documentation
```

### Development Commands
```bash
# Start backend only
npm run start:backend

# Start backend + frontend build
npm run start:all

# Build frontend only
npm run build:web

# Watch frontend changes
npm run build:web:watch
```

### Configuration
The app uses environment variables for configuration:
- `HEXY_APP_DIR` - Application directory
- `HEXY_OUTPUT_DIR` - Output directory
- `HEXY_PORT` - Server port (default: 6660)

### Adding New Content
1. **Hex Types**: Modify `generation_engine.py`
2. **City Overlays**: Add to `city_overlay_analyzer.py`
3. **Translations**: Update `translation_system.py`
4. **Lore**: Extend `mork_borg_lore_database.py`

### Database System
Content is stored in SQLite databases:
- `databases/` - SQLite files for different content types
- `database_manager.py` - Database access layer

## 🚀 Deployment

### Desktop Installation
```bash
./scripts/install-launcher.sh
```

### Systemd Service (Optional)
```bash
# Enable auto-start backend service
systemctl --user enable --now hexy.service
```

### Production Deployment
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx, Apache)
3. Configure environment variables
4. Set up SSL certificates

## 🐛 Troubleshooting

### Common Issues

**Launcher not working:**
- Check if backend is running: `curl http://127.0.0.1:7777/api/health`
- Verify port configuration in `~/.local/share/hexy/`
- Check logs: `/tmp/hexy-launcher.log`

**Hex data not loading:**
- Verify output directory: `~/.local/opt/hexy/dying_lands_output/`
- Check hex service cache: API `/api/debug-paths`
- Regenerate content: POST `/api/reset-continent`

**Frontend not updating:**
- Hard refresh browser (Ctrl+F5)
- Check browser console for errors
- Verify API connectivity

### Debug Commands
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

## 📝 Contributing

### Code Style
- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Use modern ES6+, prefer const/let over var
- **HTML**: Semantic markup, accessibility first
- **CSS**: Utility-first approach, mobile responsive

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

### Testing
```bash
# Run Python tests
python -m pytest backend/tests/

# Check code quality
flake8 backend/
pylint backend/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Mörk Borg** - The dark fantasy RPG that inspired this project
- **The Dying Lands** - The campaign setting
- **Free & Libre Software** - Built with open source tools

---

**🎲 Ready to explore The Dying Lands! Launch the app and start your hexcrawl adventure.**
