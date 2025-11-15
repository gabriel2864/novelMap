from __future__ import annotations

import sqlite3
from pathlib import Path


def get_db_path(db_path: str = "novelzone.db") -> Path:
    root = Path(__file__).resolve().parent
    return root / db_path


def print_novels_with_genres() -> None:
    db_file = get_db_path()
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        query = """
            SELECT
                n.id AS novel_id,
                n.title AS novel_title,
                u.name AS author_name,
                group_concat(g.name, ', ') AS genres
            FROM novel n
            JOIN author_profile ap ON ap.id = n.author_profile_id
            JOIN user u ON u.id = ap.user_id
            LEFT JOIN novel_genre ng ON ng.novel_id = n.id
            LEFT JOIN genre g ON g.id = ng.genre_id
            GROUP BY n.id, n.title, u.name
            ORDER BY n.popularity_score DESC;
        """
        for row in cur.execute(query):
            print(
                f"Novel #{row['novel_id']}: {row['novel_title']} "
                f"by {row['author_name']} "
                f"(genres: {row['genres']})"
            )
    finally:
        conn.close()


def print_chapters_for_novel(slug: str) -> None:
    db_file = get_db_path()
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        query = """
            SELECT c.chapter_number, c.title
            FROM chapter c
            JOIN novel n ON n.id = c.novel_id
            WHERE n.slug = ?
            ORDER BY c.chapter_number;
        """
        print(f"Chapters for novel slug '{slug}':")
        for row in cur.execute(query, (slug,)):
            print(f"  {row['chapter_number']}. {row['title']}")
    finally:
        conn.close()


if __name__ == "__main__":
    print_novels_with_genres()
    print()
    print_chapters_for_novel("the-silent-map")
