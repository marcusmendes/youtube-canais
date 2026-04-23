"""Tests for agent functions with mocked LLM and API calls.

Covers Sprint 6.1 — unit tests for all agents using mocked LLM responses.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from yt_agent.state import (
    KeywordMetrics,
    OpenLoop,
    RetentionAudit,
    Script,
    ScriptSection,
    TagsBlock,
    TagValidation,
    ThumbnailSpec,
    TitleCandidate,
    TitlesBlock,
    TitleTop3,
    VideoMetadata,
    WorkflowState,
)

PERF_INVOKE = "yt_agent.agents.performance.invoke_agent_with_tools"
COMP_INVOKE = "yt_agent.agents.competitive.invoke_agent_with_tools"
VAL_INVOKE = "yt_agent.agents.validation.invoke_agent_with_tools"
META_INVOKE = "yt_agent.agents.metadata.invoke_agent_with_tools"
SCRIPT_INVOKE = "yt_agent.agents.scriptwriter.invoke_agent_with_tools"
QA_INVOKE = "yt_agent.agents.qa.invoke_agent_with_tools"


# ── Helpers ──────────────────────────────────────────────────────────


def _perf_diagnosis_kwargs(alert: str = "none") -> dict:
    from yt_agent.state import (
        ChannelBaseline,
        CriticalPoints,
        LastVideoMetrics,
        Lessons,
        PerformanceDiagnosis,
    )

    return PerformanceDiagnosis(
        last_video=LastVideoMetrics(
            id="abc123", title="Test", type="long",
            published_at="2026-04-01", views=5000,
            avg_retention_pct=42.0, like_ratio_pct=8.5,
            comments=42, subscribers_gained=10,
        ),
        channel_baseline=ChannelBaseline(
            avg_views=3000, avg_retention_pct=40.0,
            avg_like_ratio_pct=7.0, avg_comments=30,
        ),
        retention_drops=[],
        critical_points=CriticalPoints(retention_30s_pct=60.0),
        lessons=Lessons(
            errors_to_avoid=["Long intro"],
            successes_to_keep=["Strong hook"],
        ),
        calibrations=["Faster hook"],
        alert=alert,
    )


def _comp_briefing():
    from yt_agent.state import (
        AudienceInsights,
        CompetitiveBriefing,
        CompetitorError,
        UnexploredAngle,
    )

    return CompetitiveBriefing(
        competitors_analyzed=[],
        top_errors=[
            CompetitorError(error="Clickbait", correction="Payoff", source="Nature 2025"),
            CompetitorError(error="Long intro", correction="Skip", source="MIT 2025"),
            CompetitorError(error="No sources", correction="Cite", source="IEEE 2025"),
        ],
        unexplored_angles=[
            UnexploredAngle(angle="Ethical AI", why_possible="Growing (Nature 2025)"),
            UnexploredAngle(angle="AI in Brazil", why_possible="Underserved"),
            UnexploredAngle(angle="AI regulation", why_possible="EU AI Act"),
        ],
        structural_pattern_to_avoid="Clickbait without payoff",
        differentiation_manifesto="Science-first",
        audience_insights=AudienceInsights(
            top_questions=["How does AI work?"],
            dominant_sentiment="curious",
        ),
        competitor_tags=["IA", "ciência"],
    )


def _theme_validation(verdict: str = "approved", volume: int = 500):
    from yt_agent.state import GoldenChecklist, ThemeValidation

    return ThemeValidation(
        keyword="IA medicina", volume=volume, competition=40,
        overall=65, verdict=verdict,
        alternatives=[KeywordMetrics(keyword="IA saúde", volume=800, competition=30, overall=70)],
        golden_checklist=GoldenChecklist(
            universal_angle="Health", short_premise="AI cures", persona_trigger="Hope",
        ),
    )


# ── Agent P ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_performance_agent_normal_retention():
    from yt_agent.agents.performance import run_performance_agent

    diag = _perf_diagnosis_kwargs("none")
    with patch(PERF_INVOKE, return_value=diag):
        state: WorkflowState = {"video_topic": "AI", "format": "long"}
        result = await run_performance_agent(state, vidiq=AsyncMock(), youtube=AsyncMock())
    assert result["performance_diagnosis"] is not None
    assert result["performance_diagnosis"].alert == "none"
    assert result["current_phase"] == "fase_p_done"


@pytest.mark.asyncio
async def test_performance_agent_low_retention():
    from yt_agent.agents.performance import run_performance_agent

    diag = _perf_diagnosis_kwargs("low_retention")
    with patch(PERF_INVOKE, return_value=diag):
        state: WorkflowState = {"video_topic": "AI", "format": "long"}
        result = await run_performance_agent(state, vidiq=AsyncMock(), youtube=AsyncMock())
    assert result["performance_diagnosis"].alert == "low_retention"


@pytest.mark.asyncio
async def test_performance_agent_api_failure():
    from yt_agent.agents.performance import run_performance_agent

    with patch(PERF_INVOKE, side_effect=RuntimeError("API down")):
        state: WorkflowState = {"video_topic": "AI", "format": "long", "errors": []}
        result = await run_performance_agent(state, vidiq=AsyncMock(), youtube=AsyncMock())
    assert result["performance_diagnosis"] is None
    assert "Agent P failed" in result["errors"][0]


# ── Agent 0 ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_competitive_agent_with_data():
    from yt_agent.agents.competitive import run_competitive_agent

    briefing = _comp_briefing()
    with patch(COMP_INVOKE, return_value=briefing):
        state: WorkflowState = {
            "video_topic": "AI", "sub_niche": "IA + Saúde",
            "reference_period": "2025-2026",
        }
        result = await run_competitive_agent(state, vidiq=AsyncMock(), youtube=AsyncMock())
    assert result["competitive_briefing"] is not None
    assert len(result["competitive_briefing"].top_errors) >= 3
    assert len(result["competitive_briefing"].unexplored_angles) >= 3


@pytest.mark.asyncio
async def test_competitive_agent_failure():
    from yt_agent.agents.competitive import run_competitive_agent

    with patch(COMP_INVOKE, side_effect=RuntimeError("Timeout")):
        state: WorkflowState = {"video_topic": "AI", "sub_niche": "IA", "errors": []}
        result = await run_competitive_agent(state, vidiq=AsyncMock(), youtube=AsyncMock())
    assert result["competitive_briefing"] is None
    assert "Agent 0 failed" in result["errors"][0]


# ── Agent V ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_validation_agent_approved():
    from yt_agent.agents.validation import run_validation_agent

    val = _theme_validation("approved", 500)
    with patch(VAL_INVOKE, return_value=val):
        state: WorkflowState = {"video_topic": "AI medicina", "sub_niche": "IA + Saúde"}
        result = await run_validation_agent(state, vidiq=AsyncMock())
    assert result["theme_validation"].verdict == "approved"


@pytest.mark.asyncio
async def test_validation_agent_low_demand():
    from yt_agent.agents.validation import run_validation_agent

    val = _theme_validation("low_demand", 0)
    with patch(VAL_INVOKE, return_value=val):
        state: WorkflowState = {"video_topic": "obscure topic", "sub_niche": "IA"}
        result = await run_validation_agent(state, vidiq=AsyncMock())
    assert result["theme_validation"].verdict == "low_demand"
    assert len(result["theme_validation"].alternatives) >= 1


# ── Agent Meta ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_metadata_agent_generates_titles():
    from yt_agent.agents.metadata import run_metadata_agent

    meta = _make_metadata()
    memory_mock = AsyncMock()
    memory_mock.get_last_video = AsyncMock(return_value=None)

    with patch(META_INVOKE, return_value=meta):
        state: WorkflowState = {
            "video_topic": "AI", "sub_niche": "IA", "format": "long",
        }
        result = await run_metadata_agent(state, vidiq=AsyncMock(), memory=memory_mock)
    assert result["video_metadata"] is not None
    assert len(result["video_metadata"].titles.all_10) == 10


@pytest.mark.asyncio
async def test_metadata_agent_with_alternation():
    import datetime as dt

    from yt_agent.agents.metadata import run_metadata_agent
    from yt_agent.memory.models import Video

    meta = _make_metadata()
    last_video = Video(
        id="prev", title="Previous", sub_niche="IA",
        published_at=dt.date(2026, 4, 1),
        thumbnail_aesthetic="documental_sombria",
        thumbnail_composition="A",
        thumbnail_palette="#1A1A2E",
        thumbnail_expression="urgência",
    )
    memory_mock = AsyncMock()
    memory_mock.get_last_video = AsyncMock(return_value=last_video)

    with patch(META_INVOKE, return_value=meta):
        state: WorkflowState = {
            "video_topic": "AI", "sub_niche": "IA", "format": "long",
        }
        result = await run_metadata_agent(state, vidiq=AsyncMock(), memory=memory_mock)
    assert result["video_metadata"] is not None
    memory_mock.get_last_video.assert_awaited_once()


# ── Agent QA ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_qa_agent_all_pass():
    from yt_agent.agents.qa import run_qa_agent
    from yt_agent.state import QAItem, QAReport

    qa = QAReport(
        total_items=28, passed=28, failed=0, attempt=1,
        items=[QAItem(number=i, name=f"Item {i}", status="pass") for i in range(1, 29)],
        verdict="approved",
    )
    with patch(QA_INVOKE, return_value=qa):
        state: WorkflowState = {
            "script": _make_script(), "video_metadata": _make_metadata(),
            "qa_attempt": 1,
        }
        result = await run_qa_agent(state)
    assert result["qa_report"].verdict == "approved"
    assert result["qa_report"].passed == 28


@pytest.mark.asyncio
async def test_qa_agent_detects_failures():
    from yt_agent.agents.qa import run_qa_agent
    from yt_agent.state import QAItem, QAReport

    items = [
        QAItem(number=i, name=f"Item {i}", status="pass") for i in range(1, 29)
    ]
    items[5] = QAItem(number=6, name="Item 6", status="fail", detail="Block 3 missing VISUAL")
    items[20] = QAItem(number=21, name="Item 21", status="fail", detail="Generic visual")

    qa = QAReport(
        total_items=28, passed=26, failed=2, attempt=1,
        items=items, verdict="approved_with_warnings",
    )
    with patch(QA_INVOKE, return_value=qa):
        state: WorkflowState = {
            "script": _make_script(), "video_metadata": _make_metadata(),
            "qa_attempt": 1,
        }
        result = await run_qa_agent(state)
    failed_nums = [it.number for it in result["qa_report"].items if it.status == "fail"]
    assert 6 in failed_nums
    assert 21 in failed_nums


@pytest.mark.asyncio
async def test_qa_agent_generates_fix_instructions():
    from yt_agent.agents.qa import run_qa_agent
    from yt_agent.state import QAItem, QAReport

    items = [QAItem(number=i, name=f"Item {i}", status="pass") for i in range(1, 29)]
    for idx in [5, 20, 23]:
        items[idx] = QAItem(
            number=idx + 1, name=f"Item {idx + 1}",
            status="fail", detail=f"Failure in item {idx + 1}",
        )

    qa = QAReport(
        total_items=28, passed=25, failed=3, attempt=1,
        items=items, verdict="needs_fix",
        fix_instructions=[
            "Item 6: Add VISUAL", "Item 21: Replace generic", "Item 24: Add interrupt",
        ],
    )
    with patch(QA_INVOKE, return_value=qa):
        state: WorkflowState = {
            "script": _make_script(), "video_metadata": _make_metadata(),
            "qa_attempt": 1,
        }
        result = await run_qa_agent(state)
    assert result["qa_report"].verdict == "needs_fix"
    assert len(result["qa_report"].fix_instructions) == 3


# ── Agent Roteirista ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_scriptwriter_agent_generates_script():
    from yt_agent.agents.scriptwriter import run_scriptwriter_agent

    script = _make_script()
    with patch(SCRIPT_INVOKE, return_value=script):
        state: WorkflowState = {
            "video_topic": "AI", "sub_niche": "IA", "format": "long",
            "video_metadata": _make_metadata(),
        }
        result = await run_scriptwriter_agent(state)
    assert result["script"] is not None
    assert result["script"].word_count == 1500
    assert len(result["script"].sections) == 7


@pytest.mark.asyncio
async def test_scriptwriter_fix():
    from yt_agent.agents.scriptwriter import run_scriptwriter_fix
    from yt_agent.state import QAItem, QAReport

    qa = QAReport(
        total_items=28, passed=26, failed=2, attempt=1,
        items=[QAItem(number=i, name=f"I{i}", status="pass") for i in range(1, 29)],
        verdict="needs_fix",
        fix_instructions=["Fix block 3 VISUAL"],
    )
    fixed_script = _make_script()

    with patch(SCRIPT_INVOKE, return_value=fixed_script):
        state: WorkflowState = {
            "script": _make_script(), "qa_report": qa, "qa_attempt": 1,
        }
        result = await run_scriptwriter_fix(state)
    assert result["script"] is not None
    assert result["qa_attempt"] == 2


@pytest.mark.asyncio
async def test_scriptwriter_failure():
    from yt_agent.agents.scriptwriter import run_scriptwriter_agent

    with patch(SCRIPT_INVOKE, side_effect=RuntimeError("Opus down")):
        state: WorkflowState = {
            "video_topic": "AI", "sub_niche": "IA", "format": "long",
            "errors": [],
        }
        result = await run_scriptwriter_agent(state)
    assert result["script"] is None
    assert "Agent Roteirista failed" in result["errors"][0]


# ── Helpers for fixtures ─────────────────────────────────────────────


def _make_script() -> Script:
    return Script(
        word_count=1500, estimated_duration_min=10.0,
        sections=[
            ScriptSection(type="hook", label="H", narration="Hook.", visual="V:hook"),
            ScriptSection(type="context", label="C", narration="Ctx.", visual="V:ctx"),
            ScriptSection(type="block_1", label="B1", narration="B1.", visual="V:b1"),
            ScriptSection(type="block_2", label="B2", narration="B2.", visual="V:b2"),
            ScriptSection(type="block_3", label="B3", narration="B3.", visual="V:b3"),
            ScriptSection(type="block_4", label="B4", narration="B4.", visual="V:b4"),
            ScriptSection(type="cta_final", label="CTA", narration="Sub.", visual="V:cta"),
        ],
        open_loops_map=[OpenLoop(
            loop_number=1, opens_at="0:05", content="P",
            closes_at="8:30", payoff_type="full",
        )],
        retention_audit=RetentionAudit(
            hook_delivers_promise_in_8s=True, zero_institutional_intro=True,
            first_visual_specific=True, numeric_data_in_15s=True,
            context_opens_loop=True,
        ),
        differentiation_manifesto_location="block_4",
    )


def _make_metadata() -> VideoMetadata:
    return VideoMetadata(
        titles=TitlesBlock(
            all_10=[
                TitleCandidate(title=f"T{i}", formula="f", char_count=10, word_count=2)
                for i in range(10)
            ],
            top_3=[TitleTop3(
                title="Best", formula="f", justification="j",
                keyword_validation=KeywordMetrics(
                    keyword="IA", volume=5000, competition=40, overall=72,
                ),
            )],
        ),
        thumbnail=ThumbnailSpec(
            aesthetic="documental_sombria", composition="A",
            emotion="urgência", dominant_color="#1A1A2E",
            accent_color="#00A3FF", prompt_en="shot",
        ),
        description_seo="SEO " * 70,
        tags=TagsBlock(
            list=["IA"], validation_table=[
                TagValidation(tag="IA", volume=10000, competition=80, overall=60),
            ],
        ),
        hashtags=["#IA", "#Ciência", "#Tech"],
        community_post="Test post.",
    )
