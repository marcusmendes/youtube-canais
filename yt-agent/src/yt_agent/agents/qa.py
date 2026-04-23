"""Agent QA — Checklist validation of script and metadata."""

from __future__ import annotations

from yt_agent.agents.base import get_sonnet, invoke_agent_with_tools, load_prompt
from yt_agent.state import QAReport, WorkflowState


async def run_qa_agent(state: WorkflowState) -> dict:
    """Execute the QA checklist agent.

    Validates the Script and VideoMetadata against the 28-item checklist.

    Returns a dict to merge into WorkflowState with keys:
    - qa_report: QAReport
    - current_phase: "qa_done"
    """
    system_prompt = load_prompt("qa.md")

    script = state.get("script")
    metadata = state.get("video_metadata")
    qa_attempt = state.get("qa_attempt", 1)

    script_json = "(Script não disponível)"
    if script is not None:
        script_json = script.model_dump_json(indent=2)

    metadata_json = "(Metadados não disponíveis)"
    if metadata is not None:
        metadata_json = metadata.model_dump_json(indent=2)

    has_performance = state.get("performance_diagnosis") is not None
    has_briefing = state.get("competitive_briefing") is not None
    has_validation = state.get("theme_validation") is not None

    user_message = (
        f"Execute the 28-item QA checklist on the following script and metadata.\n"
        f"This is attempt {qa_attempt} of 2.\n\n"
        f"## CONTEXT FLAGS\n"
        f"- Fase P executed: {'Yes' if has_performance else 'No (skip item 15)'}\n"
        f"- Fase 0 executed: {'Yes' if has_briefing else 'No (skip item 16)'}\n"
        f"- Theme validation executed: {'Yes' if has_validation else 'No (skip item 17)'}\n"
        f"- Format: {state.get('format', 'long')}\n\n"
        f"## SCRIPT\n```json\n{script_json}\n```\n\n"
        f"## VIDEO METADATA\n```json\n{metadata_json}\n```\n\n"
        f"Evaluate all 28 items. For each failure, generate specific fix_instructions.\n"
        f"If failures >= 3 and attempt < 2, verdict = 'needs_fix'.\n"
        f"If failures >= 3 and attempt >= 2, verdict = 'approved_with_warnings' "
        f"(prevent infinite loop).\n\n"
        f"Return the result as a JSON object matching the QAReport schema:\n"
        f"{QAReport.model_json_schema()}"
    )

    try:
        report = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=[],
            llm=get_sonnet(),
            output_schema=QAReport,
        )
    except Exception as exc:
        return {
            "qa_report": None,
            "current_phase": "qa_done",
            "errors": state.get("errors", []) + [f"Agent QA failed: {exc}"],
        }

    return {
        "qa_report": report,
        "current_phase": "qa_done",
    }


def decide_after_qa(state: WorkflowState) -> str:
    """Routing decision after QA validation.

    Returns:
        "pass" — script approved, continue to output
        "fail" — script needs fixes, route to scriptwriter_fix
        "pass_forced" — too many attempts, accept with warnings
    """
    report = state.get("qa_report")
    if report is None:
        return "pass"

    qa_attempt = state.get("qa_attempt", 1)

    if report.verdict in ("approved", "approved_with_warnings"):
        return "pass"

    if report.verdict == "needs_fix" and qa_attempt < 2:
        return "fail"

    return "pass_forced"
