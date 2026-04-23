"""Tests for Agent Roteirista — Script generation."""

from __future__ import annotations

import tempfile
from pathlib import Path

from yt_agent.agents.scriptwriter import load_writing_model
from yt_agent.state import (
    OpenLoop,
    RetentionAudit,
    Script,
    ScriptSection,
    WorkflowState,
)


def test_load_writing_model_from_valid_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "modelo-01.md"
        model_path.write_text("# Estilo documental\n\nUm exemplo de escrita.", encoding="utf-8")

        result = load_writing_model(Path(tmpdir))
        assert "Estilo documental" in result


def test_load_writing_model_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = load_writing_model(Path(tmpdir))
        assert "Nenhum modelo" in result


def test_load_writing_model_missing_dir():
    result = load_writing_model(Path("/nonexistent/path/models"))
    assert "Nenhum modelo" in result


def _make_script() -> Script:
    sections = [
        ScriptSection(
            type="hook",
            label="Hook",
            narration="A compelling opening line.",
            visual="VISUAL: Close-up of a neural network activating.",
        ),
        ScriptSection(
            type="context",
            label="Context",
            narration="Context expansion of the hook.",
            visual="VISUAL: Wide shot of a research laboratory.",
        ),
        ScriptSection(
            type="block_1",
            label="Âncora",
            narration="First block narration " * 50,
            visual="VISUAL: Scientists working in a lab.",
        ),
        ScriptSection(
            type="block_2",
            label="Escalada",
            narration="Second block narration " * 50,
            visual="VISUAL: Data visualization on screens.",
            pattern_interrupt="What if I told you this changes everything?",
        ),
        ScriptSection(
            type="block_3",
            label="Clímax",
            narration="Third block narration " * 50,
            visual="VISUAL: Dramatic reveal of breakthrough.",
            editorial_insertion="Personally, this shifted my perspective.",
        ),
        ScriptSection(
            type="block_4",
            label="Implicação",
            narration="Fourth block narration " * 50,
            visual="VISUAL: Future implications visualization.",
            cta="What do you think — is this progress or peril?",
        ),
        ScriptSection(
            type="cta_final",
            label="CTA Final",
            narration="Final crescendo and call to action.",
            visual="VISUAL: Cinematic outro.",
        ),
    ]
    return Script(
        word_count=1500,
        estimated_duration_min=10.0,
        sections=sections,
        open_loops_map=[
            OpenLoop(
                loop_number=1,
                opens_at="0:05",
                content="Promise from hook",
                closes_at="8:30",
                payoff_type="full_reveal",
            ),
            OpenLoop(
                loop_number=2,
                opens_at="0:15",
                content="Unexpected question",
                closes_at="5:00",
                payoff_type="partial_data",
            ),
            OpenLoop(
                loop_number=3,
                opens_at="0:45",
                content="Teaser of discovery",
                closes_at="7:00",
                payoff_type="narrative_bridge",
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
    )


def test_script_creation():
    script = _make_script()
    assert script.word_count == 1500
    assert len(script.sections) == 7
    assert len(script.open_loops_map) == 3
    assert script.retention_audit.hook_delivers_promise_in_8s is True


def test_script_section_types():
    script = _make_script()
    types = [s.type for s in script.sections]
    assert types == ["hook", "context", "block_1", "block_2", "block_3", "block_4", "cta_final"]


def test_script_state_merge():
    script = _make_script()
    state: WorkflowState = {
        "script": script,
        "current_phase": "script_done",
    }
    assert state["script"] is not None
    assert state["script"].estimated_duration_min == 10.0


def test_script_roundtrip_json():
    script = _make_script()
    json_str = script.model_dump_json()
    restored = Script.model_validate_json(json_str)
    assert restored.word_count == script.word_count
    assert len(restored.sections) == len(script.sections)
