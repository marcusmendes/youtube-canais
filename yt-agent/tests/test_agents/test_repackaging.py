"""Tests for Agent R — Repackaging."""

from __future__ import annotations

import datetime

import pytest

from yt_agent.agents.repackaging import find_repackaging_candidates
from yt_agent.memory.models import Video
from yt_agent.memory.repository import ChannelMemory


@pytest.mark.asyncio
async def test_find_candidates_empty_memory(db_session):
    memory = ChannelMemory(db_session)
    candidates = await find_repackaging_candidates(memory=memory)
    assert candidates == []


@pytest.mark.asyncio
async def test_find_candidates_no_metrics(db_session):
    """Videos without metrics should not be candidates."""
    memory = ChannelMemory(db_session)
    video = Video(
        id="v001", title="Test", sub_niche="IA",
        published_at=datetime.date(2026, 4, 1),
    )
    await memory.save_video(video)
    candidates = await find_repackaging_candidates(memory=memory)
    assert candidates == []


@pytest.mark.asyncio
async def test_find_candidates_detects_underperformer(db_session):
    """Video with low views but good retention should be flagged."""
    memory = ChannelMemory(db_session)

    good = Video(
        id="v001", title="Good Video", sub_niche="IA",
        published_at=datetime.date(2026, 4, 10),
        views_7d=5000, avg_retention_pct=45.0,
    )
    also_good = Video(
        id="v002", title="Also Good", sub_niche="IA",
        published_at=datetime.date(2026, 4, 8),
        views_7d=4000, avg_retention_pct=40.0,
    )
    underperformer = Video(
        id="v003", title="Underperformer", sub_niche="IA",
        published_at=datetime.date(2026, 4, 5),
        views_7d=500, avg_retention_pct=35.0,
    )
    await memory.save_video(good)
    await memory.save_video(also_good)
    await memory.save_video(underperformer)

    candidates = await find_repackaging_candidates(memory=memory)
    assert len(candidates) == 1
    assert candidates[0]["video_id"] == "v003"
    assert candidates[0]["avg_retention_pct"] == 35.0


@pytest.mark.asyncio
async def test_low_retention_not_candidate(db_session):
    """Video with low views AND low retention should NOT be flagged."""
    memory = ChannelMemory(db_session)

    normal = Video(
        id="v001", title="Normal", sub_niche="IA",
        published_at=datetime.date(2026, 4, 10),
        views_7d=5000, avg_retention_pct=45.0,
    )
    bad_content = Video(
        id="v002", title="Bad Content", sub_niche="IA",
        published_at=datetime.date(2026, 4, 5),
        views_7d=500, avg_retention_pct=10.0,
    )
    await memory.save_video(normal)
    await memory.save_video(bad_content)

    candidates = await find_repackaging_candidates(memory=memory)
    assert candidates == []
