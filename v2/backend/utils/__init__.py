"""
Utility modules for the Hexy backend.

This package contains various utility functions and classes for:
- Settlement and NPC generation
- Beast generation
- Loot generation
- Tavern generation
- Markdown formatting
- ASCII processing
- Database categories
- Hex field creation
- City helpers
"""

# Import commonly used utilities for direct access
from .database_categories import (
    get_all_categories,
    get_core_categories,
    get_lore_categories,
    get_supported_languages,
    validate_category,
    validate_language,
    get_category_path,
    validate_database_structure
)

from .ascii_processor import (
    process_ascii_blocks,
    extract_ascii_art,
    parse_loot_section_from_ascii
)

from .beast_generator import (
    generate_beast_encounter,
    generate_beast_description,
    generate_beast_markdown
)

from .npc_generator import (
    generate_npc_encounter,
    generate_npc_description,
    generate_npc_markdown
)

from .tavern_generator import (
    generate_tavern_details,
    generate_weather,
    generate_city_event
)

from .settlement_generator import (
    generate_settlement_atmosphere,
    generate_settlement_feature
)

from .loot_generator import LootGenerator

from .hex_field_creator import (
    create_common_hex_fields,
    create_loot_item
)

from .city_helpers import create_fallback_district_data

from .markdown_formatter import (
    format_beast_details,
    format_sea_encounter_details,
    format_npc_details
)

__all__ = [
    # Database categories
    'get_all_categories',
    'get_core_categories', 
    'get_lore_categories',
    'get_supported_languages',
    'validate_category',
    'validate_language',
    'get_category_path',
    'validate_database_structure',
    
    # ASCII processing
    'process_ascii_blocks',
    'extract_ascii_art',
    'parse_loot_section_from_ascii',
    
    # Beast generation
    'generate_beast_encounter',
    'generate_beast_description',
    'generate_beast_markdown',
    
    # NPC generation
    'generate_npc_encounter',
    'generate_npc_description',
    'generate_npc_markdown',
    
    # Tavern generation
    'generate_tavern_details',
    'generate_weather',
    'generate_city_event',
    
    # Settlement generation
    'generate_settlement_atmosphere',
    'generate_settlement_feature',
    
    # Loot generation
    'LootGenerator',
    
    # Hex field creation
    'create_common_hex_fields',
    'create_loot_item',
    
    # City helpers
    'create_fallback_district_data',
    
    # Markdown formatting
    'format_beast_details',
    'format_sea_encounter_details',
    'format_npc_details'
]
