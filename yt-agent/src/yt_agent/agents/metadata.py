"""Agent Meta — Video Metadata generation (titles, thumbnail, SEO, tags)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from yt_agent.agents.base import get_sonnet, invoke_agent_with_tools, load_prompt
from yt_agent.state import VideoMetadata, WorkflowState
from yt_agent.tools import get_metadata_tools

if TYPE_CHECKING:
    from yt_agent.memory.repository import ChannelMemory
    from yt_agent.tools.vidiq import VidIQClient


async def get_alternation_constraints(memory: ChannelMemory) -> dict:
    """Query the last video's thumbnail choices to enforce alternation.

    Returns a dict with last_aesthetic, last_composition, last_palette,
    last_expression, and last_sub_niche — or empty strings when no history.
    """
    last = await memory.get_last_video()
    if last is None:
        return {
            "last_aesthetic": "",
            "last_composition": "",
            "last_palette": "",
            "last_expression": "",
            "last_sub_niche": "",
        }
    return {
        "last_aesthetic": last.thumbnail_aesthetic or "",
        "last_composition": last.thumbnail_composition or "",
        "last_palette": last.thumbnail_palette or "",
        "last_expression": last.thumbnail_expression or "",
        "last_sub_niche": last.sub_niche or "",
    }


def _build_alternation_context(constraints: dict) -> str:
    """Format alternation constraints as a human-readable prompt section."""
    parts: list[str] = []
    labels = {
        "last_aesthetic": "Estética",
        "last_composition": "Composição",
        "last_palette": "Paleta dominante",
        "last_expression": "Expressão do apresentador",
        "last_sub_niche": "Sub-nicho",
    }
    for key, label in labels.items():
        val = constraints.get(key, "")
        if val:
            parts.append(f"- Último vídeo usou {label}: **{val}** → use algo DIFERENTE")

    if not parts:
        return "(Sem histórico de thumbnails — livre para escolher.)"

    return (
        "## RESTRIÇÕES DE ALTERNÂNCIA (baseado no último vídeo publicado)\n\n"
        + "\n".join(parts)
    )


async def run_metadata_agent(
    state: WorkflowState,
    *,
    vidiq: VidIQClient,
    memory: ChannelMemory,
) -> dict:
    """Execute the metadata generation agent.

    Returns a dict to merge into WorkflowState with keys:
    - video_metadata: VideoMetadata
    - current_phase: "metadata_done"
    """
    system_prompt = load_prompt("metadata.md")
    tools = get_metadata_tools(vidiq)

    constraints = await get_alternation_constraints(memory)
    alternation_block = _build_alternation_context(constraints)

    topic = state.get("video_topic", "unknown topic")
    sub_niche = state.get("sub_niche", "")
    emotion = state.get("dominant_emotion", "")
    fmt = state.get("format", "long")

    briefing = state.get("competitive_briefing")
    briefing_summary = ""
    if briefing is not None:
        angles = json.dumps(
            [a.angle for a in briefing.unexplored_angles], ensure_ascii=False
        )
        errors = json.dumps(
            [e.error for e in briefing.top_errors], ensure_ascii=False
        )
        tags = json.dumps(briefing.competitor_tags, ensure_ascii=False)
        briefing_summary = (
            f"Manifesto de diferenciação: {briefing.differentiation_manifesto}\n"
            f"Ângulos inexplorados: {angles}\n"
            f"Erros dos concorrentes: {errors}\n"
            f"Tags dos concorrentes: {tags}"
        )

    validation = state.get("theme_validation")
    validation_summary = ""
    if validation is not None:
        vol = validation.volume
        comp = validation.competition
        ovr = validation.overall
        validation_summary = (
            f"Keyword validada: {validation.keyword} "
            f"(vol={vol}, comp={comp}, overall={ovr})\n"
            f"Golden Checklist:\n"
            f"- Ângulo universal: {validation.golden_checklist.universal_angle}\n"
            f"- Premissa curta: {validation.golden_checklist.short_premise}\n"
            f"- Gatilho de persona: {validation.golden_checklist.persona_trigger}"
        )

    user_message = (
        f"Generate the complete metadata package for a new video.\n\n"
        f"## VIDEO CONTEXT\n"
        f"- Topic: {topic}\n"
        f"- Sub-niche: {sub_niche}\n"
        f"- Dominant emotion: {emotion}\n"
        f"- Format: {fmt}\n\n"
        f"{alternation_block}\n\n"
    )

    if briefing_summary:
        user_message += f"## BRIEFING COMPETITIVO\n{briefing_summary}\n\n"

    if validation_summary:
        user_message += f"## VALIDAÇÃO DE TEMA\n{validation_summary}\n\n"

    user_message += (
        f"Use vidiq_keyword_research to validate the top title keywords and "
        f"build the tags table with real volume data.\n\n"
        f"Return the result as a JSON object matching the VideoMetadata schema:\n"
        f"{VideoMetadata.model_json_schema()}"
    )

    try:
        metadata = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=tools,
            llm=get_sonnet(),
            output_schema=VideoMetadata,
        )
    except Exception as exc:
        return {
            "video_metadata": None,
            "current_phase": "metadata_done",
            "errors": state.get("errors", []) + [f"Agent Meta failed: {exc}"],
        }

    return {
        "video_metadata": metadata,
        "current_phase": "metadata_done",
    }
