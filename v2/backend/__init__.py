#!/usr/bin/env python3
"""v2 Flask application factory."""

from __future__ import annotations

from flask import Flask

from .config import get_config
from .routes import api_bp, web_bp


def create_app() -> Flask:
    cfg = get_config()
    app = Flask(__name__)
    app.config["HEXY_CONFIG"] = cfg
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    return app


