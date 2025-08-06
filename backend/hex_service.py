"""
Hex Service for The Dying Lands

This service provides a clean interface for hex data using the hex model system,
replacing the markdown parsing approach.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.hex_model import hex_manager, BaseHex, TerrainType, SettlementHex
from backend.config import get_config
from backend.terrain_system import terrain_system
from backend.mork_borg_lore_database import MorkBorgLoreDatabase
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
        
        hex_count = 0
        # Load the hex data from the generation output
        # This assumes the generation process creates structured data
        for hex_file in hexes_dir.glob("hex_*.md"):
            hex_code = hex_file.stem.replace("hex_", "")
            try:
                # For now, we'll still parse the markdown but convert to structured data
                hex_data = self._parse_hex_markdown(hex_file)
                if hex_data:
                    self.hex_data_cache[hex_code] = hex_data
                    hex_count += 1
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
                    **settlement_data
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
                dungeon_data = self._extract_dungeon_data(content, hex_code)
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
            'settlement_art': '',
            # Mörk Borg settlement fields
            'weather': '',
            'city_event': '',
            'tavern_details': None
        }
        current_section = None
        section_content = []
        in_ascii = False
        ascii_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            # ASCII art block detection
            if line == '```':
                in_ascii = not in_ascii
                if not in_ascii:
                    # End of ASCII art block
                    if ascii_lines:
                        settlement_data['settlement_art'] = '\n'.join(ascii_lines).strip()
                        ascii_lines = []
                continue
            if in_ascii:
                ascii_lines.append(line)
                continue
            # Section headers
            if line == '## Encounter':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'description'  # Map denizen section to description field
                section_content = []
            elif line == '## Notable Feature':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'atmosphere'
                section_content = []
            elif line == '## Settlement Layout':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'settlement_art'  # Map settlement layout section to settlement_art field
                section_content = []
            elif line == '## Tavern Details':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'tavern_details'
                section_content = []
            elif line == '## Loot Found':
                if current_section and section_content:
                    settlement_data[current_section] = ' '.join(section_content).strip()
                current_section = 'loot_found'
                section_content = []
            # Named fields
            elif line.startswith('⌂ **'):
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
            # Mörk Borg fields (scan every line for these)
            if '**Weather:**' in line:
                settlement_data['weather'] = line.split('**Weather:**')[1].strip()
            elif '**City Event:**' in line:
                settlement_data['city_event'] = line.split('**City Event:**')[1].strip()
            # Loot Found fields (scan every line for these, but only in loot_found section)
            elif '**Type:**' in line and current_section == 'loot_found':
                # This is loot information, don't add to section content
                pass
            elif '**Item:**' in line and current_section == 'loot_found':
                # This is loot information, don't add to section content
                pass
            elif '**Description:**' in line and current_section == 'loot_found':
                # This is loot information, don't add to section content
                pass
            elif '**Magical Effect:**' in line and current_section == 'loot_found':
                # This is loot information, don't add to section content
                pass
            # Filter out loot-related content from other sections
            elif '**Type:**' in line and current_section != 'loot_found':
                # This is loot information, don't add to section content
                pass
            elif '**Item:**' in line and current_section != 'loot_found':
                # This is loot information, don't add to section content
                pass
            elif '**Description:**' in line and current_section != 'loot_found' and '**Full Description:**' not in line:
                # This is loot information, don't add to section content
                pass
            elif '**Magical Effect:**' in line and current_section != 'loot_found':
                # This is loot information, don't add to section content
                pass
            elif '**Select Menu:**' in line:
                if settlement_data['tavern_details'] is None:
                    settlement_data['tavern_details'] = {}
                settlement_data['tavern_details']['select_menu'] = line.split('**Select Menu:**')[1].strip()
            elif '**Budget Menu:**' in line:
                if settlement_data['tavern_details'] is None:
                    settlement_data['tavern_details'] = {}
                settlement_data['tavern_details']['budget_menu'] = line.split('**Budget Menu:**')[1].strip()
            elif '**Innkeeper:**' in line:
                if settlement_data['tavern_details'] is None:
                    settlement_data['tavern_details'] = {}
                settlement_data['tavern_details']['innkeeper'] = line.split('**Innkeeper:**')[1].strip()
            elif '**Notable Patron:**' in line:
                if settlement_data['tavern_details'] is None:
                    settlement_data['tavern_details'] = {}
                settlement_data['tavern_details']['notable_patron'] = line.split('**Notable Patron:**')[1].strip()
            # Section content
            elif current_section and not line.startswith('##'):
                section_content.append(line)
        # Save last section
        if current_section and section_content:
            settlement_data[current_section] = ' '.join(section_content).strip()
        
        # Clean up duplicate content by removing embedded fields from atmosphere section
        if settlement_data.get('atmosphere'):
            atmosphere_text = settlement_data['atmosphere']
            # Remove embedded fields that are already extracted
            for field in ['**Local Tavern:**', '**Local Power:**']:
                atmosphere_text = re.sub(rf'{re.escape(field)}[^\n]*\n?', '', atmosphere_text)
            settlement_data['atmosphere'] = atmosphere_text.strip()
        
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
            'loot': None,
            # Beast specific fields
            'treasure_found': '',
            'beast_art': ''
        }
        
        current_section = None
        section_content = []
        in_ascii = False
        ascii_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # ASCII art block detection
            if line == '```':
                in_ascii = not in_ascii
                if not in_ascii:
                    # End of ASCII art block
                    if ascii_lines:
                        beast_data['beast_art'] = '\n'.join(ascii_lines).strip()
                        ascii_lines = []
                continue
            if in_ascii:
                ascii_lines.append(line)
                continue
            
            # Section headers
            if line == '## Encounter':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'denizen'
                section_content = []
            elif line == '## Notable Feature':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'atmosphere'
                section_content = []
            elif line == '## Beast Details':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'beast_details'
                section_content = []
            elif line == '## Threat Level':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'threat_level'
                section_content = []
            elif line == '## Territory':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'territory'
                section_content = []
            elif line == '## Loot Found':
                if current_section and section_content:
                    beast_data[current_section] = ' '.join(section_content).strip()
                current_section = 'loot_found'
                section_content = []
            # Named fields (scan every line)
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
            # Beast specific fields (scan every line for these)
            if '**Treasure Found:**' in line:
                beast_data['treasure_found'] = line.split('**Treasure Found:**')[1].strip()
            # Section content
            elif current_section and not line.startswith('##'):
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            beast_data[current_section] = ' '.join(section_content).strip()
        
        # Parse loot if present
        if 'loot_found' in beast_data and beast_data['loot_found']:
            # Split by sections to get the first loot_found section
            sections = content.split('## ')
            for section in sections:
                if section.startswith('Loot Found'):
                    loot_content = section.replace('Loot Found', '').strip()
                    loot_data = self._parse_loot_section(loot_content)
                    if loot_data:
                        beast_data['loot'] = loot_data
                    break
        
        # Clean up duplicate content by removing embedded fields from denizen section
        if beast_data.get('denizen'):
            denizen_text = beast_data['denizen']
            # Remove embedded fields that are already extracted
            for field in ['**Territory:**', '**Threat Level:**', '**Treasure Found:**']:
                denizen_text = re.sub(rf'{re.escape(field)}[^\n]*\n?', '', denizen_text)
            beast_data['denizen'] = denizen_text.strip()
        
        return beast_data
    
    def _extract_npc_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract NPC data from markdown content."""
        lines = content.split('\n')
        npc_data = {
            'encounter': '',
            'name': '',
            'denizen_type': '',
            # Mörk Borg NPC fields
            'trait': '',
            'concern': '',
            'want': '',
            'apocalypse_attitude': '',
            'secret': '',
            # Additional NPC fields
            'carries': '',
            'location': '',
            # Fallback fields
            'motivation': '',
            'feature': '',
            'demeanor': '',
            'notable_feature': '',
            'atmosphere': '',
            'loot': None
        }
        
        current_section = None
        section_content = []
        in_ascii = False
        ascii_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # ASCII art block detection
            if line == '```':
                in_ascii = not in_ascii
                if not in_ascii:
                    # End of ASCII art block
                    if ascii_lines:
                        # ASCII art found but not stored for NPCs
                        ascii_lines = []
                continue
            if in_ascii:
                ascii_lines.append(line)
                continue
            
            # Section headers
            if line == '## Encounter':
                if current_section and section_content:
                    npc_data[current_section] = ' '.join(section_content).strip()
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                if current_section and section_content:
                    npc_data[current_section] = ' '.join(section_content).strip()
                current_section = 'denizen'
                section_content = []
            elif line == '## Notable Feature':
                if current_section and section_content:
                    npc_data[current_section] = ' '.join(section_content).strip()
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                if current_section and section_content:
                    npc_data[current_section] = ' '.join(section_content).strip()
                current_section = 'atmosphere'
                section_content = []
            elif line == '## NPC Details':
                if current_section and section_content:
                    npc_data[current_section] = ' '.join(section_content).strip()
                current_section = 'npc_details'
                section_content = []
            elif line == '## Loot Found':
                if current_section and section_content:
                    npc_data[current_section] = ' '.join(section_content).strip()
                current_section = 'loot_found'
                section_content = []
            # Named fields (scan every line)
            elif line.startswith('☉ **') and 'Encounter' in line:
                npc_data['encounter'] = line
            elif line.startswith('**Name:**'):
                npc_data['name'] = line.replace('**Name:**', '').strip()
            elif line.startswith('**Type:**'):
                npc_data['denizen_type'] = line.replace('**Type:**', '').strip()
            # Mörk Borg NPC fields
            elif line.startswith('**Trait:**'):
                npc_data['trait'] = line.replace('**Trait:**', '').strip()
            elif line.startswith('**Concern:**'):
                npc_data['concern'] = line.replace('**Concern:**', '').strip()
            elif line.startswith('**Want:**'):
                npc_data['want'] = line.replace('**Want:**', '').strip()
            elif line.startswith('**Apocalypse Attitude:**'):
                npc_data['apocalypse_attitude'] = line.replace('**Apocalypse Attitude:**', '').strip()
            elif line.startswith('**Secret:**'):
                npc_data['secret'] = line.replace('**Secret:**', '').strip()
            # Additional NPC fields
            elif line.startswith('**Carries:**'):
                npc_data['carries'] = line.replace('**Carries:**', '').strip()
            elif line.startswith('**Location:**'):
                npc_data['location'] = line.replace('**Location:**', '').strip()
            # Fallback fields
            elif line.startswith('**Motivation:**'):
                npc_data['motivation'] = line.replace('**Motivation:**', '').strip()
            elif line.startswith('**Feature:**'):
                npc_data['feature'] = line.replace('**Feature:**', '').strip()
            elif line.startswith('**Demeanor:**'):
                npc_data['demeanor'] = line.replace('**Demeanor:**', '').strip()
            elif line.startswith('**Notable Feature:**'):
                npc_data['notable_feature'] = line.replace('**Notable Feature:**', '').strip()
            elif line.startswith('**Atmosphere:**'):
                npc_data['atmosphere'] = line.replace('**Atmosphere:**', '').strip()
            # Section content
            elif current_section and not line.startswith('##'):
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            npc_data[current_section] = ' '.join(section_content).strip()
        
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
            'loot': None,
            # Sea encounter specific fields
            'origin': '',
            'sunken_treasure': ''
        }
        
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Section headers
            if line == '## Encounter':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'encounter'
                section_content = []
            elif line == '## Denizen':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'denizen'
                section_content = []
            elif line == '## Notable Feature':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'atmosphere'
                section_content = []
            elif line == '## Sea Encounter Details':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'sea_encounter_details'
                section_content = []
            elif line == '## Threat Level':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'threat_level'
                section_content = []
            elif line == '## Territory':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'territory'
                section_content = []
            elif line == '## Loot Found':
                if current_section and section_content:
                    sea_data[current_section] = ' '.join(section_content).strip()
                current_section = 'loot_found'
                section_content = []
            # Named fields (scan every line)
            elif line.startswith('≈ **'):
                sea_data['encounter'] = line
            elif line.startswith('**Type:**'):
                sea_data['encounter_type'] = line.replace('**Type:**', '').strip()
            elif line.startswith('**Denizen:**'):
                sea_data['denizen'] = line.replace('**Denizen:**', '').strip()
            elif line.startswith('**Territory:**'):
                sea_data['territory'] = line.replace('**Territory:**', '').strip()
            elif line.startswith('**Threat Level:**'):
                sea_data['threat_level'] = line.replace('**Threat Level:**', '').strip()
            # Sea encounter specific fields
            elif line.startswith('**Origin:**'):
                sea_data['origin'] = line.replace('**Origin:**', '').strip()
            elif line.startswith('**Behavior:**'):
                # Extract behavior from embedded field
                behavior_text = line.replace('**Behavior:**', '').strip()
                if behavior_text:
                    sea_data['behavior'] = behavior_text
            elif line.startswith('**Sunken Treasure:**'):
                sea_data['sunken_treasure'] = line.replace('**Sunken Treasure:**', '').strip()
            # Section content
            elif current_section and not line.startswith('##'):
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sea_data[current_section] = ' '.join(section_content).strip()
        
        # Parse loot if present - use the first loot_found section
        if 'loot_found' in sea_data and sea_data['loot_found']:
            # Split by sections to get the first loot_found section
            sections = content.split('## ')
            for section in sections:
                if section.startswith('Loot Found'):
                    loot_content = section.replace('Loot Found', '').strip()
                    loot_data = self._parse_loot_section(loot_content)
                    if loot_data:
                        sea_data['loot'] = loot_data
                    break
        
        # Clean up duplicate content by removing embedded fields from denizen section
        if sea_data.get('denizen'):
            denizen_text = sea_data['denizen']
            # Remove embedded fields that are already extracted
            for field in ['**Origin:**', '**Behavior:**', '**Threat Level:**', '**Territory:**', '**Sunken Treasure:**']:
                denizen_text = re.sub(rf'{re.escape(field)}[^\n]*\n?', '', denizen_text)
            sea_data['denizen'] = denizen_text.strip()
        
        return sea_data
    
    def _extract_dungeon_data(self, content: str, hex_code: str) -> Dict[str, Any]:
        """Extract dungeon data from markdown content."""
        lines = content.split('\n')
        dungeon_data = {
            'encounter': '',
            'dungeon_type': '',
            'denizen': '',
            'danger': '',
            'atmosphere': '',
            'notable_feature': '',
            'treasure': '',
            'loot': None,
            'scroll': None,
            # Mörk Borg dungeon fields
            'trap_section': None,
            'dungeon_art': ''
        }
        current_section = None
        section_content = []
        in_ascii = False
        ascii_lines = []
        trap_section = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            # ASCII art block detection
            if line == '```':
                in_ascii = not in_ascii
                if not in_ascii:
                    # End of ASCII art block
                    if ascii_lines:
                        dungeon_data['dungeon_art'] = '\n'.join(ascii_lines).strip()
                        ascii_lines = []
                continue
            if in_ascii:
                ascii_lines.append(line)
                continue
            # Section headers
            if line == '## Encounter':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'encounter'
                section_content = []
            elif line == '## Dungeon Type':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'dungeon_type'
                section_content = []
            elif line == '## Denizen':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'denizen'
                section_content = []
            elif line == '## Danger':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'danger'
                section_content = []
            elif line == '## Notable Feature':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'notable_feature'
                section_content = []
            elif line == '## Atmosphere':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'atmosphere'
                section_content = []
            elif line == '## Treasure':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'treasure'
                section_content = []
            elif line == '## Trap':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'trap_section'
                section_content = []
            elif line == '## Dungeon Details':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'dungeon_details'
                section_content = []
            elif line == '## Loot Found':
                if current_section and section_content:
                    dungeon_data[current_section] = ' '.join(section_content).strip()
                current_section = 'loot_found'
                section_content = []
            # Mörk Borg trap fields (scan every line for these)
            if '**Trap Description:**' in line:
                trap_section['description'] = line.split('**Trap Description:**')[1].strip()
            elif '**Trap Effect:**' in line:
                trap_section['effect'] = line.split('**Trap Effect:**')[1].strip()
            elif '**Trap Builder:**' in line:
                trap_section['builder'] = line.split('**Trap Builder:**')[1].strip()
            # Dungeon Details fields (scan every line for these)
            elif '**Type:**' in line and current_section == 'dungeon_details':
                dungeon_data['dungeon_type'] = line.split('**Type:**')[1].strip()
            elif '**Danger:**' in line and current_section == 'dungeon_details':
                dungeon_data['danger'] = line.split('**Danger:**')[1].strip()
            elif '**Treasure:**' in line and current_section == 'dungeon_details':
                dungeon_data['treasure'] = line.split('**Treasure:**')[1].strip()
            # Denizen section fields (scan every line for these)
            elif '**Danger:**' in line and current_section == 'denizen':
                dungeon_data['danger'] = line.split('**Danger:**')[1].strip()
            elif '**Atmosphere:**' in line and current_section == 'denizen':
                dungeon_data['atmosphere'] = line.split('**Atmosphere:**')[1].strip()
            elif '**Treasure Found:**' in line and current_section == 'denizen':
                # This is loot, not treasure
                pass
            # Loot Found fields (scan every line for these)
            elif '**Type:**' in line and current_section == 'loot_found':
                if dungeon_data['loot'] is None:
                    dungeon_data['loot'] = {}
                dungeon_data['loot']['type'] = line.split('**Type:**')[1].strip()
            elif '**Item:**' in line and current_section == 'loot_found':
                if dungeon_data['loot'] is None:
                    dungeon_data['loot'] = {}
                dungeon_data['loot']['item'] = line.split('**Item:**')[1].strip()
            elif '**Description:**' in line and current_section == 'loot_found':
                if dungeon_data['loot'] is None:
                    dungeon_data['loot'] = {}
                dungeon_data['loot']['description'] = line.split('**Description:**')[1].strip()
            elif '**Magical Effect:**' in line and current_section == 'loot_found':
                if dungeon_data['loot'] is None:
                    dungeon_data['loot'] = {}
                dungeon_data['loot']['magical_effect'] = line.split('**Magical Effect:**')[1].strip()
            # Section content
            elif current_section and not line.startswith('##'):
                section_content.append(line)
        # Save last section
        if current_section and section_content:
            dungeon_data[current_section] = ' '.join(section_content).strip()
        if trap_section:
            dungeon_data['trap_section'] = trap_section
        return dungeon_data

    def _parse_loot_section(self, loot_content: str) -> Optional[Dict[str, Any]]:
        """Parse loot section content and extract structured loot data."""
        if not loot_content:
            return None
        
        loot_data = {
            'type': '',
            'item': '',
            'description': '',
            'full_description': '',
            'magical_effect': ''
        }
        
        lines = loot_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for field headers
            if line.startswith('**Type:**'):
                loot_data['type'] = line.replace('**Type:**', '').strip()
            elif line.startswith('**Item:**'):
                loot_data['item'] = line.replace('**Item:**', '').strip()
            elif line.startswith('**Description:**'):
                loot_data['description'] = line.replace('**Description:**', '').strip()
            elif line.startswith('**Full Description:**'):
                loot_data['full_description'] = line.replace('**Full Description:**', '').strip()
            elif line.startswith('**Magical Effect:**'):
                loot_data['magical_effect'] = line.replace('**Magical Effect:**', '').strip()
            # Handle bold item names (like "**Blanket**")
            elif line.startswith('**') and line.endswith('**') and not line.startswith('**Type:**') and not line.startswith('**Item:**') and not line.startswith('**Description:**') and not line.startswith('**Full Description:**') and not line.startswith('**Magical Effect:**'):
                # This is a bold item name, treat as item if we don't have one
                if not loot_data['item']:
                    loot_data['item'] = line.strip('*')
        
        # Only return if we have at least some loot data
        if any(loot_data.values()):
            return loot_data
        return None
    
    # Similar improvements can be made for beast, sea encounter, and wilderness hexes if they have special fields or ASCII art.
    # For brevity, only dungeon is shown here, but the same pattern applies: scan every line for special fields, handle ASCII art blocks, and cleanly extract section content.
    
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
                "settlement_art": hex_model.settlement_art,
                "terrain": hex_model.terrain.value,
                # Mörk Borg settlement fields
                "weather": hex_model.weather,
                "city_event": hex_model.city_event,
                "tavern_details": hex_model.tavern_details
            }
        }
    
    def get_city_details(self, hex_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed city information."""
        hardcoded = self.lore_db.get_hardcoded_hex(hex_code)
        if not hardcoded or hardcoded.get('type') != 'major_city':
            return None
        
        city_key = hardcoded['city_key']
        city_data = self.lore_db.major_cities[city_key]
        
        # Get regional NPCs and factions based on city region
        region = city_data.get('region', 'central')
        regional_npcs = self.lore_db.get_regional_npcs(region)
        regional_factions = self.lore_db.get_regional_factions(region)
        
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
            "regional_npcs": regional_npcs,
            "factions": regional_factions
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
    
    def clear_hex_cache(self, hex_code: str):
        """Clear the cache for a specific hex."""
        if hex_code in self.hex_data_cache:
            del self.hex_data_cache[hex_code]


# Global instance
hex_service = HexService() 