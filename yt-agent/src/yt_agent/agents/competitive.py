"""Agent 0 — Competitive Analysis of existing videos on the topic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from yt_agent.agents.base import get_sonnet, invoke_agent_with_tools, load_prompt
from yt_agent.state import CompetitiveBriefing, WorkflowState
from yt_agent.tools import get_competitive_tools

if TYPE_CHECKING:
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient


async def run_competitive_agent(
    state: WorkflowState,
    *,
    vidiq: VidIQClient,
    youtube: YouTubeClient,
) -> dict:
    """Execute the competitive analysis agent.

    Returns a dict to merge into WorkflowState with keys:
    - competitive_briefing: CompetitiveBriefing
    - current_phase: "fase_0_done"
    """
    system_prompt = load_prompt("competitive.md")
    tools = get_competitive_tools(vidiq, youtube)

    topic = state.get("video_topic", "unknown topic")
    sub_niche = state.get("sub_niche", "")
    period = state.get("reference_period", "2025-2026")

    user_message = (
        f"Perform a competitive analysis for the following video topic:\n\n"
        f"- Topic: {topic}\n"
        f"- Sub-niche: {sub_niche}\n"
        f"- Reference period: {period}\n\n"
        f"Search in BOTH Portuguese and English. Find outliers and trending videos, "
        f"extract transcripts from the top 3-5, analyze comments from the top 2-3, "
        f"and produce a competitive briefing.\n\n"
        f"Return the result as a JSON object matching the CompetitiveBriefing schema:\n"
        f"{CompetitiveBriefing.model_json_schema()}"
    )

    try:
        briefing = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=tools,
            llm=get_sonnet(),
            output_schema=CompetitiveBriefing,
        )
    except Exception as exc:
        return {
            "competitive_briefing": None,
            "current_phase": "fase_0_done",
            "errors": state.get("errors", []) + [f"Agent 0 failed: {exc}"],
        }

    return {
        "competitive_briefing": briefing,
        "current_phase": "fase_0_done",
    }
