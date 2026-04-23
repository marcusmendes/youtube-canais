#!/usr/bin/env python3
"""
sessionStart hook — injects channel memory from SQLite into
the conversation as additional_context.
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "memory.db"


def get_connection() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_baseline(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT * FROM channel_baseline ORDER BY updated_at DESC LIMIT 1"
    ).fetchone()
    if not row:
        return "- Baseline não disponível (execute /yt-performance primeiro)\n"
    return (
        f"- Views médias: {row['avg_views']:.0f} "
        f"| Retenção: {row['avg_retention_pct']:.1f}% "
        f"| Like ratio: {row['avg_like_ratio']:.1f}% "
        f"| Comentários médios: {row['avg_comments']:.0f} "
        f"| Total vídeos: {row['total_videos']}\n"
    )


def fetch_last_diagnostic(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        """SELECT summary, created_at FROM agent_runs
           WHERE agent_type = 'yt-performance'
           ORDER BY created_at DESC LIMIT 1"""
    ).fetchone()
    if not row:
        return "- Nenhum diagnóstico anterior registrado\n"
    summary = row["summary"]
    if len(summary) > 500:
        summary = summary[:500] + "..."
    return f"- Último diagnóstico ({row['created_at'][:10]}):\n  {summary}\n"


def fetch_last_thumbnail(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT * FROM thumbnail_history ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not row:
        return "- Nenhuma thumbnail anterior registrada\n"
    return (
        f"- Estética: {row['aesthetic']} | Composição: {row['composition']} "
        f"| Paleta: {row['dominant_color']} + {row['accent_color']} "
        f"| Expressão: {row['expression']}\n"
        f"- (próxima deve usar estética e composição DIFERENTES)\n"
    )


def fetch_last_subnicho(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        """SELECT video_topic FROM agent_runs
           WHERE agent_type = 'yt-scriptwriter' AND video_topic IS NOT NULL
           ORDER BY created_at DESC LIMIT 1"""
    ).fetchone()
    if not row:
        return "- Nenhum sub-nicho anterior registrado\n"
    return f"- Último sub-nicho: {row['video_topic']} (próximo deve ser diferente)\n"


def fetch_recent_keywords(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        """SELECT keyword, volume, overall FROM keyword_cache
           WHERE volume > 0
           ORDER BY cached_at DESC LIMIT 10"""
    ).fetchall()
    if not rows:
        return "- Nenhuma keyword em cache\n"
    parts = []
    for r in rows:
        parts.append(f'  - "{r["keyword"]}" (vol: {r["volume"]}, overall: {r["overall"]})')
    return "\n".join(parts) + "\n"


def build_context() -> str:
    conn = get_connection()
    if conn is None:
        return (
            "## Channel Memory (auto-loaded)\n\n"
            "Banco de memória não inicializado. Execute:\n"
            "`python3 .cursor/hooks/init-db.py` para criar o schema.\n"
        )

    try:
        sections = [
            "## Channel Memory (auto-loaded)\n",
            "### Baseline do canal\n",
            fetch_baseline(conn),
            "\n### Último diagnóstico (Fase P)\n",
            fetch_last_diagnostic(conn),
            "\n### Última thumbnail\n",
            fetch_last_thumbnail(conn),
            "\n### Último sub-nicho\n",
            fetch_last_subnicho(conn),
            "\n### Keywords recentes com volume\n",
            fetch_recent_keywords(conn),
        ]
        return "".join(sections)
    finally:
        conn.close()


def main() -> None:
    _input = json.load(sys.stdin)  # noqa: F841
    context = build_context()
    output = {"additional_context": context}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
