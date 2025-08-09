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
    # If launched via installer, anchor working dir to installed APP_DIR
    app_dir_env = os.getenv('HEXY_APP_DIR')
    if app_dir_env and os.path.isdir(app_dir_env):
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
    # Register blueprints
    from .routes import main_bp, api_bp, assets_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(assets_bp)
    add_cache_busting_headers(app)
    return app

def add_cache_busting_headers(app):
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store'
        return response 