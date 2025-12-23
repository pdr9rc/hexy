#!/usr/bin/env python3
"""
Simple Lambda handler for Hexy Flask app
"""

import os
import sys
import threading
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_init_error: Exception | None = None
app = None

try:
    from backend import create_app
    import serverless_wsgi

    app = create_app()

    # Optional background reset on cold start
    if os.environ.get('AUTO_RESET_ON_COLD_START', '1') == '1':
        def _bg_reset():
            try:
                from backend.routes import reset_continent
                with app.app_context():
                    try:
                        reset_continent()  # generate all languages by default
                    except Exception:
                        pass
            except Exception:
                pass
        threading.Thread(target=_bg_reset, daemon=True).start()

except Exception as e:  # capture init error for later invocations
    _init_error = e


def lambda_handler(event, context):
    """AWS Lambda entry point."""
    if _init_error is not None:
        return {
            'statusCode': 500,
            'body': f'Initialization error: {str(_init_error)}'
        }
    assert app is not None
    try:
        return serverless_wsgi.handle_request(app, event, context)
    except Exception as e:  # surface runtime errors
        return {
            'statusCode': 500,
            'body': f'Runtime error: {e}'
        }
