from __future__ import annotations

from typing import Any
from flask import Flask, render_template

def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask app"""
    app = Flask(__name__)

    if config:
        app.config.update(config)

    @app.get("/") # = @app.route("/", methods=["GET"])
    def home() -> str:
        return render_template("home.html")

    @app.get("/health")
    def health() ->str:
        return "ok"

    return app
