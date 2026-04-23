"""Agent Roteirista — Script generation using Claude Opus."""

from __future__ import annotations

import json
import logging
import random
from typing import TYPE_CHECKING

from yt_agent.agents.base import get_opus, invoke_agent_with_tools, load_prompt

if TYPE_CHECKING:
    from pathlib import Path
from yt_agent.config import get_settings
from yt_agent.state import Script, WorkflowState

logger = logging.getLogger(__name__)


def load_writing_model(models_dir: Path) -> str:
    """Read a random .md file from the writing models directory.

    Returns the file content as a reference for the scriptwriter's voice/style,
    or a fallback message if no models are available.
    """
    if not models_dir.exists():
        logger.warning("Models directory not found: %s", models_dir)
        return "(Nenhum modelo de escrita disponível.)"

    md_files = list(models_dir.glob("*.md"))
    if not md_files:
        logger.warning("No .md files found in %s", models_dir)
        return "(Nenhum modelo de escrita disponível.)"

    chosen = random.choice(md_files)  # noqa: S311
    logger.info("Writing model selected: %s", chosen.name)
    return chosen.read_text(encoding="utf-8")


def _summarize_briefing(state: WorkflowState) -> str:
    """Extract a compact summary of the competitive briefing for context."""
    briefing = state.get("competitive_briefing")
    if briefing is None:
        return "(Sem briefing competitivo disponível.)"

    angles = [a.angle for a in briefing.unexplored_angles[:3]]
    errors = [e.error for e in briefing.top_errors[:3]]

    return (
        f"**Manifesto de diferenciação:** {briefing.differentiation_manifesto}\n"
        f"**Top ângulos inexplorados:** {json.dumps(angles, ensure_ascii=False)}\n"
        f"**Top erros dos concorrentes:** {json.dumps(errors, ensure_ascii=False)}"
    )


def _extract_calibrations(state: WorkflowState) -> str:
    """Extract performance calibrations from Agent P's diagnosis."""
    diagnosis = state.get("performance_diagnosis")
    if diagnosis is None:
        return "(Sem calibrações de performance disponíveis.)"

    return "\n".join(f"- {c}" for c in diagnosis.calibrations)


async def run_scriptwriter_agent(state: WorkflowState) -> dict:
    """Execute the scriptwriter agent using Claude Opus.

    Returns a dict to merge into WorkflowState with keys:
    - script: Script
    - current_phase: "script_done"
    """
    system_prompt = load_prompt("scriptwriter.md")
    settings = get_settings()
    writing_model = load_writing_model(settings.models_dir)

    topic = state.get("video_topic", "unknown topic")
    sub_niche = state.get("sub_niche", "")
    emotion = state.get("dominant_emotion", "")
    fmt = state.get("format", "long")
    angle = state.get("editorial_angle", "")
    detail = state.get("technical_detail", "intermediate")
    context_notes = state.get("context_notes", "")

    metadata = state.get("video_metadata")
    chosen_title = "(título não definido)"
    if metadata is not None and metadata.titles.top_3:
        chosen_title = metadata.titles.top_3[0].title

    calibrations = _extract_calibrations(state)
    briefing_summary = _summarize_briefing(state)

    user_message = (
        f"Write the complete script for the following video.\n\n"
        f"## CAMPOS VARIÁVEIS\n"
        f"- Título escolhido: **{chosen_title}**\n"
        f"- Tema: {topic}\n"
        f"- Sub-nicho: {sub_niche}\n"
        f"- Emoção dominante: {emotion}\n"
        f"- Ângulo editorial: {angle}\n"
        f"- Nível técnico: {detail}\n"
        f"- Formato: {fmt}\n"
    )

    if context_notes:
        user_message += f"- Notas de contexto: {context_notes}\n"

    user_message += (
        f"\n## CALIBRAÇÕES DO AGENTE P\n{calibrations}\n\n"
        f"## BRIEFING COMPETITIVO (resumo)\n{briefing_summary}\n\n"
        f"## MODELO DE ESCRITA DE REFERÊNCIA\n"
        f"Use o estilo, ritmo e tom do modelo abaixo como referência "
        f"(NÃO copie o conteúdo, apenas absorva a voz):\n\n"
        f"---\n{writing_model[:3000]}\n---\n\n"
        f"Return the result as a JSON object matching the Script schema:\n"
        f"{Script.model_json_schema()}"
    )

    try:
        script = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=[],
            llm=get_opus(),
            output_schema=Script,
        )
    except Exception as exc:
        return {
            "script": None,
            "current_phase": "script_done",
            "errors": state.get("errors", []) + [f"Agent Roteirista failed: {exc}"],
        }

    return {
        "script": script,
        "current_phase": "script_done",
    }


async def run_scriptwriter_fix(state: WorkflowState) -> dict:
    """Rewrite sections of the script based on QA fix instructions.

    Receives fix_instructions from the QA report and asks the LLM
    to correct only the problematic sections, preserving the rest.

    Returns a dict to merge into WorkflowState with keys:
    - script: Script (corrected)
    - qa_attempt: incremented
    - current_phase: "script_fix_done"
    """
    system_prompt = load_prompt("scriptwriter.md")

    qa_report = state.get("qa_report")
    current_script = state.get("script")

    if qa_report is None or current_script is None:
        return {
            "current_phase": "script_fix_done",
            "errors": state.get("errors", []) + [
                "Script fix called without QA report or existing script"
            ],
        }

    fix_list = "\n".join(f"- {instr}" for instr in qa_report.fix_instructions)
    current_json = current_script.model_dump_json(indent=2)

    user_message = (
        f"The QA agent found problems in the script. Fix ONLY the sections listed below.\n"
        f"Preserve everything else exactly as-is.\n\n"
        f"## FIX INSTRUCTIONS\n{fix_list}\n\n"
        f"## CURRENT SCRIPT (JSON)\n```json\n{current_json}\n```\n\n"
        f"Return the corrected script as a JSON object matching the Script schema:\n"
        f"{Script.model_json_schema()}"
    )

    qa_attempt = state.get("qa_attempt", 1) + 1

    try:
        fixed_script = await invoke_agent_with_tools(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=[],
            llm=get_opus(),
            output_schema=Script,
        )
    except Exception as exc:
        return {
            "qa_attempt": qa_attempt,
            "current_phase": "script_fix_done",
            "errors": state.get("errors", []) + [f"Script fix failed: {exc}"],
        }

    return {
        "script": fixed_script,
        "qa_attempt": qa_attempt,
        "current_phase": "script_fix_done",
    }
