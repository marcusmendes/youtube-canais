"""Tests for Agent QA — Checklist validation."""

from __future__ import annotations

from yt_agent.agents.qa import decide_after_qa
from yt_agent.state import QAItem, QAReport, WorkflowState


def _make_report(
    verdict: str = "approved",
    passed: int = 26,
    failed: int = 2,
    attempt: int = 1,
    fix_instructions: list[str] | None = None,
) -> QAReport:
    items = [
        QAItem(number=i, name=f"Item {i}", status="pass" if i <= passed else "fail")
        for i in range(1, 29)
    ]
    return QAReport(
        total_items=28,
        passed=passed,
        failed=failed,
        attempt=attempt,
        items=items,
        verdict=verdict,
        fix_instructions=fix_instructions or [],
    )


def test_decide_pass_when_no_report():
    state: WorkflowState = {}
    assert decide_after_qa(state) == "pass"


def test_decide_pass_when_approved():
    state: WorkflowState = {"qa_report": _make_report("approved")}
    assert decide_after_qa(state) == "pass"


def test_decide_pass_when_approved_with_warnings():
    state: WorkflowState = {"qa_report": _make_report("approved_with_warnings")}
    assert decide_after_qa(state) == "pass"


def test_decide_fail_when_needs_fix_first_attempt():
    state: WorkflowState = {
        "qa_report": _make_report(
            "needs_fix",
            passed=24,
            failed=4,
            attempt=1,
            fix_instructions=[
                "Item 6: Block 3 missing VISUAL",
                "Item 21: Generic visual in block 2",
                "Item 24: Missing pattern interrupt at 2min",
                "Item 26: Informal contraction found",
            ],
        ),
        "qa_attempt": 1,
    }
    assert decide_after_qa(state) == "fail"


def test_decide_pass_forced_on_second_attempt():
    state: WorkflowState = {
        "qa_report": _make_report(
            "needs_fix",
            passed=24,
            failed=4,
            attempt=2,
            fix_instructions=["Item 6: Still missing VISUAL"],
        ),
        "qa_attempt": 2,
    }
    assert decide_after_qa(state) == "pass_forced"


def test_qa_report_items_count():
    report = _make_report()
    assert len(report.items) == 28
    assert report.total_items == 28


def test_qa_report_fix_instructions_present():
    report = _make_report(
        "needs_fix",
        passed=25,
        failed=3,
        fix_instructions=[
            "Item 6: Add VISUAL to block 3",
            "Item 21: Replace generic visual",
            "Item 24: Add pattern interrupt",
        ],
    )
    assert len(report.fix_instructions) == 3
    assert all("Item" in instr for instr in report.fix_instructions)


def test_qa_report_roundtrip_json():
    report = _make_report(
        "needs_fix",
        passed=25,
        failed=3,
        fix_instructions=["Fix block 3 visual"],
    )
    json_str = report.model_dump_json()
    restored = QAReport.model_validate_json(json_str)
    assert restored.verdict == "needs_fix"
    assert restored.failed == 3
    assert len(restored.fix_instructions) == 1
