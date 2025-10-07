#!/usr/bin/env python3
"""
Flask Routes for The Dying Lands
Separated route definitions for better organization.
"""

import re
import os
import time
import threading
import secrets
import logging
import traceback
from flask import Blueprint, jsonify, request, abort, render_template
from flask import Response, send_file
import os
from backend.config import get_config, get_output_dir_for_language
from backend.utils import setup_project_paths, validate_hex_code

# Setup project paths for imports
setup_project_paths()

# Import after path setup
from backend.mork_borg_lore_database import MorkBorgLoreDatabase
from backend.terrain_system import terrain_system
from backend.main_map_generator import MainMapGenerator
from backend.translation_system import translation_system
# City overlay analyzer may fail to import during development; guard it
try:
    from backend.city_overlay_analyzer import city_overlay_analyzer  # type: ignore
except Exception as _e:  # SyntaxError or other import-time errors
    city_overlay_analyzer = None  # type: ignore
    _CITY_OVERLAY_IMPORT_ERROR = _e  # type: ignore
from backend.hex_service import hex_service
from backend.hex_model import hex_manager
from backend.utils.city_processor import create_major_city_response
from backend.utils.markdown_parser import parse_content_sections, parse_loot_section, parse_magical_effect, extract_title_from_content, determine_hex_type
from backend.utils.response_helpers import create_overlay_response, handle_exception_response
from backend.utils.content_detector import get_hex_content_type, check_hex_has_loot
from backend.utils.grid_generator import generate_hex_grid, determine_content_symbol, determine_css_class
import io
import zipfile
import tempfile
import shutil
from pathlib import Path
import backend.terrain_system as terrain_module

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
assets_bp = Blueprint('assets', __name__, url_prefix='/')

# Initialize systems
config = get_config()
lore_db = MorkBorgLoreDatabase()
current_language = config.language

# ===== Backend lifetime management via client heartbeat =====
_HEXY_HEARTBEAT_TS = time.monotonic()
_HEXY_HEARTBEAT_TOKEN = secrets.token_urlsafe(24)
_HEXY_TIMEOUT_SECONDS = int(os.getenv('HEXY_IDLE_TIMEOUT', '90'))  # shutdown after 90s idle by default

def _hexy_inactivity_monitor():
    while True:
        time.sleep(5)
        try:
            if time.monotonic() - _HEXY_HEARTBEAT_TS > _HEXY_TIMEOUT_SECONDS:
                # Graceful shutdown if possible (Werkzeug dev server), else hard exit
                shutdown = None
                try:
                    from flask import request
                    shutdown = request.environ.get('werkzeug.server.shutdown')  # type: ignore
                except Exception:
                    shutdown = None
                if shutdown:
                    shutdown()
                else:
                    os._exit(0)
        except Exception:
            # Never crash monitor
            pass

_t = threading.Thread(target=_hexy_inactivity_monitor, name='hexy-inactivity-monitor', daemon=True)
_t.start()

def get_main_map_generator():
    """Get main map generator with current language configuration."""
    output_dir = get_output_dir_for_language(current_language)
    return MainMapGenerator({'language': current_language, 'output_directory': str(output_dir)})

# Initialize with default language
main_map_generator = get_main_map_generator()

# Add this normalization function near the top (after imports)
def normalize_terrain_name(name: str) -> str:
    name = name.strip().lower()
    mapping = {
        # English terrain names
        "plain": "plains",
        "plains": "plains",
        "forest": "forest",
        "mountain": "mountain",
        "mountains": "mountain",
        "coast": "coast",
        "swamp": "swamp",
        "desert": "desert",
        "sea": "sea",
        "ocean": "sea",
        "snow": "snow",
        "tundra": "snow",
        "unknown": "unknown",
        # Portuguese terrain names
        "planície": "plains",
        "planicies": "plains",
        "floresta": "forest",
        "montanha": "mountain",
        "montanhas": "mountain",
        "costa": "coast",
        "pântano": "swamp",
        "pantano": "swamp",
        "deserto": "desert",
        "mar": "sea",
        "oceano": "sea",
        "neve": "snow",
        "tundra": "snow",
        "desconhecido": "unknown",
    }
    return mapping.get(name, "unknown")

# ===== MAIN ROUTES =====

@main_bp.route('/')
def main_map():
    """Main map page with integrated lore."""
    config = get_config()
    
    if not config.paths.output_path.exists():
        config.paths.output_path.mkdir(parents=True, exist_ok=True)
    # If output is empty, show world with empty state; user can press Reset from UI
    
    # Auto-regenerate output if flag is set
    if getattr(config, 'auto_regenerate_output', False):
        print("[AUTO] Regenerating Dying Lands output (auto_regenerate_output=True)...")
        main_map_generator.generate_full_map()
    
    # Get map dimensions
    map_width, map_height = terrain_system.get_map_dimensions()
    
    # Generate ASCII map data
    ascii_map_data = generate_ascii_map_data()

    # If map is empty, regenerate and reload
    if not ascii_map_data:
        print("[AUTO] Map data empty, regenerating full map...")
        main_map_generator.generate_full_map()
        ascii_map_data = generate_ascii_map_data()
    
    # Ensure all keys are strings
    ascii_map_data = {str(k): v for k, v in ascii_map_data.items()}
    
    return render_template('main_map.html',
                         ascii_map=ascii_map_data,
                         map_width=map_width,
                         map_height=map_height,
                         major_cities=get_major_cities_data(),
                         total_hexes=map_width * map_height,
                           current_language=current_language,
                           hexy_token=_HEXY_HEARTBEAT_TOKEN)

# ===== PWA ASSETS =====
@assets_bp.route('/manifest.webmanifest')
def serve_manifest():
    manifest = {
        "name": "The Dying Lands",
        "short_name": "Dying Lands",
        "start_url": ".",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",
        "icons": [
            {"src": "static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    }
    return jsonify(manifest)

@assets_bp.route('/service-worker.js')
def serve_service_worker():
    # Progressive Web App service worker with basic precache and runtime caching
    version = (_HEXY_HEARTBEAT_TOKEN[:8] if isinstance(_HEXY_HEARTBEAT_TOKEN, str) else 'v')
    sw_js = (
        f"const CACHE_NAME='dl-{version}';\n"
        f"const RUNTIME_CACHE='dl-runtime-{version}';\n"
        "const PRECACHE_URLS=[\n"
        "  'manifest.webmanifest',\n"
        "  'static/main.js',\n"
        "  'static/main.css',\n"
        "  'static/fonts.css',\n"
        "  'static/icons/icon-192.png',\n"
        "  'static/icons/icon-512.png'\n"
        "];\n"
        "self.addEventListener('install',event=>{\n"
        "  event.waitUntil((async()=>{\n"
        "    const cache=await caches.open(CACHE_NAME);\n"
        "    try { await cache.addAll(PRECACHE_URLS); } catch(e){}\n"
        "    self.skipWaiting();\n"
        "  })());\n"
        "});\n"
        "self.addEventListener('activate',event=>{\n"
        "  event.waitUntil((async()=>{\n"
        "    const names=await caches.keys();\n"
        "    await Promise.all(names.map(n=>{ if(n!==CACHE_NAME && n!==RUNTIME_CACHE){ return caches.delete(n);} }));\n"
        "    self.clients.claim();\n"
        "  })());\n"
        "});\n"
        "self.addEventListener('message', async (event)=>{\n"
        "  if(!event || !event.data) return;\n"
        "  if(event.data.type==='CLEAR_CACHES'){\n"
        "    const names=await caches.keys();\n"
        "    await Promise.all(names.map(n=>caches.delete(n)));\n"
        "    try{ const clients=await self.clients.matchAll({type:'window'}); clients.forEach(c=>c.navigate(c.url)); }catch(e){}\n"
        "  }\n"
        "});\n"
        "self.addEventListener('fetch',event=>{\n"
        "  const req=event.request;\n"
        "  const url=new URL(req.url);\n"
        "  if(req.method!=='GET'){ return; }\n"
        "  // API: network-first, fallback to cache, and never use http cache\n"
        "  if(url.origin===location.origin && url.pathname.includes('/api/')){\n"
        "    event.respondWith((async()=>{\n"
        "      try{\n"
        "        const fresh=await fetch(new Request(req,{cache:'no-store'}));\n"
        "        const cache=await caches.open(RUNTIME_CACHE);\n"
        "        cache.put(req, fresh.clone());\n"
        "        return fresh;\n"
        "      }catch(e){\n"
        "        const cached=await caches.match(req);\n"
        "        if(cached) return cached;\n"
        "        throw e;\n"
        "      }\n"
        "    })());\n"
        "    return;\n"
        "  }\n"
        "  // Static assets: cache-first (stage-aware by using relative paths)\n"
        "  if(url.origin===location.origin && (url.pathname.includes('/static/') )){\n"
        "    event.respondWith((async()=>{\n"
        "      const cached=await caches.match(req);\n"
        "      if(cached) return cached;\n"
        "      const resp=await fetch(req);\n"
        "      const runtime=await caches.open(RUNTIME_CACHE);\n"
        "      runtime.put(req, resp.clone());\n"
        "      return resp;\n"
        "    })());\n"
        "    return;\n"
        "  }\n"
        "  // Default: try network, fallback to cache\n"
        "  event.respondWith(fetch(req).catch(()=>caches.match(req)));\n"
        "});\n"
    )
    from flask import Response
    return Response(sw_js, mimetype='application/javascript')

@assets_bp.route('/lottie.js')
def serve_lottie_js():
    """Serve lottie-web player. Prefer node_modules during dev, fallback to static vendor."""
    try:
        from pathlib import Path
        base = Path(__file__).parent.parent  # backend/
        project_root = base.parent  # repo root
        node_path = project_root / 'node_modules' / 'lottie-web' / 'build' / 'player' / 'lottie.min.js'
        vendor_path = base / 'web' / 'static' / 'vendor' / 'lottie.min.js'
        target = node_path if node_path.exists() else vendor_path
        with open(target, 'rb') as f:
            data = f.read()
        from flask import Response
        return Response(data, mimetype='application/javascript')
    except Exception as e:
        # Last resort: minimal shim so app does not crash
        shim = b"(function(){window.lottie=window.lottie||{loadAnimation:function(){return {play:function(){},stop:function(){},destroy:function(){}}}}})();"
        from flask import Response
        return Response(shim, mimetype='application/javascript')

# ===== Heartbeat/Health API =====
@api_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    global _HEXY_HEARTBEAT_TS
    # Be permissive: accept heartbeats unconditionally to avoid idle shutdowns
    # when the page is served from cache or after a backend restart.
    _HEXY_HEARTBEAT_TS = time.monotonic()
    return jsonify({'success': True})

@api_bp.route('/health', methods=['GET'])
def health():
    """Simple health endpoint used by the frontend to detect backend availability."""
    return jsonify({'ok': True})

@api_bp.route('/debug-paths', methods=['GET'])
def debug_paths():
    try:
        from backend.config import get_config
        cfg = get_config()
        return jsonify({
            'cwd': os.getcwd(),
            'HEXY_APP_DIR': os.getenv('HEXY_APP_DIR'),
            'HEXY_OUTPUT_DIR': os.getenv('HEXY_OUTPUT_DIR'),
            'output_path': str(cfg.paths.output_path),
            'project_root': str(cfg.paths.project_root)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== Export / Import API =====
@api_bp.route('/export', methods=['GET'])
def export_output_zip():
    try:
        output_dir = config.paths.output_path
        if not output_dir.exists():
            return jsonify({'error': 'Output directory not found'}), 404
        # Build zip in-memory to keep it simple
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            base_name = 'dying_lands_output'
            for root, _, files in os.walk(output_dir):
                for fname in files:
                    full = Path(root) / fname
                    # arcname should start with base_name/
                    rel = full.relative_to(output_dir)
                    zf.write(str(full), arcname=str(Path(base_name) / rel))
        mem.seek(0)
        ts = time.strftime('%Y%m%d%H%M%S')
        filename = f"dying_lands_output-{ts}.zip"
        return send_file(
            mem,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/import', methods=['POST'])
def import_output_zip():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Missing file'}), 400
        file = request.files['file']
        if not file.filename.lower().endswith('.zip'):
            return jsonify({'error': 'File must be a .zip'}), 400

        # Save uploaded content to memory and open as zip
        data = file.read()
        tmpdir = Path(tempfile.mkdtemp(prefix='hexy-import-'))
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for info in zf.infolist():
                    # Prevent Zip Slip
                    dest_path = (tmpdir / info.filename).resolve()
                    if not str(dest_path).startswith(str(tmpdir.resolve())):
                        continue
                    if info.is_dir():
                        dest_path.mkdir(parents=True, exist_ok=True)
                    else:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info, 'r') as src, open(dest_path, 'wb') as dst:
                            shutil.copyfileobj(src, dst)

            # Determine extracted root
            extracted_root = tmpdir / 'dying_lands_output'
            src_dir = extracted_root if extracted_root.exists() else tmpdir
            # Ensure src has expected structure (at least 'hexes' or something)
            if not any(p.is_dir() for p in src_dir.iterdir()):
                return jsonify({'error': 'Archive appears empty'}), 400

            final_dir = config.paths.output_path
            final_dir.parent.mkdir(parents=True, exist_ok=True)
            # Backup current directory if exists
            backup = None
            if final_dir.exists():
                backup = final_dir.parent / f"{final_dir.name}.bak-{int(time.time())}"
                shutil.move(str(final_dir), str(backup))
            # Move imported content into place
            shutil.move(str(src_dir), str(final_dir))
            # Clean temp
            shutil.rmtree(tmpdir, ignore_errors=True)
            return jsonify({'ok': True, 'backup': str(backup) if backup else None})
        except Exception:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== API ROUTES =====

@api_bp.route('/reset-continent', methods=['POST'])
def reset_continent():
    """Reset the entire continent and regenerate all content.
    Optionally accepts {"language": "en|pt"} to switch language before regenerating.
    """
    try:
        # Optional language override from request body
        try:
            data = request.get_json(silent=True) or {}
        except Exception:
            data = {}
        new_language = data.get('language') if isinstance(data, dict) else None

        # Determine languages to generate: requested one or all supported
        supported = getattr(translation_system, 'get_supported_languages', lambda: ['en','pt'])()
        langs = [new_language] if new_language in supported else list(supported)

        # Preserve current state
        global current_language, main_map_generator
        original_language = current_language

        last_result = None
        for lang in langs:
            try:
                current_language = lang
                translation_system.set_language(lang)
                # Re-init generator for this language
                main_map_generator = get_main_map_generator()
                last_result = main_map_generator.reset_continent()
            except Exception:
                logging.exception(f"Reset failed for language {lang}")

        # Restore original language and output path
        try:
            current_language = original_language
            translation_system.set_language(original_language)
            main_map_generator = get_main_map_generator()
        except Exception:
            pass
        # Invalidate overlay caches if any
        try:
            from backend.city_overlay_analyzer import city_overlay_analyzer
            city_overlay_analyzer.invalidate_cache()
        except Exception:
            pass
        # Clear hex service cache after reset
        hex_service.hex_data_cache.clear()
        hex_manager.clear_cache()
        logging.info("Continent reset for languages %s and caches cleared.", langs)
        return jsonify(last_result or { 'ok': True })
    except Exception as e:
        logging.error(f"Error resetting continent: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/hex/<hex_code>')
def get_hex_info(hex_code):
    if not validate_hex_code(hex_code):
        return jsonify({'error': 'Invalid hex code format'}), 400

    # Prefer language-specific output path if it exists
    # Resolve language-specific output directory using {lang} stub if present
    lang_output = get_output_dir_for_language(current_language)
    chosen_hex_dir = (lang_output / "hexes")

    hex_data = hex_service.get_hex_dict(hex_code)
    if hex_data:
        # Add raw markdown if available
        hex_file_path = chosen_hex_dir / f"hex_{hex_code}.md"
        if hex_file_path.exists():
            from backend.utils import safe_file_read
            hex_data['raw_markdown'] = safe_file_read(hex_file_path)
        return jsonify(hex_data)

    # If not in cache, check for a hex file and parse it for content
    hex_file_path = chosen_hex_dir / f"hex_{hex_code}.md"
    if hex_file_path.exists():
        from backend.utils import safe_file_read
        content = safe_file_read(hex_file_path)
        hex_type = _determine_hex_type(content)
        
        # Base response with raw markdown
        base_response = {
            "hex_code": hex_code,
            "raw_markdown": content,
            "exists": True
        }
        
        if hex_type == 'settlement':
            parsed = extract_settlement_data(content)
            return jsonify({
                **base_response,
                "hex_type": "settlement",
                "content_type": "settlement",
                "is_settlement": True,
                "is_major_city": False,
                "terrain": parsed.get('terrain', 'unknown'),
                "name": parsed.get('name'),
                "description": parsed.get('description'),
                "population": parsed.get('population'),
                "atmosphere": parsed.get('atmosphere'),
                "notable_feature": parsed.get('notable_feature'),
                "local_tavern": parsed.get('local_tavern'),
                "local_power": parsed.get('local_power'),
                "settlement_art": parsed.get('settlement_art'),
                # Mörk Borg settlement fields
                "weather": parsed.get('weather'),
                "city_event": parsed.get('city_event'),
                "tavern_details": parsed.get('tavern_details'),
            })
        elif hex_type == 'beast':
            parsed = extract_beast_data(content)
            return jsonify({
                **base_response,
                "hex_type": "beast",
                "content_type": "beast",
                "is_beast": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "beast_type": parsed.get('beast_type'),
                "beast_feature": parsed.get('beast_feature'),
                "beast_behavior": parsed.get('beast_behavior'),
                "denizen": parsed.get('denizen'),
                "territory": parsed.get('territory'),
                "threat_level": parsed.get('threat_level'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
                "loot": parsed.get('loot'),
                "magical_effect": parsed.get('magical_effect'),
                # Beast specific fields
                "treasure_found": parsed.get('treasure_found'),
                "beast_art": parsed.get('beast_art'),
            })
        elif hex_type == 'dungeon':
            parsed = extract_dungeon_data(content)
            return jsonify({
                **base_response,
                "hex_type": "dungeon",
                "content_type": "dungeon",
                "is_dungeon": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "dungeon_type": parsed.get('dungeon_type'),
                "denizen": parsed.get('denizen'),
                "danger": parsed.get('danger'),
                "atmosphere": parsed.get('atmosphere'),
                "notable_feature": parsed.get('notable_feature'),
                "treasure": parsed.get('treasure'),
                "ancient_knowledge": parsed.get('ancient_knowledge'),
                "loot": parsed.get('loot'),
                "magical_effect": parsed.get('magical_effect'),
                "description": parsed.get('description'),
                # Mörk Borg trap information
                "trap_section": parsed.get('trap_section'),
            })
        elif hex_type == 'npc':
            parsed = extract_npc_data(content)
            return jsonify({
                **base_response,
                "hex_type": "npc",
                "is_npc": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "encounter": parsed.get('encounter'),
                "name": parsed.get('name'),
                "denizen_type": parsed.get('denizen_type'),
                # Mörk Borg NPC fields
                "trait": parsed.get('trait'),
                "concern": parsed.get('concern'),
                "want": parsed.get('want'),
                "apocalypse_attitude": parsed.get('apocalypse_attitude'),
                "secret": parsed.get('secret'),
                # Fallback fields
                "motivation": parsed.get('motivation'),
                "feature": parsed.get('feature'),
                "demeanor": parsed.get('demeanor'),
                "key_npcs": parsed.get('key_npcs'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
                "description": parsed.get('description'),
                "denizen": parsed.get('denizen'),
                # Additional NPC fields
                "carries": parsed.get('carries'),
                "location": parsed.get('location'),
            })
        elif hex_type == 'sea_encounter':
            # Use hex_service for consistent parsing
            hex_data = hex_service.get_hex_dict(hex_code)
            if hex_data:
                hex_data['raw_markdown'] = content
                return jsonify(hex_data)
            else:
                return jsonify({'error': 'Sea encounter not found'}), 404
        elif hex_type == 'ruins':
            parsed = extract_ruins_data(content)
            return jsonify({
                **base_response,
                "hex_type": "ruins",
                "is_ruins": True,
                "terrain": parsed.get('terrain', 'unknown'),
                "description": parsed.get('description'),
                "danger": parsed.get('danger'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
            })
        else:
            parsed = extract_hex_data(content)
            return jsonify({
                **base_response,
                "terrain": parsed.get('terrain', 'unknown'),
                "hex_type": "wilderness",
                "is_settlement": False,
                "is_major_city": False,
                "description": parsed.get('description'),
                "encounter": parsed.get('encounter'),
                "notable_feature": parsed.get('notable_feature'),
                "atmosphere": parsed.get('atmosphere'),
            })

    # If file still not found, generate on-demand and return
    try:
        generated = main_map_generator.generate_single_hex(hex_code)
        # Re-read via service (lazy parser will pick up from filesystem)
        hex_service.hex_data_cache.pop(hex_code, None)
        from backend.hex_model import hex_manager
        hex_manager.clear_cache()
        generated_dict = hex_service.get_hex_dict(hex_code)
        if generated_dict:
            # Attach raw markdown if just generated
            gen_path = chosen_hex_dir / f"hex_{hex_code}.md"
            if gen_path.exists():
                from backend.utils import safe_file_read
                generated_dict['raw_markdown'] = safe_file_read(gen_path)
            return jsonify(generated_dict)
    except Exception:
        # fall through to default response
        pass

    # Default fallback for missing hexes
    return jsonify({
        "hex_code": hex_code,
        "terrain": "unknown",
        "exists": True,
        "hex_type": "wilderness",
        "is_settlement": False,
        "is_major_city": False,
        "description": None,
        "encounter": None,
        "notable_feature": None,
        "atmosphere": None,
        "raw_markdown": None,
    })

@api_bp.route('/terrain-debug')
def terrain_debug():
    try:
        ts = terrain_module.terrain_system
        ia = getattr(ts, 'image_analyzer', None)
        info = {
            'use_image_analysis': getattr(ts, 'use_image_analysis', False),
            'map_dimensions': [getattr(ts, 'map_width', None), getattr(ts, 'map_height', None)],
            'image_path': getattr(ia, 'map_image_path', None) if ia else None,
            'image_loaded': bool(getattr(ia, 'map_image', None)) if ia else False,
            'mapping_mode': getattr(ts, 'image_analyzer', None).mapping_mode if ia else None,
        }
        # Include ImageAnalyzer map info if available
        if ia and hasattr(ia, 'get_map_info'):
            try:
                info['map_info'] = ia.get_map_info()
            except Exception:
                pass
        return jsonify({'success': True, 'terrain_system': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/set-language', methods=['POST'])
def set_language():
    """Set the current language for content generation."""
    global current_language, main_map_generator
    
    data = request.get_json()
    new_language = data.get('language', 'en')
    
    if new_language in ['en', 'pt']:
        current_language = new_language
        # Update translation system
        translation_system.set_language(new_language)
        # Re-initialize main map generator with new language
        main_map_generator = get_main_map_generator()
        # Clear caches so services reload from the new language directory
        try:
            hex_service.hex_data_cache.clear()
            hex_manager.clear_cache()
        except Exception:
            pass
        # Update city overlay analyzer with new language
        from backend.city_overlay_analyzer import city_overlay_analyzer
        from backend.database_manager import database_manager
        city_overlay_analyzer.language = new_language
        city_overlay_analyzer.content_tables = database_manager.load_tables(new_language)
        
        return jsonify({
            'success': True,
            'language': current_language,
            'message': f'Language set to {current_language}'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid language. Use "en" or "pt"'
        }), 400

@api_bp.route('/city/<hex_code>')
def get_city_details(hex_code):
    """Get detailed information for a major city."""
    city_data = hex_service.get_city_details(hex_code)
    
    if city_data:
        return jsonify(city_data)
    else:
        return jsonify({'success': False, 'error': 'Not a major city'}), 404

@api_bp.route('/settlement/<hex_code>')
def get_settlement_details(hex_code):
    """Get detailed information for a settlement."""
    # Try model-based service first
    settlement_data = hex_service.get_settlement_details(hex_code)
    if settlement_data:
        return jsonify(settlement_data)

    # Fallback: read and parse the hex markdown directly if present
    try:
        from backend.utils import safe_file_read
        hex_file_path = config.paths.output_path \
            / "hexes" / f"hex_{hex_code}.md"
        if hex_file_path.exists():
            content = safe_file_read(hex_file_path)
            if '⌂ **' in content:
                parsed = extract_settlement_data(content)
                return jsonify({
                    'success': True,
                    'settlement': {
                        'name': parsed.get('name', ''),
                        'description': parsed.get('description', ''),
                        'population': parsed.get('population', ''),
                        'atmosphere': parsed.get('atmosphere', ''),
                        'notable_feature': parsed.get('notable_feature', ''),
                        'local_tavern': parsed.get('local_tavern', ''),
                        'local_power': parsed.get('local_power', ''),
                        'settlement_art': parsed.get('settlement_art', ''),
                        # Mörk Borg settlement fields
                        'weather': parsed.get('weather'),
                        'city_event': parsed.get('city_event'),
                        'tavern_details': parsed.get('tavern_details')
                    }
                })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

        return jsonify({'success': False, 'error': 'Not a settlement or not found'}), 404

@api_bp.route('/hex/<hex_code>', methods=['PUT'])
def update_hex_content(hex_code):
    """Update hex content with new markdown."""
    if not validate_hex_code(hex_code):
        return jsonify({'error': 'Invalid hex code format'}), 400
    
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing content field'}), 400
        
        content = data['content']
        
        # Write the content to the hex file
        hex_file_path = config.paths.output_path / "hexes" / f"hex_{hex_code}.md"
        hex_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(hex_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Clear the cache for this hex
        hex_service.clear_hex_cache(hex_code)
        
        return jsonify({
            'success': True,
            'message': f'Hex {hex_code} updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to update hex: {str(e)}'}), 500

@api_bp.route('/lore-overview')
def get_lore_overview():
    """Get overview of lore and world information."""
    try:
        # Get major cities
        major_cities = [city_data['name'] for city_data in lore_db.major_cities.values()]
        
        # Get factions (this would need to be implemented based on your lore structure)
        factions = ['The Church of the Basilisk', 'The Heretical Priests', 'The Mercenary Companies']
        
        # Get notable NPCs (this would need to be implemented based on your lore structure)
        notable_npcs = ['The Basilisk', 'The Queen', 'The King']
        
        # Get regional lore (this would need to be implemented based on your lore structure)
        regional_lore = ['The Dying Lands', 'The Two-Headed Basilisks', 'The End Times']
        
        return jsonify({
            'success': True,
            'lore': {
                'major_cities': major_cities,
                'factions': factions,
                'notable_npcs': notable_npcs,
                'regional_lore': regional_lore
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/city-overlays')
def get_city_overlays():
    overlays = [
        {"name": key, "display_name": city["name"]}
        for key, city in lore_db.major_cities.items()
    ]
    return jsonify({"success": True, "overlays": overlays})

@api_bp.route('/city-overlay/<overlay_name>')
def get_city_overlay(overlay_name):
    try:
        if city_overlay_analyzer is None:
            return jsonify({'success': False, 'error': f'City overlay analyzer unavailable: {_CITY_OVERLAY_IMPORT_ERROR}'}), 500
        
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        if not overlay_data:
            
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        if not overlay_data:
            return jsonify({'success': False, 'error': 'Failed to generate overlay data'}), 404

        

        compact_overlay = {
            'name': overlay_data['name'],
            'display_name': overlay_data['display_name'],
            'filename': overlay_data['filename'],
            'grid_type': overlay_data.get('grid_type', 'round'),
            'radius': overlay_data.get('radius', 3),
            'hex_grid': {},
            'total_hexes': overlay_data['total_hexes']
        }
        for hex_id, hex_data in overlay_data['hex_grid'].items():
            content = hex_data.get('content', {})
            compact_overlay['hex_grid'][hex_id] = {
                'id': hex_data.get('id', hex_id),
                'row': hex_data.get('row', 0),
                'col': hex_data.get('col', 0),
                'district': hex_data.get('district', 'unknown'),  # Include district information
                'content': {
                    'name': content.get('name', 'Unknown'),
                    'type': content.get('type', 'unknown'),
                    'description': content.get('description', 'No description available'),
                    'encounter': content.get('encounter', 'No encounter available'),
                    'atmosphere': content.get('atmosphere', 'No atmosphere available'),
                    'position_type': content.get('position_type', 'unknown')
                }
            }
            # Truncate long text fields
            if len(compact_overlay['hex_grid'][hex_id]['content']['description']) > 200:
                compact_overlay['hex_grid'][hex_id]['content']['description'] = compact_overlay['hex_grid'][hex_id]['content']['description'][:200] + '...'
            if len(compact_overlay['hex_grid'][hex_id]['content']['encounter']) > 150:
                compact_overlay['hex_grid'][hex_id]['content']['encounter'] = compact_overlay['hex_grid'][hex_id]['content']['encounter'][:150] + '...'
            if len(compact_overlay['hex_grid'][hex_id]['content']['atmosphere']) > 100:
                compact_overlay['hex_grid'][hex_id]['content']['atmosphere'] = compact_overlay['hex_grid'][hex_id]['content']['atmosphere'][:100] + '...'
        
           
        return create_overlay_response(compact_overlay)
    except Exception as e:
        return handle_exception_response(e, "loading city overlay")

@api_bp.route('/city-overlay/<overlay_name>/ascii')
def get_city_overlay_ascii(overlay_name):
    try:
        if city_overlay_analyzer is None:
            return jsonify({'success': False, 'error': f'City overlay analyzer unavailable: {_CITY_OVERLAY_IMPORT_ERROR}'}), 500
        ascii_view = city_overlay_analyzer.get_overlay_ascii_view(overlay_name)
        return jsonify({
            'success': True,
            'ascii': ascii_view
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/city-context/<city_name>')
def get_city_context(city_name):
    """Get city context information for the left panel."""
    try:
        if city_overlay_analyzer is None:
            return jsonify({'success': False, 'error': f'City overlay analyzer unavailable: {_CITY_OVERLAY_IMPORT_ERROR}'}), 500
        context = city_overlay_analyzer.get_city_context(city_name)
        response = jsonify({
            'success': True,
            'context': context
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/city-overlay/<overlay_name>/hex/<hex_id>')
def get_city_overlay_hex(overlay_name, hex_id):
    try:
        if city_overlay_analyzer is None:
            return jsonify({'success': False, 'error': f'City overlay analyzer unavailable: {_CITY_OVERLAY_IMPORT_ERROR}'}), 500
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        if not overlay_data:
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        hex_data = overlay_data['hex_grid'].get(hex_id)
        if not hex_data:
            return jsonify({'success': False, 'error': 'Hex not found'})
        
        # Return only hex-specific content (remove city context)
        hex_content = hex_data.get('content', {})
        hex_specific_data = {
            'id': hex_data.get('id', hex_id),
            'row': hex_data.get('row', 0),
            'col': hex_data.get('col', 0),
            'district': hex_data.get('district', 'unknown'),
            'content': {
                'name': hex_content.get('name', 'Unknown'),
                'type': hex_content.get('type', 'unknown'),
                'description': hex_content.get('description', 'No description available'),
                'encounter': hex_content.get('encounter', 'No encounter available'),
                'atmosphere': hex_content.get('atmosphere', 'No atmosphere available'),
                'position_type': hex_content.get('position_type', 'unknown'),
                # Hex-specific enriched content
                'weather': hex_content.get('weather'),
                'city_event': hex_content.get('city_event'),
                                            'npc_name': hex_content.get('npc_name'),
                            'npc_trade': hex_content.get('npc_trade'),
                            'npc_trait': hex_content.get('npc_trait'),
                            'npc_concern': hex_content.get('npc_concern'),
                            'npc_want': hex_content.get('npc_want'),
                            'npc_secret': hex_content.get('npc_secret'),
                            'npc_affiliation': hex_content.get('npc_affiliation'),
                            'npc_attitude': hex_content.get('npc_attitude'),
                'tavern_menu': hex_content.get('tavern_menu'),
                'tavern_innkeeper': hex_content.get('tavern_innkeeper'),
                'tavern_patron': hex_content.get('tavern_patron'),
                'related_hexes': hex_content.get('related_hexes'),
                'random_table': hex_content.get('random_table'),
                'notable_features': hex_content.get('notable_features'),
                # Additional fields
                'population': hex_content.get('population'),
                'services': hex_content.get('services'),
                'items_sold': hex_content.get('items_sold'),
                'beast_prices': hex_content.get('beast_prices'),
                'key_npcs': hex_content.get('key_npcs'),
                'active_factions': hex_content.get('active_factions'),
                'patrons': hex_content.get('patrons')
            }
        }
        
        response = jsonify({
            'success': True,
            'hex': hex_specific_data
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/regenerate-hex/<overlay_name>/<hex_id>', methods=['POST'])
def regenerate_hex(overlay_name, hex_id):
    """Regenerate a specific hex in a city overlay."""
    try:
        if city_overlay_analyzer is None:
            return jsonify({'success': False, 'error': f'City overlay analyzer unavailable: {_CITY_OVERLAY_IMPORT_ERROR}'}), 500
        # Load or generate the city overlay
        overlay_data = city_overlay_analyzer.load_overlay_data(overlay_name)
        if not overlay_data:
            overlay_data = city_overlay_analyzer.generate_city_overlay(overlay_name)
        
        # Parse hex_id to get row and column
        try:
            # hex_id format is typically "row_col" (e.g., "0_0", "1_2")
            row, col = map(int, hex_id.split('_'))
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid hex ID format'}), 400
        
        # Load city data for context
        city_data = city_overlay_analyzer.load_city_database(overlay_name.lower())
        
        # Generate new content for the hex
        # First, determine if this is a district hex or position-based hex
        district_name = None
        if 'district_matrix' in overlay_data:
            # Check if this position has a district
            matrix = overlay_data['district_matrix']
            if 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
                district_name = matrix[row][col]
        
        if district_name and district_name.lower() not in ['empty', 'unknown']:
            # Generate district-based content
            new_hex_data = city_overlay_analyzer.generate_district_based_content(
                district_name, row, col, overlay_name, city_data
            )
        else:
            # Generate position-based content
            radius = overlay_data.get('radius', 3)
            distance = city_overlay_analyzer.hex_distance(row, col, radius, radius)
            new_hex_data = city_overlay_analyzer.generate_position_based_content(
                row, col, distance, radius, overlay_name, city_data
            )
        
        # Update the overlay data with the new hex
        overlay_data['hex_grid'][hex_id] = new_hex_data
        
        # Save the updated overlay data
        city_overlay_analyzer.save_overlay_data(overlay_name, overlay_data)
        
        return jsonify({
            'success': True,
            'hex_data': new_hex_data,
            'message': f'Hex {hex_id} regenerated successfully'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/regenerate-overlay/<overlay_name>', methods=['POST'])
def regenerate_overlay(overlay_name):
    """Regenerate an entire city overlay."""
    try:
        if city_overlay_analyzer is None:
            return jsonify({'success': False, 'error': f'City overlay analyzer unavailable: {_CITY_OVERLAY_IMPORT_ERROR}'}), 500
          
        # Regenerate the entire overlay
        overlay_data = city_overlay_analyzer.regenerate_overlay(overlay_name)
        
        return jsonify({
            'success': True,
            'message': f'Overlay {overlay_name} regenerated successfully',
            'overlay_data': {
                'name': overlay_data['name'],
                'display_name': overlay_data['display_name'],
                'total_hexes': overlay_data['total_hexes']
            }
        })
        
    except Exception as e:
        print(f"Error regenerating overlay: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== HELPER FUNCTIONS =====

def _get_major_city_info(hex_code: str, hardcoded: dict) -> dict:
    city_key = hardcoded['city_key']
    city_data = lore_db.major_cities[city_key]
    return create_major_city_response(city_data, hex_code, current_language)

def _get_hex_file_info(hex_code: str, hex_file) -> dict:
    try:
        from backend.utils import safe_file_read
        content = safe_file_read(hex_file)
        if '⌂ **' in content:
            settlement_data = extract_settlement_data(content)
            return jsonify({
                'exists': True,
                'is_settlement': True,
                'hex_type': 'settlement',
                'terrain': 'unknown',
                'title': settlement_data['name'],
                'description': settlement_data['description'],
                'population': settlement_data['population'],
                'atmosphere': settlement_data['atmosphere'],
                'notable_feature': settlement_data['notable_feature'],
                'local_tavern': settlement_data['local_tavern'],
                'local_power': settlement_data['local_power'],
                'settlement_art': settlement_data['settlement_art'],
                'hex_code': hex_code,
                'redirect_to': 'settlement'
            })
        try:
            import markdown
            html = markdown.markdown(content, extensions=['codehilite', 'fenced_code', 'tables'])
        except ImportError:
            html = f'<pre>{content}</pre>'
        title = extract_title(content)
        hex_data = extract_hex_data(content)
        hex_type = _determine_hex_type(content)
        terrain = hex_data.get('terrain', 'unknown')
        terrain_name = main_map_generator._get_translated_terrain_name(terrain)
        response_data = {
            'exists': True,
            'is_major_city': False,
            'is_settlement': hex_type == 'settlement',
            'is_dungeon': hex_type == 'dungeon',
            'is_beast': hex_type == 'beast',
            'is_npc': hex_type == 'npc',
            'hex_type': hex_type,
            'title': title,
            'html': html,
            'raw': content,
            'terrain': terrain,
            'terrain_name': terrain_name,
            'hex_code': hex_code,
            'encounter': hex_data.get('encounter', 'Unknown encounter'),
            'denizen': hex_data.get('denizen', 'No denizen information'),
            'notable_feature': hex_data.get('notable_feature', 'No notable features'),
            'atmosphere': hex_data.get('atmosphere', 'Unknown atmosphere'),
            'loot': hex_data.get('loot'),
            'scroll': hex_data.get('scroll'),
            'threat_level': hex_data.get('threat_level'),
            'territory': hex_data.get('territory'),
            'danger': hex_data.get('danger'),
            'treasure': hex_data.get('treasure'),
            'beast_type': hex_data.get('beast_type'),
            'beast_feature': hex_data.get('beast_feature'),
            'beast_behavior': hex_data.get('beast_behavior'),
            'dungeon_type': hex_data.get('dungeon_type'),
            'encounter_type': hex_data.get('encounter_type'),
            'name': hex_data.get('name'),
            'denizen_type': hex_data.get('denizen_type'),
            'motivation': hex_data.get('motivation'),
            'feature': hex_data.get('feature'),
            'demeanor': hex_data.get('demeanor'),
            'carries': hex_data.get('carries'),
            'local_tavern': hex_data.get('local_tavern'),
            'local_power': hex_data.get('local_power'),
            'ancient_knowledge': hex_data.get('ancient_knowledge'),
            'hex_data': hex_data
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': f'Failed to read hex file: {e}'}), 500

def generate_ascii_map_data():
    # Use centralized grid generator for base grid
    base_grid = generate_hex_grid(lore_db)
    
    # Process each hex to add content-specific information
    for hex_code, hex_data in base_grid.items():
        if hex_data.get('is_city'):
            # Major city - add city-specific data
            city_data = hex_data['city_data']
            hex_data.update({
                'terrain': normalize_terrain_name(hex_data['terrain']),
                'symbol': '◆',
                'city_name': city_data['name'],
                'population': city_data['population'],
                'region': city_data['region'],
                'has_content': True,
                'css_class': 'major-city'
            })
        else:
            # Regular terrain - check for generated content
            terrain = terrain_system.get_terrain_for_hex(hex_code, lore_db)
            hex_file_exists = (config.paths.output_path / "hexes" / f"hex_{hex_code}.md").exists()
            has_loot = False
            content_type = None
            
            if hex_file_exists:
                with open(config.paths.output_path / "hexes" / f"hex_{hex_code}.md", "r", encoding="utf-8") as f:
                    content = f.read()
                hex_data_content = extract_hex_data(content)
                terrain = normalize_terrain_name(hex_data_content.get('terrain', 'unknown'))
                content_type = get_hex_content_type(hex_code)
                has_loot = check_hex_has_loot(hex_code)
            
            # Use centralized symbol and CSS class determination
            symbol = determine_content_symbol(content_type, terrain) if hex_file_exists else get_terrain_symbol(terrain)
            css_class = determine_css_class(content_type, terrain)
            if has_loot:
                css_class += ' has-content'
            
            hex_data.update({
                'terrain': terrain,
                'symbol': symbol,
                'has_content': has_loot,
                'content_type': content_type,
                'css_class': css_class
            })
    
    if not isinstance(base_grid, dict):
        return {}
    return base_grid

def get_major_cities_data():
    cities = []
    # Load cities from database manager with current language
    from backend.database_manager import database_manager
    cities_table = database_manager.get_table('cities', 'major_cities', current_language)
    
    for city in cities_table:
        if isinstance(city, dict):
            cities.append({
                'key': city.get('key', ''),
                'name': city.get('name', ''),
                'coordinates': city.get('coordinates', [0, 0]),
                'population': city.get('population', 'Unknown'),
                'region': city.get('region', 'central')
            })
    return cities

def extract_title(content: str) -> str:
    return extract_title_from_content(content)

def extract_hex_data(content):
    """Extract structured data from hex content."""
    if not content:
        return {}
    data = {}
    def extract_field(field):
        # Matches both 'Field: value' and '**Field:** value' (Markdown bold)
        pattern = rf'(?:\*\*)?{field}:(?:\*\*)?\s*([^\n]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    # Extract terrain in both English and Portuguese
    terrain = extract_field('Terrain')
    if not terrain:
        terrain = extract_field('Terreno')
    data['terrain'] = terrain
    data['features'] = extract_field('Notable Features?')
    data['encounters'] = extract_field('Encounters?')
    data['resources'] = extract_field('Resources?')
    return data

def extract_settlement_data(content):
    """Extract settlement-specific data from content."""
    if not content:
        return {}
    
    # Use the hex_service method for consistent extraction
    from backend.hex_service import hex_service
    return hex_service._extract_settlement_data(content, "temp")

def _determine_hex_type(content: str) -> str:
    return determine_hex_type(content)

def get_terrain_symbol(terrain):
    return terrain_system.get_terrain_symbol(terrain)

# Use centralized content detector utilities
# check_hex_has_loot and get_hex_content_type are now imported from utils.content_detector 

# Extraction stubs for missing types

def extract_beast_data(content):
    data = {}
    beast_type_match = re.search(r'## Beast Details\n\*\*Type:\*\*\s*([^\n]+)', content)
    if beast_type_match:
        data['beast_type'] = beast_type_match.group(1).strip()
    feature_match = re.search(r'## Beast Details\n.*\*\*Feature:\*\*\s*([^\n]+)', content)
    if feature_match:
        data['beast_feature'] = feature_match.group(1).strip()
    behavior_match = re.search(r'## Beast Details\n.*\*\*Behavior:\*\*\s*([^\n]+)', content)
    if behavior_match:
        data['beast_behavior'] = behavior_match.group(1).strip()
    threat_level_match = re.search(r'## Threat Level\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if threat_level_match:
        data['threat_level'] = threat_level_match.group(1).strip()
    territory_match = re.search(r'## Territory\n(.+?)(?:\n##|$)', content, re.DOTALL)
    if territory_match:
        data['territory'] = territory_match.group(1).strip()
    # Use centralized content parser for common fields
    parsed_sections = parse_content_sections(content)
    data.update(parsed_sections)
    
    # Parse loot and magical effect
    loot_data = parse_loot_section(content)
    if loot_data:
        data['loot'] = loot_data
    
    magical_effect = parse_magical_effect(content)
    if magical_effect:
        data['magical_effect'] = magical_effect
    return data

def extract_dungeon_data(content):
    data = {}
    dungeon_type_match = re.search(r'## Dungeon Details\n\*\*Type:\*\*\s*([^\n]+)', content)
    if dungeon_type_match:
        data['dungeon_type'] = dungeon_type_match.group(1).strip()
    danger_match = re.search(r'## Dungeon Details\n.*\*\*Danger:\*\*\s*([^\n]+)', content)
    if danger_match:
        data['danger'] = danger_match.group(1).strip()
    treasure_match = re.search(r'## Dungeon Details\n.*\*\*Treasure:\*\*\s*([^\n]+)', content)
    if treasure_match:
        data['treasure'] = treasure_match.group(1).strip()
    
    # Mörk Borg trap information
    trap_section_match = re.search(r'## Trap\n\*\*Description:\*\*\s*([^\n]+).*\*\*Effect:\*\*\s*([^\n]+).*\*\*Builder:\*\*\s*([^\n]+)', content, re.DOTALL)
    if trap_section_match:
        data['trap_section'] = {
            'description': trap_section_match.group(1).strip(),
            'effect': trap_section_match.group(2).strip(),
            'builder': trap_section_match.group(3).strip()
        }
    
    # Ancient Knowledge
    ancient_knowledge_match = re.search(r'## Ancient Knowledge\n\*\*Type:\*\*\s*([^\n]+).*\*\*Content:\*\*\s*([^\n]+).*\*\*Effect:\*\*\s*([^\n]+).*\*\*Description:\*\*\s*([^\n]+)', content, re.DOTALL)
    if ancient_knowledge_match:
        data['ancient_knowledge'] = {
            'type': ancient_knowledge_match.group(1).strip(),
            'content': ancient_knowledge_match.group(2).strip(),
            'effect': ancient_knowledge_match.group(3).strip(),
            'description': ancient_knowledge_match.group(4).strip()
        }
    # Use centralized content parser for common fields
    parsed_sections = parse_content_sections(content)
    data.update(parsed_sections)
    
    # Parse loot and magical effect
    loot_data = parse_loot_section(content)
    if loot_data:
        data['loot'] = loot_data
    
    magical_effect = parse_magical_effect(content)
    if magical_effect:
        data['magical_effect'] = magical_effect
    return data

def extract_npc_data(content):
    data = {}
    name_match = re.search(r'\*\*Name:\*\*\s*([^\n]+)', content)
    if name_match:
        data['name'] = name_match.group(1).strip()
    type_match = re.search(r'\*\*Type:\*\*\s*([^\n]+)', content)
    if type_match:
        data['denizen_type'] = type_match.group(1).strip()
    
    # Mörk Borg NPC fields
    trait_match = re.search(r'\*\*Trait:\*\*\s*([^\n]+)', content)
    if trait_match:
        data['trait'] = trait_match.group(1).strip()
    concern_match = re.search(r'\*\*Concern:\*\*\s*([^\n]+)', content)
    if concern_match:
        data['concern'] = concern_match.group(1).strip()
    want_match = re.search(r'\*\*Want:\*\*\s*([^\n]+)', content)
    if want_match:
        data['want'] = want_match.group(1).strip()
    apocalypse_attitude_match = re.search(r'\*\*Apocalypse Attitude:\*\*\s*([^\n]+)', content)
    if apocalypse_attitude_match:
        data['apocalypse_attitude'] = apocalypse_attitude_match.group(1).strip()
    secret_match = re.search(r'\*\*Secret:\*\*\s*([^\n]+)', content)
    if secret_match:
        data['secret'] = secret_match.group(1).strip()
    
    # Fallback to old fields if new ones not available
    motivation_match = re.search(r'\*\*Motivation:\*\*\s*([^\n]+)', content)
    if motivation_match:
        data['motivation'] = motivation_match.group(1).strip()
    feature_match = re.search(r'\*\*Feature:\*\*\s*([^\n]+)', content)
    if feature_match:
        data['feature'] = feature_match.group(1).strip()
    demeanor_match = re.search(r'\*\*Demeanor:\*\*\s*([^\n]+)', content)
    if demeanor_match:
        data['demeanor'] = demeanor_match.group(1).strip()
    
    location_match = re.search(r'\*\*Location:\*\*\s*([^\n]+)', content)
    if location_match:
        data['location'] = location_match.group(1).strip()
    key_npcs_match = re.search(r'\*\*Key NPCs:\*\*\s*([^\n]+)', content)
    if key_npcs_match:
        data['key_npcs'] = [npc.strip() for npc in key_npcs_match.group(1).split(',')]
    
    # Use centralized content parser for common fields
    parsed_sections = parse_content_sections(content)
    data.update(parsed_sections)
    return data



def extract_ruins_data(content):
    """Extract ruins-specific data from content."""
    data = {}
    
    # Parse ruins-specific fields
    ruins_type_match = re.search(r'\*\*Type:\*\*\s*([^\n]+)', content)
    if ruins_type_match:
        data['ruins_type'] = ruins_type_match.group(1).strip()
    
    age_match = re.search(r'\*\*Age:\*\*\s*([^\n]+)', content)
    if age_match:
        data['age'] = age_match.group(1).strip()
    
    builder_match = re.search(r'\*\*Builder:\*\*\s*([^\n]+)', content)
    if builder_match:
        data['builder'] = builder_match.group(1).strip()
    
    # Use centralized content parser for common fields
    parsed_sections = parse_content_sections(content)
    data.update(parsed_sections)
    
    # Parse loot and magical effect
    loot_data = parse_loot_section(content)
    if loot_data:
        data['loot'] = loot_data
    
    magical_effect = parse_magical_effect(content)
    if magical_effect:
        data['magical_effect'] = magical_effect
    
    return data

# Translation API Routes
@api_bp.route('/translations/ui/<language>', methods=['GET'])
def get_ui_translations(language):
    """Get UI translations for the specified language."""
    try:
        # Validate language
        if language not in translation_system.get_supported_languages():
            language = 'en'  # fallback to English
        
        # Get UI translations
        ui_translations = translation_system.get_ui_translations(language)
        
        return jsonify(ui_translations)
        
    except Exception as e:
        logging.error(f"Error getting UI translations for language {language}: {e}")
        # Return empty dict on error, frontend will use defaults
        return jsonify({}) 