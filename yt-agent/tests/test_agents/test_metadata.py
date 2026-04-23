"""Tests for Agent Meta — Metadata generation."""

from __future__ import annotations

import datetime

import pytest

from yt_agent.agents.metadata import (
    _build_alternation_context,
    get_alternation_constraints,
)
from yt_agent.memory.models import Video
from yt_agent.memory.repository import ChannelMemory
from yt_agent.state import (
    KeywordMetrics,
    TagsBlock,
    TagValidation,
    ThumbnailSpec,
    TitleCandidate,
    TitlesBlock,
    TitleTop3,
    VideoMetadata,
    WorkflowState,
)


@pytest.mark.asyncio
async def test_alternation_constraints_no_history(db_session):
    memory = ChannelMemory(db_session)
    constraints = await get_alternation_constraints(memory)
    assert constraints["last_aesthetic"] == ""
    assert constraints["last_composition"] == ""
    assert constraints["last_sub_niche"] == ""


@pytest.mark.asyncio
async def test_alternation_constraints_with_history(db_session):
    memory = ChannelMemory(db_session)
    video = Video(
        id="v001",
        title="Test Video",
        sub_niche="medicina",
        published_at=datetime.date(2026, 4, 1),
        thumbnail_aesthetic="documental_sombria",
        thumbnail_composition="A",
        thumbnail_palette="#1A1A2E",
        thumbnail_expression="preocupação",
    )
    await memory.save_video(video)

    constraints = await get_alternation_constraints(memory)
    assert constraints["last_aesthetic"] == "documental_sombria"
    assert constraints["last_composition"] == "A"
    assert constraints["last_palette"] == "#1A1A2E"
    assert constraints["last_expression"] == "preocupação"
    assert constraints["last_sub_niche"] == "medicina"


def test_build_alternation_context_empty():
    ctx = _build_alternation_context({})
    assert "Sem histórico" in ctx


def test_build_alternation_context_with_data():
    ctx = _build_alternation_context({
        "last_aesthetic": "ficção_científica",
        "last_composition": "B",
        "last_palette": "#00A3FF",
        "last_expression": "surpresa",
        "last_sub_niche": "robótica",
    })
    assert "DIFERENTE" in ctx
    assert "ficção_científica" in ctx
    assert "robótica" in ctx


def test_metadata_state_merge():
    """Verify that VideoMetadata can be stored in workflow state."""
    metadata = VideoMetadata(
        titles=TitlesBlock(
            all_10=[
                TitleCandidate(
                    title=f"Title {i}",
                    formula="pergunta_existencial",
                    char_count=20,
                    word_count=3,
                )
                for i in range(10)
            ],
            top_3=[
                TitleTop3(
                    title="Best Title",
                    formula="pergunta_existencial",
                    justification="High curiosity",
                    keyword_validation=KeywordMetrics(
                        keyword="IA", volume=5000, competition=40, overall=72
                    ),
                )
            ],
        ),
        thumbnail=ThumbnailSpec(
            aesthetic="documental_sombria",
            composition="A",
            emotion="urgência",
            dominant_color="#1A1A2E",
            accent_color="#00A3FF",
            prompt_en="A dramatic close-up...",
        ),
        description_seo="Test description with 250+ words " * 20,
        tags=TagsBlock(
            list=["IA", "ciência"],
            validation_table=[
                TagValidation(tag="IA", volume=10000, competition=80, overall=60)
            ],
        ),
        hashtags=["#IA", "#Ciência", "#Tecnologia"],
        community_post="A test community post.",
    )
    state: WorkflowState = {
        "video_metadata": metadata,
        "current_phase": "metadata_done",
    }
    assert state["video_metadata"] is not None
    assert len(state["video_metadata"].titles.all_10) == 10
