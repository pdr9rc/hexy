#!/usr/bin/env python3
"""
The Dying Lands - AWS Lambda Handler
Lambda-compatible entry point for the Flask application.
"""

import os
import sys
from pathlib import Path
from mangum import Mangum
from backend import create_app
from backend.config import get_config
from backend.utils import setup_project_paths
from asgiref.wsgi import WsgiToAsgi

# Setup project paths for Lambda environment
setup_project_paths()

# Create Flask application
app = create_app()

# Wrap Flask app with WsgiToAsgi for ASGI compatibility
asgi_app = WsgiToAsgi(app)

# Create Lambda handler using Mangum
handler = Mangum(asgi_app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        API Gateway response
    """
    try:
        # Set environment variables for Lambda
        os.environ.setdefault('HEXY_OUTPUT_DIR', '/tmp/hexy_output')
        os.environ.setdefault('HEXY_APP_DIR', '/tmp/hexy_app')
        
        # Ensure output directory exists
        output_dir = Path('/tmp/hexy_output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Call the Mangum handler
        return handler(event, context)
        
    except Exception as e:
        print(f"❌ Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': {
                'error': 'Internal server error',
                'message': str(e)
            }
        }

# For local testing
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
