#!/usr/bin/env python3
"""
subagentStop hook — persists subagent results to SQLite.

Captures the summary from completed yt-* subagents and stores it
in the agent_runs table. For specific agent types, also updates
specialized tables (channel_baseline, thumbnail_history).
"""

import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "memory.db"

YT_AGENT_TYPES = {
    "yt-performance",
    "yt-competitive",
    "yt-validation",
    "yt-metadata",
    "yt-scriptwriter",
    "yt-qa",
    "yt-repackaging",
    "yt-algorithm-audit",
    "yt-calendar",
}


def get_connection() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def extract_agent_type(task: str, description: str) -> str | None:
    """Try to identify which yt-* agent produced this result."""
    combined = f"{task} {description}".lower()
    for agent_type in YT_AGENT_TYPES:
        if agent_type.replace("-", " ") in combined or agent_type in combined:
            return agent_type
    return None


def extract_video_id(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9_-]{11}", text)
    return match.group(0) if match else None


def extract_video_topic(text: str) -> str | None:
    match = re.search(r'"([^"]{5,80})"', text)
    return match.group(1) if match else None


def save_agent_run(
    conn: sqlite3.Connection,
    agent_type: str,
    summary: str,
    task: str,
    status: str,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    video_id = extract_video_id(task) if agent_type == "yt-repackaging" else None
    video_topic = extract_video_topic(task) if agent_type != "yt-repackaging" else None

    conn.execute(
        """INSERT INTO agent_runs (agent_type, video_topic, video_id, summary, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (agent_type, video_topic, video_id, summary, status, now),
    )


def extract_month_year(text: str) -> str | None:
    """Extract month/year like '2026-06' from calendar summary or task."""
    m = re.search(r"(\d{4})[-/](\d{2})", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    months_pt = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03",
        "abril": "04", "maio": "05", "junho": "06", "julho": "07",
        "agosto": "08", "setembro": "09", "outubro": "10",
        "novembro": "11", "dezembro": "12",
    }
    for name, num in months_pt.items():
        pattern = rf"{name}\s+(\d{{4}})"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return f"{m.group(1)}-{num}"
    return None


def save_calendar_topics(
    conn: sqlite3.Connection, summary: str, task: str,
) -> None:
    """Parse weekly topics from calendar summary and insert into content_calendar."""
    month_year = extract_month_year(f"{task} {summary}")
    if not month_year:
        return

    now = datetime.now(timezone.utc).isoformat()
    week_pattern = re.compile(
        r"Semana\s+(\d+).*?Sub-nicho[:\s]*([^\n|]+)",
        re.IGNORECASE | re.DOTALL,
    )

    for match in week_pattern.finditer(summary):
        week = int(match.group(1))
        sub_niche = match.group(2).strip().rstrip("|").strip()

        conn.execute(
            """INSERT OR IGNORE INTO content_calendar
               (month_year, week_number, content_type, topic, sub_niche, status, created_at)
               VALUES (?, ?, 'long', ?, ?, 'planned', ?)""",
            (month_year, week, sub_niche, sub_niche, now),
        )


def update_baseline_from_summary(conn: sqlite3.Connection, summary: str) -> None:
    """Extract baseline numbers from performance summary if present."""
    numbers: dict[str, float | int] = {}

    patterns = {
        "avg_views": r"views?\s*m[ée]dias?[:\s]+(\d+(?:\.\d+)?)",
        "avg_retention_pct": r"reten[çc][ãa]o[:\s]+(\d+(?:\.\d+)?)%",
        "avg_like_ratio": r"like\s*ratio[:\s]+(\d+(?:\.\d+)?)%",
        "avg_comments": r"coment[áa]rios?\s*m[ée]dios?[:\s]+(\d+(?:\.\d+)?)",
        "total_videos": r"total\s*(?:de\s*)?v[íi]deos?[:\s]+(\d+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            val = match.group(1)
            numbers[key] = int(val) if key == "total_videos" else float(val)

    if not numbers:
        return

    now = datetime.now(timezone.utc).isoformat()
    cols = list(numbers.keys()) + ["updated_at"]
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    values = list(numbers.values()) + [now]

    conn.execute(
        f"INSERT INTO channel_baseline ({col_names}) VALUES ({placeholders})",
        values,
    )


def main() -> None:
    payload = json.load(sys.stdin)

    status = payload.get("status", "")
    if status != "completed":
        print(json.dumps({}))
        return

    task = payload.get("task", "")
    description = payload.get("description", "")
    summary = payload.get("summary", "")

    agent_type = extract_agent_type(task, description)
    if agent_type is None:
        print(json.dumps({}))
        return

    conn = get_connection()
    if conn is None:
        print(json.dumps({}))
        return

    try:
        save_agent_run(conn, agent_type, summary, task, status)

        if agent_type == "yt-performance":
            update_baseline_from_summary(conn, summary)

        if agent_type == "yt-calendar":
            save_calendar_topics(conn, summary, task)

        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

    print(json.dumps({}))


if __name__ == "__main__":
    main()
