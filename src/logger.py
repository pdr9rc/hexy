#!/usr/bin/env python3
"""
Logging System for The Dying Lands
Structured logging with file rotation and multiple output formats.
"""

import logging
import logging.handlers
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from .config import get_config
except ImportError:
    from config import get_config

class DyingLandsLogger:
    """Structured logger for The Dying Lands application."""
    
    def __init__(self, name: str = "dying_lands"):
        """Initialize the logger with configuration."""
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with handlers and formatters."""
        config = get_config().get_logging_config()
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, config['level'].upper())
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(config['format'])
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if config.get('file'):
            try:
                file_handler = logging.handlers.RotatingFileHandler(
                    config['file'],
                    maxBytes=config.get('max_file_size', 10 * 1024 * 1024),  # 10MB
                    backupCount=config.get('backup_count', 5),
                    encoding='utf-8'
                )
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except (IOError, OSError) as e:
                # Fallback to console only if file logging fails
                self.warning(f"Could not setup file logging: {e}")
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional context."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with context support."""
        if kwargs:
            # Add context to message
            context_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)
    
    def log_generation_start(self, hex_code: str, terrain: str):
        """Log the start of hex generation."""
        self.info("Starting hex generation", hex_code=hex_code, terrain=terrain)
    
    def log_generation_complete(self, hex_code: str, content_type: str):
        """Log the completion of hex generation."""
        self.info("Hex generation complete", hex_code=hex_code, content_type=content_type)
    
    def log_generation_error(self, hex_code: str, error: str):
        """Log generation errors."""
        self.error("Hex generation failed", hex_code=hex_code, error=error)
    
    def log_map_generation_start(self, width: int, height: int, language: str):
        """Log the start of full map generation."""
        self.info("Starting full map generation", 
                 width=width, height=height, language=language)
    
    def log_map_generation_progress(self, current: int, total: int):
        """Log map generation progress."""
        percentage = (current / total) * 100
        self.info("Map generation progress", 
                 current=current, total=total, percentage=f"{percentage:.1f}%")
    
    def log_map_generation_complete(self, generated: int, skipped: int):
        """Log the completion of full map generation."""
        self.info("Full map generation complete", 
                 generated=generated, skipped=skipped)
    
    def log_web_request(self, endpoint: str, method: str, status_code: int):
        """Log web interface requests."""
        self.info("Web request", endpoint=endpoint, method=method, status_code=status_code)
    
    def log_database_operation(self, operation: str, table: str, success: bool):
        """Log database operations."""
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, "Database operation", 
                       operation=operation, table=table, success=success)
    
    def log_configuration_change(self, key: str, old_value: Any, new_value: Any):
        """Log configuration changes."""
        self.info("Configuration changed", key=key, old_value=old_value, new_value=new_value)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.info("Performance metric", operation=operation, duration=f"{duration:.3f}s", **kwargs)

# Global logger instance
main_logger = DyingLandsLogger("dying_lands")

# Convenience functions
def get_logger(name: Optional[str] = None) -> DyingLandsLogger:
    """Get a logger instance."""
    if name:
        return DyingLandsLogger(name)
    return main_logger

def log_info(message: str, **kwargs):
    """Log info message using global logger."""
    main_logger.info(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message using global logger."""
    main_logger.warning(message, **kwargs)

def log_error(message: str, **kwargs):
    """Log error message using global logger."""
    main_logger.error(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Log debug message using global logger."""
    main_logger.debug(message, **kwargs)

def log_critical(message: str, **kwargs):
    """Log critical message using global logger."""
    main_logger.critical(message, **kwargs)