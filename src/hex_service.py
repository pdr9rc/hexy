"""
Hex Service for The Dying Lands

This service provides a clean interface for hex data using the hex model system,
replacing the markdown parsing approach.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.hex_model import hex_manager, BaseHex, TerrainType, SettlementHex
from src.config import get_config
from src.terrain_system import terrain_system
from src.mork_borg_lore_database import MorkBorgLoreDatabase
import re


class HexService:
    """Service for managing hex data using the model system."""
    
    def __init__(self):
        self.config = get_config()
        self.lore_db = MorkBorgLoreDatabase()
        self.hex_data_cache: Dict[str, Dict[str, Any]] = {}
        self._load_hex_data()
    
    def _load_hex_data(self):
        """Load all hex data from the generated JSON files."""
        hexes_dir = self.config.paths.output_path / "hexes"
        if not hexes_dir.exists():
            return
        
        # Load the hex data from the generation output
        # This assumes the generation process creates structured data
        for hex_file in hexes_dir.glob("hex_*.md"):
            hex_code = hex_file.stem.replace("hex_", "")
            try:
                # For now, we'll still parse the markdown but convert to structured data
                hex_data = self._parse_hex_markdown(hex_file)
                if hex_data:
                    self.hex_data_cache[hex_code] = hex_data
            except Exception as e:
                print(f"Error loading hex {hex_code}: {e}")
    
    def _parse_hex_markdown(self, hex_file: Path) -> Optional[Dict[str, Any]]:
        """Parse markdown hex file and convert to structured data."""
        try:
            with open(hex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.split('\n')
            hex_code = hex_file.stem.replace("hex_", "")
            # Extract terrain from markdown
            terrain = self._extract_terrain(content)
            # If terrain is missing or 'plains', use terrain_system
            if not terrain or terrain == 'plains':
                terrain = terrain_system.get_terrain_for_hex(hex_code, self.lore_db)
            # Check if it's a settlement
            if '⌂ **' in content:
                settlement_data = self._extract_settlement_data(content, hex_code)
                return {
                    "hex_code": hex_code,
                    "terrain": terrain,
                    "is_settlement": True,
                    "name": settlement_data['name'],
                    "description": settlement_data['description'],
                    "population": settlement_data['population'],
                    "atmosphere": settlement_data['atmosphere'],
                    "notable_feature": settlement_data['notable_feature'],
                    "local_tavern": settlement_data['local_tavern'],
                    "local_power": settlement_data['local_power'],
                    "settlement_art": settlement_data['settlement_art']
                }
            # Check if it's a beast
            elif '※ **' in content:
                beast_data = self._extract_beast_data(content, hex_code)
                return {
                    "hex_code": hex_code,
                    "terrain": terrain,
                    "is_beast": True,
                    **beast_data
                }
            # Check if it's a dungeon
            elif '▲ **' in content:
                dungeon_data = self._extract_hex_data(content, hex_code)
                dungeon_data["hex_code"] = hex_code
                dungeon_data["terrain"] = terrain
                dungeon_data["is_dungeon"] = True
                return dungeon_data
            # Check if it's an NPC
            elif '☉ **' in content:
                npc_data = self._extract_npc_data(content, hex_code)
                return {
                    "hex_code": hex_code,
                    "terrain": terrain,
                    "is_npc": True,
                    **npc_data
                }
            # Check if it's a sea encounter
            elif '≈ **' in content:
                sea_data = self._extract_sea_data(content, hex_code)
                return {
                    "hex_code": hex_code,
                    "terrain": terrain,
                    "is_sea_encounter": True,
                    **sea_data
                }
            else:
                # Use the existing hex data extraction
                hex_data = self._extract_hex_data(content, hex_code)
                hex_data["hex_code"] = hex_code
                hex_data["terrain"] = terrain
                return hex_data
        except Exception as e:
            print(f"Error parsing hex file {hex_file}: {e}")
            return None
    
    def _extract_hex_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract hex data from markdown content, robustly splitting sections and extracting subfields, code blocks, and normalizing fields."""
        import re
        section_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)
        code_block_pattern = re.compile(r'```([\s\S]*?)```', re.MULTILINE)
        sections = {}
        last_pos = 0
        last_section = None
        for match in section_pattern.finditer(content):
            section_name = match.group(1).strip().lower().replace(' ', '_')
            if last_section is not None:
                sections[last_section] = content[last_pos:match.start()].strip()
            last_section = section_name
            last_pos = match.end()
        if last_section is not None:
            sections[last_section] = content[last_pos:].strip()

        def extract_subfields_and_code(section_text):
            """Extract '**Key:** Value' pairs as a dict, code blocks, and return (dict, raw_text, code_blocks)."""
            subfields = {}
            lines = section_text.split('\n')
            raw_lines = []
            code_blocks = []
            in_code = False
            code_accum = []
            for line in lines:
                if line.strip().startswith('```'):
                    if not in_code:
                        in_code = True
                        code_accum = []
                        continue
                    else:
                        in_code = False
                        code_blocks.append('\n'.join(code_accum))
                        continue
                if in_code:
                    code_accum.append(line)
                    continue
                m = re.match(r'^\*\*(.+?):\*\*\s*(.+)$', line)
                if m:
                    key = m.group(1).strip().lower().replace(' ', '_')
                    value = m.group(2).strip()
                    # Store as list if key repeats
                    if key in subfields:
                        if isinstance(subfields[key], list):
                            subfields[key].append(value)
                        else:
                            subfields[key] = [subfields[key], value]
                    else:
                        subfields[key] = value
                else:
                    raw_lines.append(line)
            raw_text = '\n'.join(raw_lines).strip()
            return subfields, raw_text, code_blocks

        # Normalize loot/treasure fields
        loot_keys = {'treasure_found', 'loot_found', 'treasure', 'loot'}
        hex_data = {'hex_code': hex_code}
        loot_collected = []
        # For each expected section, extract both structured subfields, raw text, and code blocks
        for section in ['encounter', 'denizen', 'danger', 'atmosphere', 'notable_feature', 'treasure', 'loot_found', 'ancient_knowledge', 'npc_details', 'beast_details', 'threat_level', 'territory']:
            section_text = sections.get(section, '').strip()
            subfields, raw_text, code_blocks = extract_subfields_and_code(section_text)
            # Collect loot/treasure fields
            for k, v in subfields.items():
                if k in loot_keys:
                    loot_collected.append(v)
            # City/settlement specific: population, key_npcs
            if section == 'encounter':
                # Try to extract population from encounter line
                pop_match = re.search(r'Population[:\s]*([\d,\+]+)', section_text, re.IGNORECASE)
                if pop_match:
                    hex_data['population'] = pop_match.group(1).strip()
            if section == 'denizen':
                # Try to extract key_npcs
                npc_match = re.search(r'\*\*Key NPCs:\*\*\s*(.+)', section_text)
                if npc_match:
                    hex_data['key_npcs'] = [n.strip() for n in npc_match.group(1).split(',')]
            hex_data[section] = {'raw': raw_text, 'fields': subfields, 'ascii_art': code_blocks}
        # For backward compatibility, set top-level fields for most common sections
        for key in ['encounter', 'denizen', 'danger', 'atmosphere', 'notable_feature', 'treasure']:
            hex_data[key] = hex_data[key]['raw']
        # Loot and scroll/ancient knowledge special handling
        if loot_collected:
            hex_data['loot'] = loot_collected if len(loot_collected) > 1 else loot_collected[0]
        else:
            hex_data['loot'] = None
        if hex_data['ancient_knowledge']['fields']:
            hex_data['scroll'] = hex_data['ancient_knowledge']['fields']
        else:
            hex_data['scroll'] = None
        return hex_data
    
    def _extract_settlement_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract settlement data from markdown content."""
        lines = content.split('\n')
        settlement_data = {
            'name': '',
            'description': '',
            'population': '',
            'atmosphere': '',
            'notable_feature': '',
            'local_tavern': '',
            'local_power': '',
            'settlement_art': ''
        }
        
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line == '## Encounter':
                # Save previous section content
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                # Save previous section content
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'denizen'
                section_content = []
            elif line == '## Notable Feature':
                # Save previous section content
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                # Save previous section content
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'atmosphere'
                section_content = []
            elif line == '## Settlement Layout':
                # Save previous section content
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'settlement_layout'
                section_content = []
            elif line.startswith('⌂ **'):
                # Extract settlement name from encounter line
                encounter_line = line
                if ' - ' in encounter_line:
                    name_part = encounter_line.split(' - ')[0]
                    settlement_data['name'] = name_part.replace('⌂ **', '').replace('**', '').strip()
                    population_part = encounter_line.split(' - ')[1]
                    settlement_data['population'] = population_part.strip()
                else:
                    settlement_data['name'] = encounter_line.replace('⌂ **', '').replace('**', '').strip()
            elif line.startswith('**Local Tavern:**'):
                settlement_data['local_tavern'] = line.replace('**Local Tavern:**', '').strip()
            elif line.startswith('**Local Power:**'):
                settlement_data['local_power'] = line.replace('**Local Power:**', '').strip()
            elif current_section and not line.startswith('**') and not line.startswith('##'):
                # Add content to current section
                section_content.append(line)
        
        # Save final section content
        if current_section and section_content:
            settlement_data[current_section] = ' '.join(section_content).strip()
        
        return settlement_data
    
    def _extract_beast_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract beast data from markdown content."""
        lines = content.split('\n')
        beast_data = {
            'encounter': '',
            'beast_type': '',
            'beast_feature': '',
            'beast_behavior': '',
            'denizen': '',
            'territory': '',
            'threat_level': '',
            'notable_feature': '',
            'atmosphere': '',
            'loot': None
        }
        
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line == '## Encounter':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'denizen'
                section_content = []
            elif line == '## Notable Feature':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'atmosphere'
                section_content = []
            elif line == '## Beast Details':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'beast_details'
                section_content = []
            elif line == '## Threat Level':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'threat_level'
                section_content = []
            elif line == '## Territory':
                # Save previous section content
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'territory'
                section_content = []
            elif line.startswith('**Type:**'):
                beast_data['beast_type'] = line.replace('**Type:**', '').strip()
            elif line.startswith('**Feature:**'):
                beast_data['beast_feature'] = line.replace('**Feature:**', '').strip()
            elif line.startswith('**Behavior:**'):
                beast_data['beast_behavior'] = line.replace('**Behavior:**', '').strip()
            elif line.startswith('**Territory:**'):
                beast_data['territory'] = line.replace('**Territory:**', '').strip()
            elif line.startswith('**Threat Level:**'):
                beast_data['threat_level'] = line.replace('**Threat Level:**', '').strip()
            elif current_section and not line.startswith('**') and not line.startswith('##'):
                # Add content to current section
                section_content.append(line)
        
        # Save final section content
        if current_section and section_content:
            beast_data[current_section] = ' '.join(section_content).strip()
        
        return beast_data
    
    def _extract_npc_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract NPC data from markdown content."""
        lines = content.split('\n')
        npc_data = {
            'encounter': '',
            'name': '',
            'denizen_type': '',
            'motivation': '',
            'feature': '',
            'demeanor': '',
            'notable_feature': '',
            'atmosphere': '',
            'loot': None
        }
        
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line.startswith('☉ **') and 'Encounter' in line:
                current_section = 'encounter'
                npc_data['encounter'] = line
            elif line.startswith('**Name:**'):
                current_section = 'name'
                npc_data['name'] = line.replace('**Name:**', '').strip()
            elif line.startswith('**Type:**'):
                current_section = 'denizen_type'
                npc_data['denizen_type'] = line.replace('**Type:**', '').strip()
            elif line.startswith('**Motivation:**'):
                current_section = 'motivation'
                npc_data['motivation'] = line.replace('**Motivation:**', '').strip()
            elif line.startswith('**Feature:**'):
                current_section = 'feature'
                npc_data['feature'] = line.replace('**Feature:**', '').strip()
            elif line.startswith('**Demeanor:**'):
                current_section = 'demeanor'
                npc_data['demeanor'] = line.replace('**Demeanor:**', '').strip()
            elif line.startswith('**Notable Feature:**'):
                current_section = 'notable_feature'
                npc_data['notable_feature'] = line.replace('**Notable Feature:**', '').strip()
            elif line.startswith('**Atmosphere:**'):
                current_section = 'atmosphere'
                npc_data['atmosphere'] = line.replace('**Atmosphere:**', '').strip()
            elif current_section and not line.startswith('**'):
                # Add content to current section
                if npc_data[current_section] and isinstance(npc_data[current_section], str):
                    npc_data[current_section] += ' ' + line
                elif not npc_data[current_section]:
                    npc_data[current_section] = line
        
        return npc_data
    
    def _extract_sea_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract sea encounter data from markdown content."""
        lines = content.split('\n')
        sea_data = {
            'encounter': '',
            'encounter_type': '',
            'denizen': '',
            'territory': '',
            'threat_level': '',
            'notable_feature': '',
            'atmosphere': '',
            'loot': None
        }
        
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line == '## Encounter':
                # Save previous section content
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                # Save previous section content
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'denizen'
                section_content = []
            elif line == '## Notable Feature':
                # Save previous section content
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                # Save previous section content
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                
                current_section = 'atmosphere'
                section_content = []
            elif line.startswith('≈ **'):
                # Extract encounter name
                encounter_line = line
                sea_data['encounter'] = encounter_line
            elif line.startswith('**Type:**'):
                sea_data['encounter_type'] = line.replace('**Type:**', '').strip()
            elif line.startswith('**Denizen:**'):
                sea_data['denizen'] = line.replace('**Denizen:**', '').strip()
            elif line.startswith('**Territory:**'):
                sea_data['territory'] = line.replace('**Territory:**', '').strip()
            elif line.startswith('**Threat Level:**'):
                sea_data['threat_level'] = line.replace('**Threat Level:**', '').strip()
            elif current_section and not line.startswith('**') and not line.startswith('##'):
                # Add content to current section
                section_content.append(line)
        
        # Save final section content
        if current_section and section_content:
            sea_data[current_section] = ' '.join(section_content).strip()
        
        return sea_data
    
    def _extract_terrain(self, content: str) -> str:
        """Extract terrain from hex content, robust to leading spaces and markdown variations."""
        match = re.search(r'^\s*\*\*Terrain:\*\*\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if match:
            terrain = match.group(1).strip().lower()
            # Normalize common variants
            terrain_map = {
                'plains': 'plains',
                'plain': 'plains',
                'mountain': 'mountain',
                'mountains': 'mountain',
                'forest': 'forest',
                'coast': 'coast',
                'swamp': 'swamp',
                'sea': 'sea',
            }
            return terrain_map.get(terrain, 'plains')
        return 'plains'  # Default
    
    def get_hex(self, hex_code: str) -> Optional[BaseHex]:
        """Get a hex model for the given hex code."""
        # Check cache first
        cached_hex = hex_manager.get_hex(hex_code)
        if cached_hex:
            return cached_hex
        
        # Check if it's a major city
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('type') == 'major_city':
            return self._create_major_city_hex(hex_code, hardcoded)
        
        # Get from hex data cache
        hex_data = self.hex_data_cache.get(hex_code)
        if not hex_data:
            return None
        
        # Create hex model
        hex_model = hex_manager.create_hex_from_data(hex_code, hex_data)
        hex_manager.cache_hex(hex_code, hex_model)
        return hex_model
    
    def _create_major_city_hex(self, hex_code: str, hardcoded: Dict[str, Any]) -> BaseHex:
        """Create a major city hex model."""
        city_key = hardcoded['city_key']
        city_data = self.lore_db.major_cities[city_key]
        
        terrain = TerrainType(terrain_system.get_terrain_for_hex(hex_code, self.lore_db))
        
        return SettlementHex(
            hex_code=hex_code,
            terrain=terrain,
            name=city_data['name'],
            description=city_data['description'],
            population=city_data['population'],
            atmosphere=city_data['atmosphere'],
            notable_feature=city_data['notable_features'],
            local_tavern="Major city establishment",
            local_power="City authority",
            settlement_art="Major city layout",
            is_major_city=True  # Set this for major cities
        )
    
    def get_hex_dict(self, hex_code: str) -> Optional[Dict[str, Any]]:
        """Get hex data as dictionary for API response."""
        hex_model = self.get_hex(hex_code)
        if hex_model:
            return hex_model.to_dict()
        return None
    
    def get_settlement_details(self, hex_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed settlement information."""
        hex_model = self.get_hex(hex_code)
        if not hex_model or not isinstance(hex_model, SettlementHex):
            return None
        
        return {
            "success": True,
            "settlement": {
                "name": hex_model.name,
                "description": hex_model.description,
                "population": hex_model.population,
                "atmosphere": hex_model.atmosphere,
                "notable_feature": hex_model.notable_feature,
                "local_tavern": hex_model.local_tavern,
                "local_power": hex_model.local_power,
                "terrain": hex_model.terrain.value
            }
        }
    
    def get_city_details(self, hex_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed city information."""
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if not hardcoded or hardcoded.get('type') != 'major_city':
            return None
        
        city_key = hardcoded['city_key']
        city_data = self.lore_db.major_cities[city_key]
        
        return {
            "success": True,
            "city": {
                "name": city_data['name'],
                "description": city_data['description'],
                "population": city_data['population'],
                "region": city_data['region'],
                "atmosphere": city_data['atmosphere'],
                "notable_features": city_data['notable_features'],
                "key_npcs": city_data['key_npcs']
            },
            "regional_npcs": city_data.get('regional_npcs', []),
            "factions": city_data.get('factions', [])
        }
    
    def get_all_hexes(self) -> Dict[str, BaseHex]:
        """Get all available hexes."""
        hexes = {}
        for hex_code in self.hex_data_cache.keys():
            hex_model = self.get_hex(hex_code)
            if hex_model:
                hexes[hex_code] = hex_model
        return hexes
    
    def get_hexes_by_type(self, hex_type: str) -> List[BaseHex]:
        """Get all hexes of a specific type."""
        hexes = []
        for hex_code in self.hex_data_cache.keys():
            hex_model = self.get_hex(hex_code)
            if hex_model and hex_model.get_hex_type().value == hex_type:
                hexes.append(hex_model)
        return hexes
    
    def search_hexes(self, query: str) -> List[BaseHex]:
        """Search hexes by content."""
        results = []
        query_lower = query.lower()
        
        for hex_code in self.hex_data_cache.keys():
            hex_model = self.get_hex(hex_code)
            if not hex_model:
                continue
            
            # Search in hex data
            hex_dict = hex_model.to_dict()
            for key, value in hex_dict.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(hex_model)
                    break
        
        return results
    
    def get_hex_statistics(self) -> Dict[str, Any]:
        """Get statistics about hex distribution."""
        stats = {
            "total": 0,
            "by_type": {},
            "by_terrain": {},
            "with_loot": 0,
            "with_scrolls": 0
        }
        
        for hex_code in self.hex_data_cache.keys():
            hex_model = self.get_hex(hex_code)
            if not hex_model:
                continue
            
            stats["total"] += 1
            
            # Count by type
            hex_type = hex_model.get_hex_type().value
            stats["by_type"][hex_type] = stats["by_type"].get(hex_type, 0) + 1
            
            # Count by terrain
            terrain = hex_model.terrain.value
            stats["by_terrain"][terrain] = stats["by_terrain"].get(terrain, 0) + 1
            
            # Count with loot
            hex_dict = hex_model.to_dict()
            if hex_dict.get('loot'):
                stats["with_loot"] += 1
            
            # Count with scrolls
            if hex_dict.get('scroll'):
                stats["with_scrolls"] += 1
        
        return stats


# Global instance
hex_service = HexService() 