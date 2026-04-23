"""Async engine and session factory for SQLite."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from yt_agent.config import get_settings
from yt_agent.memory.models import Base

_engine = None
_session_factory = None


def _ensure_db_directory(url: str) -> None:
    """Create the parent directory for a file-based SQLite URL."""
    prefix = "sqlite"
    if not url.startswith(prefix):
        return
    # sqlite:///path or sqlite+aiosqlite:///path → extract path after ///
    idx = url.find("///")
    if idx == -1:
        return
    db_path = Path(url[idx + 3 :])
    db_path.parent.mkdir(parents=True, exist_ok=True)


def async_engine():
    global _engine
    if _engine is None:
        url = get_settings().database_url
        _ensure_db_directory(url)
        _engine = create_async_engine(url, echo=False)
    return _engine


def async_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            async_engine(),
            expire_on_commit=False,
        )
    return _session_factory


async def init_db() -> None:
    engine = async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
