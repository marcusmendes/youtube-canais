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

        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

    print(json.dumps({}))


if __name__ == "__main__":
    main()
