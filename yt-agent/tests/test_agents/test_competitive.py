"""Tests for Agent 0 — Competitive Analysis."""

from __future__ import annotations

from yt_agent.state import CompetitiveBriefing, WorkflowState


def test_competitive_briefing_state_merge():
    """Verify that a competitive briefing can be stored in workflow state."""
    briefing = CompetitiveBriefing(
        competitors_analyzed=[],
        top_errors=[],
        unexplored_angles=[],
        structural_pattern_to_avoid="Clickbait without payoff",
        differentiation_manifesto="Unique angle based on real source",
        audience_insights={"top_questions": [], "dominant_sentiment": "positive"},
    )
    state: WorkflowState = {
        "competitive_briefing": briefing,
        "current_phase": "fase_0_done",
    }
    assert state["competitive_briefing"] is not None
    assert state["competitive_briefing"].differentiation_manifesto != ""
    assert state["current_phase"] == "fase_0_done"
