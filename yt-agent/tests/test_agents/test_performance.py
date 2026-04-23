"""Tests for Agent P — Performance Diagnosis."""

from __future__ import annotations

from datetime import date

from yt_agent.agents.performance import decide_after_performance
from yt_agent.state import (
    ChannelBaseline,
    CriticalPoints,
    LastVideoMetrics,
    Lessons,
    PerformanceDiagnosis,
    WorkflowState,
)


def _make_diagnosis(alert: str = "none", avg_retention: float = 45.0) -> PerformanceDiagnosis:
    return PerformanceDiagnosis(
        last_video=LastVideoMetrics(
            id="abc123",
            title="Test Video",
            type="long",
            published_at=date(2026, 4, 1),
            views=5000,
            avg_retention_pct=avg_retention,
            like_ratio_pct=8.5,
            comments=42,
            subscribers_gained=10,
        ),
        channel_baseline=ChannelBaseline(
            avg_views=3000,
            avg_retention_pct=40.0,
            avg_like_ratio_pct=7.0,
            avg_comments=30,
        ),
        critical_points=CriticalPoints(retention_30s_pct=60.0),
        lessons=Lessons(
            errors_to_avoid=["Too long intro"],
            successes_to_keep=["Strong hook"],
        ),
        calibrations=["Use faster hook"],
        alert=alert,
    )


def test_decide_ok_when_no_diagnosis():
    state: WorkflowState = {}
    assert decide_after_performance(state) == "ok"


def test_decide_ok_when_alert_none():
    state: WorkflowState = {"performance_diagnosis": _make_diagnosis("none")}
    assert decide_after_performance(state) == "ok"


def test_decide_ok_when_alert_low_engagement():
    state: WorkflowState = {"performance_diagnosis": _make_diagnosis("low_engagement")}
    assert decide_after_performance(state) == "ok"


def test_decide_low_retention():
    state: WorkflowState = {
        "performance_diagnosis": _make_diagnosis("low_retention", avg_retention=12.0)
    }
    assert decide_after_performance(state) == "low_retention"
