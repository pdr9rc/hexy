import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("HEXY_DEBUG", "0")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def app(monkeypatch, tmp_path):
    # Point output to a temp directory
    out = tmp_path / "output"
    monkeypatch.setenv("HEXY_OUTPUT_DIR", str(out))

    from backend import create_app, config
    from backend import generation, routes
    from backend.hex_service import HexService

    # Reload config to pick up temp env
    config._CONFIG = config.load_config()

    # Stub generation to avoid heavy work
    monkeypatch.setattr(generation, "ensure_generated", lambda cfg: {"status": "mock"})
    monkeypatch.setattr(routes, "ensure_generated", lambda cfg: {"status": "mock"})

    app = create_app()
    cfg = app.config["HEXY_CONFIG"]
    cfg.supported_languages = ["en", "pt"]
    cfg.language = "en"
    # Rebind hex_service to use test output path
    routes.hex_service = HexService()

    # Seed a sample hex markdown
    hex_dir = cfg.paths.output_path / "en" / "hexes"
    hex_dir.mkdir(parents=True, exist_ok=True)
    (hex_dir / "hex_0101.md").write_text("# Hex 0101\n\n**Terrain:** Plains\n\n## Encounter\nTest", encoding="utf-8")

    # Seed ASCII map for /api/map
    ascii_map = cfg.paths.output_path / "en" / "ascii_map.txt"
    ascii_map.parent.mkdir(parents=True, exist_ok=True)
    ascii_map.write_text(
        "THE DYING LANDS - ASCII MAP\n===\n\n   01 02\n01  .  ⌂\n02  ~  #\n",
        encoding="utf-8",
    )

    # Seed a sample overlay markdown/ascii
    overlay_dir = cfg.paths.output_path / "en" / "city_overlays"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    (overlay_dir / "sample.md").write_text("# City Overlay: Sample\n\n## Hex 0_0\n- District: core\n", encoding="utf-8")
    (overlay_dir / "sample.txt").write_text("ASCII OVERLAY", encoding="utf-8")

    # Reload hex cache after seeding
    routes.hex_service._load_hex_data("en")

    return app

