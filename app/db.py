from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """
    Get a SQLite connection for the current request.
    Uses Flask's `g` so each request reuses a single connection.
    """
    if "db" not in g:
        db_path = Path(current_app.config["DATABASE"]).resolve()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # so rows act like dicts: row["title"]
        g.db = conn
    return g.db  # type: ignore[return-value]


def close_db(_: Any | None = None) -> None:
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
