"""Test SQLAlchemy models and ChannelMemory repository."""

from __future__ import annotations

from datetime import date

import pytest

from yt_agent.memory.models import Video, WorkflowRun
from yt_agent.memory.repository import ChannelMemory


@pytest.fixture
def repo(db_session):
    return ChannelMemory(db_session)


async def test_save_and_get_last_video(repo):
    video = Video(
        id="abc123",
        title="Test Video",
        sub_niche="IA + Medicina/Saúde",
        published_at=date(2026, 4, 1),
        format="long",
        thumbnail_aesthetic="documental_sombria",
        thumbnail_composition="A",
        thumbnail_palette="#1A1A2E",
    )
    await repo.save_video(video)

    last = await repo.get_last_video()
    assert last is not None
    assert last.id == "abc123"
    assert last.title == "Test Video"
    assert last.sub_niche == "IA + Medicina/Saúde"
    assert last.format == "long"


async def test_get_last_n_videos(repo):
    for i in range(5):
        v = Video(
            id=f"vid{i}",
            title=f"Video {i}",
            sub_niche="test",
            published_at=date(2026, 4, i + 1),
        )
        await repo.save_video(v)

    videos = await repo.get_last_n_videos(3)
    assert len(videos) == 3
    assert videos[0].published_at >= videos[1].published_at


async def test_save_and_get_workflow_run(repo):
    run = WorkflowRun(
        id="run-001",
        status="created",
        topic="teste",
        sub_niche="IA + Medicina/Saúde",
    )
    await repo.save_workflow_run(run)

    fetched = await repo.get_workflow_run("run-001")
    assert fetched is not None
    assert fetched.topic == "teste"
    assert fetched.status == "created"


async def test_update_workflow_run(repo):
    run = WorkflowRun(id="run-002", status="created")
    await repo.save_workflow_run(run)

    await repo.update_workflow_run("run-002", status="running", current_node="fase_p")

    fetched = await repo.get_workflow_run("run-002")
    assert fetched is not None
    assert fetched.status == "running"
    assert fetched.current_node == "fase_p"


async def test_update_nonexistent_run_raises(repo):
    with pytest.raises(ValueError, match="not found"):
        await repo.update_workflow_run("nonexistent", status="failed")


async def test_get_video_and_update(repo):
    video = Video(
        id="v-upd", title="Update Test", sub_niche="IA",
        published_at=date(2026, 4, 1),
    )
    await repo.save_video(video)

    fetched = await repo.get_video("v-upd")
    assert fetched is not None
    assert fetched.views_7d is None

    await repo.update_video("v-upd", views_7d=3000, avg_retention_pct=42.5)

    updated = await repo.get_video("v-upd")
    assert updated is not None
    assert updated.views_7d == 3000
    assert updated.avg_retention_pct == 42.5


async def test_update_nonexistent_video_raises(repo):
    with pytest.raises(ValueError, match="not found"):
        await repo.update_video("nonexistent", views_7d=100)


async def test_get_all_videos(repo):
    for i in range(3):
        v = Video(
            id=f"all-{i}", title=f"V {i}", sub_niche="IA",
            published_at=date(2026, 4, i + 1),
        )
        await repo.save_video(v)

    all_vids = await repo.get_all_videos()
    assert len(all_vids) == 3
    assert all_vids[0].published_at >= all_vids[-1].published_at


async def test_save_tags(repo):
    from yt_agent.memory.models import TagPerformance

    video = Video(
        id="v-tags", title="Tag Test", sub_niche="IA",
        published_at=date(2026, 4, 1),
    )
    await repo.save_video(video)

    tags = [
        TagPerformance(tag="IA", video_id="v-tags", volume_at_use=5000),
        TagPerformance(tag="medicina", video_id="v-tags", volume_at_use=3000),
    ]
    await repo.save_tags(tags)

    all_tags = await repo.get_tags_by_performance()
    assert len(all_tags) == 2
