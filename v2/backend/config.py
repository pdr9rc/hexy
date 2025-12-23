#!/usr/bin/env python3
"""
v2 configuration for Hexy.

Defaults favor local development while keeping production/Lambda compatibility.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


def _is_lambda() -> bool:
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def _default_output_dir() -> Path:
    override = os.getenv("HEXY_OUTPUT_DIR")
    if override:
        return Path(override).expanduser().resolve()
    # Use durable per-user location
    return Path.home() / ".local" / "share" / "hexy" / "dying_lands_output"


def _default_cache_dir(output_dir: Path) -> Path:
    if os.getenv("HEXY_CACHE_DIR"):
        return Path(os.getenv("HEXY_CACHE_DIR")).expanduser().resolve()
    if _is_lambda():
        return Path("/tmp/hexy-cache")
    return output_dir.parent / ".hexy-cache"


def _config_file_path() -> Path:
    """Get path to persistent config file."""
    config_dir = Path.home() / ".config" / "hexy"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def _load_persistent_config() -> dict:
    """Load persistent configuration from file."""
    config_file = _config_file_path()
    if config_file.exists():
        try:
            return json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_persistent_config(config: dict) -> None:
    """Save persistent configuration to file."""
    config_file = _config_file_path()
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")


@dataclass
class PathConfig:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    data_path: Path = field(init=False)
    database_path: Path = field(init=False)
    output_path: Path = field(default_factory=_default_output_dir)
    cache_root: Path = field(init=False)
    map_image: Path = field(init=False)

    def __post_init__(self) -> None:
        self.data_path = self.project_root / "data"
        self.database_path = self.project_root / "databases"
        self.cache_root = _default_cache_dir(self.output_path)
        self.map_image = self.data_path / "mork_borg_official_map.png"
        for path in (self.output_path, self.cache_root):
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class AppConfig:
    debug: bool = bool(os.getenv("HEXY_DEBUG", "1") not in ("0", "false", "False"))
    host: str = os.getenv("HEXY_HOST", "127.0.0.1")
    port: int = int(os.getenv("HEXY_PORT", "6660"))
    language: str = os.getenv("HEXY_LANGUAGE", "en")
    paths: PathConfig = field(default_factory=PathConfig)
    enable_overlays: bool = bool(os.getenv("HEXY_ENABLE_OVERLAYS", "1") not in ("0", "false", "False"))
    supported_languages: List[str] = field(default_factory=list)
    map_dimensions: Tuple[int, int] = field(default_factory=lambda: (30, 60))
    
    def set_map_dimensions(self, width: int, height: int) -> None:
        """Set map dimensions and persist to config file."""
        if width < 1 or height < 1:
            raise ValueError("Map dimensions must be positive integers")
        if width > 100 or height > 100:
            raise ValueError("Map dimensions cannot exceed 100x100")
        self.map_dimensions = (width, height)
        _save_persistent_config({"map_dimensions": [width, height]})
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        """Get current map dimensions."""
        return self.map_dimensions


def load_config() -> AppConfig:
    cfg = AppConfig()
    # Derive supported languages from databases/languages/*
    languages_dir = cfg.paths.database_path / "languages"
    if languages_dir.exists():
        langs = sorted([p.name for p in languages_dir.iterdir() if p.is_dir()])
        if langs:
            cfg.supported_languages = langs
    if not cfg.supported_languages:
        cfg.supported_languages = ["en"]
    if cfg.language not in cfg.supported_languages:
        cfg.language = cfg.supported_languages[0]
    
    # Load persistent config (e.g., map_dimensions)
    persistent = _load_persistent_config()
    if "map_dimensions" in persistent:
        dims = persistent["map_dimensions"]
        if isinstance(dims, list) and len(dims) == 2:
            cfg.map_dimensions = (int(dims[0]), int(dims[1]))
    
    return cfg


# Backwards-compatible singleton accessor for modules ported from v1
_CONFIG = load_config()


def get_config() -> AppConfig:
    return _CONFIG


