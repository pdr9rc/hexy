"""
Hex Model System for The Dying Lands

This module provides a clean data model interface for hex content,
replacing the markdown parsing approach with structured data classes.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from .utils.hex_field_creator import create_common_hex_fields, create_loot_item
from .models import LootItem, LootType, AncientKnowledge


class TerrainType(Enum):
    """Terrain types available in the hex system."""
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    COAST = "coast"
    SWAMP = "swamp"
    DESERT = "desert"
    SEA = "sea"
    RIVER = "river"
    BRIDGE = "bridge"
    HILLS = "hills"


class HexType(Enum):
    """Types of hex content."""
    WILDERNESS = "wilderness"
    SETTLEMENT = "settlement"
    DUNGEON = "dungeon"
    BEAST = "beast"
    NPC = "npc"
    SEA_ENCOUNTER = "sea_encounter"





@dataclass
class BaseHex:
    """Base class for all hex types."""
    hex_code: str
    terrain: TerrainType
    exists: bool = True
    has_road: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert hex to dictionary for API response."""
        return {
            "hex_code": self.hex_code,
            "terrain": self.terrain.value,
            "exists": self.exists,
            "has_road": self.has_road,
            "hex_type": self.get_hex_type().value,
            "content_type": self.get_hex_type().value
        }
    
    def get_hex_type(self) -> HexType:
        """Get the hex type - to be implemented by subclasses."""
        return HexType.WILDERNESS


@dataclass
class WildernessHex(BaseHex):
    """Basic wilderness hex with minimal content."""
    
    def get_hex_type(self) -> HexType:
        return HexType.WILDERNESS


@dataclass
class SettlementHex:
    """Settlement hex with population, services, and local authority."""
    hex_code: str
    terrain: TerrainType
    name: str
    description: str
    population: str
    atmosphere: str
    notable_feature: str
    local_tavern: str
    local_power: str
    settlement_art: str
    # Mörk Borg settlement fields
    weather: str = ""
    city_event: str = ""
    tavern_details: Optional[Dict[str, Any]] = None
    exists: bool = True
    has_road: bool = False
    is_major_city: bool = False  # NEW FIELD
    
    def get_hex_type(self) -> HexType:
        return HexType.SETTLEMENT
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex_code": self.hex_code,
            "terrain": self.terrain.value,
            "exists": self.exists,
            "has_road": self.has_road,
            "hex_type": self.get_hex_type().value,
            "is_settlement": not self.is_major_city,  # Only true if not a major city
            "is_major_city": self.is_major_city,      # True for major cities
            "name": self.name,
            "description": self.description,
            "population": self.population,
            "atmosphere": self.atmosphere,
            "notable_feature": self.notable_feature,
            "local_tavern": self.local_tavern,
            "local_power": self.local_power,
            "settlement_art": self.settlement_art,
            # Mörk Borg settlement fields
            "weather": self.weather,
            "city_event": self.city_event,
            "tavern_details": self.tavern_details,
            "redirect_to": "city" if self.is_major_city else "settlement"
        }


@dataclass
class DungeonHex:
    """Dungeon hex with dangers, treasures, and ancient knowledge."""
    hex_code: str
    terrain: TerrainType
    encounter: str
    dungeon_type: str
    denizen: str
    danger: str
    atmosphere: str
    notable_feature: str
    treasure: str
    loot: Optional[LootItem] = None
    scroll: Optional[AncientKnowledge] = None
    # Mörk Borg dungeon fields
    trap_section: Optional[Dict[str, Any]] = None
    exists: bool = True
    has_road: bool = False
    
    def get_hex_type(self) -> HexType:
        return HexType.DUNGEON
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex_code": self.hex_code,
            "terrain": self.terrain.value,
            "exists": self.exists,
            "has_road": self.has_road,
            "hex_type": self.get_hex_type().value,
            "is_dungeon": True,
            "encounter": self.encounter,
            "dungeon_type": self.dungeon_type,
            "denizen": self.denizen,
            "danger": self.danger,
            "atmosphere": self.atmosphere,
            "notable_feature": self.notable_feature,
            "treasure": self.treasure,
            "loot": self.loot.to_dict() if self.loot else None,
            "scroll": self.scroll.to_dict() if self.scroll else None,
            # Mörk Borg dungeon fields
            "trap_section": self.trap_section
        }


@dataclass
class BeastHex:
    """Beast hex with creature details, territory, and threat level."""
    hex_code: str
    terrain: TerrainType
    encounter: str
    beast_type: str
    beast_feature: str
    beast_behavior: str
    denizen: str
    territory: str
    threat_level: str
    notable_feature: str
    atmosphere: str
    loot: Optional[LootItem] = None
    # Beast specific fields
    treasure_found: str = ""
    beast_art: str = ""
    exists: bool = True
    has_road: bool = False
    
    def get_hex_type(self) -> HexType:
        return HexType.BEAST
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex_code": self.hex_code,
            "terrain": self.terrain.value,
            "exists": self.exists,
            "has_road": self.has_road,
            "hex_type": self.get_hex_type().value,
            "is_beast": True,
            "encounter": self.encounter,
            "beast_type": self.beast_type,
            "beast_feature": self.beast_feature,
            "beast_behavior": self.beast_behavior,
            "denizen": self.denizen,
            "territory": self.territory,
            "threat_level": self.threat_level,
            "notable_feature": self.notable_feature,
            "atmosphere": self.atmosphere,
            "loot": self.loot.to_dict() if self.loot else None,
            # Beast specific fields
            "treasure_found": self.treasure_found,
            "beast_art": self.beast_art
        }


@dataclass
class NPCHex:
    """NPC hex with character details, motivations, and demeanor."""
    hex_code: str
    terrain: TerrainType
    encounter: str
    name: str
    denizen_type: str
    # Mörk Borg NPC fields
    trait: str = ""
    concern: str = ""
    want: str = ""
    apocalypse_attitude: str = ""
    secret: str = ""
    # Additional NPC fields
    carries: str = ""
    location: str = ""
    # Fallback fields
    motivation: str = ""
    feature: str = ""
    demeanor: str = ""
    notable_feature: str = ""
    atmosphere: str = ""
    loot: Optional[LootItem] = None
    exists: bool = True
    has_road: bool = False
    
    def get_hex_type(self) -> HexType:
        return HexType.NPC
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex_code": self.hex_code,
            "terrain": self.terrain.value,
            "exists": self.exists,
            "has_road": self.has_road,
            "hex_type": self.get_hex_type().value,
            "is_npc": True,
            "encounter": self.encounter,
            "name": self.name,
            "denizen_type": self.denizen_type,
            # Mörk Borg NPC fields
            "trait": self.trait,
            "concern": self.concern,
            "want": self.want,
            "apocalypse_attitude": self.apocalypse_attitude,
            "secret": self.secret,
            # Fallback fields
            "motivation": self.motivation,
            "feature": self.feature,
            "demeanor": self.demeanor,
            "notable_feature": self.notable_feature,
            "atmosphere": self.atmosphere,
            "loot": self.loot.to_dict() if self.loot else None,
            # Additional NPC fields
            "carries": self.carries,
            "location": self.location
        }


@dataclass
class SeaEncounterHex:
    """Sea encounter hex with abyssal entities and oceanic horrors."""
    hex_code: str
    terrain: TerrainType
    encounter: str
    encounter_type: str
    denizen: str
    territory: str
    threat_level: str
    notable_feature: str
    atmosphere: str
    loot: Optional[LootItem] = None
    # Sea encounter specific fields
    origin: str = ""
    sunken_treasure: str = ""
    exists: bool = True
    has_road: bool = False
    
    def get_hex_type(self) -> HexType:
        return HexType.SEA_ENCOUNTER
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex_code": self.hex_code,
            "terrain": self.terrain.value,
            "exists": self.exists,
            "has_road": self.has_road,
            "hex_type": self.get_hex_type().value,
            "is_sea_encounter": True,
            "encounter": self.encounter,
            "encounter_type": self.encounter_type,
            "denizen": self.denizen,
            "territory": self.territory,
            "threat_level": self.threat_level,
            "notable_feature": self.notable_feature,
            "atmosphere": self.atmosphere,
            "loot": self.loot.to_dict() if self.loot else None,
            # Sea encounter specific fields
            "origin": self.origin,
            "sunken_treasure": self.sunken_treasure
        }


class HexModelManager:
    """Manager class for creating and managing hex models."""
    
    def __init__(self):
        self.hex_cache: Dict[str, BaseHex] = {}
    
    def create_hex_from_data(self, hex_code: str, data: Dict[str, Any]) -> BaseHex:
        """Create a hex model from raw data."""
        terrain = TerrainType(data.get('terrain', 'plains'))
        
        # Determine hex type and create appropriate model
        if data.get('is_settlement'):
            return SettlementHex(
                hex_code=hex_code,
                terrain=terrain,
                name=data.get('name', 'Unknown Settlement'),
                description=data.get('description', 'An unknown settlement.'),
                population=data.get('population', 'Unknown'),
                atmosphere=data.get('atmosphere', 'Uneasy'),
                notable_feature=data.get('notable_feature', 'A notable landmark'),
                local_tavern=data.get('local_tavern', 'A local tavern'),
                local_power=data.get('local_power', 'A local authority'),
                settlement_art=data.get('settlement_art', 'ASCII art placeholder'),
                # Mörk Borg settlement fields
                weather=data.get('weather', ''),
                city_event=data.get('city_event', ''),
                tavern_details=data.get('tavern_details'),
                is_major_city=data.get('is_major_city', False) # NEW FIELD
            )
        elif data.get('is_dungeon'):
            return DungeonHex(
                hex_code=hex_code,
                terrain=terrain,
                encounter=data.get('encounter', 'Unknown dungeon'),
                dungeon_type=data.get('dungeon_type', 'Unknown'),
                denizen=data.get('denizen', 'No denizen information'),
                danger=data.get('danger', 'Unknown danger'),
                atmosphere=data.get('atmosphere', 'Unknown atmosphere'),
                notable_feature=data.get('notable_feature', 'No notable features'),
                treasure=data.get('treasure', 'No treasure'),
                loot=create_loot_item(data.get('loot')) if data.get('loot') else None,
                scroll=self._create_ancient_knowledge(data.get('scroll')) if data.get('scroll') else None,
                # Mörk Borg dungeon fields
                trap_section=data.get('trap_section')
            )
        elif data.get('is_beast'):
            # Use centralized field creator for common fields
            common_fields = create_common_hex_fields(data, hex_code, terrain)
            return BeastHex(
                beast_type=data.get('beast_type', 'Unknown'),
                beast_feature=data.get('beast_feature', 'Unknown'),
                beast_behavior=data.get('beast_behavior', 'Unknown'),
                # Beast specific fields
                treasure_found=data.get('treasure_found', ''),
                beast_art=data.get('beast_art', ''),
                **common_fields
            )
        elif data.get('is_npc'):
            # Use centralized field creator for common fields, but exclude fields that NPCHex doesn't have
            common_fields = create_common_hex_fields(data, hex_code, terrain)
            # Remove fields that NPCHex doesn't have
            fields_to_remove = ['denizen', 'territory', 'threat_level']
            for field in fields_to_remove:
                if field in common_fields:
                    del common_fields[field]
            return NPCHex(
                name=data.get('name', 'Unknown'),
                denizen_type=data.get('denizen_type', 'Unknown'),
                # Mörk Borg NPC fields
                trait=data.get('trait', ''),
                concern=data.get('concern', ''),
                want=data.get('want', ''),
                apocalypse_attitude=data.get('apocalypse_attitude', ''),
                secret=data.get('secret', ''),
                # Additional NPC fields
                carries=data.get('carries', ''),
                location=data.get('location', ''),
                # Fallback fields
                motivation=data.get('motivation', ''),
                feature=data.get('feature', ''),
                demeanor=data.get('demeanor', ''),
                **common_fields
            )
        elif data.get('is_sea_encounter'):
            # Use centralized field creator for common fields
            common_fields = create_common_hex_fields(data, hex_code, terrain)
            return SeaEncounterHex(
                encounter_type=data.get('encounter_type', 'Unknown'),
                # Sea encounter specific fields
                origin=data.get('origin', ''),
                sunken_treasure=data.get('sunken_treasure', ''),
                **common_fields
            )
        else:
            return WildernessHex(hex_code=hex_code, terrain=terrain)
    
    # Use centralized loot item creator from utils.hex_field_creator
    
    def _create_ancient_knowledge(self, scroll_data: Dict[str, Any]) -> AncientKnowledge:
        """Create an AncientKnowledge from raw data."""
        return AncientKnowledge(
            content=scroll_data.get('content', ''),
            description=scroll_data.get('description', ''),
            effect=scroll_data.get('effect', ''),
            type=scroll_data.get('type', '')
        )
    
    def get_hex(self, hex_code: str) -> Optional[BaseHex]:
        """Get a hex from cache or create it."""
        if hex_code in self.hex_cache:
            return self.hex_cache[hex_code]
        return None
    
    def cache_hex(self, hex_code: str, hex_model: BaseHex):
        """Cache a hex model."""
        self.hex_cache[hex_code] = hex_model
    
    def clear_cache(self):
        """Clear the hex cache."""
        self.hex_cache.clear()


# Global instance
hex_manager = HexModelManager() 