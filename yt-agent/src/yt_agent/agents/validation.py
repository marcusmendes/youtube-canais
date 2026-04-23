"""Agent V — Theme Validation via keyword research."""

from __future__ import annotations

from typing import TYPE_CHECKING

from yt_agent.agents.base import get_sonnet, invoke_agent_with_tools, load_prompt
from yt_agent.state import ThemeValidation, WorkflowState
from yt_agent.tools import get_validation_tools

if TYPE_CHECKING:
    from yt_agent.tools.vidiq import VidIQClient


async def run_validation_agent(
    state: WorkflowState,
    *,
    vidiq: VidIQClient,
) -> dict:
    """Execute the theme validation agent.

    Returns a dict to merge into WorkflowState with keys:
    - theme_validation: ThemeValidation
    - current_phase: "validation_done"
    """
    system_prompt = load_prompt("validation.md")
    tools = get_validation_tools(vidiq)

    topic = state.get("video_topic", "unknown topic")
    sub_niche = state.get("sub_niche", "")
    emotion = state.get("dominant_emotion", "")

    user_message = (
        f"Validate the following video topic for the channel:\n\n"
        f"- Topic: {topic}\n"
        f"- Sub-niche: {sub_niche}\n"
        f"- Dominant emotion: {emotion}\n\n"
        f"Use vidiq_keyword_research to check the main keyword. If volume is 0, "
        f"check related keywords for viable alternatives.\n\n"
        f"Also complete the Golden Checklist:\n"
        f"1. Universal Angle: How does someone without technical background care?\n"
        f"2. Short Premise: ≤10 word summary\n"
        f"3. Persona Trigger: What fear or desire of the 'Explorer of the Frontier' "
        f"does this video activate?\n\n"
        f"Return the result as a JSON object matching the ThemeValidation schema:\n"
        f"{ThemeValidation.model_json_schema()}"
    )

    try:
        validation = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=tools,
            llm=get_sonnet(),
            output_schema=ThemeValidation,
        )
    except Exception as exc:
        return {
            "theme_validation": None,
            "current_phase": "validation_done",
            "errors": state.get("errors", []) + [f"Agent V failed: {exc}"],
        }

    return {
        "theme_validation": validation,
        "current_phase": "validation_done",
    }


def decide_after_validation(state: WorkflowState) -> str:
    """Routing decision after Agent V.

    Returns:
        "ok" — continue to metadata generation
        "low_demand" — pause for human decision
    """
    validation = state.get("theme_validation")
    if validation is None:
        return "ok"
    if validation.verdict in ("low_demand", "rejected"):
        return "low_demand"
    return "ok"
