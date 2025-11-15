PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('reader', 'author', 'admin'))
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS author_profile(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    bio TEXT,
    approx_latitude REAL,
    approx_longitude REAL,
    country_code TEXT,
    created_at NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS novel(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auhtor_profile_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE
    synopsis TEXT,
    cover_url TEXT,
    popularity_score REAL NOT NULL DEFAULT 0,
    created_at NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at TEXT,

    FOREIGN KEY (auhtor_profile_id) REFERENCES author_profile(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_novel_author ON novel(auhtor_profile_id);
CREATE INDEX IF NOT EXISTS idx_novel_populariry ON novel(popularity_score DESC);

CREATE TABLE IF NOT EXISTS genre(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS novel_genre(
    novel_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,

    PRIMARY KEY (novel_id, genre_id),
    FOREIGN KEY (novel_id) REFERENCES novel(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genre(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapter(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL, -- HTML OR MD
    created_at NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at TEXT,

    FOREIGN KEY (novel_id) REFERENCES novel(id) ON DELETE CASCADE,
    UNIQUE (novel_id, chapter_number)
);

CREATE INDEX IF NOT EXISTS idx_chapter_novel_number ON chapter(novel_id, chapter_number);
