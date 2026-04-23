"""Agent R — Repackaging of underperforming videos."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from yt_agent.agents.base import get_sonnet, invoke_agent_with_tools, load_prompt
from yt_agent.config import get_settings
from yt_agent.state import RepackagingProposal
from yt_agent.tools import get_repackaging_tools

if TYPE_CHECKING:
    from yt_agent.memory.repository import ChannelMemory
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient

logger = logging.getLogger(__name__)


async def find_repackaging_candidates(
    *,
    memory: ChannelMemory,
) -> list[dict]:
    """Identify videos with low views but decent retention.

    Criteria:
    - Published 5+ days ago
    - views_7d < 50% of channel average
    - avg_retention_pct > 25%

    Returns a list of dicts with video info for display.
    """
    videos = await memory.get_last_n_videos(20)
    if not videos:
        return []

    videos_with_metrics = [
        v for v in videos if v.views_7d is not None and v.avg_retention_pct is not None
    ]

    if not videos_with_metrics:
        return []

    avg_views = sum(v.views_7d for v in videos_with_metrics) / len(videos_with_metrics)

    candidates = []
    for v in videos_with_metrics:
        if v.views_7d < avg_views * 0.5 and v.avg_retention_pct > 25.0:
            candidates.append({
                "video_id": v.id,
                "title": v.title,
                "views_7d": v.views_7d,
                "avg_retention_pct": v.avg_retention_pct,
                "avg_channel_views": int(avg_views),
                "reason": (
                    f"Views ({v.views_7d:,}) < 50% da média ({int(avg_views):,}) "
                    f"mas retenção ({v.avg_retention_pct:.1f}%) > 25%"
                ),
            })

    return candidates


async def run_repackaging_agent(
    video_id: str,
    *,
    vidiq: VidIQClient,
    youtube: YouTubeClient,
) -> RepackagingProposal:
    """Generate a repackaging proposal for a specific video.

    Queries VidIQ/YouTube for the video's current data and baseline,
    then generates new title, thumbnail, description, and tags.
    """
    settings = get_settings()
    channel = settings.channel_handle
    raw_prompt = load_prompt("repackaging.md")
    system_prompt = raw_prompt.replace("{channel_handle}", channel)
    tools = get_repackaging_tools(vidiq, youtube)

    user_message = (
        f"Analyze and generate a repackaging proposal for video ID: {video_id}\n\n"
        f"## CHANNEL IDENTITY (DO NOT CHANGE)\n"
        f"channel_id for ALL VidIQ calls = `{channel}`\n"
        f"DO NOT use any other handle or channel ID.\n\n"
        f"## STEPS\n"
        f"1. `vidiq_video_stats(video_id=\"{video_id}\", granularity=\"daily\")`\n"
        f"2. `youtube_get_video_analytics(video_id=\"{video_id}\")`\n"
        f"3. `vidiq_channel_videos(channel_id=\"{channel}\", video_format=\"long\", popular=true)` "
        f"— baseline do canal\n"
        f"4. Diagnose why the video underperformed\n"
        f"5. Use `vidiq_keyword_research` to find better keywords\n"
        f"6. Generate the complete repackaging proposal\n\n"
        f"Return the result as a JSON object matching the "
        f"RepackagingProposal schema:\n"
        f"{RepackagingProposal.model_json_schema()}"
    )

    return await invoke_agent_with_tools(
        system_prompt=system_prompt,
        user_message=user_message,
        tools=tools,
        llm=get_sonnet(),
        output_schema=RepackagingProposal,
    )
