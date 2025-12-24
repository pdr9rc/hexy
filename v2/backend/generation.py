#!/usr/bin/env python3
"""Generation orchestration for v2 backend."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from .cache import BootCache
from .config import AppConfig
from .main_map_generator import MainMapGenerator


def _generate_full_map(target_dir: Path, language: str, cfg: AppConfig) -> Dict:
    target_dir.mkdir(parents=True, exist_ok=True)
    width, height = cfg.get_map_dimensions()
    generator = MainMapGenerator(
        {
            "language": language,
            "map_dimensions": (width, height),
            "output_directory": str(target_dir),
            "skip_existing": False,
            "create_summary": True,
            "create_ascii_map": True,
            "generate_roads": True,
        }
    )
    result = generator.generate_full_map({"skip_existing": False})
    # City overlays are now handled entirely by frontend city.js - no backend generation needed
    now = datetime.now(timezone.utc)
    return {
        "version": str(int(now.timestamp())),
        "generatedAt": now.isoformat().replace("+00:00", "Z"),
        "generated_count": result.get("generated_count"),
        "skipped_count": result.get("skipped_count"),
    }


def ensure_generated(cfg: AppConfig) -> Dict[str, str]:
    cache = BootCache(cfg)
    statuses = []
    for language in cfg.supported_languages:
        statuses.append(cache.ensure_generated(lambda target: _generate_full_map(target, language, cfg), language))
    # Return last status for convenience
    return statuses[-1] if statuses else {"status": "noop"}


