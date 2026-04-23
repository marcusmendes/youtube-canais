"""LangGraph workflow — orchestrates all agents into a state graph."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from yt_agent.agents.competitive import run_competitive_agent
from yt_agent.agents.metadata import run_metadata_agent
from yt_agent.agents.performance import (
    decide_after_performance,
    run_performance_agent,
)
from yt_agent.agents.qa import decide_after_qa, run_qa_agent
from yt_agent.agents.scriptwriter import run_scriptwriter_agent, run_scriptwriter_fix
from yt_agent.agents.validation import decide_after_validation, run_validation_agent
from yt_agent.state import HumanDecision, WorkflowState

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.state import CompiledStateGraph

    from yt_agent.memory.repository import ChannelMemory
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient

logger = logging.getLogger(__name__)


def build_graph(
    *,
    vidiq: VidIQClient,
    youtube: YouTubeClient,
    memory: ChannelMemory,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Build and compile the full video production workflow graph.

    The graph follows this flow:
    START → fase_p → decide_fase_p
      ├─ ok → fase_0
      └─ low_retention → human_pause_retention → fase_0
    fase_0 → validacao_tema → decide_tema
      ├─ ok → metadados
      └─ low_demand → human_pause_tema → metadados
    metadados → roteirista → qa → decide_qa
      ├─ pass/pass_forced → render_output → END
      └─ fail → roteirista_fix → qa (loop)
    """
    graph = StateGraph(WorkflowState)

    # ── Node wrappers (close over shared resources) ──────────────

    async def fase_p(state: WorkflowState) -> dict:
        logger.info("▶ Running Agent P — Performance Diagnosis")
        return await run_performance_agent(state, vidiq=vidiq, youtube=youtube)

    async def fase_0(state: WorkflowState) -> dict:
        logger.info("▶ Running Agent 0 — Competitive Analysis")
        return await run_competitive_agent(state, vidiq=vidiq, youtube=youtube)

    async def validacao_tema(state: WorkflowState) -> dict:
        logger.info("▶ Running Agent V — Theme Validation")
        return await run_validation_agent(state, vidiq=vidiq)

    async def metadados(state: WorkflowState) -> dict:
        logger.info("▶ Running Agent Meta — Metadata Generation")
        return await run_metadata_agent(state, vidiq=vidiq, memory=memory)

    async def roteirista(state: WorkflowState) -> dict:
        logger.info("▶ Running Agent Roteirista — Script Writing")
        return await run_scriptwriter_agent(state)

    async def qa(state: WorkflowState) -> dict:
        logger.info("▶ Running Agent QA — Checklist Validation")
        return await run_qa_agent(state)

    async def roteirista_fix(state: WorkflowState) -> dict:
        attempt = state.get("qa_attempt", 1)
        logger.info("▶ Running Agent Roteirista — Script Fix (attempt %s)", attempt)
        return await run_scriptwriter_fix(state)

    async def save_to_memory(state: WorkflowState) -> dict:
        """Persist video data and tags to channel memory after a successful run."""
        import datetime as dt

        from yt_agent.memory.models import TagPerformance, Video

        logger.info("▶ Saving to channel memory")

        meta = state.get("video_metadata")
        if meta is None:
            return {"current_phase": "memory_saved"}

        title = "(sem título)"
        if meta.titles.top_3:
            title = meta.titles.top_3[0].title

        video = Video(
            id=f"draft-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            sub_niche=state.get("sub_niche", ""),
            published_at=dt.date.today(),
            format=state.get("format", "long"),
            thumbnail_aesthetic=meta.thumbnail.aesthetic,
            thumbnail_composition=meta.thumbnail.composition,
            thumbnail_palette=meta.thumbnail.dominant_color,
            thumbnail_expression=meta.thumbnail.emotion,
        )
        await memory.save_video(video)

        tag_records = [
            TagPerformance(
                tag=tv.tag,
                video_id=video.id,
                volume_at_use=tv.volume,
            )
            for tv in meta.tags.validation_table
        ]
        if tag_records:
            await memory.save_tags(tag_records)

        logger.info("Saved video '%s' + %d tags to memory", title, len(tag_records))
        return {"current_phase": "memory_saved"}

    async def render_output(state: WorkflowState) -> dict:
        from yt_agent.output.renderer import render_to_markdown

        logger.info("▶ Rendering final output")
        render_to_markdown(state)
        return {"current_phase": "completed"}

    # ── Human-in-the-loop nodes ──────────────────────────────────

    async def human_pause_retention(state: WorkflowState) -> dict:
        diagnosis = state.get("performance_diagnosis")
        retention = "N/A"
        if diagnosis is not None:
            retention = f"{diagnosis.last_video.avg_retention_pct:.1f}%"
            calibrations = "\n".join(f"  - {c}" for c in diagnosis.calibrations)
        else:
            calibrations = "  (sem dados)"

        question = (
            f"⚠️  Alerta de retenção baixa ({retention}).\n\n"
            f"Calibrações sugeridas:\n{calibrations}\n\n"
            f"Opções:\n"
            f"  [1] Continuar com reforço de hooks\n"
            f"  [2] Executar Repackaging no vídeo anterior\n"
            f"  [3] Mudar de tema"
        )

        chosen = interrupt(question)

        decision = HumanDecision(
            phase="fase_p",
            question=question,
            options=["continuar_hooks", "repackaging", "mudar_tema"],
            chosen=str(chosen),
            timestamp=datetime.now(),
        )

        decisions = list(state.get("human_decisions", []))
        decisions.append(decision)
        return {"human_decisions": decisions, "current_phase": "human_retention_done"}

    async def human_pause_tema(state: WorkflowState) -> dict:
        validation = state.get("theme_validation")

        keyword_info = ""
        alternatives_info = ""
        if validation is not None:
            keyword_info = (
                f"Keyword: {validation.keyword}\n"
                f"  Volume: {validation.volume} | "
                f"Competition: {validation.competition} | "
                f"Overall: {validation.overall}\n"
                f"  Verdict: {validation.verdict}"
            )
            if validation.alternatives:
                alt_lines = []
                for alt in validation.alternatives:
                    alt_lines.append(
                        f"  - {alt.keyword} (vol={alt.volume}, "
                        f"comp={alt.competition}, overall={alt.overall})"
                    )
                alternatives_info = "\n".join(alt_lines)

        question = (
            f"⚠️  Tema com demanda baixa.\n\n"
            f"{keyword_info}\n\n"
            f"Alternativas sugeridas:\n{alternatives_info or '  (nenhuma)'}\n\n"
            f"Opções:\n"
            f"  [1] Continuar mesmo assim\n"
            f"  [2] Usar keyword alternativa\n"
            f"  [3] Informar novo tema"
        )

        chosen = interrupt(question)

        decision = HumanDecision(
            phase="validacao_tema",
            question=question,
            options=["continuar", "usar_alternativa", "novo_tema"],
            chosen=str(chosen),
            timestamp=datetime.now(),
        )

        decisions = list(state.get("human_decisions", []))
        decisions.append(decision)
        return {"human_decisions": decisions, "current_phase": "human_tema_done"}

    # ── Register nodes ───────────────────────────────────────────

    graph.add_node("fase_p", fase_p)
    graph.add_node("decide_fase_p", lambda state: {})
    graph.add_node("human_pause_retention", human_pause_retention)
    graph.add_node("fase_0", fase_0)
    graph.add_node("validacao_tema", validacao_tema)
    graph.add_node("decide_tema", lambda state: {})
    graph.add_node("human_pause_tema", human_pause_tema)
    graph.add_node("metadados", metadados)
    graph.add_node("roteirista", roteirista)
    graph.add_node("qa", qa)
    graph.add_node("decide_qa", lambda state: {})
    graph.add_node("roteirista_fix", roteirista_fix)
    graph.add_node("save_to_memory", save_to_memory)
    graph.add_node("render_output", render_output)

    # ── Define edges ─────────────────────────────────────────────

    graph.add_edge(START, "fase_p")
    graph.add_edge("fase_p", "decide_fase_p")

    graph.add_conditional_edges(
        "decide_fase_p",
        decide_after_performance,
        {"ok": "fase_0", "low_retention": "human_pause_retention"},
    )

    graph.add_edge("human_pause_retention", "fase_0")

    graph.add_edge("fase_0", "validacao_tema")
    graph.add_edge("validacao_tema", "decide_tema")

    graph.add_conditional_edges(
        "decide_tema",
        decide_after_validation,
        {"ok": "metadados", "low_demand": "human_pause_tema"},
    )

    graph.add_edge("human_pause_tema", "metadados")

    graph.add_edge("metadados", "roteirista")
    graph.add_edge("roteirista", "qa")
    graph.add_edge("qa", "decide_qa")

    graph.add_conditional_edges(
        "decide_qa",
        decide_after_qa,
        {"pass": "save_to_memory", "fail": "roteirista_fix", "pass_forced": "save_to_memory"},
    )

    graph.add_edge("roteirista_fix", "qa")
    graph.add_edge("save_to_memory", "render_output")
    graph.add_edge("render_output", END)

    # ── Compile ──────────────────────────────────────────────────

    compile_kwargs: dict = {}
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer

    return graph.compile(**compile_kwargs)
