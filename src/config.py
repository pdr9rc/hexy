#!/usr/bin/env python3
"""
Configuration Management for The Dying Lands
Centralized configuration for all application settings.
"""

import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class MapConfig:
    """Map generation configuration."""
    width: int = 30
    height: int = 60
    start_x: int = 1
    start_y: int = 1
    
@dataclass
class GenerationConfig:
    """Content generation rules."""
    settlement_chance: float = 0.15
    dungeon_chance: float = 0.45
    beast_chance: float = 0.50
    npc_chance: float = 0.40
    loot_chance: float = 0.60
    scroll_chance: float = 0.35

@dataclass
class PathConfig:
    """File and directory paths."""
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    database_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "databases")
    output_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "dying_lands_output")
    overlay_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "city_overlays")
    web_templates: Path = field(default_factory=lambda: Path(__file__).parent.parent / "web" / "templates")
    web_static: Path = field(default_factory=lambda: Path(__file__).parent.parent / "web" / "static")
    
    def __post_init__(self):
        """Ensure all paths exist."""
        for path in [self.database_path, self.output_path, self.overlay_path, 
                    self.web_templates, self.web_static]:
            path.mkdir(parents=True, exist_ok=True)

@dataclass
class AppConfig:
    """Main application configuration."""
    language: str = 'en'
    supported_languages: Tuple[str, ...] = ('en', 'pt')
    debug: bool = False
    host: str = '127.0.0.1'
    port: int = 5000
    
    # Map configuration
    map: MapConfig = field(default_factory=MapConfig)
    
    # Generation configuration
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    
    # Path configuration
    paths: PathConfig = field(default_factory=PathConfig)
    
    # Output formats
    output_formats: Tuple[str, ...] = ('markdown', 'ascii')
    
    # Feature flags
    skip_existing: bool = True
    create_summary: bool = True
    create_ascii_map: bool = True
    # Auto-regenerate output on server start or map request
    auto_regenerate_output: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'language': self.language,
            'debug': self.debug,
            'host': self.host,
            'port': self.port,
            'map': {
                'width': self.map.width,
                'height': self.map.height,
                'start_x': self.map.start_x,
                'start_y': self.map.start_y
            },
            'generation': {
                'settlement_chance': self.generation.settlement_chance,
                'dungeon_chance': self.generation.dungeon_chance,
                'beast_chance': self.generation.beast_chance,
                'npc_chance': self.generation.npc_chance,
                'loot_chance': self.generation.loot_chance,
                'scroll_chance': self.generation.scroll_chance
            },
            'paths': {
                'project_root': str(self.paths.project_root),
                'database_path': str(self.paths.database_path),
                'output_path': str(self.paths.output_path),
                'overlay_path': str(self.paths.overlay_path),
                'web_templates': str(self.paths.web_templates),
                'web_static': str(self.paths.web_static)
            },
            'output_formats': self.output_formats,
            'skip_existing': self.skip_existing,
            'create_summary': self.create_summary,
            'create_ascii_map': self.create_ascii_map,
            'auto_regenerate_output': self.auto_regenerate_output
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        if 'language' in data:
            config.language = data['language']
        if 'debug' in data:
            config.debug = data['debug']
        if 'host' in data:
            config.host = data['host']
        if 'port' in data:
            config.port = data['port']
        
        # Update map config
        if 'map' in data:
            map_data = data['map']
            config.map.width = map_data.get('width', config.map.width)
            config.map.height = map_data.get('height', config.map.height)
            config.map.start_x = map_data.get('start_x', config.map.start_x)
            config.map.start_y = map_data.get('start_y', config.map.start_y)
        
        # Update generation config
        if 'generation' in data:
            gen_data = data['generation']
            config.generation.settlement_chance = gen_data.get('settlement_chance', config.generation.settlement_chance)
            config.generation.dungeon_chance = gen_data.get('dungeon_chance', config.generation.dungeon_chance)
            config.generation.beast_chance = gen_data.get('beast_chance', config.generation.beast_chance)
            config.generation.npc_chance = gen_data.get('npc_chance', config.generation.npc_chance)
            config.generation.loot_chance = gen_data.get('loot_chance', config.generation.loot_chance)
            config.generation.scroll_chance = gen_data.get('scroll_chance', config.generation.scroll_chance)
        
        return config

# Global configuration instance
config = AppConfig()

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config

def update_config(new_config: Dict[str, Any]) -> AppConfig:
    """Update the global configuration."""
    global config
    config = AppConfig.from_dict(new_config)
    return config

def load_config_from_file(file_path: str) -> AppConfig:
    """Load configuration from JSON file."""
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return update_config(data)

def save_config_to_file(file_path: str) -> None:
    """Save current configuration to JSON file."""
    import json
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False) 