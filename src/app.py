#!/usr/bin/env python3
"""
The Dying Lands - Main Application
Refactored entry point using modular architecture.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config, update_config
from src.utils import setup_project_paths, log_operation
from src.web import create_app

def main():
    """Main application entry point."""
    try:
        # Setup project paths
        setup_project_paths()
        
        # Get configuration
        config = get_config()
        
        # Create Flask application
        app = create_app()
        
        # Log startup
        log_operation("app_startup", True, f"Starting on {config.host}:{config.port}")
        
        # Run the application
        app.run(
            host=config.host,
            port=config.port,
            debug=config.debug
        )
        
    except Exception as e:
        log_operation("app_startup", False, str(e))
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 