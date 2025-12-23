#!/usr/bin/env python3
"""Boot-time cache helper for Lambda/local cold-start reuse."""

from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path
from typing import Callable, Dict, Optional

from .config import AppConfig


class BootCache:
    """Ensure expensive generation runs once per boot and reuses cached output."""

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.cache_root = cfg.paths.cache_root
        self.cache_root.mkdir(parents=True, exist_ok=True)

    def _paths_for_language(self, language: str):
        cache_output = self.cache_root / language / "dying_lands_output"
        lock_file = self.cache_root / language / ".generate.lock"
        manifest = cache_output / "version.json"
        return cache_output, lock_file, manifest

    # --- public API -----------------------------------------------------
    def ensure_generated(self, generator: Callable[[Path], Dict], language: str) -> Dict[str, str]:
        """Guarantee generated output exists in cache and hydrated to output_path for a language."""
        cache_output, lock_file, manifest = self._paths_for_language(language)

        if self._is_warm(manifest, cache_output):
            self._hydrate_output(cache_output, language)
            return {"status": "warm", "cache": str(cache_output), "language": language}

        if not self._acquire_lock(lock_file):
            # Another worker is generating; wait briefly and hydrate when done.
            self._wait_for_generation(manifest, cache_output)
            self._hydrate_output(cache_output, language)
            return {"status": "warm-after-wait", "cache": str(cache_output), "language": language}

        try:
            result = generator(cache_output)
            self._write_manifest(manifest, result, language)
            self._hydrate_output(cache_output, language)
            return {"status": "generated", "cache": str(cache_output), "language": language}
        finally:
            self._release_lock(lock_file)

    def describe(self) -> Dict[str, Optional[str]]:
        return {
            "cache_root": str(self.cache_root),
            "languages": self.cfg.supported_languages,
        }

    # --- internals ------------------------------------------------------
    def _is_warm(self, manifest: Path, cache_output: Path) -> bool:
        return manifest.exists() and cache_output.exists()

    def _hydrate_output(self, cache_output: Path, language: str) -> None:
        target = self.cfg.paths.output_path / language
        if cache_output.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(cache_output, target, dirs_exist_ok=True)

    def _write_manifest(self, manifest_path: Path, generation_result: Dict, language: str) -> None:
        manifest_data = {
            "version": generation_result.get("version") or str(int(time.time())),
            "generatedAt": generation_result.get("generatedAt")
            or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "language": language,
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

    def _acquire_lock(self, lock_file: Path) -> bool:
        try:
            # Use atomic create; if exists, someone else holds it.
            lock_file.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            return False

    def _release_lock(self, lock_file: Path) -> None:
        try:
            if lock_file.exists():
                lock_file.unlink()
        except OSError:
            pass

    def _wait_for_generation(self, manifest: Path, cache_output: Path, timeout: float = 60.0) -> None:
        start = time.time()
        while time.time() - start < timeout:
            if self._is_warm(manifest, cache_output):
                return
            time.sleep(0.5)


