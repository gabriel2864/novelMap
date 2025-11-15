from __future__ import annotations

import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    return root / "novelzone.db"


def test_at_least_one_novel_exists() -> None:
    db_file = get_db_path()
    assert db_file.exists(), "Database file does not exist."

    conn = sqlite3.connect(db_file)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM novel")
        (count,) = cur.fetchone()
        assert count >= 1, "Expected at least one novel in the database."
    finally:
        conn.close()
