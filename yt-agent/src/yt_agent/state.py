"""Pydantic schemas for agent outputs and LangGraph workflow state."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, TypedDict

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Agent P — Performance Diagnosis
# ---------------------------------------------------------------------------


class LastVideoMetrics(BaseModel):
    id: str
    title: str
    type: Literal["long", "short"]
    published_at: date
    views: int
    avg_retention_pct: float
    like_ratio_pct: float
    comments: int
    subscribers_gained: int


class ChannelBaseline(BaseModel):
    avg_views: int
    avg_retention_pct: float
    avg_like_ratio_pct: float
    avg_comments: int


class RetentionDrop(BaseModel):
    timestamp: str = Field(description="mm:ss format")
    retention_before_pct: float
    retention_after_pct: float
    drop_pct: float
    script_excerpt: str
    diagnosis: str
    corrective_action: str


class CriticalPoints(BaseModel):
    retention_30s_pct: float | None = None
    retention_2min_pct: float | None = None
    midpoint_retention_pct: float | None = None


class Lessons(BaseModel):
    errors_to_avoid: list[str]
    successes_to_keep: list[str]


class PerformanceDiagnosis(BaseModel):
    last_video: LastVideoMetrics
    channel_baseline: ChannelBaseline
    retention_drops: list[RetentionDrop] = Field(default_factory=list)
    critical_points: CriticalPoints
    lessons: Lessons
    calibrations: list[str]
    alert: Literal["none", "low_retention", "low_engagement"] = "none"


# ---------------------------------------------------------------------------
# Agent 0 — Competitive Briefing
# ---------------------------------------------------------------------------


class CompetitorVideo(BaseModel):
    title: str
    channel: str
    views: int
    published_at: date
    breakout_score: float | None = None
    tags: list[str] = Field(default_factory=list)


class CompetitorError(BaseModel):
    error: str
    correction: str
    source: str = Field(description="Real source / study")


class UnexploredAngle(BaseModel):
    angle: str
    why_possible: str = Field(description="Real source / study")


class AudienceInsights(BaseModel):
    top_questions: list[str] = Field(default_factory=list)
    dominant_sentiment: str = ""
    recurring_objections: list[str] = Field(default_factory=list)
    perceived_gaps: list[str] = Field(default_factory=list)


class CompetitiveBriefing(BaseModel):
    competitors_analyzed: list[CompetitorVideo]
    top_errors: list[CompetitorError]
    unexplored_angles: list[UnexploredAngle]
    structural_pattern_to_avoid: str
    differentiation_manifesto: str
    audience_insights: AudienceInsights
    competitor_tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent V — Theme Validation
# ---------------------------------------------------------------------------


class KeywordMetrics(BaseModel):
    keyword: str
    volume: int
    competition: int
    overall: int


class GoldenChecklist(BaseModel):
    universal_angle: str
    short_premise: str = Field(description="≤10 words")
    persona_trigger: str


class ThemeValidation(BaseModel):
    keyword: str
    volume: int
    competition: int
    overall: int
    verdict: Literal["approved", "low_demand", "rejected"]
    alternatives: list[KeywordMetrics] = Field(default_factory=list)
    golden_checklist: GoldenChecklist


# ---------------------------------------------------------------------------
# Agent Meta — Video Metadata
# ---------------------------------------------------------------------------


class TitleCandidate(BaseModel):
    title: str
    formula: str
    char_count: int
    word_count: int


class TitleTop3(BaseModel):
    title: str
    formula: str
    justification: str
    keyword_validation: KeywordMetrics


class TitlesBlock(BaseModel):
    all_10: list[TitleCandidate]
    top_3: list[TitleTop3]


class ThumbnailSpec(BaseModel):
    aesthetic: Literal["documental_sombria", "ficção_científica"]
    composition: Literal["A", "B", "C"]
    emotion: str
    dominant_color: str = Field(description="Hex code, e.g. #1A1A2E")
    accent_color: str = Field(description="Hex code")
    text_overlay: str | None = None
    prompt_en: str


class TagValidation(BaseModel):
    tag: str
    volume: int
    competition: int
    overall: int


class TagsBlock(BaseModel):
    list_: list[str] = Field(alias="list")
    validation_table: list[TagValidation]


class VideoMetadata(BaseModel):
    titles: TitlesBlock
    thumbnail: ThumbnailSpec
    description_seo: str = Field(description="250-400 words, full template")
    tags: TagsBlock
    hashtags: list[str] = Field(min_length=3, max_length=5)
    community_post: str = Field(description="≤150 words")


# ---------------------------------------------------------------------------
# Agent Roteirista — Script
# ---------------------------------------------------------------------------


class ScriptSection(BaseModel):
    type: Literal[
        "hook", "context", "block_1", "block_2", "block_3", "block_4", "cta_final"
    ]
    label: str
    narration: str
    visual: str
    pattern_interrupt: str | None = None
    editorial_insertion: str | None = None
    cta: str | None = None


class OpenLoop(BaseModel):
    loop_number: int
    opens_at: str
    content: str
    closes_at: str
    payoff_type: str


class RetentionAudit(BaseModel):
    hook_delivers_promise_in_8s: bool
    zero_institutional_intro: bool
    first_visual_specific: bool
    numeric_data_in_15s: bool
    context_opens_loop: bool


class Script(BaseModel):
    word_count: int
    estimated_duration_min: float
    sections: list[ScriptSection]
    open_loops_map: list[OpenLoop] = Field(default_factory=list)
    retention_audit: RetentionAudit
    differentiation_manifesto_location: str


# ---------------------------------------------------------------------------
# Agent QA — Quality Assurance Report
# ---------------------------------------------------------------------------


class QAItem(BaseModel):
    number: int
    name: str
    status: Literal["pass", "fail", "skip"]
    detail: str = ""


class QAReport(BaseModel):
    total_items: int = 38
    passed: int
    failed: int
    attempt: int = Field(ge=1, le=2)
    items: list[QAItem]
    verdict: Literal["approved", "needs_fix", "approved_with_warnings"]
    fix_instructions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent R — Repackaging Proposal
# ---------------------------------------------------------------------------


class RepackagingCandidate(BaseModel):
    video_id: str
    title: str
    views: int
    avg_retention_pct: float
    reason: str


class RepackagingSuggestion(BaseModel):
    video_id: str
    new_title: str
    new_thumbnail_prompt: str
    new_description: str
    new_tags: list[str]
    rationale: str


class RepackagingProposal(BaseModel):
    candidates: list[RepackagingCandidate]
    suggestions: list[RepackagingSuggestion]


# ---------------------------------------------------------------------------
# Human Decision (for human-in-the-loop)
# ---------------------------------------------------------------------------


class HumanDecision(BaseModel):
    phase: str
    question: str
    options: list[str]
    chosen: str
    timestamp: datetime = Field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Workflow State (LangGraph TypedDict)
# ---------------------------------------------------------------------------


class WorkflowState(TypedDict, total=False):
    # --- User inputs ---
    video_topic: str
    sub_niche: str
    format: Literal["long", "short"]
    editorial_angle: str
    dominant_emotion: str
    technical_detail: Literal["basic", "intermediate", "advanced"]
    reference_period: str
    related_video: str | None
    context_notes: str | None

    # --- Agent outputs ---
    performance_diagnosis: PerformanceDiagnosis | None
    competitive_briefing: CompetitiveBriefing | None
    theme_validation: ThemeValidation | None
    video_metadata: VideoMetadata | None
    script: Script | None
    qa_report: QAReport | None

    # --- Flow control ---
    human_decisions: list[HumanDecision]
    qa_attempt: int
    current_phase: str
    errors: list[str]
