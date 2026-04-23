"""Tests for the LangGraph workflow graph — compilation, routing, and integration.

Sprint 6.2: Tests for happy path, branching, and QA loop.
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from yt_agent.state import (
    AudienceInsights,
    ChannelBaseline,
    CompetitiveBriefing,
    CriticalPoints,
    GoldenChecklist,
    KeywordMetrics,
    LastVideoMetrics,
    Lessons,
    OpenLoop,
    PerformanceDiagnosis,
    QAItem,
    QAReport,
    RetentionAudit,
    Script,
    ScriptSection,
    TagsBlock,
    TagValidation,
    ThemeValidation,
    ThumbnailSpec,
    TitleCandidate,
    TitlesBlock,
    TitleTop3,
    VideoMetadata,
    WorkflowState,
)


@pytest.fixture
def mock_vidiq():
    return AsyncMock()


@pytest.fixture
def mock_youtube():
    return AsyncMock()


@pytest.fixture
def mock_memory():
    m = AsyncMock()
    m.save_video = AsyncMock()
    m.save_tags = AsyncMock()
    m.get_last_video = AsyncMock(return_value=None)
    return m


def test_graph_compiles(mock_vidiq, mock_youtube, mock_memory):
    """The graph should compile without errors."""
    from yt_agent.graph import build_graph

    graph = build_graph(
        vidiq=mock_vidiq,
        youtube=mock_youtube,
        memory=mock_memory,
    )
    assert graph is not None


def test_graph_has_expected_nodes(mock_vidiq, mock_youtube, mock_memory):
    """The compiled graph should contain all expected nodes."""
    from yt_agent.graph import build_graph

    graph = build_graph(
        vidiq=mock_vidiq,
        youtube=mock_youtube,
        memory=mock_memory,
    )

    node_names = set(graph.get_graph().nodes.keys())

    expected = {
        "__start__",
        "__end__",
        "fase_p",
        "decide_fase_p",
        "human_pause_retention",
        "fase_0",
        "validacao_tema",
        "decide_tema",
        "human_pause_tema",
        "metadados",
        "roteirista",
        "qa",
        "decide_qa",
        "roteirista_fix",
        "save_to_memory",
        "render_output",
    }
    assert expected.issubset(node_names), f"Missing nodes: {expected - node_names}"


def test_decide_fase_p_routes_ok():
    """Normal performance → routes to fase_0."""
    from yt_agent.agents.performance import decide_after_performance

    diag = PerformanceDiagnosis(
        last_video=LastVideoMetrics(
            id="v1", title="T", type="long", published_at=date(2026, 4, 1),
            views=5000, avg_retention_pct=45.0, like_ratio_pct=8.0,
            comments=30, subscribers_gained=10,
        ),
        channel_baseline=ChannelBaseline(
            avg_views=3000, avg_retention_pct=40.0,
            avg_like_ratio_pct=7.0, avg_comments=25,
        ),
        critical_points=CriticalPoints(),
        lessons=Lessons(errors_to_avoid=[], successes_to_keep=[]),
        calibrations=["test"],
        alert="none",
    )
    state: WorkflowState = {"performance_diagnosis": diag}
    assert decide_after_performance(state) == "ok"


def test_decide_fase_p_routes_low_retention():
    """Low retention → routes to human pause."""
    from yt_agent.agents.performance import decide_after_performance

    diag = PerformanceDiagnosis(
        last_video=LastVideoMetrics(
            id="v1", title="T", type="long", published_at=date(2026, 4, 1),
            views=500, avg_retention_pct=5.0, like_ratio_pct=2.0,
            comments=3, subscribers_gained=0,
        ),
        channel_baseline=ChannelBaseline(
            avg_views=3000, avg_retention_pct=40.0,
            avg_like_ratio_pct=7.0, avg_comments=25,
        ),
        critical_points=CriticalPoints(),
        lessons=Lessons(errors_to_avoid=[], successes_to_keep=[]),
        calibrations=["fix hooks"],
        alert="low_retention",
    )
    state: WorkflowState = {"performance_diagnosis": diag}
    assert decide_after_performance(state) == "low_retention"


def test_decide_tema_routes_ok():
    """Approved theme → routes to metadados."""
    from yt_agent.agents.validation import decide_after_validation

    val = ThemeValidation(
        keyword="IA medicina", volume=500, competition=40, overall=65,
        verdict="approved",
        golden_checklist=GoldenChecklist(
            universal_angle="Everyone cares",
            short_premise="AI cures",
            persona_trigger="Hope",
        ),
    )
    state: WorkflowState = {"theme_validation": val}
    assert decide_after_validation(state) == "ok"


def test_decide_tema_routes_low_demand():
    """Low demand → routes to human pause."""
    from yt_agent.agents.validation import decide_after_validation

    val = ThemeValidation(
        keyword="obscure topic", volume=0, competition=0, overall=5,
        verdict="low_demand",
        golden_checklist=GoldenChecklist(
            universal_angle="Niche",
            short_premise="Too niche",
            persona_trigger="None",
        ),
    )
    state: WorkflowState = {"theme_validation": val}
    assert decide_after_validation(state) == "low_demand"


def test_decide_qa_routes_pass():
    """Approved QA → routes to save_to_memory."""
    from yt_agent.agents.qa import decide_after_qa

    report = QAReport(
        passed=27, failed=1, attempt=1,
        items=[QAItem(number=i, name=f"Item {i}", status="pass") for i in range(1, 29)],
        verdict="approved",
    )
    state: WorkflowState = {"qa_report": report, "qa_attempt": 1}
    assert decide_after_qa(state) == "pass"


def test_decide_qa_routes_fail():
    """Needs fix → routes to roteirista_fix."""
    from yt_agent.agents.qa import decide_after_qa

    items = [
        QAItem(number=i, name=f"Item {i}", status="pass" if i <= 24 else "fail")
        for i in range(1, 29)
    ]
    report = QAReport(
        passed=24, failed=4, attempt=1,
        items=items,
        verdict="needs_fix",
        fix_instructions=["Fix item 25", "Fix item 26", "Fix item 27", "Fix item 28"],
    )
    state: WorkflowState = {"qa_report": report, "qa_attempt": 1}
    assert decide_after_qa(state) == "fail"


def test_decide_qa_routes_pass_forced():
    """Second attempt with failures → force pass."""
    from yt_agent.agents.qa import decide_after_qa

    items = [
        QAItem(number=i, name=f"Item {i}", status="pass" if i <= 24 else "fail")
        for i in range(1, 29)
    ]
    report = QAReport(
        passed=24, failed=4, attempt=2,
        items=items,
        verdict="needs_fix",
        fix_instructions=["Still broken"],
    )
    state: WorkflowState = {"qa_report": report, "qa_attempt": 2}
    assert decide_after_qa(state) == "pass_forced"


# ── Integration tests: full graph execution with mocked agents ──────


def _make_performance_diagnosis(alert: str = "none") -> PerformanceDiagnosis:
    return PerformanceDiagnosis(
        last_video=LastVideoMetrics(
            id="v1", title="T", type="long", published_at=date(2026, 4, 1),
            views=5000, avg_retention_pct=42.0, like_ratio_pct=8.0,
            comments=30, subscribers_gained=10,
        ),
        channel_baseline=ChannelBaseline(
            avg_views=3000, avg_retention_pct=40.0,
            avg_like_ratio_pct=7.0, avg_comments=25,
        ),
        critical_points=CriticalPoints(),
        lessons=Lessons(errors_to_avoid=[], successes_to_keep=[]),
        calibrations=["test"],
        alert=alert,
    )


def _make_competitive_briefing() -> CompetitiveBriefing:
    return CompetitiveBriefing(
        competitors_analyzed=[],
        top_errors=[],
        unexplored_angles=[],
        structural_pattern_to_avoid="Clickbait",
        differentiation_manifesto="Unique angle",
        audience_insights=AudienceInsights(),
    )


def _make_validation(verdict: str = "approved") -> ThemeValidation:
    return ThemeValidation(
        keyword="IA medicina", volume=500, competition=40, overall=65,
        verdict=verdict,
        golden_checklist=GoldenChecklist(
            universal_angle="Matters", short_premise="AI cures",
            persona_trigger="Hope",
        ),
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
                    keyword="IA", volume=5000, competition=40, overall=72
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


def _make_script() -> Script:
    return Script(
        word_count=1500, estimated_duration_min=10.0,
        sections=[
            ScriptSection(type="hook", label="H", narration="H.", visual="V"),
            ScriptSection(type="context", label="C", narration="C.", visual="V"),
            ScriptSection(type="block_1", label="B1", narration="B1.", visual="V"),
            ScriptSection(type="block_2", label="B2", narration="B2.", visual="V"),
            ScriptSection(type="block_3", label="B3", narration="B3.", visual="V"),
            ScriptSection(type="block_4", label="B4", narration="B4.", visual="V"),
            ScriptSection(type="cta_final", label="CTA", narration="S.", visual="V"),
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


def _make_qa_report(verdict: str = "approved", attempt: int = 1) -> QAReport:
    return QAReport(
        passed=28, failed=0, attempt=attempt,
        items=[QAItem(number=i, name=f"I{i}", status="pass") for i in range(1, 29)],
        verdict=verdict,
    )


@pytest.mark.asyncio
async def test_integration_happy_path(mock_vidiq, mock_youtube, mock_memory):
    """Full workflow with all agents returning valid data (no branching)."""
    from yt_agent.graph import build_graph

    graph = build_graph(
        vidiq=mock_vidiq, youtube=mock_youtube, memory=mock_memory,
    )

    perf = _make_performance_diagnosis("none")
    briefing = _make_competitive_briefing()
    validation = _make_validation("approved")
    metadata = _make_metadata()
    script = _make_script()
    qa = _make_qa_report("approved")

    with (
        patch(
            "yt_agent.graph.run_performance_agent",
            return_value={"performance_diagnosis": perf, "current_phase": "fase_p_done"},
        ),
        patch(
            "yt_agent.graph.run_competitive_agent",
            return_value={"competitive_briefing": briefing, "current_phase": "fase_0_done"},
        ),
        patch(
            "yt_agent.graph.run_validation_agent",
            return_value={"theme_validation": validation, "current_phase": "validation_done"},
        ),
        patch(
            "yt_agent.graph.run_metadata_agent",
            return_value={"video_metadata": metadata, "current_phase": "metadata_done"},
        ),
        patch(
            "yt_agent.graph.run_scriptwriter_agent",
            return_value={"script": script, "current_phase": "script_done"},
        ),
        patch(
            "yt_agent.graph.run_qa_agent",
            return_value={"qa_report": qa, "current_phase": "qa_done"},
        ),
        tempfile.TemporaryDirectory() as tmpdir,
        patch("yt_agent.output.renderer.OUTPUT_DIR", Path(tmpdir)),
    ):
        initial_state: WorkflowState = {
            "video_topic": "AI",
            "sub_niche": "Health",
            "format": "long",
            "editorial_angle": "revelador",
            "dominant_emotion": "admiration",
            "technical_detail": "intermediate",
            "reference_period": "2025-2026",
            "human_decisions": [],
            "qa_attempt": 1,
            "current_phase": "start",
            "errors": [],
        }

        result = await graph.ainvoke(initial_state)

    assert result["performance_diagnosis"] is not None
    assert result["competitive_briefing"] is not None
    assert result["theme_validation"] is not None
    assert result["video_metadata"] is not None
    assert result["script"] is not None
    assert result["qa_report"] is not None
    assert result["current_phase"] == "completed"
    mock_memory.save_video.assert_awaited_once()
    mock_memory.save_tags.assert_awaited_once()


@pytest.mark.asyncio
async def test_integration_qa_fail_triggers_fix_loop(
    mock_vidiq, mock_youtube, mock_memory,
):
    """QA failure on first attempt → roteirista_fix → QA pass on second attempt."""
    from yt_agent.graph import build_graph

    graph = build_graph(
        vidiq=mock_vidiq, youtube=mock_youtube, memory=mock_memory,
    )

    qa_fail = QAReport(
        passed=24, failed=4, attempt=1,
        items=[
            QAItem(number=i, name=f"I{i}", status="pass" if i <= 24 else "fail")
            for i in range(1, 29)
        ],
        verdict="needs_fix",
        fix_instructions=["Fix block 3"],
    )
    qa_pass = _make_qa_report("approved_with_warnings", attempt=2)
    qa_call_count = 0

    async def mock_qa(*_args, **_kwargs):
        nonlocal qa_call_count
        qa_call_count += 1
        if qa_call_count == 1:
            return {"qa_report": qa_fail, "current_phase": "qa_done"}
        return {"qa_report": qa_pass, "current_phase": "qa_done"}

    fix_called = False

    async def mock_fix(*_args, **_kwargs):
        nonlocal fix_called
        fix_called = True
        return {
            "script": _make_script(),
            "qa_attempt": 2,
            "current_phase": "script_fix_done",
        }

    with (
        patch(
            "yt_agent.graph.run_performance_agent",
            return_value={
                "performance_diagnosis": _make_performance_diagnosis(),
                "current_phase": "fase_p_done",
            },
        ),
        patch(
            "yt_agent.graph.run_competitive_agent",
            return_value={
                "competitive_briefing": _make_competitive_briefing(),
                "current_phase": "fase_0_done",
            },
        ),
        patch(
            "yt_agent.graph.run_validation_agent",
            return_value={
                "theme_validation": _make_validation(),
                "current_phase": "validation_done",
            },
        ),
        patch(
            "yt_agent.graph.run_metadata_agent",
            return_value={
                "video_metadata": _make_metadata(),
                "current_phase": "metadata_done",
            },
        ),
        patch(
            "yt_agent.graph.run_scriptwriter_agent",
            return_value={
                "script": _make_script(),
                "current_phase": "script_done",
            },
        ),
        patch("yt_agent.graph.run_qa_agent", side_effect=mock_qa),
        patch("yt_agent.graph.run_scriptwriter_fix", side_effect=mock_fix),
        tempfile.TemporaryDirectory() as tmpdir,
        patch("yt_agent.output.renderer.OUTPUT_DIR", Path(tmpdir)),
    ):
        result = await graph.ainvoke({
            "video_topic": "AI", "sub_niche": "Health", "format": "long",
            "human_decisions": [], "qa_attempt": 1,
            "current_phase": "start", "errors": [],
        })

    assert fix_called, "Script fix should have been called"
    assert qa_call_count == 2, "QA should have been called twice"
    assert result["qa_report"].verdict == "approved_with_warnings"
    assert result["current_phase"] == "completed"


@pytest.mark.asyncio
async def test_integration_low_retention_pauses(
    mock_vidiq, mock_youtube, mock_memory,
):
    """Low retention triggers interrupt — graph pauses at human_pause_retention."""
    from langgraph.checkpoint.memory import MemorySaver

    from yt_agent.graph import build_graph

    checkpointer = MemorySaver()
    graph = build_graph(
        vidiq=mock_vidiq, youtube=mock_youtube, memory=mock_memory,
        checkpointer=checkpointer,
    )

    perf = _make_performance_diagnosis("low_retention")
    config = {"configurable": {"thread_id": "test-low-ret"}}

    with patch(
        "yt_agent.graph.run_performance_agent",
        return_value={
            "performance_diagnosis": perf,
            "current_phase": "fase_p_done",
        },
    ):
        await graph.ainvoke(
            {
                "video_topic": "AI", "sub_niche": "Health", "format": "long",
                "human_decisions": [], "qa_attempt": 1,
                "current_phase": "start", "errors": [],
            },
            config,
        )

    snapshot = await graph.aget_state(config)
    assert snapshot.next, "Graph should be paused with pending nodes"
    assert "human_pause_retention" in snapshot.next


@pytest.mark.asyncio
async def test_integration_low_demand_pauses(
    mock_vidiq, mock_youtube, mock_memory,
):
    """Low demand triggers interrupt — graph pauses at human_pause_tema."""
    from langgraph.checkpoint.memory import MemorySaver

    from yt_agent.graph import build_graph

    checkpointer = MemorySaver()
    graph = build_graph(
        vidiq=mock_vidiq, youtube=mock_youtube, memory=mock_memory,
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": "test-low-demand"}}

    with (
        patch(
            "yt_agent.graph.run_performance_agent",
            return_value={
                "performance_diagnosis": _make_performance_diagnosis("none"),
                "current_phase": "fase_p_done",
            },
        ),
        patch(
            "yt_agent.graph.run_competitive_agent",
            return_value={
                "competitive_briefing": _make_competitive_briefing(),
                "current_phase": "fase_0_done",
            },
        ),
        patch(
            "yt_agent.graph.run_validation_agent",
            return_value={
                "theme_validation": _make_validation("low_demand"),
                "current_phase": "validation_done",
            },
        ),
    ):
        await graph.ainvoke(
            {
                "video_topic": "AI", "sub_niche": "Health", "format": "long",
                "human_decisions": [], "qa_attempt": 1,
                "current_phase": "start", "errors": [],
            },
            config,
        )

    snapshot = await graph.aget_state(config)
    assert snapshot.next, "Graph should be paused with pending nodes"
    assert "human_pause_tema" in snapshot.next


@pytest.mark.asyncio
async def test_integration_agent_failure_graceful(
    mock_vidiq, mock_youtube, mock_memory,
):
    """Agent P failure → workflow continues with None diagnosis."""
    from yt_agent.graph import build_graph

    graph = build_graph(
        vidiq=mock_vidiq, youtube=mock_youtube, memory=mock_memory,
    )

    with (
        patch(
            "yt_agent.graph.run_performance_agent",
            return_value={
                "performance_diagnosis": None,
                "current_phase": "fase_p_done",
                "errors": ["Agent P failed: VidIQ unavailable"],
            },
        ),
        patch(
            "yt_agent.graph.run_competitive_agent",
            return_value={
                "competitive_briefing": _make_competitive_briefing(),
                "current_phase": "fase_0_done",
            },
        ),
        patch(
            "yt_agent.graph.run_validation_agent",
            return_value={
                "theme_validation": _make_validation(),
                "current_phase": "validation_done",
            },
        ),
        patch(
            "yt_agent.graph.run_metadata_agent",
            return_value={
                "video_metadata": _make_metadata(),
                "current_phase": "metadata_done",
            },
        ),
        patch(
            "yt_agent.graph.run_scriptwriter_agent",
            return_value={
                "script": _make_script(),
                "current_phase": "script_done",
            },
        ),
        patch(
            "yt_agent.graph.run_qa_agent",
            return_value={
                "qa_report": _make_qa_report(),
                "current_phase": "qa_done",
            },
        ),
        tempfile.TemporaryDirectory() as tmpdir,
        patch("yt_agent.output.renderer.OUTPUT_DIR", Path(tmpdir)),
    ):
        result = await graph.ainvoke({
            "video_topic": "AI", "sub_niche": "Health", "format": "long",
            "human_decisions": [], "qa_attempt": 1,
            "current_phase": "start", "errors": [],
        })

    assert result["performance_diagnosis"] is None
    assert "VidIQ unavailable" in result["errors"][0]
    assert result["current_phase"] == "completed"


@pytest.mark.asyncio
async def test_integration_output_rendered(
    mock_vidiq, mock_youtube, mock_memory,
):
    """Verify that the final output markdown file is created."""
    from yt_agent.graph import build_graph

    graph = build_graph(
        vidiq=mock_vidiq, youtube=mock_youtube, memory=mock_memory,
    )

    with (
        patch(
            "yt_agent.graph.run_performance_agent",
            return_value={
                "performance_diagnosis": _make_performance_diagnosis(),
                "current_phase": "fase_p_done",
            },
        ),
        patch(
            "yt_agent.graph.run_competitive_agent",
            return_value={
                "competitive_briefing": _make_competitive_briefing(),
                "current_phase": "fase_0_done",
            },
        ),
        patch(
            "yt_agent.graph.run_validation_agent",
            return_value={
                "theme_validation": _make_validation(),
                "current_phase": "validation_done",
            },
        ),
        patch(
            "yt_agent.graph.run_metadata_agent",
            return_value={
                "video_metadata": _make_metadata(),
                "current_phase": "metadata_done",
            },
        ),
        patch(
            "yt_agent.graph.run_scriptwriter_agent",
            return_value={
                "script": _make_script(),
                "current_phase": "script_done",
            },
        ),
        patch(
            "yt_agent.graph.run_qa_agent",
            return_value={
                "qa_report": _make_qa_report(),
                "current_phase": "qa_done",
            },
        ),
        tempfile.TemporaryDirectory() as tmpdir,
        patch("yt_agent.output.renderer.OUTPUT_DIR", Path(tmpdir)),
    ):
        await graph.ainvoke({
            "video_topic": "AI Test", "sub_niche": "Health", "format": "long",
            "human_decisions": [], "qa_attempt": 1,
            "current_phase": "start", "errors": [],
        })

        output_files = list(Path(tmpdir).glob("*.md"))
        assert len(output_files) >= 1
        content = output_files[0].read_text(encoding="utf-8")
        assert "AI Test" in content
