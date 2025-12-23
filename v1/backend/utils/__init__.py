"""
Utility modules for the Hexy backend.

This package contains various utility functions and classes for:
- Content processing and parsing
- Database management
- Grid generation
- Settlement and NPC generation
- Markdown formatting
- Response handling
- Core utilities
"""

# Import core utilities
from .core_utils import (
    setup_project_paths,
    log_operation,
    validate_hex_code,
    parse_hex_coordinates,
    format_hex_code,
    safe_file_write,
    safe_file_read,
    weighted_choice,
    extract_title_from_content,
    sanitize_filename,
    merge_dictionaries,
    chunk_list,
    flatten_list,
    get_file_size_mb,
    format_file_size,
    ensure_directory_exists,
    list_files_with_extension,
    backup_file,
    is_valid_json,
    retry_operation
)

# Import commonly used utilities for easier access
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

from .content_detector import (
    get_hex_content_type,
    check_hex_has_loot,
    extract_title
)

from .grid_generator import (
    generate_hex_grid,
    get_terrain_for_hex,
    get_terrain_symbol,
    determine_content_symbol,
    determine_css_class
)

from .settlement_generator import (
    generate_settlement_atmosphere,
    generate_settlement_feature,
    generate_tavern_details,
    generate_weather,
    generate_city_event
)

from .ascii_processor import (
    process_ascii_blocks,
    extract_ascii_art,
    parse_loot_section_from_ascii
)

from .markdown_parser import (
    parse_content_sections,
    parse_loot_section,
    parse_magical_effect,
    extract_title_from_content,
    determine_hex_type
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
    generate_tavern_details as generate_tavern_details_centralized,
    generate_weather as generate_weather_centralized,
    generate_city_event as generate_city_event_centralized
)

from .loot_generator import LootGenerator

from .settlement_data_creator import (
    create_settlement_response_data,
    create_major_city_response_data
)

from .response_helpers import (
    create_overlay_response,
    handle_exception_response
)

__all__ = [
    # Core utilities
    'setup_project_paths',
    'log_operation',
    'validate_hex_code',
    'parse_hex_coordinates',
    'format_hex_code',
    'safe_file_write',
    'safe_file_read',
    'weighted_choice',
    'extract_title_from_content',
    'sanitize_filename',
    'merge_dictionaries',
    'chunk_list',
    'flatten_list',
    'get_file_size_mb',
    'format_file_size',
    'ensure_directory_exists',
    'list_files_with_extension',
    'backup_file',
    'is_valid_json',
    'retry_operation',
    
    # Database categories
    'get_all_categories',
    'get_core_categories', 
    'get_lore_categories',
    'get_supported_languages',
    'validate_category',
    'validate_language',
    'get_category_path',
    'validate_database_structure',
    
    # Content detection
    'get_hex_content_type',
    'check_hex_has_loot',
    'extract_title',
    
    # Grid generation
    'generate_hex_grid',
    'get_terrain_for_hex',
    'get_terrain_symbol',
    'determine_content_symbol',
    'determine_css_class',
    
    # Settlement generation
    'generate_settlement_atmosphere',
    'generate_settlement_feature',
    'generate_tavern_details',
    'generate_weather',
    'generate_city_event',
    
    # ASCII processing
    'process_ascii_blocks',
    'extract_ascii_art',
    'parse_loot_section_from_ascii',
    
    # Markdown parsing
    'parse_content_sections',
    'parse_loot_section',
    'parse_magical_effect',
    'extract_title_from_content',
    'determine_hex_type',
    
    # Beast generation
    'generate_beast_encounter',
    'generate_beast_description',
    'generate_beast_markdown',
    
    # NPC generation
    'generate_npc_encounter',
    'generate_npc_description',
    'generate_npc_markdown',
    
    # Tavern generation
    'generate_tavern_details_centralized',
    'generate_weather_centralized',
    'generate_city_event_centralized',
    
    # Loot generation
    'LootGenerator',
    
    # Settlement data creation
    'create_settlement_response_data',
    'create_major_city_response_data',
    
    # Response helpers
    'create_overlay_response',
    'handle_exception_response'
] 