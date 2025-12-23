#!/usr/bin/env python3
"""
Lore Database
Generalized repository of canonical locations, NPCs, factions, and lore for accurate map placement.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .config import get_config


class LoreDatabase:
    """Database of canonical lore for accurate map placement."""
    
    def __init__(self):
        self.cfg = get_config()
        self.major_cities = self._init_major_cities()
        self.factions = self._init_factions()
        self.notable_npcs = self._init_notable_npcs()
        self.regional_lore = self._init_regional_lore()
        self.hardcoded_hexes = self._init_hardcoded_hexes()
    
    def _init_major_cities(self) -> Dict:
        """Initialize major cities from lore tables."""
        from .database_manager import database_manager
        raw = database_manager.get_table("cities", "major_cities", getattr(self.cfg, "language", "en")) or []
        cities: Dict[str, Dict] = {}
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            key = entry.get("key") or entry.get("name", "").lower()
            if not key:
                continue
            cities[key] = entry
        if cities:
            return cities
        return {}

    def _load_json_major_cities(self) -> Dict:
        lang = getattr(self.cfg, "language", "en")
        base = self.cfg.paths.database_path / "cities" / lang / "major_cities.json"
        if not base.exists():
            return {}
        try:
            data = json.loads(base.read_text(encoding="utf-8"))
            if isinstance(data, list):
                out = {}
                for entry in data:
                    key = entry.get("key") or entry.get("name", "").lower()
                    if key:
                        out[key] = entry
                return out
            if isinstance(data, dict):
                return data
        except Exception:
            return {}
        return {}
    
    # Note: placeholder city data removed; all city metadata should come from databases/cities/* tables.
    
    def _init_factions(self) -> Dict:
        """Load factions from data files."""
        from .database_manager import database_manager
        lang = getattr(self.cfg, "language", "en")
        factions_list = database_manager.get_table("factions", "major_factions", lang) or []
        local_list = database_manager.get_table("factions", "local_factions", lang) or []
        merged = factions_list + local_list
        factions: Dict[str, Dict] = {}
        for entry in merged:
            if not isinstance(entry, dict):
                continue
            key = entry.get("key") or entry.get("name", "").lower().replace(" ", "_")
            if key:
                factions[key] = entry
        return factions
    
    def _init_notable_npcs(self) -> Dict:
        """Load notable NPCs from data files."""
        from .database_manager import database_manager
        lang = getattr(self.cfg, "language", "en")
        npc_list = database_manager.get_table("lore", "notable_npcs", lang) or []
        npcs: Dict[str, Dict] = {}
        for entry in npc_list:
            if not isinstance(entry, dict):
                continue
            key = entry.get("key") or entry.get("name", "").lower().replace(" ", "_")
            if key:
                npcs[key] = entry
        return npcs
    
    def _init_regional_lore(self) -> Dict:
        """Initialize regional lore and biases from data files."""
        from .database_manager import database_manager
        lang = getattr(self.cfg, "language", "en")
        entries = database_manager.get_table("lore", "regional_lore", lang) or []
        regions: Dict[str, Dict] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            key = entry.get("region", "").lower()
            if key:
                regions[key] = entry
        return regions
    
    def _init_hardcoded_hexes(self) -> Dict:
        """Initialize specific hex locations from data tables (no literals)."""
        from .database_manager import database_manager
        hardcoded: Dict[str, Dict] = {}
        lang = getattr(self.cfg, "language", "en")
        specials = database_manager.get_table("lore", "special_locations", lang) or []
        
        # Place major cities
        for city_key, city_data in self.major_cities.items():
            coords = city_data.get('coordinates')
            if not coords or len(coords) != 2:
                continue
            try:
                x, y = int(coords[0]), int(coords[1])
            except Exception:
                continue
            hex_code = f"{x:02d}{y:02d}"
            hardcoded[hex_code] = {
                'type': 'major_city',
                'city_key': city_key,
                'terrain': city_data.get('terrain'),
                'name': city_data.get('name'),
                'description': city_data.get('description'),
                'population': city_data.get('population'),
                'notable_features': city_data.get('notable_features', []),
                'key_npcs': city_data.get('key_npcs', []),
                'atmosphere': city_data.get('atmosphere'),
                'locked': True
            }
        
        # Add special locations from data
        for entry in specials:
            if not isinstance(entry, dict):
                continue
            hex_code = entry.get("hex_code")
            if not hex_code:
                continue
            hardcoded[hex_code] = entry
        
        return hardcoded
    
    def get_regional_bias(self, x: int, y: int) -> str:
        """Get regional classification for coordinates."""
        # Determine region based on coordinates
        if y <= 10:  # Northern regions
            if x <= 10:
                return 'northwest'
            else:
                return 'north'
        elif y >= 20:  # Southern regions
            return 'south'
        elif x <= 8:  # Western regions
            return 'west'
        elif x >= 18:  # Eastern regions
            return 'east'
        else:  # Central regions
            return 'central'
    
    def get_hardcoded_hex(self, hex_code: str) -> Optional[Dict]:
        """Get hardcoded information for a specific hex."""
        return self.hardcoded_hexes.get(hex_code)
    
    def get_city_by_location(self, x: int, y: int) -> Optional[Dict]:
        """Get city information by coordinates."""
        hex_code = f"{x:02d}{y:02d}"
        hardcoded = self.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('type') == 'major_city':
            city_key = hardcoded['city_key']
            return self.major_cities[city_key]
        return None
    
    def get_regional_npcs(self, region: str) -> List[str]:
        """Get NPCs commonly found in a region."""
        if region in self.regional_lore and isinstance(self.regional_lore[region], dict):
            data = self.regional_lore[region]
            if "regional_npcs" in data:
                return data.get("regional_npcs", [])
        return ['Wandering Scavenger', 'Plague Victim', 'Mad Hermit']
    
    def get_regional_factions(self, region: str) -> List[str]:
        """Get factions active in a region."""
        if region in self.regional_lore and isinstance(self.regional_lore[region], dict):
            data = self.regional_lore[region]
            if "regional_factions" in data:
                return data.get("regional_factions", [])
        return ['nechrubel_cult']

def main():
    """Test the lore database."""
    lore_db = LoreDatabase()
    
    print("🏰 MÖRK BORG LORE DATABASE")
    print("=" * 40)
    
    print(f"\n📍 Major Cities: {len(lore_db.major_cities)}")
    for city_key, city in lore_db.major_cities.items():
        x, y = city['coordinates']
        print(f"  {city['name']} ({x:02d},{y:02d}) - {city['terrain']}")
    
    print(f"\n⚔️ Factions: {len(lore_db.factions)}")
    for faction_key, faction in lore_db.factions.items():
        print(f"  {faction['name']} - {faction['influence']}")
    
    print(f"\n🌍 Regional Biases:")
    for region, data in lore_db.regional_lore.items():
        print(f"  {region}: {data['themes'][:2]}...")

if __name__ == "__main__":
    main() 