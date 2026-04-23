"""Render the final workflow output as a Markdown document."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yt_agent.state import WorkflowState

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")


def render_to_markdown(
    state: WorkflowState,
    *,
    run_id: str = "draft",
    output_dir: Path | None = None,
) -> Path:
    """Build a comprehensive Markdown document from the workflow state.

    Sections (in order):
    1. Diagnóstico de Performance (Fase P)
    2. Briefing Competitivo (Fase 0)
    3. Validação de Tema
    4. Metadados (títulos, thumbnail, tags, descrição, post)
    5. Roteiro completo
    6. Mapa de Open Loops
    7. QA Report

    Returns the path to the saved file.
    """
    dest = (output_dir or OUTPUT_DIR) / f"{run_id}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    parts.append(f"# Workflow Output — {run_id}\n")
    parts.append(f"**Tema:** {state.get('video_topic', '—')}\n")
    parts.append(f"**Sub-nicho:** {state.get('sub_niche', '—')}\n")
    parts.append(f"**Formato:** {state.get('format', '—')}\n")
    parts.append("---\n")

    # ── 1. Performance Diagnosis ─────────────────────────────────
    parts.append("## 1. Diagnóstico de Performance (Fase P)\n")
    diag = state.get("performance_diagnosis")
    if diag is None:
        parts.append("_Não executado ou sem dados._\n")
    else:
        lv = diag.last_video
        parts.append(
            f"**Último vídeo:** [{lv.title}](https://youtube.com/watch?v={lv.id})\n"
        )
        parts.append(f"- Views: {lv.views:,}\n")
        parts.append(f"- Retenção média: {lv.avg_retention_pct:.1f}%\n")
        parts.append(f"- Like ratio: {lv.like_ratio_pct:.1f}%\n")
        parts.append(f"- Comentários: {lv.comments}\n")
        parts.append(f"- Inscritos ganhos: {lv.subscribers_gained}\n\n")

        bl = diag.channel_baseline
        parts.append("**Baseline do canal:**\n")
        parts.append(
            f"- Views médias: {bl.avg_views:,} | "
            f"Retenção: {bl.avg_retention_pct:.1f}% | "
            f"Like ratio: {bl.avg_like_ratio_pct:.1f}%\n\n"
        )

        if diag.calibrations:
            parts.append("**Calibrações para o próximo vídeo:**\n")
            for c in diag.calibrations:
                parts.append(f"- {c}\n")
            parts.append("\n")

        if diag.alert != "none":
            parts.append(f"**⚠️ Alerta:** {diag.alert}\n\n")

    # ── 2. Competitive Briefing ──────────────────────────────────
    parts.append("## 2. Briefing Competitivo (Fase 0)\n")
    brief = state.get("competitive_briefing")
    if brief is None:
        parts.append("_Não executado ou sem dados._\n")
    else:
        parts.append(f"**Manifesto de diferenciação:** {brief.differentiation_manifesto}\n\n")

        if brief.unexplored_angles:
            parts.append("**Ângulos inexplorados:**\n")
            for a in brief.unexplored_angles:
                parts.append(f"- {a.angle} — {a.why_possible}\n")
            parts.append("\n")

        if brief.top_errors:
            parts.append("**Erros dos concorrentes:**\n")
            for e in brief.top_errors:
                parts.append(f"- {e.error} → {e.correction} (fonte: {e.source})\n")
            parts.append("\n")

        if brief.competitors_analyzed:
            parts.append("**Concorrentes analisados:**\n")
            parts.append("| Título | Canal | Views |\n")
            parts.append("|---|---|---|\n")
            for cv in brief.competitors_analyzed:
                parts.append(f"| {cv.title} | {cv.channel} | {cv.views:,} |\n")
            parts.append("\n")

    # ── 3. Theme Validation ──────────────────────────────────────
    parts.append("## 3. Validação de Tema\n")
    val = state.get("theme_validation")
    if val is None:
        parts.append("_Não executado ou sem dados._\n")
    else:
        parts.append(
            f"**Keyword:** {val.keyword} — "
            f"Volume: {val.volume} | "
            f"Competition: {val.competition} | "
            f"Overall: {val.overall}\n"
        )
        parts.append(f"**Veredito:** {val.verdict}\n\n")

        gc = val.golden_checklist
        parts.append("**Golden Checklist:**\n")
        parts.append(f"- Ângulo universal: {gc.universal_angle}\n")
        parts.append(f"- Premissa curta: {gc.short_premise}\n")
        parts.append(f"- Gatilho de persona: {gc.persona_trigger}\n\n")

        if val.alternatives:
            parts.append("**Keywords alternativas:**\n")
            for alt in val.alternatives:
                parts.append(
                    f"- {alt.keyword} (vol={alt.volume}, "
                    f"comp={alt.competition}, overall={alt.overall})\n"
                )
            parts.append("\n")

    # ── 4. Metadados ─────────────────────────────────────────────
    parts.append("## 4. Metadados do Vídeo\n")
    meta = state.get("video_metadata")
    if meta is None:
        parts.append("_Não gerado._\n")
    else:
        parts.append("### Títulos (Top 3)\n")
        for i, t in enumerate(meta.titles.top_3, 1):
            parts.append(f"{i}. **{t.title}** ({t.formula})\n")
            parts.append(f"   - {t.justification}\n")
        parts.append("\n")

        parts.append("### Todos os 10 títulos\n")
        for i, t in enumerate(meta.titles.all_10, 1):
            parts.append(f"{i}. {t.title} ({t.char_count} chars, {t.formula})\n")
        parts.append("\n")

        th = meta.thumbnail
        parts.append("### Thumbnail\n")
        parts.append(f"- Estética: {th.aesthetic}\n")
        parts.append(f"- Composição: {th.composition}\n")
        parts.append(f"- Emoção: {th.emotion}\n")
        parts.append(f"- Cor dominante: {th.dominant_color}\n")
        parts.append(f"- Cor de acento: {th.accent_color}\n")
        if th.text_overlay:
            parts.append(f"- Text overlay: {th.text_overlay}\n")
        parts.append(f"\n**Prompt (EN):**\n```\n{th.prompt_en}\n```\n\n")

        parts.append("### Tags\n")
        parts.append("| Tag | Volume | Competition | Overall |\n")
        parts.append("|---|---|---|---|\n")
        for tv in meta.tags.validation_table:
            parts.append(
                f"| {tv.tag} | {tv.volume:,} | {tv.competition} | {tv.overall} |\n"
            )
        parts.append("\n")

        parts.append(f"### Hashtags\n{', '.join(meta.hashtags)}\n\n")

        parts.append("### Descrição SEO\n")
        parts.append(f"```\n{meta.description_seo}\n```\n\n")

        parts.append("### Post Comunidade\n")
        parts.append(f"```\n{meta.community_post}\n```\n\n")

    # ── 5. Roteiro ───────────────────────────────────────────────
    parts.append("## 5. Roteiro\n")
    script = state.get("script")
    if script is None:
        parts.append("_Não gerado._\n")
    else:
        parts.append(
            f"**Contagem de palavras:** {script.word_count} | "
            f"**Duração estimada:** {script.estimated_duration_min:.1f} min\n\n"
        )

        for section in script.sections:
            label = section.label or section.type.upper()
            parts.append(f"### [{section.type.upper()}] {label}\n\n")
            parts.append(f"{section.narration}\n\n")
            parts.append(f"**VISUAL:** {section.visual}\n\n")
            if section.pattern_interrupt:
                parts.append(f"**Pattern Interrupt:** {section.pattern_interrupt}\n\n")
            if section.editorial_insertion:
                parts.append(f"**Inserção Editorial:** {section.editorial_insertion}\n\n")
            if section.cta:
                parts.append(f"**CTA:** {section.cta}\n\n")

        # ── 6. Open Loops ────────────────────────────────────────
        if script.open_loops_map:
            parts.append("## 6. Mapa de Open Loops\n")
            parts.append("| # | Abre em | Conteúdo | Fecha em | Payoff |\n")
            parts.append("|---|---|---|---|---|\n")
            for loop in script.open_loops_map:
                parts.append(
                    f"| {loop.loop_number} | {loop.opens_at} | "
                    f"{loop.content} | {loop.closes_at} | {loop.payoff_type} |\n"
                )
            parts.append("\n")

        # ── Retention Audit ──────────────────────────────────────
        ra = script.retention_audit
        parts.append("### Auditoria de Retenção (primeiros 30s)\n")
        checks = [
            ("Hook entrega promessa em ≤8s", ra.hook_delivers_promise_in_8s),
            ("Zero introdução institucional", ra.zero_institutional_intro),
            ("Primeiro VISUAL específico", ra.first_visual_specific),
            ("Dado numérico nos primeiros 15s", ra.numeric_data_in_15s),
            ("Contexto abre loop", ra.context_opens_loop),
        ]
        for label, ok in checks:
            icon = "✅" if ok else "❌"
            parts.append(f"- {icon} {label}\n")
        parts.append("\n")

    # ── 7. QA Report ─────────────────────────────────────────────
    parts.append("## 7. QA Report\n")
    report = state.get("qa_report")
    if report is None:
        parts.append("_Não executado._\n")
    else:
        parts.append(
            f"**Veredito:** {report.verdict} | "
            f"Passed: {report.passed}/28 | "
            f"Failed: {report.failed} | "
            f"Tentativa: {report.attempt}\n\n"
        )

        if report.items:
            failed_items = [it for it in report.items if it.status == "fail"]
            if failed_items:
                parts.append("**Itens reprovados:**\n")
                for it in failed_items:
                    parts.append(f"- **Item {it.number}** ({it.name}): {it.detail}\n")
                parts.append("\n")

            skipped = [it for it in report.items if it.status == "skip"]
            if skipped:
                parts.append(f"**Itens pulados:** {len(skipped)}\n\n")

        if report.fix_instructions:
            parts.append("**Instruções de correção:**\n")
            for instr in report.fix_instructions:
                parts.append(f"- {instr}\n")
            parts.append("\n")

    # ── Errors ───────────────────────────────────────────────────
    errors = state.get("errors", [])
    if errors:
        parts.append("## ⚠️ Erros durante execução\n")
        for err in errors:
            parts.append(f"- {err}\n")
        parts.append("\n")

    content = "".join(parts)
    dest.write_text(content, encoding="utf-8")
    logger.info("Output saved to %s", dest)
    return dest


def print_summary(state: WorkflowState, output_path: Path) -> None:
    """Print a concise executive summary to the terminal using Rich."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    meta = state.get("video_metadata")
    script = state.get("script")
    report = state.get("qa_report")

    title_text = "—"
    if meta is not None and meta.titles.top_3:
        title_text = meta.titles.top_3[0].title

    word_count = "—"
    duration = "—"
    if script is not None:
        word_count = str(script.word_count)
        duration = f"{script.estimated_duration_min:.1f} min"

    qa_score = "—"
    qa_verdict = "—"
    if report is not None:
        qa_score = f"{report.passed}/28"
        qa_verdict = report.verdict

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="bold")
    table.add_column("Value")
    table.add_row("Título escolhido", title_text)
    table.add_row("Contagem de palavras", word_count)
    table.add_row("Duração estimada", duration)
    table.add_row("QA Score", qa_score)
    table.add_row("QA Veredito", qa_verdict)
    table.add_row("Arquivo", str(output_path))

    errors = state.get("errors", [])
    if errors:
        table.add_row("⚠️ Erros", str(len(errors)))

    console.print(Panel(table, title="🎬 Resumo Executivo", border_style="green"))
