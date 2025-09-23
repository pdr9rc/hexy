#!/usr/bin/env python3
"""
Web Application for The Dying Lands
Flask-based web interface for the interactive map viewer.
"""

import os
from flask import Flask
from backend.config import get_config
from flask_cors import CORS

# Check if running on AWS Lambda
IS_LAMBDA = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

def create_app() -> Flask:
    """Create and configure the Flask application."""
    # If launched via installer, anchor working dir to installed APP_DIR.
    # Do NOT change CWD on AWS Lambda to preserve package-relative paths (e.g., databases/**).
    app_dir_env = os.getenv('HEXY_APP_DIR')
    if app_dir_env and os.path.isdir(app_dir_env) and not IS_LAMBDA:
        try:
            os.chdir(app_dir_env)
        except Exception:
            pass
    config = get_config()
    # If running from installed app, ensure output path exists
    try:
        if not config.paths.output_path.exists():
            config.paths.output_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'web', 'templates'),
        static_folder=os.path.join(base_dir, 'web', 'static'),
        static_url_path='/static'
    )
    app.config['SECRET_KEY'] = 'mork-borg-dying-lands-secret-key'
    app.config['DEBUG'] = config.debug
    # Enable CORS for API routes (allow CloudFront domain and API Gateway domain)
    try:
        CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)
    except Exception:
        pass
    # Register blueprints
    from .routes import main_bp, api_bp, assets_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(assets_bp)
    add_cache_busting_headers(app)
    add_api_cache_headers(app)
    return app

def add_cache_busting_headers(app):
    @app.after_request
    def add_header(response):
        try:
            from flask import request
            # Do not force no-store on GET /api/* so CDN can cache per sandbox
            if request.method == 'GET' and request.path.startswith('/api/'):
                return response
        except Exception:
            pass
        response.headers['Cache-Control'] = 'no-store'
        return response 

def add_api_cache_headers(app):
    @app.after_request
    def add_api_header(response):
        try:
            # Enable CDN caching for GET /api/* responses; others remain no-store
            from flask import request
            if request.method == 'GET' and request.path.startswith('/api/'):
                # Short TTL on origin; CloudFront will honor behavior TTLs
                response.headers['Cache-Control'] = 'public, max-age=60'
                # Vary by sandbox query for safety at proxies
                response.headers['Vary'] = (response.headers.get('Vary', '') + ', Accept-Encoding, Origin').strip(', ')
        except Exception:
            pass
        return response