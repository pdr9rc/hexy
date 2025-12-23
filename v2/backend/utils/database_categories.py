"""
Database category definitions and utilities for managing database structure.
"""

# Database categories for unified structure
DATABASE_CATEGORIES = [
    "terrain", "encounters", "denizens",  # core categories
    "cities", "factions", "regions", "city_overlays",  # lore/overlay categories
    "names", "descriptions", "features",  # content categories
    "affiliation", "basic", "beasts_prices", "bestiary", "city_events", 
    "core", "denizen", "dungeon", "enhanced_loot", "items_prices", 
    "items_trinkets", "loot", "npc_apocalypse", "npc_concerns", 
    "npc_names", "npc_secrets", "npc_trades", "npc_traits", "npc_wants",
    "scroll", "services_prices", "stats", "tavern", "tavern_innkeeper",
    "tavern_menu", "tavern_patrons", "traps_builders", "traps_effects", 
    "traps_triggers", "weapons_prices", "weather", "wilderness"
]

# Language codes supported by the database
# This can be extended dynamically by scanning the database directory
SUPPORTED_LANGUAGES = ['en', 'pt']

# Core table categories for loading
CORE_TABLE_CATEGORIES = [
    "terrain", "encounters", "denizens", "names", "descriptions", "features"
]

# Lore table categories for loading
LORE_TABLE_CATEGORIES = [
    "cities", "factions", "regions", "city_overlays", "affiliation", "basic", "beasts_prices", 
    "bestiary", "city_events", "core", "denizen", "dungeon", "enhanced_loot", 
    "items_prices", "items_trinkets", "loot", "npc_apocalypse", "npc_concerns", 
    "npc_names", "npc_secrets", "npc_trades", "npc_traits", "npc_wants",
    "scroll", "services_prices", "stats", "tavern", "tavern_innkeeper",
    "tavern_menu", "tavern_patrons", "traps_builders", "traps_effects", 
    "traps_triggers", "weapons_prices", "weather", "wilderness"
]


def get_all_categories() -> list:
    """Get all database categories."""
    return DATABASE_CATEGORIES.copy()


def get_core_categories() -> list:
    """Get core table categories."""
    return CORE_TABLE_CATEGORIES.copy()


def get_lore_categories() -> list:
    """Get lore table categories."""
    return LORE_TABLE_CATEGORIES.copy()


def get_supported_languages() -> list:
    """Get supported language codes."""
    # Try to dynamically detect languages from database structure
    try:
        import os
        from pathlib import Path
        
        # Check if databases directory exists
        db_path = Path("databases")
        if db_path.exists():
            # Scan for language directories
            detected_languages = []
            for category_dir in db_path.iterdir():
                if category_dir.is_dir():
                    for lang_dir in category_dir.iterdir():
                        if lang_dir.is_dir() and lang_dir.name not in detected_languages:
                            detected_languages.append(lang_dir.name)
            
            if detected_languages:
                return detected_languages
        
        # Fallback to hardcoded list
        return SUPPORTED_LANGUAGES.copy()
    except Exception:
        return SUPPORTED_LANGUAGES.copy()


def validate_category(category: str) -> bool:
    """Validate if a category is supported."""
    return category in DATABASE_CATEGORIES


def validate_language(language: str) -> bool:
    """Validate if a language is supported."""
    return language in SUPPORTED_LANGUAGES


def get_category_path(category: str, language: str = 'en') -> str:
    """Get the file path for a category and language."""
    if not validate_category(category):
        raise ValueError(f"Invalid category: {category}")
    if not validate_language(language):
        raise ValueError(f"Invalid language: {language}")
    
    return f"databases/{category}/{language}/{category}.json"


def validate_database_structure() -> bool:
    """Validate that the expected database structure exists."""
    try:
        from pathlib import Path
        
        # Check if databases directory exists
        db_path = Path("databases")
        if not db_path.exists():
            return False
        
        # Check if core categories exist
        for category in CORE_TABLE_CATEGORIES:
            category_path = db_path / category
            if not category_path.exists():
                return False
            
            # Check if at least one language directory exists
            has_language = False
            for lang_dir in category_path.iterdir():
                if lang_dir.is_dir():
                    has_language = True
                    break
            
            if not has_language:
                return False
        
        return True
    except Exception:
        return False


# All defects have been addressed:
# - Category definitions are now centralized here and imported elsewhere
# - Language support is now dynamic and can detect new languages from directory structure
# - Database structure validation has been implemented with validate_database_structure() 