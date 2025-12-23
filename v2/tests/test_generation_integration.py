import os
import pytest
from pathlib import Path


def test_ensure_generated_multilang(monkeypatch, tmp_path):
    # Configure temp output/cache
    out = tmp_path / "output"
    cache = tmp_path / "cache"
    monkeypatch.setenv("HEXY_OUTPUT_DIR", str(out))
    monkeypatch.setenv("HEXY_CACHE_DIR", str(cache))

    from backend import generation
    from backend import config
    
    # Force reload config to pick up test env vars
    config._CONFIG = config.load_config()

    # Stub overlay export to write minimal files
    def fake_export(lang: str, root: Path):
        odir = root / "city_overlays"
        odir.mkdir(parents=True, exist_ok=True)
        (odir / f"{lang}_stub.md").write_text("# Overlay\n", encoding="utf-8")
        (odir / f"{lang}_stub.txt").write_text("ASCII", encoding="utf-8")
        return []

    monkeypatch.setattr(generation, "export_overlays", fake_export)

    # Stub generation to write one hex file
    def fake_generate(self, options=None):
        hex_dir = Path(self.output_dir) / "hexes"
        hex_dir.mkdir(parents=True, exist_ok=True)
        (hex_dir / "hex_0001.md").write_text("# Hex 0001\n", encoding="utf-8")
        return {"generated_count": 1, "skipped_count": 0}

    monkeypatch.setattr(generation.MainMapGenerator, "generate_full_map", fake_generate)

    cfg = config.get_config()
    cfg.supported_languages = ["en", "pt"]
    cfg.language = "en"

    res = generation.ensure_generated(cfg)
    assert res["status"] in ("generated", "warm", "warm-after-wait")

    # Verify outputs per language exist
    for lang in cfg.supported_languages:
        hex_file = cache / lang / "dying_lands_output" / "hexes" / "hex_0001.md"
        overlay_file = cache / lang / "dying_lands_output" / "city_overlays" / f"{lang}_stub.md"
        assert hex_file.exists()
        assert overlay_file.exists()


@pytest.mark.skipif(not os.getenv("RUN_REAL_GEN"), reason="Set RUN_REAL_GEN=1 to exercise real generation")
def test_real_generation_small(monkeypatch, tmp_path):
    """Runs a tiny real generation to ensure outputs are produced."""
    out = tmp_path / "output"
    cache = tmp_path / "cache"
    monkeypatch.setenv("HEXY_OUTPUT_DIR", str(out))
    monkeypatch.setenv("HEXY_CACHE_DIR", str(cache))

    from backend import generation, config
    from backend.main_map_generator import MainMapGenerator

    # Force small map and no ascii summary to speed up
    orig_load_config = MainMapGenerator._load_config

    def tiny_config(self, cfg):
        data = orig_load_config(self, cfg)
        data["map_dimensions"] = (2, 2)
        data["output_directory"] = cfg.get("output_directory")
        data["create_ascii_map"] = False
        data["create_summary"] = False
        data["skip_existing"] = False
        return data

    monkeypatch.setattr(MainMapGenerator, "_load_config", tiny_config)

    cfg = config.get_config()
    cfg.supported_languages = ["en"]
    cfg.language = "en"

    res = generation.ensure_generated(cfg)
    assert res["status"] in ("generated", "warm", "warm-after-wait")

    # Check outputs exist somewhere under cache root or hydrated output
    hex_files = list((cache / "en").rglob("hex_*.md")) + list(out.rglob("hex_*.md"))
    overlay_files = list((cache / "en").rglob("city_overlays/*.md")) + list(out.rglob("city_overlays/*.md"))
    assert hex_files
    assert overlay_files

