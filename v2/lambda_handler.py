#!/usr/bin/env python3
"""
AWS Lambda entrypoint for the v2 Flask app using serverless-wsgi.
"""

import os
import sys

# Ensure the bundled backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_init_error = None
app = None

try:
    from backend import create_app
    import serverless_wsgi

    app = create_app()
except Exception as exc:  # capture init-time errors
    _init_error = exc


def lambda_handler(event, context):
    if _init_error is not None:
        return {"statusCode": 500, "body": f"Initialization error: {_init_error}"}
    assert app is not None
    try:
        return serverless_wsgi.handle_request(app, event, context)
    except Exception as exc:
        return {"statusCode": 500, "body": f"Runtime error: {exc}"}
