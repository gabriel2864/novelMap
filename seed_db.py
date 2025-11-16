from __future__ import annotations

import sqlite3
from pathlib import Path


def get_db_path(db_path: str = "novelzone.db") -> Path:
    root = Path(__file__).resolve().parent
    return root / db_path


def seed_db(db_path: str = "novelzone.db") -> None:
    """Insert some sample data into the database."""
    db_file = get_db_path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(
            f"Database file not found: {db_file}. Run init_db.py first."
        )

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # so we can access columns by name
    cur = conn.cursor()

    try:
        # Create a reader and an author user
        cur.execute(
            """
            INSERT INTO user (email, password_hash, name, role)
            VALUES (?, ?, ?, ?)
            """,
            ("reader@example.com", "HASHED_PASSWORD", "reader_user", "reader"),
        )

        cur.execute(
            """
            INSERT INTO user (email, password_hash, name, role)
            VALUES (?, ?, ?, ?)
            """,
            ("author@example.com", "HASHED_PASSWORD", "author_user", "author"),
        )

        cur.execute("SELECT id FROM user WHERE email = ?", ("author@example.com",))
        author_user_id = cur.fetchone()["id"]

        # Create an author_profile for the author user
        cur.execute(
            """
            INSERT INTO author_profile (
                user_id, bio, approx_latitude, approx_longitude, country_code
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                author_user_id,
                "Fantasy author based in Paris.",
                48.8566,
                2.3522,
                "FR",
            ),
        )

        cur.execute(
            "SELECT id FROM author_profile WHERE user_id = ?", (author_user_id,)
        )
        author_profile_id = cur.fetchone()["id"]

        # Insert a couple of genres
        cur.executemany(
            "INSERT INTO genre (name, slug) VALUES (?, ?)",
            [
                ("Fantasy", "fantasy"),
                ("Science Fiction", "science-fiction"),
            ],
        )

        # Grab the genre ids
        cur.execute("SELECT id, slug FROM genre")
        genres = {row["slug"]: row["id"] for row in cur.fetchall()}

        # Insert one novel
        cur.execute(
            """
            INSERT INTO novel (
                author_profile_id, title, slug, synopsis, popularity_score
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                author_profile_id,
                "The Silent Map",
                "the-silent-map",
                "A fantasy story about a world-wide story map.",
                42.0,
            ),
        )

        cur.execute(
            "SELECT id FROM novel WHERE slug = ?", ("the-silent-map",)
        )
        novel_id = cur.fetchone()["id"]

        # Link the novel to the "Fantasy" genre
        fantasy_id = genres["fantasy"]
        cur.execute(
            "INSERT INTO novel_genre (novel_id, genre_id) VALUES (?, ?)",
            (novel_id, fantasy_id),
        )

        # Insert a couple of chapters
        cur.executemany(
            """
            INSERT INTO chapter (novel_id, chapter_number, title, content)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    novel_id,
                    1,
                    "The Awakening",
                    "Once upon a time, the story map awakened...",
                ),
                (
                    novel_id,
                    2,
                    "The First Zone",
                    "The first zone of the map revealed a hidden city...",
                ),
            ],
        )

        cur.execute(
            "SELECT id FROM user WHERE email = ?", ("reader@example.com",)
        )
        reader_user_id = cur.fetchone()["id"]

        cur.execute(
            """
            INSERT INTO reading_progress (
                user_id, novel_id, last_chapter_number
            )
            VALUES (?, ?, ?)
            """,
            (reader_user_id, novel_id, 2),  # reader is at chapter 2
        )

        conn.commit()
        print("Database seeded with sample data.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_db()
