"""Tests for the output renderer."""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

from yt_agent.output.renderer import render_to_markdown
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


def _full_state() -> WorkflowState:
    """Build a complete workflow state with all agents' outputs."""
    return WorkflowState(
        video_topic="IA e Medicina",
        sub_niche="IA + Saúde",
        format="long",
        performance_diagnosis=PerformanceDiagnosis(
            last_video=LastVideoMetrics(
                id="abc123", title="Test Video", type="long",
                published_at=date(2026, 4, 1), views=5000,
                avg_retention_pct=42.0, like_ratio_pct=8.5,
                comments=42, subscribers_gained=10,
            ),
            channel_baseline=ChannelBaseline(
                avg_views=3000, avg_retention_pct=40.0,
                avg_like_ratio_pct=7.0, avg_comments=30,
            ),
            critical_points=CriticalPoints(retention_30s_pct=60.0),
            lessons=Lessons(
                errors_to_avoid=["Long intro"],
                successes_to_keep=["Strong hook"],
            ),
            calibrations=["Faster hook", "More data in first 15s"],
        ),
        competitive_briefing=CompetitiveBriefing(
            competitors_analyzed=[],
            top_errors=[],
            unexplored_angles=[],
            structural_pattern_to_avoid="Clickbait",
            differentiation_manifesto="Unique science angle",
            audience_insights=AudienceInsights(),
        ),
        theme_validation=ThemeValidation(
            keyword="IA medicina", volume=500, competition=40, overall=65,
            verdict="approved",
            golden_checklist=GoldenChecklist(
                universal_angle="Health matters",
                short_premise="AI transforms medicine",
                persona_trigger="Hope for cures",
            ),
        ),
        video_metadata=VideoMetadata(
            titles=TitlesBlock(
                all_10=[
                    TitleCandidate(
                        title=f"Title {i}", formula="pergunta",
                        char_count=20, word_count=3,
                    )
                    for i in range(10)
                ],
                top_3=[
                    TitleTop3(
                        title="Best Title", formula="pergunta",
                        justification="High CTR",
                        keyword_validation=KeywordMetrics(
                            keyword="IA", volume=5000,
                            competition=40, overall=72,
                        ),
                    )
                ],
            ),
            thumbnail=ThumbnailSpec(
                aesthetic="documental_sombria", composition="A",
                emotion="urgência", dominant_color="#1A1A2E",
                accent_color="#00A3FF", prompt_en="A dramatic shot",
            ),
            description_seo="SEO description text " * 20,
            tags=TagsBlock(
                list=["IA", "medicina"],
                validation_table=[
                    TagValidation(
                        tag="IA", volume=10000,
                        competition=80, overall=60,
                    )
                ],
            ),
            hashtags=["#IA", "#Medicina", "#Ciência"],
            community_post="Test community post.",
        ),
        script=Script(
            word_count=1500,
            estimated_duration_min=10.0,
            sections=[
                ScriptSection(
                    type="hook", label="Hook",
                    narration="Opening line.",
                    visual="VISUAL: Neural network.",
                ),
                ScriptSection(
                    type="context", label="Context",
                    narration="Context text.",
                    visual="VISUAL: Lab scene.",
                ),
                ScriptSection(
                    type="block_1", label="Âncora",
                    narration="Block 1 text.",
                    visual="VISUAL: Scientist.",
                ),
                ScriptSection(
                    type="block_2", label="Escalada",
                    narration="Block 2 text.",
                    visual="VISUAL: Data.",
                    pattern_interrupt="Did you know?",
                ),
                ScriptSection(
                    type="block_3", label="Clímax",
                    narration="Block 3 text.",
                    visual="VISUAL: Breakthrough.",
                    editorial_insertion="This changed my view.",
                ),
                ScriptSection(
                    type="block_4", label="Implicação",
                    narration="Block 4 text.",
                    visual="VISUAL: Future.",
                    cta="What do you think?",
                ),
                ScriptSection(
                    type="cta_final", label="CTA",
                    narration="Subscribe.",
                    visual="VISUAL: Outro.",
                ),
            ],
            open_loops_map=[
                OpenLoop(
                    loop_number=1, opens_at="0:05",
                    content="Hook promise",
                    closes_at="8:30", payoff_type="full",
                ),
            ],
            retention_audit=RetentionAudit(
                hook_delivers_promise_in_8s=True,
                zero_institutional_intro=True,
                first_visual_specific=True,
                numeric_data_in_15s=True,
                context_opens_loop=True,
            ),
            differentiation_manifesto_location="block_4",
        ),
        qa_report=QAReport(
            passed=27, failed=1, attempt=1,
            items=[
                QAItem(number=i, name=f"Item {i}", status="pass")
                for i in range(1, 29)
            ],
            verdict="approved",
        ),
        human_decisions=[],
        qa_attempt=1,
        current_phase="completed",
        errors=[],
    )


def test_render_full_state():
    """Rendering a complete state produces a valid Markdown file."""
    state = _full_state()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = render_to_markdown(state, run_id="test-001", output_dir=Path(tmpdir))
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "# Workflow Output — test-001" in content
        assert "IA e Medicina" in content
        assert "Diagnóstico de Performance" in content
        assert "Briefing Competitivo" in content
        assert "Validação de Tema" in content
        assert "Metadados" in content
        assert "Roteiro" in content
        assert "QA Report" in content


def test_render_empty_state():
    """Rendering an empty state still produces a valid file without errors."""
    state: WorkflowState = {"video_topic": "Test", "errors": []}
    with tempfile.TemporaryDirectory() as tmpdir:
        path = render_to_markdown(state, run_id="empty-001", output_dir=Path(tmpdir))
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Não executado" in content or "Não gerado" in content


def test_render_with_errors():
    """Errors in state are rendered in the output."""
    state: WorkflowState = {
        "video_topic": "Test",
        "errors": ["Agent P failed: timeout", "Agent QA failed: parse error"],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        path = render_to_markdown(state, run_id="err-001", output_dir=Path(tmpdir))
        content = path.read_text(encoding="utf-8")
        assert "Erros durante execução" in content
        assert "Agent P failed" in content
        assert "Agent QA failed" in content


def test_render_creates_output_dir():
    """The renderer auto-creates the output directory if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested = Path(tmpdir) / "sub" / "dir"
        path = render_to_markdown(
            {"video_topic": "Test", "errors": []},
            run_id="nested-001",
            output_dir=nested,
        )
        assert path.exists()
        assert nested.exists()
