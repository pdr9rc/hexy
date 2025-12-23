#!/usr/bin/env python3
"""Local dev entrypoint for v2 backend."""

from __future__ import annotations

from . import create_app
from .config import get_config


def main() -> None:
    cfg = get_config()
    app = create_app()
    app.run(host=cfg.host, port=cfg.port, debug=cfg.debug)


if __name__ == "__main__":
    main()


