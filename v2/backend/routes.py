#!/usr/bin/env python3
"""Minimal API surface for v2 (markdown-only)."""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Tuple

from flask import Blueprint, current_app, jsonify, request, send_file, send_from_directory

from .cache import BootCache
from .config import AppConfig
from .generation import ensure_generated
from .translation_system import translation_system
from .hex_service import hex_service
from .lore_database import LoreDatabase
from .database_manager import database_manager

api_bp = Blueprint("api", __name__, url_prefix="/api")
web_bp = Blueprint(
    "web",
    __name__,
    static_folder=str(Path(__file__).resolve().parent / "web" / "static"),
    static_url_path="/static",
)


def _cfg() -> AppConfig:
    return current_app.config["HEXY_CONFIG"]


def _get_language(cfg: AppConfig) -> str:
    lang = request.args.get("language") or request.headers.get("X-Hexy-Language") or cfg.language
    if lang not in cfg.supported_languages:
        lang = cfg.language
    return lang


def _hex_path(cfg: AppConfig, lang: str, hex_code: str) -> Path:
    return cfg.paths.output_path / lang / "hexes" / f"hex_{hex_code}.md"


def _load_city_data(city_name: str, lang: str) -> Dict[str, Any]:
    """Load city JSON file and encounter tables. NO processing, NO logic."""
    cfg = _cfg()
    city_path = cfg.paths.database_path / "cities" / lang / f"{city_name.lower()}.json"
    
    if not city_path.exists():
        raise FileNotFoundError(f"City file not found: {city_path}")
    
    with open(city_path, 'r', encoding='utf-8') as f:
        city_data = json.load(f)
    
    # Load all generic encounter tables
    encounter_types = [
        'building_encounters',
        'street_encounters',
        'landmark_encounters',
        'market_encounters',
        'temple_encounters',
        'tavern_encounters',
        'guild_encounters',
        'residence_encounters',
        'ruins_encounters',
        'district_encounters'
    ]
    
    encounter_tables = {}
    for encounter_type in encounter_types:
        table = database_manager.get_table('encounters', encounter_type, lang)
        if table:
            # Remove '_encounters' suffix for key
            key = encounter_type.replace('_encounters', '')
            encounter_tables[key] = table
    
    return {
        "city_data": city_data,
        "encounter_tables": encounter_tables
    }


def _city_key_for_hex(hex_code: str, lang: str) -> str | None:
    try:
        x = int(hex_code[:2])
        y = int(hex_code[2:])
    except Exception:
        return None
    lore = LoreDatabase()
    # ensure lore uses the same language
    translation_system.set_language(lang)
    for key, city in lore.major_cities.items():
        coords = city.get("coordinates") or city.get("coords")
        if not coords or len(coords) != 2:
            continue
        try:
            cx, cy = int(coords[0]), int(coords[1])
        except Exception:
            continue
        if cx == x and cy == y:
            return key
    return None


def _validate_hex_code(hex_code: str) -> Tuple[bool, str]:
    if re.fullmatch(r"\d{4}", hex_code):
        return True, hex_code
    return False, "Invalid hex code format; expected 4 digits like 1215"


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@api_bp.route("/languages", methods=["GET"])
def languages():
    cfg = _cfg()
    return jsonify({"languages": cfg.supported_languages, "current": cfg.language})


@api_bp.route("/set-language", methods=["POST"])
def set_language():
    cfg = _cfg()
    body = request.get_json(silent=True) or {}
    lang = body.get("language")
    if not lang or lang not in cfg.supported_languages:
        return jsonify({"error": "Invalid language", "supported": cfg.supported_languages}), 400
    cfg.language = lang
    translation_system.set_language(lang)
    # ensure cache for new language
    ensure_generated(cfg)
    try:
        hex_service.set_language(lang)
    except Exception:
        pass
    return jsonify({"success": True, "language": lang})


@api_bp.route("/map-dimensions", methods=["GET"])
def get_map_dimensions():
    """Get current map dimensions."""
    cfg = _cfg()
    width, height = cfg.get_map_dimensions()
    return jsonify({
        "width": width,
        "height": height,
        "dimensions": [width, height]
    })


@api_bp.route("/map-dimensions", methods=["POST"])
def set_map_dimensions():
    """Set map dimensions and trigger regeneration."""
    cfg = _cfg()
    body = request.get_json(silent=True) or {}
    
    # Support both {width, height} and {dimensions: [w, h]} formats
    if "dimensions" in body:
        dims = body["dimensions"]
        if not isinstance(dims, list) or len(dims) != 2:
            return jsonify({"error": "dimensions must be [width, height]"}), 400
        width, height = int(dims[0]), int(dims[1])
    elif "width" in body and "height" in body:
        width = int(body["width"])
        height = int(body["height"])
    else:
        return jsonify({"error": "Must provide 'dimensions' [width, height] or 'width' and 'height'"}), 400
    
    try:
        cfg.set_map_dimensions(width, height)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    # Clear cache to force regeneration with new dimensions
    from .cache import BootCache
    cache = BootCache(cfg)
    for language in cfg.supported_languages:
        cache_output, lock_file, manifest = cache._paths_for_language(language)
        try:
            if cache_output.exists():
                import shutil
                shutil.rmtree(cache_output, ignore_errors=True)
            if manifest.exists():
                manifest.unlink(missing_ok=True)
            if lock_file.exists():
                lock_file.unlink(missing_ok=True)
        except Exception:
            pass
    
    return jsonify({
        "success": True,
        "width": width,
        "height": height,
        "dimensions": [width, height],
        "message": "Map dimensions updated. Call /api/bootstrap to regenerate the map."
    })


@api_bp.route("/debug-cache", methods=["GET"])
def debug_cache():
    cfg = _cfg()
    cache = BootCache(cfg)
    info = cache.describe()
    if cache.manifest.exists():
        try:
            info["manifest_data"] = json.loads(cache.manifest.read_text(encoding="utf-8"))
        except Exception:
            info["manifest_data"] = None
    return jsonify(info)


@api_bp.route("/bootstrap", methods=["POST"])
def bootstrap():
    try:
        cfg = _cfg()
        # Check if force parameter is provided
        body = request.get_json(silent=True) or {}
        force = body.get("force", False)
        
        if force:
            # Clear cache and output to force regeneration
            cache = BootCache(cfg)
            for language in cfg.supported_languages:
                # Use the internal method to get paths (it's the only way to access them)
                cache_output, lock_file, manifest = cache._paths_for_language(language)
                # Remove cache and manifest to force regeneration
                try:
                    if cache_output.exists():
                        shutil.rmtree(cache_output, ignore_errors=True)
                    if manifest.exists():
                        manifest.unlink(missing_ok=True)
                    if lock_file.exists():
                        lock_file.unlink(missing_ok=True)
                    # Also clear output path to ensure fresh generation
                    output_path = cfg.paths.output_path / language
                    if output_path.exists():
                        shutil.rmtree(output_path, ignore_errors=True)
                except Exception as e:
                    # Log but continue - don't fail if cleanup has issues
                    print(f"Warning: Error clearing cache for {language}: {e}")
        
        result = ensure_generated(cfg)
        return jsonify(result)
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({"error": error_msg, "traceback": traceback.format_exc()}), 500


@api_bp.route("/hex/<hex_code>", methods=["GET"])
def get_hex(hex_code: str):
    valid, message = _validate_hex_code(hex_code)
    if not valid:
        return jsonify({"error": message}), 400

    cfg = _cfg()
    lang = _get_language(cfg)
    ensure_generated(cfg)

    hex_file = _hex_path(cfg, lang, hex_code)
    if not hex_file.exists():
        return jsonify({"error": "Hex not found", "hex_code": hex_code}), 404

    content = hex_file.read_text(encoding="utf-8")
    return jsonify({"hex_code": hex_code, "language": lang, "raw_markdown": content, "exists": True})


@api_bp.route("/map", methods=["GET"])
def get_map():
    cfg = _cfg()
    lang = _get_language(cfg)
    ensure_generated(cfg)
    ascii_path = cfg.paths.output_path / lang / "ascii_map.txt"
    if not ascii_path.exists():
        return jsonify({"error": "Map not found", "language": lang}), 404
    
    # Get terrain data for each hex from hex files
    terrain_map = {}
    hexes_dir = cfg.paths.output_path / lang / "hexes"
    if hexes_dir.exists():
        from .terrain_system import terrain_system
        lore_db = LoreDatabase()
        for hex_file in hexes_dir.glob("hex_*.md"):
            hex_code = hex_file.stem.replace("hex_", "")
            try:
                # Get terrain from hex file
                content = hex_file.read_text(encoding="utf-8")
                terrain_match = re.search(r'^\s*\*\*Terrain:\*\*\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
                if terrain_match:
                    terrain_name = terrain_match.group(1).strip()
                    # Normalize to lowercase terrain type
                    terrain = hex_service._extract_terrain(content)
                    terrain_map[hex_code] = terrain
                else:
                    # Fallback to terrain_system
                    terrain = terrain_system.get_terrain_for_hex(hex_code, lore_db)
                    terrain_map[hex_code] = terrain
            except Exception:
                # Fallback to terrain_system if file read fails
                try:
                    terrain = terrain_system.get_terrain_for_hex(hex_code, lore_db)
                    terrain_map[hex_code] = terrain
                except Exception:
                    terrain_map[hex_code] = "plains"
    
    # Load road data if available
    roads_file = cfg.paths.output_path / lang / "roads.json"
    road_hexes = []
    if roads_file.exists():
        try:
            road_hexes = json.loads(roads_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    return jsonify({
        "language": lang,
        "ascii": ascii_path.read_text(encoding="utf-8"),
        "terrain_map": terrain_map,
        "road_hexes": road_hexes
    })


# Export / Import (local-only)
@api_bp.route("/export", methods=["GET"])
def export_output_zip():
    cfg = _cfg()
    output_dir = cfg.paths.output_path
    if not output_dir.exists():
        return jsonify({"error": "Output directory not found"}), 404
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        base_name = "dying_lands_output"
        for root, _, files in os.walk(output_dir):
            for fname in files:
                full = Path(root) / fname
                rel = full.relative_to(output_dir)
                zf.write(str(full), arcname=str(Path(base_name) / rel))
        # Add placeholder for client cache (frontend will add it via separate endpoint or include in request)
        # For now, we'll add it via a separate endpoint that frontend can call
    mem.seek(0)
    ts = time.strftime("%Y%m%d%H%M%S")
    filename = f"dying_lands_output-{ts}.zip"
    return send_file(mem, mimetype="application/zip", as_attachment=True, download_name=filename)


@api_bp.route("/export-cache", methods=["GET"])
def export_cache():
    """Export frontend cache data as JSON."""
    cfg = _cfg()
    lang = _get_language(cfg)
    # Return a placeholder - frontend will call this and include cache data
    # Or frontend can export cache directly via cache.exportCacheData()
    return jsonify({"message": "Use frontend cache.exportCacheData() to get cache data"})


@api_bp.route("/import-cache", methods=["POST"])
def import_cache():
    """Import frontend cache data from JSON."""
    cfg = _cfg()
    body = request.get_json(silent=True) or {}
    cache_data = body.get("cacheData")
    language = body.get("language", _get_language(cfg))
    
    if not cache_data:
        return jsonify({"error": "Missing cacheData"}), 400
    
    # Return cache data to frontend for processing
    return jsonify({"ok": True, "cacheData": cache_data, "language": language})


@api_bp.route("/import", methods=["POST"])
def import_output_zip():
    cfg = _cfg()
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400
    file = request.files["file"]
    if not file.filename.lower().endswith(".zip"):
        return jsonify({"error": "File must be a .zip"}), 400
    data = file.read()
    tmpdir = Path(tempfile.mkdtemp(prefix="hexy-v2-import-"))
    cache_data = None
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            zf.extractall(tmpdir)
            # Check for client_cache.json in ZIP
            cache_file = tmpdir / "client_cache.json"
            if cache_file.exists():
                try:
                    cache_data = json.loads(cache_file.read_text(encoding="utf-8"))
                except Exception as e:
                    print(f"Warning: Failed to read client_cache.json: {e}")
        extracted_root = tmpdir / "dying_lands_output"
        src_dir = extracted_root if extracted_root.exists() else tmpdir
        if not any(p.is_dir() for p in src_dir.iterdir()):
            return jsonify({"error": "Archive appears empty"}), 400
        final_dir = cfg.paths.output_path
        final_dir.parent.mkdir(parents=True, exist_ok=True)
        backup = None
        if final_dir.exists():
            backup = final_dir.parent / f"{final_dir.name}.bak-{int(time.time())}"
            shutil.move(str(final_dir), str(backup))
        shutil.move(str(src_dir), str(final_dir))
        return jsonify({
            "ok": True,
            "backup": str(backup) if backup else None,
            "cacheData": cache_data
        })
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# City/Settlement/Overlay markdown-serving endpoints
def _read_markdown_file(path: Path):
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


@api_bp.route("/city-overlays", methods=["GET"])
def list_overlays():
    """List available cities from database. NO file system access."""
    cfg = _cfg()
    lang = _get_language(cfg)
    
    # Get cities from lore database
    lore = LoreDatabase()
    overlays = []
    for city_key, city_data in lore.major_cities.items():
        overlays.append({
            "name": city_key,
            "display_name": city_data.get("name", city_key),
            "filename": None  # No longer using files
        })
    
    return jsonify({"overlays": overlays, "language": lang})


@api_bp.route("/city-overlay/<overlay_name>", methods=["GET"])
def get_overlay(overlay_name: str):
    """Return raw city data. NO generation, NO logic."""
    cfg = _cfg()
    lang = _get_language(cfg)
    
    try:
        # Load city data (NO processing, NO logic)
        city_info = _load_city_data(overlay_name, lang)
        city_data = city_info["city_data"]
        encounter_tables = city_info["encounter_tables"]
        
        # Extract district_matrix (static, no processing)
        district_matrix = city_data.get("district_matrix", [])
        
        return jsonify({
            "success": True,
            "city_data": city_data,
            "district_matrix": district_matrix,
            "encounter_tables": encounter_tables,
            "language": lang,
        })
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# Removed /city-overlay/<overlay_name>/ascii endpoint - city content is now generated dynamically by frontend city.js


@api_bp.route("/city-overlay/by-hex/<hex_code>", methods=["GET"])
def get_overlay_by_hex(hex_code: str):
    """Return city name for a hex code - used to load city overlay. NO generation, NO logic."""
    valid, message = _validate_hex_code(hex_code)
    if not valid:
        return jsonify({"error": message}), 400
    cfg = _cfg()
    lang = _get_language(cfg)
    city_key = _city_key_for_hex(hex_code, lang)
    if not city_key:
        return jsonify({"error": "City not found for hex", "hex_code": hex_code}), 404
    # Return city name only - frontend will load city data via /city-overlay/<city_name>
    return jsonify(
        {
            "name": city_key,
            "hex_code": hex_code,
            "language": lang,
        }
    )


@api_bp.route("/city/<hex_code>", methods=["GET"])
def get_city(hex_code: str):
    cfg = _cfg()
    lang = _get_language(cfg)
    file = _hex_path(cfg, lang, hex_code)
    content = _read_markdown_file(file)
    if content is None:
        return jsonify({"error": "City not found"}), 404
    return jsonify({"hex_code": hex_code, "language": lang, "raw_markdown": content})


@api_bp.route("/settlement/<hex_code>", methods=["GET"])
def get_settlement(hex_code: str):
    cfg = _cfg()
    lang = _get_language(cfg)
    file = _hex_path(cfg, lang, hex_code)
    content = _read_markdown_file(file)
    if content is None:
        return jsonify({"error": "Settlement not found"}), 404
    return jsonify({"hex_code": hex_code, "language": lang, "raw_markdown": content})


@api_bp.route("/city-overlay/<overlay_name>/hex/<hex_id>", methods=["GET"])
def get_overlay_hex(overlay_name: str, hex_id: str):
    """Return raw hex position data. NO generation, NO logic."""
    cfg = _cfg()
    lang = _get_language(cfg)
    
    try:
        # Parse hex_id to get row and col (simple string split: "0_0" -> [0, 0])
        try:
            parts = hex_id.split('_')
            if len(parts) != 2:
                raise ValueError(f"Invalid hex_id format: {hex_id}")
            row = int(parts[0])
            col = int(parts[1])
        except (ValueError, IndexError) as e:
            return jsonify({"success": False, "error": f"Invalid hex_id format: {hex_id}"}), 400
        
        # Load city data (NO processing, NO logic)
        city_info = _load_city_data(overlay_name, lang)
        city_data = city_info["city_data"]
        encounter_tables = city_info["encounter_tables"]
        
        # Extract district from district_matrix at position [row][col]
        district_matrix = city_data.get("district_matrix", [])
        district = ""
        if row < len(district_matrix) and col < len(district_matrix[row]):
            district = district_matrix[row][col] or ""
        
        return jsonify({
            "success": True,
            "hex": {
                "id": hex_id,
                "row": row,
                "col": col,
                "district": district
            },
            "city_data": city_data,
            "encounter_tables": encounter_tables,
            "language": lang,
        })
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# --- web shell (static) -----------------------------------------------------
@web_bp.route("/", methods=["GET"])
def web_index():
    return send_from_directory(web_bp.static_folder, "index.html")


@web_bp.route("/<path:filename>", methods=["GET"])
def web_static(filename: str):
    return send_from_directory(web_bp.static_folder, filename)


