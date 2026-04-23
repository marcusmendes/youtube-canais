"""Agent P — Performance Diagnosis of the last published video."""

from __future__ import annotations

from typing import TYPE_CHECKING

from yt_agent.agents.base import get_sonnet, invoke_agent_with_tools, load_prompt
from yt_agent.config import get_settings
from yt_agent.state import PerformanceDiagnosis, WorkflowState
from yt_agent.tools import get_performance_tools

if TYPE_CHECKING:
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient


async def run_performance_agent(
    state: WorkflowState,
    *,
    vidiq: VidIQClient,
    youtube: YouTubeClient,
) -> dict:
    """Execute the performance diagnosis agent.

    Returns a dict to merge into WorkflowState with keys:
    - performance_diagnosis: PerformanceDiagnosis
    - current_phase: "fase_p_done"
    """
    settings = get_settings()
    channel = settings.channel_handle
    system_prompt = load_prompt("performance.md").replace("{channel_handle}", channel)
    tools = get_performance_tools(vidiq, youtube)

    topic = state.get("video_topic", "unknown topic")
    fmt = state.get("format", "long")

    user_message = (
        f"Analyze the performance of the last published video on the channel.\n\n"
        f"IMPORTANT: The channel handle is `{channel}`. "
        f"Always use `{channel}` as channel_id for VidIQ calls.\n\n"
        f"Context for the NEXT video:\n"
        f"- Topic: {topic}\n"
        f"- Format: {fmt}\n\n"
        f"Use the available tools to gather data, starting with "
        f"`vidiq_channel_videos` using channel_id='{channel}'.\n\n"
        f"Return the result as a JSON object matching the PerformanceDiagnosis schema:\n"
        f"{PerformanceDiagnosis.model_json_schema()}"
    )

    try:
        diagnosis = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=tools,
            llm=get_sonnet(),
            output_schema=PerformanceDiagnosis,
        )
    except Exception as exc:
        return {
            "performance_diagnosis": None,
            "current_phase": "fase_p_done",
            "errors": state.get("errors", []) + [f"Agent P failed: {exc}"],
        }

    return {
        "performance_diagnosis": diagnosis,
        "current_phase": "fase_p_done",
    }


def decide_after_performance(state: WorkflowState) -> str:
    """Routing decision after Agent P.

    Returns:
        "ok" — continue to Agent 0
        "low_retention" — pause for human decision
    """
    diagnosis = state.get("performance_diagnosis")
    if diagnosis is None:
        return "ok"
    if diagnosis.alert == "low_retention":
        return "low_retention"
    return "ok"
