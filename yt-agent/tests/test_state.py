"""Validate that all Pydantic agent output schemas can be instantiated and serialized."""

from __future__ import annotations

from datetime import date, datetime

from yt_agent.state import (
    AudienceInsights,
    ChannelBaseline,
    CompetitiveBriefing,
    CompetitorError,
    CompetitorVideo,
    CriticalPoints,
    GoldenChecklist,
    HumanDecision,
    KeywordMetrics,
    LastVideoMetrics,
    Lessons,
    OpenLoop,
    PerformanceDiagnosis,
    QAItem,
    QAReport,
    RepackagingCandidate,
    RepackagingProposal,
    RepackagingSuggestion,
    RetentionAudit,
    RetentionDrop,
    Script,
    ScriptSection,
    TagsBlock,
    TagValidation,
    ThemeValidation,
    ThumbnailSpec,
    TitleCandidate,
    TitlesBlock,
    TitleTop3,
    UnexploredAngle,
    VideoMetadata,
)


def test_performance_diagnosis_roundtrip():
    diag = PerformanceDiagnosis(
        last_video=LastVideoMetrics(
            id="abc123",
            title="Test Video",
            type="long",
            published_at=date(2026, 4, 1),
            views=5000,
            avg_retention_pct=45.0,
            like_ratio_pct=8.5,
            comments=42,
            subscribers_gained=10,
        ),
        channel_baseline=ChannelBaseline(
            avg_views=3000,
            avg_retention_pct=40.0,
            avg_like_ratio_pct=7.0,
            avg_comments=30,
        ),
        retention_drops=[
            RetentionDrop(
                timestamp="01:30",
                retention_before_pct=50.0,
                retention_after_pct=35.0,
                drop_pct=15.0,
                script_excerpt="...",
                diagnosis="Drop after intro",
                corrective_action="Shorten intro",
            )
        ],
        critical_points=CriticalPoints(retention_30s_pct=60.0),
        lessons=Lessons(
            errors_to_avoid=["Too long intro"],
            successes_to_keep=["Strong hook"],
        ),
        calibrations=["Use faster hook"],
    )
    json_str = diag.model_dump_json()
    restored = PerformanceDiagnosis.model_validate_json(json_str)
    assert restored.last_video.id == "abc123"
    assert restored.alert == "none"


def test_competitive_briefing_roundtrip():
    briefing = CompetitiveBriefing(
        competitors_analyzed=[
            CompetitorVideo(
                title="Rival Video",
                channel="RivalCh",
                views=10000,
                published_at=date(2026, 3, 15),
            )
        ],
        top_errors=[
            CompetitorError(
                error="Wrong stat", correction="Correct stat", source="PubMed 2026"
            )
        ],
        unexplored_angles=[
            UnexploredAngle(angle="Novo ângulo", why_possible="Study X")
        ],
        structural_pattern_to_avoid="Clickbait without payoff",
        differentiation_manifesto="Sempre com fonte real",
        audience_insights=AudienceInsights(top_questions=["Does X work?"]),
    )
    json_str = briefing.model_dump_json()
    restored = CompetitiveBriefing.model_validate_json(json_str)
    assert len(restored.competitors_analyzed) == 1


def test_theme_validation_roundtrip():
    tv = ThemeValidation(
        keyword="inteligência artificial medicina",
        volume=1200,
        competition=45,
        overall=65,
        verdict="approved",
        alternatives=[
            KeywordMetrics(keyword="IA saúde", volume=800, competition=30, overall=70)
        ],
        golden_checklist=GoldenChecklist(
            universal_angle="Todos se preocupam com saúde",
            short_premise="IA cura doenças",
            persona_trigger="Curiosos sobre tecnologia",
        ),
    )
    json_str = tv.model_dump_json()
    restored = ThemeValidation.model_validate_json(json_str)
    assert restored.verdict == "approved"


def test_video_metadata_roundtrip():
    meta = VideoMetadata(
        titles=TitlesBlock(
            all_10=[
                TitleCandidate(title="T1", formula="F1", char_count=20, word_count=4)
            ],
            top_3=[
                TitleTop3(
                    title="T1",
                    formula="F1",
                    justification="Best",
                    keyword_validation=KeywordMetrics(
                        keyword="test", volume=100, competition=20, overall=50
                    ),
                )
            ],
        ),
        thumbnail=ThumbnailSpec(
            aesthetic="documental_sombria",
            composition="A",
            emotion="Admiração",
            dominant_color="#1A1A2E",
            accent_color="#E94560",
            prompt_en="A cinematic portrait...",
        ),
        description_seo="Test description for SEO...",
        tags=TagsBlock(
            **{
                "list": ["tag1", "tag2"],
                "validation_table": [
                    TagValidation(tag="tag1", volume=500, competition=30, overall=60)
                ],
            }
        ),
        hashtags=["#AI", "#Health", "#Science"],
        community_post="Check out our new video!",
    )
    json_str = meta.model_dump_json(by_alias=True)
    restored = VideoMetadata.model_validate_json(json_str)
    assert len(restored.hashtags) == 3


def test_script_roundtrip():
    script = Script(
        word_count=2500,
        estimated_duration_min=12.5,
        sections=[
            ScriptSection(
                type="hook",
                label="Hook",
                narration="In 2026, AI did something extraordinary...",
                visual="Close-up of a lab, dramatic lighting",
            ),
            ScriptSection(
                type="cta_final",
                label="CTA",
                narration="Subscribe for more...",
                visual="Channel logo animation",
                cta="CTA 3: Inscreva-se",
            ),
        ],
        open_loops_map=[
            OpenLoop(
                loop_number=1,
                opens_at="hook 0:05",
                content="What AI discovered",
                closes_at="block_3 8:30",
                payoff_type="revelation",
            )
        ],
        retention_audit=RetentionAudit(
            hook_delivers_promise_in_8s=True,
            zero_institutional_intro=True,
            first_visual_specific=True,
            numeric_data_in_15s=True,
            context_opens_loop=True,
        ),
        differentiation_manifesto_location="block_2",
    )
    json_str = script.model_dump_json()
    restored = Script.model_validate_json(json_str)
    assert restored.word_count == 2500
    assert len(restored.sections) == 2


def test_qa_report_roundtrip():
    report = QAReport(
        passed=25,
        failed=3,
        attempt=1,
        items=[
            QAItem(number=1, name="Hook < 8s", status="pass"),
            QAItem(number=2, name="Visual específico", status="fail", detail="Genérico"),
        ],
        verdict="needs_fix",
        fix_instructions=["Make visuals more specific"],
    )
    json_str = report.model_dump_json()
    restored = QAReport.model_validate_json(json_str)
    assert restored.failed == 3


def test_repackaging_proposal_roundtrip():
    prop = RepackagingProposal(
        candidates=[
            RepackagingCandidate(
                video_id="xyz",
                title="Old Video",
                views=100,
                avg_retention_pct=15.0,
                reason="Below 50% of channel average",
            )
        ],
        suggestions=[
            RepackagingSuggestion(
                video_id="xyz",
                new_title="New Title",
                new_thumbnail_prompt="A dramatic scene...",
                new_description="Updated description",
                new_tags=["tag1"],
                rationale="Current title is too generic",
            )
        ],
    )
    json_str = prop.model_dump_json()
    restored = RepackagingProposal.model_validate_json(json_str)
    assert len(restored.suggestions) == 1


def test_human_decision():
    hd = HumanDecision(
        phase="fase_p",
        question="Continue with low retention?",
        options=["yes", "no", "repackage"],
        chosen="yes",
        timestamp=datetime(2026, 4, 19, 10, 30),
    )
    json_str = hd.model_dump_json()
    restored = HumanDecision.model_validate_json(json_str)
    assert restored.chosen == "yes"
