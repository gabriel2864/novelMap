# from __future__ import annotations

# from typing import Any
# from flask import Flask, render_template

# def create_app(config: dict[str, Any] | None = None) -> Flask:
#     """Create and configure the Flask app"""
#     app = Flask(__name__)

#     if config:
#         app.config.update(config)

#     @app.get("/") # = @app.route("/", methods=["GET"])
#     def home() -> str:
#         return render_template("home.html")

#     @app.get("/health")
#     def health() ->str:
#         return "ok"

#     return app

from __future__ import annotations

from typing import Any
from pathlib import Path

from flask import Flask, render_template, abort, redirect, url_for

from app.db import get_db, close_db


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    # Base config
    root = Path(__file__).resolve().parent.parent   # project root
    app.config.setdefault("DATABASE", str(root / "novelzone.db"))

    if config:
        app.config.update(config)

    # Teardown: close DB after each request
    app.teardown_appcontext(close_db)

    @app.get("/health")
    def health() -> str:
        return "ok"
    
    @app.get("/")
    def home() -> str:
        """Home page: navigation, popular novels, continue reading."""
        db = get_db()

        # Popular novels: top 4 by popularity_score
        popular_rows = db.execute(
            """
            SELECT
                n.id,
                n.title,
                n.slug,
                n.popularity_score,
                u.name AS author_name
            FROM novel n
            JOIN author_profile ap ON ap.id = n.author_profile_id
            JOIN user u ON u.id = ap.user_id
            ORDER BY n.popularity_score DESC
            LIMIT 4
            """
        ).fetchall()

        # For now, mock a single logged-in user (reader with id 1)
        current_user_id = 1

        # Continue reading: top 4 novels where this user has progress
        continue_rows = db.execute(
            """
            SELECT
                n.id,
                n.title,
                n.slug,
                u.name AS author_name,
                rp.last_chapter_number
            FROM reading_progress rp
            JOIN novel n ON n.id = rp.novel_id
            JOIN author_profile ap ON ap.id = n.author_profile_id
            JOIN user u ON u.id = ap.user_id
            WHERE rp.user_id = ?
            ORDER BY rp.updated_at DESC
            LIMIT 4
            """,
            (current_user_id,),
        ).fetchall()

        popular_novels = [dict(r) for r in popular_rows]
        continue_reading = [dict(r) for r in continue_rows]

        return render_template(
            "home.html",
            popular_novels=popular_novels,
            continue_reading=continue_reading,
        )


    @app.get("/browse")
    def browse() -> str:
        """List novels from the database, ordered by popularity."""
        db = get_db()
        rows = db.execute(
            """
            SELECT
                n.id,
                n.title,
                n.slug,
                n.synopsis,
                n.popularity_score,
                u.name AS author_name
            FROM novel n
            JOIN author_profile ap ON ap.id = n.author_profile_id
            JOIN user u ON u.id = ap.user_id
            ORDER BY n.popularity_score DESC
            """
        ).fetchall()

        novels = [dict(row) for row in rows]
        return render_template("novels_list.html", novels=novels)


    @app.get("/novels")
    def novels_redirect():
        return redirect(url_for("browse"))


    @app.get("/novels/<slug>")
    def novel_detail(slug: str) -> str:
        """Show a single novel and its chapters."""
        db = get_db()
        novel_row = db.execute(
            """
            SELECT
                n.id,
                n.title,
                n.slug,
                n.synopsis,
                n.popularity_score,
                u.name AS author_name
            FROM novel n
            JOIN author_profile ap ON ap.id = n.author_profile_id
            JOIN user u ON u.id = ap.user_id
            WHERE n.slug = ?
            """,
            (slug,),
        ).fetchone()

        if novel_row is None:
            abort(404)

        chapters = db.execute(
            """
            SELECT chapter_number, title
            FROM chapter
            WHERE novel_id = ?
            ORDER BY chapter_number
            """,
            (novel_row["id"],),
        ).fetchall()

        return render_template(
            "novel_detail.html",
            novel=dict(novel_row),
            chapters=[dict(c) for c in chapters],
        )
    
    @app.get("/read/<slug>/<int:chapter_number>")
    def read_chapter(slug: str, chapter_number: int) -> str:
        """
        Reader page for a specific chapter of a novel.
        Shows chapter content and next/previous navigation.
        """
        db = get_db()

        # Load the novel (by slug)
        novel_row = db.execute(
            """
            SELECT
                n.id,
                n.title,
                n.slug,
                u.name AS author_name
            FROM novel n
            JOIN author_profile ap ON ap.id = n.author_profile_id
            JOIN user u ON u.id = ap.user_id
            WHERE n.slug = ?
            """,
            (slug,),
        ).fetchone()

        if novel_row is None:
            abort(404)

        novel_id = novel_row["id"]

        # Load this specific chapter
        chapter_row = db.execute(
            """
            SELECT
                chapter_number,
                title,
                content
            FROM chapter
            WHERE novel_id = ? AND chapter_number = ?
            """,
            (novel_id, chapter_number),
        ).fetchone()

        if chapter_row is None:
            abort(404)

        # Previous chapter (if any)
        prev_row = db.execute(
            """
            SELECT chapter_number
            FROM chapter
            WHERE novel_id = ? AND chapter_number < ?
            ORDER BY chapter_number DESC
            LIMIT 1
            """,
            (novel_id, chapter_number),
        ).fetchone()
        prev_chapter = prev_row["chapter_number"] if prev_row else None

        # Next chapter (if any)
        next_row = db.execute(
            """
            SELECT chapter_number
            FROM chapter
            WHERE novel_id = ? AND chapter_number > ?
            ORDER BY chapter_number ASC
            LIMIT 1
            """,
            (novel_id, chapter_number),
        ).fetchone()
        next_chapter = next_row["chapter_number"] if next_row else None

        return render_template(
            "reader.html",
            novel=dict(novel_row),
            chapter=dict(chapter_row),
            prev_chapter=prev_chapter,
            next_chapter=next_chapter,
        )

    return app
