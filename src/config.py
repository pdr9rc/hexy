#!/usr/bin/env python3
"""
Configuration Management for The Dying Lands
Centralized configuration system with environment variable support and validation.
"""

import os
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

class ConfigManager:
    """Centralized configuration management with validation and environment support."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_file = config_file or "config.json"
        self._config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables."""
        # Default configuration
        default_config = {
            # Map generation settings
            'map': {
                'width': 30,
                'height': 25,
                'start_x': 1,
                'start_y': 1,
                'output_directory': 'dying_lands_output'
            },
            
            # Generation rules
            'generation': {
                'settlement_chance': 0.15,
                'dungeon_chance': 0.45,
                'beast_chance': 0.50,
                'npc_chance': 0.40,
                'loot_chance': 0.60,
                'scroll_chance': 0.35,
                'skip_existing': True,
                'create_summary': True,
                'create_ascii_map': True
            },
            
            # Sandbox settings
            'sandbox': {
                'enabled': True,
                'faction_influence': True,
                'detailed_settlements': True,
                'castle_generation': True,
                'conflict_generation': True,
                'economic_modeling': True
            },
            
            # Web interface settings
            'web': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'threaded': True,
                'max_content_length': 16 * 1024 * 1024  # 16MB
            },
            
            # Database settings
            'database': {
                'cache_enabled': True,
                'cache_ttl': 3600,  # 1 hour
                'connection_pool_size': 10,
                'auto_migrate': True
            },
            
            # Logging settings
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'dying_lands.log',
                'max_file_size': 10 * 1024 * 1024,  # 10MB
                'backup_count': 5
            },
            
            # Output formats
            'output': {
                'formats': ['markdown', 'ascii'],
                'include_metadata': True,
                'compress_output': False
            },
            
            # Language settings
            'language': {
                'default': 'en',
                'supported': ['en', 'pt'],
                'fallback': 'en'
            }
        }
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                default_config = self._deep_merge(default_config, file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Override with environment variables
        default_config = self._apply_environment_overrides(default_config)
        
        return default_config
    
    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'DYING_LANDS_MAP_WIDTH': ('map', 'width'),
            'DYING_LANDS_MAP_HEIGHT': ('map', 'height'),
            'DYING_LANDS_OUTPUT_DIR': ('map', 'output_directory'),
            'DYING_LANDS_SETTLEMENT_CHANCE': ('generation', 'settlement_chance'),
            'DYING_LANDS_DUNGEON_CHANCE': ('generation', 'dungeon_chance'),
            'DYING_LANDS_BEAST_CHANCE': ('generation', 'beast_chance'),
            'DYING_LANDS_NPC_CHANCE': ('generation', 'npc_chance'),
            'DYING_LANDS_LOOT_CHANCE': ('generation', 'loot_chance'),
            'DYING_LANDS_SCROLL_CHANCE': ('generation', 'scroll_chance'),
            'DYING_LANDS_WEB_HOST': ('web', 'host'),
            'DYING_LANDS_WEB_PORT': ('web', 'port'),
            'DYING_LANDS_WEB_DEBUG': ('web', 'debug'),
            'DYING_LANDS_LOG_LEVEL': ('logging', 'level'),
            'DYING_LANDS_LOG_FILE': ('logging', 'file'),
            'DYING_LANDS_DEFAULT_LANGUAGE': ('language', 'default'),
            'DYING_LANDS_SANDBOX_ENABLED': ('sandbox', 'enabled'),
            'DYING_LANDS_CACHE_ENABLED': ('database', 'cache_enabled'),
            'DYING_LANDS_CACHE_TTL': ('database', 'cache_ttl')
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config, config_path, self._parse_env_value(env_value))
        
        return config
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer values
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # String values (default)
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], path: Tuple[str, ...], value: Any):
        """Set a nested value in the configuration dictionary."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate map dimensions
        if self._config['map']['width'] <= 0 or self._config['map']['height'] <= 0:
            raise ValueError("Map dimensions must be positive integers")
        
        # Validate generation chances
        for chance_key in ['settlement_chance', 'dungeon_chance', 'beast_chance', 'npc_chance', 'loot_chance', 'scroll_chance']:
            chance = self._config['generation'][chance_key]
            if not 0 <= chance <= 1:
                raise ValueError(f"Generation chance {chance_key} must be between 0 and 1")
        
        # Validate web port
        if not 1 <= self._config['web']['port'] <= 65535:
            raise ValueError("Web port must be between 1 and 65535")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self._config['logging']['level'] not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {valid_log_levels}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot notation key."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self, filename: Optional[str] = None):
        """Save current configuration to file."""
        save_file = filename or self.config_file
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Could not save configuration to {save_file}: {e}")
    
    def reload(self):
        """Reload configuration from file."""
        self._config = self._load_config()
        self._validate_config()
    
    def get_map_config(self) -> Dict[str, Any]:
        """Get map-specific configuration."""
        return self._config['map']
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Get generation-specific configuration."""
        return self._config['generation']
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web interface configuration."""
        return self._config['web']
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self._config['logging']
    
    def get_sandbox_config(self) -> Dict[str, Any]:
        """Get sandbox configuration."""
        return self._config['sandbox']
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self._config['database']
    
    def get_language_config(self) -> Dict[str, Any]:
        """Get language configuration."""
        return self._config['language']
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self._config['output']
    
    def to_dict(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary."""
        return self._config.copy()

# Global configuration instance
config_manager = ConfigManager()

# Convenience functions
def get_config() -> ConfigManager:
    """Get the global configuration manager."""
    return config_manager

def get_setting(key: str, default: Any = None) -> Any:
    """Get a configuration setting by key."""
    return config_manager.get(key, default)