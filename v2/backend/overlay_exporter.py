#!/usr/bin/env python3
"""Export city overlays into markdown and ASCII per language."""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

def export_overlays(language: str, output_root: Path) -> List[Dict]:
    """Generate overlays and write markdown + ASCII into output_root/city_overlays."""
    # Lazy imports to avoid heavy initialization during module import (tests).
    from .city_overlay_analyzer import CityOverlayAnalyzer
    from .lore_database import LoreDatabase
    from .translation_system import translation_system

    translation_system.set_language(language)
    analyzer = CityOverlayAnalyzer(language=language, output_directory=str(output_root))
    overlays_dir = output_root / "city_overlays"
    overlays_dir.mkdir(parents=True, exist_ok=True)

    lore = LoreDatabase()
    results: List[Dict] = []

    for key in lore.major_cities.keys():
        md_path = overlays_dir / f"{key}.md"
        ascii_path = overlays_dir / f"{key}.txt"
        try:
            overlay_data = analyzer.generate_city_overlay(key)
            if overlay_data:
                _write_overlay_markdown(md_path, overlay_data)
                ascii_view = analyzer.get_overlay_ascii_view(key)
                if ascii_view:
                    ascii_path.write_text(ascii_view, encoding="utf-8")
                results.append({"name": key, "markdown": str(md_path), "ascii": str(ascii_path)})
                continue
        except Exception:
            # fall back to stub below
            pass
        # Fallback stub overlay to ensure files exist
        city = lore.major_cities.get(key, {"name": key})
        md_path.write_text(f"# City Overlay: {city.get('name', key)}\n\n_No overlay data available._\n", encoding="utf-8")
        ascii_path.write_text("Overlay unavailable.", encoding="utf-8")
        results.append({"name": key, "markdown": str(md_path), "ascii": str(ascii_path), "stub": True})
    return results


def _write_overlay_markdown(md_path: Path, overlay_data: Dict) -> None:
    lines: List[str] = []
    lines.append(f"# City Overlay: {overlay_data.get('display_name', overlay_data.get('name', 'unknown'))}")
    lines.append("")
    lines.append(f"- Grid type: {overlay_data.get('grid_type', 'round')}")
    lines.append(f"- Radius: {overlay_data.get('radius', 3)}")
    lines.append(f"- Total hexes: {overlay_data.get('total_hexes', len(overlay_data.get('hex_grid', {})))}")
    lines.append("")
    for hex_id, hex_data in overlay_data.get("hex_grid", {}).items():
        content = hex_data.get("content", {})
        lines.append(f"## Hex {hex_id}")
        lines.append(f"- District: {hex_data.get('district', 'unknown')}")
        lines.append(f"- Type: {content.get('type', 'unknown')}")
        lines.append(f"- Name: {content.get('name', 'Unknown')}")
        lines.append(f"- Description: {content.get('description', '')}")
        lines.append(f"- Encounter: {content.get('encounter', '')}")
        lines.append(f"- Atmosphere: {content.get('atmosphere', '')}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

