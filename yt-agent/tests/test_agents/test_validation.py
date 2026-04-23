"""Tests for Agent V — Theme Validation."""

from __future__ import annotations

from yt_agent.agents.validation import decide_after_validation
from yt_agent.state import GoldenChecklist, KeywordMetrics, ThemeValidation, WorkflowState


def _make_validation(
    verdict: str = "approved", volume: int = 500, overall: int = 65
) -> ThemeValidation:
    return ThemeValidation(
        keyword="inteligência artificial medicina",
        volume=volume,
        competition=45,
        overall=overall,
        verdict=verdict,
        alternatives=[
            KeywordMetrics(keyword="IA saúde", volume=800, competition=30, overall=70)
        ],
        golden_checklist=GoldenChecklist(
            universal_angle="Everyone cares about health",
            short_premise="AI cures diseases",
            persona_trigger="Fear of missing out on medical breakthroughs",
        ),
    )


def test_decide_ok_when_no_validation():
    state: WorkflowState = {}
    assert decide_after_validation(state) == "ok"


def test_decide_ok_when_approved():
    state: WorkflowState = {"theme_validation": _make_validation("approved")}
    assert decide_after_validation(state) == "ok"


def test_decide_low_demand():
    state: WorkflowState = {
        "theme_validation": _make_validation("low_demand", volume=0, overall=15)
    }
    assert decide_after_validation(state) == "low_demand"


def test_decide_rejected():
    state: WorkflowState = {
        "theme_validation": _make_validation("rejected", volume=0, overall=5)
    }
    assert decide_after_validation(state) == "low_demand"
