#!/usr/bin/env python3
"""
The Dying Lands - Main Application Entry Point
Simple entry point for running the Flask application.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app import main

if __name__ == '__main__':
    main() 