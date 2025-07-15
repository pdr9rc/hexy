#!/usr/bin/env python3
"""
Base Classes for The Dying Lands
Common base classes to reduce code duplication and provide shared functionality.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

try:
    from .config import get_config, get_setting
    from .logger import get_logger
except ImportError:
    from config import get_config, get_setting
    from logger import get_logger

class BaseGenerator(ABC):
    """Base class for all content generators."""
    
    def __init__(self, language: str = "en"):
        """Initialize base generator."""
        self.language = language
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__)
        self._initialize()
    
    def _initialize(self):
        """Initialize generator-specific components."""
        pass
    
    @abstractmethod
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content based on context."""
        pass
    
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate generation context."""
        required_fields = self.get_required_fields()
        for field in required_fields:
            if field not in context:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields for generation."""
        return []
    
    def log_generation_start(self, context: Dict[str, Any]):
        """Log the start of generation."""
        self.logger.log_generation_start(
            context.get('hex_code', 'unknown'),
            context.get('terrain', 'unknown')
        )
    
    def log_generation_complete(self, context: Dict[str, Any], content_type: str):
        """Log the completion of generation."""
        self.logger.log_generation_complete(
            context.get('hex_code', 'unknown'),
            content_type
        )
    
    def log_generation_error(self, context: Dict[str, Any], error: str):
        """Log generation errors."""
        self.logger.log_generation_error(
            context.get('hex_code', 'unknown'),
            error
        )

class BaseContentGenerator(BaseGenerator):
    """Base class for content-specific generators."""
    
    def __init__(self, language: str = "en"):
        """Initialize content generator."""
        super().__init__(language)
        self.content_type = self.get_content_type()
        self.templates = self._load_templates()
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get the content type this generator produces."""
        pass
    
    def _load_templates(self) -> Dict[str, str]:
        """Load content templates."""
        return {}
    
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content with validation and logging."""
        if not self.validate_context(context):
            raise ValueError(f"Invalid context for {self.content_type} generation")
        
        self.log_generation_start(context)
        
        try:
            content = self._generate_content(context)
            self.log_generation_complete(context, self.content_type)
            return content
        except Exception as e:
            self.log_generation_error(context, str(e))
            raise
    
    @abstractmethod
    def _generate_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the actual content."""
        pass
    
    def apply_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Apply template to data."""
        if template_name not in self.templates:
            self.logger.warning(f"Template not found: {template_name}")
            return str(data)
        
        template = self.templates[template_name]
        try:
            return template.format(**data)
        except KeyError as e:
            self.logger.error(f"Missing template variable: {e}")
            return template

class BaseDatabaseManager:
    """Base class for database operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__)
        self.cache = {}
        self.cache_enabled = self.config.get('database.cache_enabled', True)
        self.cache_ttl = self.config.get('database.cache_ttl', 3600)
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if available and not expired."""
        if not self.cache_enabled:
            return None
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        
        return None
    
    def set_cached_data(self, key: str, data: Any):
        """Set data in cache with timestamp."""
        if self.cache_enabled:
            self.cache[key] = (data, datetime.now().timestamp())
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def log_operation(self, operation: str, table: str, success: bool):
        """Log database operation."""
        self.logger.log_database_operation(operation, table, success)

class BaseWebHandler:
    """Base class for web interface handlers."""
    
    def __init__(self):
        """Initialize web handler."""
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__)
    
    def log_request(self, endpoint: str, method: str, status_code: int):
        """Log web request."""
        self.logger.log_web_request(endpoint, method, status_code)
    
    def create_response(self, data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
        """Create standardized API response."""
        response = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        if message:
            response['message'] = message
        
        return response
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle and log errors."""
        error_message = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_message)
        
        return self.create_response(
            data=None,
            success=False,
            message=error_message
        )

class BaseTerrainSystem:
    """Base class for terrain-related operations."""
    
    def __init__(self):
        """Initialize terrain system."""
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__)
        self.terrain_cache = {}
    
    def get_terrain_for_hex(self, hex_code: str) -> str:
        """Get terrain type for a hex with caching."""
        if hex_code in self.terrain_cache:
            return self.terrain_cache[hex_code]
        
        terrain = self._calculate_terrain(hex_code)
        self.terrain_cache[hex_code] = terrain
        return terrain
    
    @abstractmethod
    def _calculate_terrain(self, hex_code: str) -> str:
        """Calculate terrain for a hex."""
        pass
    
    def clear_terrain_cache(self):
        """Clear terrain cache."""
        self.terrain_cache.clear()
        self.logger.info("Terrain cache cleared")

class BaseTranslationSystem:
    """Base class for translation operations."""
    
    def __init__(self):
        """Initialize translation system."""
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__)
        self.current_language = self.config.get('language.default', 'en')
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation data."""
        pass
    
    def set_language(self, language: str):
        """Set current language."""
        if language in self.config.get('language.supported', ['en', 'pt']):
            self.current_language = language
            self.logger.info(f"Language set to {language}")
        else:
            self.logger.warning(f"Unsupported language: {language}")
    
    def translate(self, key: str, default: str = None) -> str:
        """Translate a key to current language."""
        if default is None:
            default = key
        
        # Implementation depends on specific translation system
        return default
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.config.get('language.supported', ['en', 'pt'])

class BaseError(Exception):
    """Base exception class for The Dying Lands."""
    
    def __init__(self, message: str, context: Dict[str, Any] = None):
        """Initialize base error."""
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        """String representation of error."""
        if self.context:
            context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{self.message} | {context_str}"
        return self.message

class GenerationError(BaseError):
    """Exception raised during content generation."""
    pass

class DatabaseError(BaseError):
    """Exception raised during database operations."""
    pass

class ConfigurationError(BaseError):
    """Exception raised during configuration operations."""
    pass

class ValidationError(BaseError):
    """Exception raised during data validation."""
    pass