"""YT-Agent CLI — entry point for the agentic video production workflow."""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from yt_agent.state import RepackagingProposal

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from yt_agent import __version__

app = typer.Typer(
    name="yt-agent",
    help="Agentic workflow para produção de vídeos YouTube — powered by LangGraph + Claude",
    no_args_is_help=True,
)
console = Console()
logger = logging.getLogger(__name__)

CHECKPOINT_DB = "data/checkpoints.sqlite"


def _run(coro):
    """Run an async function from the sync Typer context."""
    return asyncio.run(coro)


async def _init_checkpointer_and_memory():
    """Initialize database, memory and checkpointer (no MCP sessions)."""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    from yt_agent.memory import ChannelMemory, async_session_factory, init_db

    await init_db()

    session_factory = async_session_factory()
    session = session_factory()
    memory = ChannelMemory(session)

    from pathlib import Path

    Path(CHECKPOINT_DB).parent.mkdir(parents=True, exist_ok=True)
    checkpointer = AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB)
    await checkpointer.setup()

    return {
        "memory": memory,
        "session": session,
        "checkpointer": checkpointer,
    }


def _build_youtube_env() -> dict[str, str]:
    """Build env vars dict for the YouTube MCP stdio server."""
    import os

    from yt_agent.config import get_settings

    settings = get_settings()
    env: dict[str, str] = {**os.environ}
    api_key = settings.youtube_api_key.get_secret_value()
    if api_key:
        env["YOUTUBE_API_KEY"] = api_key
    if settings.google_client_secret_path:
        env["GOOGLE_CLIENT_SECRET_PATH"] = settings.google_client_secret_path
    return env


async def _save_workflow_run(
    *,
    run_id: str,
    topic: str,
    sub_niche: str,
    format_: str,
    angle: str,
    emotion: str,
    detail: str,
    period: str,
) -> None:
    from yt_agent.memory import ChannelMemory, async_session_factory
    from yt_agent.memory.models import WorkflowRun

    async with async_session_factory()() as session:
        repo = ChannelMemory(session)
        run = WorkflowRun(
            id=run_id,
            status="running",
            topic=topic,
            sub_niche=sub_niche,
            format=format_,
            editorial_angle=angle,
            dominant_emotion=emotion,
            technical_detail=detail,
            reference_period=period,
        )
        await repo.save_workflow_run(run)


async def _update_run_status(run_id: str, status: str, node: str | None = None) -> None:
    from yt_agent.memory import ChannelMemory, async_session_factory

    async with async_session_factory()() as session:
        repo = ChannelMemory(session)
        kwargs: dict = {"status": status}
        if node is not None:
            kwargs["current_node"] = node
        await repo.update_workflow_run(run_id, **kwargs)


async def _run_workflow(
    *,
    run_id: str,
    initial_state: dict,
    resume_state: dict | None = None,
) -> None:
    """Execute (or resume) the full workflow graph."""
    from langgraph.types import Command

    from yt_agent.config import get_settings
    from yt_agent.graph import build_graph
    from yt_agent.output.renderer import print_summary
    from yt_agent.tools.mcp_client import vidiq_session, youtube_session
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient

    resources = await _init_checkpointer_and_memory()
    settings = get_settings()

    async with (
        vidiq_session(
            settings.vidiq_mcp_url,
            settings.vidiq_api_key.get_secret_value(),
        ) as vidiq_sess,
        youtube_session(
            settings.youtube_mcp_command,
            env=_build_youtube_env(),
        ) as yt_sess,
    ):
        vidiq = VidIQClient(vidiq_sess, channel_handle=settings.channel_handle)
        youtube = YouTubeClient(yt_sess)

        graph = build_graph(
            vidiq=vidiq,
            youtube=youtube,
            memory=resources["memory"],
            checkpointer=resources["checkpointer"],
        )

        config = {"configurable": {"thread_id": run_id}}

        try:
            if resume_state is not None:
                human_input = resume_state.get("human_input", "1")
                console.print(f"[dim]Resuming with input: {human_input}[/dim]")
                async for event in graph.astream(
                    Command(resume=human_input), config
                ):
                    _log_event(event)
            else:
                async for event in graph.astream(initial_state, config):
                    _log_event(event)

        except Exception as exc:
            if "interrupt" in str(type(exc).__name__).lower():
                raise
            logger.exception("Workflow error")
            await _update_run_status(run_id, "failed")
            console.print(f"[red]Workflow failed: {exc}[/red]")
            return

        snapshot = await graph.aget_state(config)

        if snapshot.next:
            await _update_run_status(run_id, "paused", node=snapshot.next[0])
            console.print(
                Panel(
                    f"[yellow]Workflow pausado — aguardando decisão humana.[/yellow]\n\n"
                    f"Próximo nó: {snapshot.next[0]}\n"
                    f"Retome com: [bold]yt-agent resume --run-id {run_id}[/bold]",
                    title="⏸️  Pausa — Human-in-the-Loop",
                    border_style="yellow",
                )
            )
            return

        final_state = snapshot.values
        await _update_run_status(run_id, "completed")

        from yt_agent.output.renderer import render_to_markdown

        output_path = render_to_markdown(final_state, run_id=run_id)
        print_summary(final_state, output_path)

    await resources["session"].close()
    await resources["checkpointer"].conn.close()


def _log_event(event: dict) -> None:
    """Log graph stream events to the console."""
    for node_name, node_output in event.items():
        phase = ""
        if isinstance(node_output, dict):
            phase = node_output.get("current_phase", "")
        logger.info("Node '%s' completed → phase: %s", node_name, phase)
        console.print(f"  [dim]✓ {node_name}[/dim]", highlight=False)


@app.command()
def new(
    topic: Annotated[str, typer.Option("--topic", "-t", help="Tema do vídeo")],
    sub_niche: Annotated[
        str,
        typer.Option("--sub-niche", "-s", help="Sub-nicho (ex: 'IA + Medicina/Saúde')"),
    ],
    format_: Annotated[
        str,
        typer.Option("--format", "-f", help="Formato: long ou short"),
    ] = "long",
    angle: Annotated[
        str,
        typer.Option("--angle", "-a", help="Ângulo editorial"),
    ] = "revelador",
    emotion: Annotated[
        str,
        typer.Option("--emotion", "-e", help="Emoção dominante"),
    ] = "Admiração",
    detail: Annotated[
        str,
        typer.Option("--detail", "-d", help="Nível técnico: basic, intermediate, advanced"),
    ] = "intermediate",
    period: Annotated[
        str,
        typer.Option("--period", "-p", help="Período de referência (ex: '2025-2026')"),
    ] = "2025-2026",
    context_notes: Annotated[
        str | None,
        typer.Option("--notes", "-n", help="Notas de contexto adicionais"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Ativar logging detalhado"),
    ] = False,
) -> None:
    """Create and execute a new video production workflow."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s — %(message)s")

    run_id = str(uuid.uuid4())

    console.print(
        Panel(
            f"[bold green]Iniciando workflow...[/bold green]\n\n"
            f"[bold]Run ID:[/bold] {run_id}\n"
            f"[bold]Tema:[/bold] {topic}\n"
            f"[bold]Sub-nicho:[/bold] {sub_niche}\n"
            f"[bold]Formato:[/bold] {format_}\n"
            f"[bold]Ângulo:[/bold] {angle}\n"
            f"[bold]Emoção:[/bold] {emotion}",
            title="🎬 YT-Agent — New Run",
            border_style="green",
        )
    )

    initial_state = {
        "video_topic": topic,
        "sub_niche": sub_niche,
        "format": format_,
        "editorial_angle": angle,
        "dominant_emotion": emotion,
        "technical_detail": detail,
        "reference_period": period,
        "context_notes": context_notes or "",
        "human_decisions": [],
        "qa_attempt": 1,
        "current_phase": "start",
        "errors": [],
    }

    async def _execute():
        from yt_agent.memory import init_db

        await init_db()
        await _save_workflow_run(
            run_id=run_id,
            topic=topic,
            sub_niche=sub_niche,
            format_=format_,
            angle=angle,
            emotion=emotion,
            detail=detail,
            period=period,
        )
        await _run_workflow(run_id=run_id, initial_state=initial_state)

    _run(_execute())


@app.command()
def resume(
    run_id: Annotated[str, typer.Option("--run-id", "-r", help="ID do run a retomar")],
    input_: Annotated[
        str,
        typer.Option("--input", "-i", help="Resposta para o human-in-the-loop (ex: '1')"),
    ] = "1",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Ativar logging detalhado"),
    ] = False,
) -> None:
    """Resume a paused workflow run from the last checkpoint."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s — %(message)s")

    console.print(
        Panel(
            f"[yellow]Retomando workflow...[/yellow]\n\n"
            f"Run ID: {run_id}\n"
            f"Input: {input_}",
            title="▶️  Resume",
            border_style="yellow",
        )
    )

    async def _execute():
        from yt_agent.memory import init_db

        await init_db()
        await _run_workflow(
            run_id=run_id,
            initial_state={},
            resume_state={"human_input": input_},
        )

    _run(_execute())


@app.command()
def repackage(
    check: Annotated[
        bool, typer.Option("--check", help="Listar candidatos a repackaging")
    ] = False,
    video_id: Annotated[
        str | None, typer.Option("--video-id", help="ID do vídeo para repackaging")
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Ativar logging detalhado")
    ] = False,
) -> None:
    """Identify underperforming videos and suggest repackaging."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s — %(message)s")

    if check:
        _run(_repackage_check())
    elif video_id:
        _run(_repackage_execute(video_id))
    else:
        console.print("[red]Forneça --check ou --video-id[/red]")
        raise typer.Exit(code=1)


async def _repackage_check() -> None:
    from yt_agent.agents.repackaging import find_repackaging_candidates
    from yt_agent.memory import ChannelMemory, async_session_factory, init_db

    await init_db()
    async with async_session_factory()() as session:
        memory = ChannelMemory(session)
        candidates = await find_repackaging_candidates(memory=memory)

    if not candidates:
        console.print("[dim]Nenhum candidato a repackaging encontrado.[/dim]")
        return

    table = Table(title="📦 Candidatos a Repackaging")
    table.add_column("Video ID", style="cyan", no_wrap=True)
    table.add_column("Título", style="white")
    table.add_column("Views 7d", style="bold", justify="right")
    table.add_column("Retenção", justify="right")
    table.add_column("Motivo", style="dim")
    for c in candidates:
        table.add_row(
            c["video_id"],
            c["title"],
            f"{c['views_7d']:,}",
            f"{c['avg_retention_pct']:.1f}%",
            c["reason"],
        )
    console.print(table)


async def _repackage_execute(video_id: str) -> None:
    from yt_agent.agents.repackaging import run_repackaging_agent
    from yt_agent.config import get_settings
    from yt_agent.memory import init_db
    from yt_agent.tools.mcp_client import vidiq_session, youtube_session
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient

    await init_db()
    settings = get_settings()

    async with (
        vidiq_session(
            settings.vidiq_mcp_url,
            settings.vidiq_api_key.get_secret_value(),
        ) as vidiq_sess,
        youtube_session(
            settings.youtube_mcp_command,
            env=_build_youtube_env(),
        ) as yt_sess,
    ):
        vidiq = VidIQClient(vidiq_sess, channel_handle=settings.channel_handle)
        youtube = YouTubeClient(yt_sess)

        console.print(f"[dim]Gerando proposta de repackaging para {video_id}...[/dim]")
        try:
            proposal = await run_repackaging_agent(
                video_id, vidiq=vidiq, youtube=youtube
            )
        except Exception as exc:
            console.print(f"[red]Repackaging failed: {exc}[/red]")
            return

        for sug in proposal.suggestions:
            console.print(
                Panel(
                    f"[bold]Novo título:[/bold] {sug.new_title}\n"
                    f"[bold]Thumbnail:[/bold] {sug.new_thumbnail_prompt[:100]}...\n"
                    f"[bold]Tags:[/bold] {', '.join(sug.new_tags)}\n\n"
                    f"[bold]Rationale:[/bold] {sug.rationale}",
                    title=f"📦 Proposta — {sug.video_id}",
                    border_style="green",
                )
            )

        output_path = _save_repackaging_output(video_id, proposal)
        console.print(f"\n[dim]Salvo em:[/dim] [bold]{output_path}[/bold]")


def _save_repackaging_output(
    video_id: str,
    proposal: RepackagingProposal,
) -> Path:
    """Persist the repackaging proposal as a Markdown file under output/."""
    from datetime import datetime

    output_dir = Path("output") / "repackaging"
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = output_dir / f"{video_id}_{ts}.md"

    parts: list[str] = []
    parts.append(f"# Repackaging Proposal — {video_id}\n")
    parts.append(f"**Data:** {datetime.now().isoformat()}\n")
    parts.append("---\n")

    for i, sug in enumerate(proposal.suggestions, 1):
        parts.append(f"\n## Sugestão {i} — `{sug.video_id}`\n")
        parts.append(f"### Novo Título\n{sug.new_title}\n")
        parts.append(f"\n### Thumbnail Prompt\n{sug.new_thumbnail_prompt}\n")
        parts.append(f"\n### Nova Descrição\n{sug.new_description}\n")
        parts.append(f"\n### Tags\n{', '.join(sug.new_tags)}\n")
        parts.append(f"\n### Rationale\n{sug.rationale}\n")

    if proposal.candidates:
        parts.append("\n---\n## Candidatos Analisados\n")
        parts.append("| Video ID | Título | Views | Retenção | Motivo |\n")
        parts.append("|---|---|---|---|---|\n")
        for c in proposal.candidates:
            parts.append(
                f"| {c.video_id} | {c.title} | {c.views:,} "
                f"| {c.avg_retention_pct:.1f}% | {c.reason} |\n"
            )

    content = "".join(parts)
    dest.write_text(content, encoding="utf-8")
    return dest


@app.command()
def history(
    videos: Annotated[
        bool, typer.Option("--videos", help="Mostrar histórico de vídeos (memória do canal)")
    ] = False,
) -> None:
    """Show recent workflow runs or video history."""
    if videos:
        _run(_show_video_history())
    else:
        _run(_show_workflow_history())


async def _show_workflow_history() -> None:
    from sqlalchemy import desc, select

    from yt_agent.memory import async_session_factory, init_db
    from yt_agent.memory.models import WorkflowRun

    await init_db()
    async with async_session_factory()() as session:
        result = await session.execute(
            select(WorkflowRun).order_by(desc(WorkflowRun.started_at)).limit(20)
        )
        runs = list(result.scalars().all())

    if not runs:
        console.print("[dim]Nenhum workflow encontrado.[/dim]")
        return

    table = Table(title="📋 Workflow History")
    table.add_column("Run ID", style="cyan", no_wrap=True, max_width=36)
    table.add_column("Topic", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Started", style="dim")
    for run in runs:
        status_color = {
            "created": "blue",
            "running": "yellow",
            "paused": "yellow",
            "completed": "green",
            "failed": "red",
        }.get(run.status, "white")
        table.add_row(
            run.id[:12] + "…",
            run.topic or "—",
            f"[{status_color}]{run.status}[/{status_color}]",
            str(run.started_at.strftime("%Y-%m-%d %H:%M")) if run.started_at else "—",
        )
    console.print(table)


async def _show_video_history() -> None:
    from yt_agent.memory import ChannelMemory, async_session_factory, init_db

    await init_db()
    async with async_session_factory()() as session:
        memory = ChannelMemory(session)
        videos = await memory.get_all_videos()

    if not videos:
        console.print("[dim]Nenhum vídeo na memória do canal.[/dim]")
        return

    table = Table(title="🎬 Channel Memory — Vídeos")
    table.add_column("ID", style="cyan", no_wrap=True, max_width=30)
    table.add_column("Título", style="white", max_width=40)
    table.add_column("Sub-nicho", style="dim")
    table.add_column("Data", style="dim")
    table.add_column("Estética", style="magenta")
    table.add_column("Comp.", style="magenta")
    table.add_column("Views 7d", justify="right")
    table.add_column("Retenção", justify="right")
    for v in videos:
        views = f"{v.views_7d:,}" if v.views_7d is not None else "—"
        retention = f"{v.avg_retention_pct:.1f}%" if v.avg_retention_pct is not None else "—"
        table.add_row(
            v.id[:28] + ("…" if len(v.id) > 28 else ""),
            v.title[:38] + ("…" if len(v.title) > 38 else ""),
            v.sub_niche or "—",
            str(v.published_at),
            v.thumbnail_aesthetic or "—",
            v.thumbnail_composition or "—",
            views,
            retention,
        )
    console.print(table)


@app.command(name="update-metrics")
def update_metrics(
    video_id: Annotated[str, typer.Option("--video-id", help="YouTube video ID")],
    views: Annotated[
        int | None, typer.Option("--views", help="Views nos primeiros 7 dias")
    ] = None,
    retention: Annotated[
        float | None, typer.Option("--retention", help="Retenção média (%)")
    ] = None,
    like_ratio: Annotated[
        float | None, typer.Option("--like-ratio", help="Like ratio (%)")
    ] = None,
) -> None:
    """Update performance metrics for a published video."""

    async def _update():
        from yt_agent.memory import ChannelMemory, async_session_factory, init_db

        await init_db()
        async with async_session_factory()() as session:
            memory = ChannelMemory(session)
            video = await memory.get_video(video_id)

            if video is None:
                console.print(f"[red]Vídeo {video_id!r} não encontrado na memória.[/red]")
                raise typer.Exit(code=1)

            kwargs: dict = {}
            if views is not None:
                kwargs["views_7d"] = views
            if retention is not None:
                kwargs["avg_retention_pct"] = retention
            if like_ratio is not None:
                kwargs["like_ratio_pct"] = like_ratio

            if not kwargs:
                console.print("[yellow]Nenhuma métrica fornecida para atualizar.[/yellow]")
                return

            await memory.update_video(video_id, **kwargs)

            lines = ["[bold green]Métricas atualizadas![/bold green]\n"]
            lines.append(f"[bold]Vídeo:[/bold] {video.title}")
            if views is not None:
                lines.append(f"[bold]Views 7d:[/bold] {views:,}")
            if retention is not None:
                lines.append(f"[bold]Retenção:[/bold] {retention:.1f}%")
            if like_ratio is not None:
                lines.append(f"[bold]Like ratio:[/bold] {like_ratio:.1f}%")
            console.print(
                Panel(
                    "\n".join(lines),
                    title="📊 Update Metrics",
                    border_style="green",
                )
            )

    _run(_update())


@app.command()
def version() -> None:
    """Show the current version."""
    console.print(f"yt-agent v{__version__}")


if __name__ == "__main__":
    app()
