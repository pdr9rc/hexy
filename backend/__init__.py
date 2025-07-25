#!/usr/bin/env python3
"""
Web Application for The Dying Lands
Flask-based web interface for the interactive map viewer.
"""

import os
from flask import Flask
from backend.config import get_config

def create_app() -> Flask:
    """Create and configure the Flask application."""
    config = get_config()
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'web', 'templates'),
        static_folder=os.path.join(base_dir, 'web', 'static')
    )
    app.config['SECRET_KEY'] = 'mork-borg-dying-lands-secret-key'
    app.config['DEBUG'] = config.debug
    # Register blueprints
    from .routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    add_cache_busting_headers(app)
    return app

def add_cache_busting_headers(app):
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store'
        return response 