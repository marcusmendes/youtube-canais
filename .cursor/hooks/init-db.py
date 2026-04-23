#!/usr/bin/env python3
"""
Initialize the SQLite memory database for the YT pipeline.

Run once: python3 .cursor/hooks/init-db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type    TEXT NOT NULL,
    video_topic   TEXT,
    video_id      TEXT,
    summary       TEXT NOT NULL,
    status        TEXT DEFAULT 'completed',
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS channel_baseline (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    avg_views         REAL,
    avg_retention_pct REAL,
    avg_like_ratio    REAL,
    avg_comments      REAL,
    total_videos      INTEGER,
    updated_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS video_history (
    id                TEXT PRIMARY KEY,
    title             TEXT,
    published_at      TEXT,
    views             INTEGER,
    avg_retention_pct REAL,
    like_ratio_pct    REAL,
    comments          INTEGER,
    subscribers_gained INTEGER,
    last_analyzed_at  TEXT
);

CREATE TABLE IF NOT EXISTS thumbnail_history (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id       TEXT,
    aesthetic      TEXT,
    composition    TEXT,
    dominant_color TEXT,
    accent_color   TEXT,
    expression     TEXT,
    created_at     TEXT
);

CREATE TABLE IF NOT EXISTS keyword_cache (
    keyword       TEXT PRIMARY KEY,
    volume        REAL,
    competition   REAL,
    overall       REAL,
    related_json  TEXT,
    cached_at     TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_type ON agent_runs(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_runs_created ON agent_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_thumbnail_created ON thumbnail_history(created_at);
CREATE INDEX IF NOT EXISTS idx_keyword_cached ON keyword_cache(cached_at);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        print(f"Database initialized at {DB_PATH}")
        print("Tables: agent_runs, channel_baseline, video_history, thumbnail_history, keyword_cache")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
