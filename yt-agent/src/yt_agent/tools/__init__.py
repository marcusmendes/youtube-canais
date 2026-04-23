"""LangChain tool wrappers for VidIQ and YouTube APIs.

Tools are grouped by agent responsibility so each agent only receives
the tools it needs, keeping context focused.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.tools import StructuredTool

if TYPE_CHECKING:
    from yt_agent.tools.vidiq import VidIQClient
    from yt_agent.tools.youtube import YouTubeClient


def _build_vidiq_tools(client: VidIQClient) -> dict[str, StructuredTool]:
    """Build a dict name→StructuredTool wrapping every VidIQClient method."""
    from pydantic import BaseModel, Field

    class KeywordInput(BaseModel):
        keyword: str
        include_related: bool = True

    class OutliersInput(BaseModel):
        keyword: str | None = None
        content_type: str = "all"
        published_within: str | None = None
        sort: str | None = None
        limit: int = 20

    class TrendingInput(BaseModel):
        video_format: str
        title_query: str | None = None
        sort_by: str = "relevance"
        limit: int = 10

    class VideoIdInput(BaseModel):
        video_id: str

    class VideoCommentsInput(BaseModel):
        video_id: str
        order: str = "relevance"
        max_result: int = 20

    class VideoStatsInput(BaseModel):
        video_id: str
        granularity: str
        from_date: str | None = Field(None, alias="from")
        to_date: str | None = Field(None, alias="to")

    class ChannelIdInput(BaseModel):
        channel_id: str

    class ChannelVideosInput(BaseModel):
        channel_id: str
        video_format: str
        popular: bool = True

    class ChannelAnalyticsInput(BaseModel):
        channel_id: str
        start_date: str | None = None
        end_date: str | None = None
        metrics: list[str] | None = None
        dimensions: list[str] | None = None
        filters: str | None = None

    return {
        "vidiq_keyword_research": StructuredTool.from_function(
            coroutine=lambda **kw: client.keyword_research(**kw),
            name="vidiq_keyword_research",
            description="Research keyword volume, competition and related keywords via VidIQ",
            args_schema=KeywordInput,
        ),
        "vidiq_outliers": StructuredTool.from_function(
            coroutine=lambda **kw: client.outliers(**kw),
            name="vidiq_outliers",
            description="Find outlier/breakout videos for a keyword via VidIQ",
            args_schema=OutliersInput,
        ),
        "vidiq_trending_videos": StructuredTool.from_function(
            coroutine=lambda **kw: client.trending_videos(**kw),
            name="vidiq_trending_videos",
            description=(
                "Get trending videos by format via VidIQ. "
                "video_format must be 'long' or 'short'."
            ),
            args_schema=TrendingInput,
        ),
        "vidiq_video_transcript": StructuredTool.from_function(
            coroutine=lambda **kw: client.video_transcript(**kw),
            name="vidiq_video_transcript",
            description="Get video transcript via VidIQ",
            args_schema=VideoIdInput,
        ),
        "vidiq_video_comments": StructuredTool.from_function(
            coroutine=lambda **kw: client.video_comments(**kw),
            name="vidiq_video_comments",
            description="Get video comments via VidIQ",
            args_schema=VideoCommentsInput,
        ),
        "vidiq_video_stats": StructuredTool.from_function(
            coroutine=lambda **kw: client.video_stats(**kw),
            name="vidiq_video_stats",
            description=(
                "Get video statistics over time via VidIQ. "
                "granularity must be 'hourly', 'daily', or 'monthly'."
            ),
            args_schema=VideoStatsInput,
        ),
        "vidiq_user_channels": StructuredTool.from_function(
            coroutine=lambda: client.user_channels(),
            name="vidiq_user_channels",
            description="List channels owned by the authenticated VidIQ user",
        ),
        "vidiq_channel_videos": StructuredTool.from_function(
            coroutine=lambda **kw: client.channel_videos(**kw),
            name="vidiq_channel_videos",
            description=(
                "List videos from a channel via VidIQ. "
                "video_format must be 'long', 'short', or 'live'. "
                "channel_id should be a YouTube channel ID (UCxx...) or handle (@name)."
            ),
            args_schema=ChannelVideosInput,
        ),
        "vidiq_channel_analytics": StructuredTool.from_function(
            coroutine=lambda **kw: client.channel_analytics(**kw),
            name="vidiq_channel_analytics",
            description="Get channel analytics via VidIQ",
            args_schema=ChannelAnalyticsInput,
        ),
        "vidiq_channel_performance_trends": StructuredTool.from_function(
            coroutine=lambda **kw: client.channel_performance_trends(**kw),
            name="vidiq_channel_performance_trends",
            description="Get channel performance trends (view velocity curve) via VidIQ",
            args_schema=ChannelIdInput,
        ),
        "vidiq_channel_stats": StructuredTool.from_function(
            coroutine=lambda **kw: client.channel_stats(**kw),
            name="vidiq_channel_stats",
            description="Get channel stats and daily history via VidIQ",
            args_schema=ChannelIdInput,
        ),
    }


def _build_youtube_tools(client: YouTubeClient) -> dict[str, StructuredTool]:
    """Build a dict name→StructuredTool wrapping every YouTubeClient method."""
    from pydantic import BaseModel

    class SearchInput(BaseModel):
        query: str
        duration: str | None = None
        published_after: str | None = None
        max_results: int = 10

    class VideoIdInput(BaseModel):
        video_id: str

    class TranscriptInput(BaseModel):
        video_id: str
        language: str | None = None

    class ListOwnInput(BaseModel):
        status: str | None = None
        max_results: int = 20

    class VideoAnalyticsInput(BaseModel):
        video_id: str
        start_date: str | None = None
        end_date: str | None = None
        metrics: str = "views,estimatedMinutesWatched,likes,comments"

    class ChannelAnalyticsInput(BaseModel):
        start_date: str | None = None
        end_date: str | None = None
        metrics: str = "views,estimatedMinutesWatched,subscribersGained"
        dimensions: str = "day"

    class TopVideosInput(BaseModel):
        start_date: str | None = None
        end_date: str | None = None
        max_results: int = 10
        sort_by: str = "views"

    class ChannelIdInput(BaseModel):
        channel_id: str

    return {
        "youtube_search_videos": StructuredTool.from_function(
            coroutine=lambda **kw: client.search_videos(**kw),
            name="youtube_search_videos",
            description="Search YouTube videos by query",
            args_schema=SearchInput,
        ),
        "youtube_get_video": StructuredTool.from_function(
            coroutine=lambda **kw: client.get_video(**kw),
            name="youtube_get_video",
            description="Get detailed info for a YouTube video",
            args_schema=VideoIdInput,
        ),
        "youtube_get_transcript": StructuredTool.from_function(
            coroutine=lambda **kw: client.get_transcript(**kw),
            name="youtube_get_transcript",
            description="Get transcript for a YouTube video",
            args_schema=TranscriptInput,
        ),
        "youtube_list_own_videos": StructuredTool.from_function(
            coroutine=lambda **kw: client.list_own_videos(**kw),
            name="youtube_list_own_videos",
            description="List videos from your own channel (requires OAuth)",
            args_schema=ListOwnInput,
        ),
        "youtube_get_video_analytics": StructuredTool.from_function(
            coroutine=lambda **kw: client.get_video_analytics(**kw),
            name="youtube_get_video_analytics",
            description="Get analytics for a specific video",
            args_schema=VideoAnalyticsInput,
        ),
        "youtube_get_channel_analytics": StructuredTool.from_function(
            coroutine=lambda **kw: client.get_channel_analytics(**kw),
            name="youtube_get_channel_analytics",
            description="Get channel-level analytics",
            args_schema=ChannelAnalyticsInput,
        ),
        "youtube_get_top_videos": StructuredTool.from_function(
            coroutine=lambda **kw: client.get_top_videos(**kw),
            name="youtube_get_top_videos",
            description="Get top-performing videos from your channel",
            args_schema=TopVideosInput,
        ),
        "youtube_get_channel": StructuredTool.from_function(
            coroutine=lambda **kw: client.get_channel(**kw),
            name="youtube_get_channel",
            description="Get info for a YouTube channel",
            args_schema=ChannelIdInput,
        ),
    }


def get_performance_tools(
    vidiq: VidIQClient, youtube: YouTubeClient
) -> list[StructuredTool]:
    """Tools for Agent P (Performance Diagnosis)."""
    vtools = _build_vidiq_tools(vidiq)
    ytools = _build_youtube_tools(youtube)
    return [
        vtools["vidiq_user_channels"],
        vtools["vidiq_channel_videos"],
        vtools["vidiq_video_stats"],
        vtools["vidiq_channel_analytics"],
        vtools["vidiq_channel_performance_trends"],
        ytools["youtube_list_own_videos"],
        ytools["youtube_get_video_analytics"],
        ytools["youtube_get_channel_analytics"],
        ytools["youtube_get_top_videos"],
    ]


def get_competitive_tools(
    vidiq: VidIQClient, youtube: YouTubeClient
) -> list[StructuredTool]:
    """Tools for Agent 0 (Competitive Analysis)."""
    vtools = _build_vidiq_tools(vidiq)
    ytools = _build_youtube_tools(youtube)
    return [
        vtools["vidiq_outliers"],
        vtools["vidiq_trending_videos"],
        vtools["vidiq_video_transcript"],
        vtools["vidiq_video_comments"],
        ytools["youtube_search_videos"],
        ytools["youtube_get_video"],
        ytools["youtube_get_transcript"],
    ]


def get_validation_tools(vidiq: VidIQClient) -> list[StructuredTool]:
    """Tools for Agent V (Theme Validation)."""
    vtools = _build_vidiq_tools(vidiq)
    return [vtools["vidiq_keyword_research"]]


def get_metadata_tools(vidiq: VidIQClient) -> list[StructuredTool]:
    """Tools for Agent Meta (Metadata generation)."""
    vtools = _build_vidiq_tools(vidiq)
    return [vtools["vidiq_keyword_research"]]


def get_repackaging_tools(
    vidiq: VidIQClient, youtube: YouTubeClient
) -> list[StructuredTool]:
    """Tools for Agent R (Repackaging)."""
    vtools = _build_vidiq_tools(vidiq)
    ytools = _build_youtube_tools(youtube)
    return [
        vtools["vidiq_channel_videos"],
        vtools["vidiq_video_stats"],
        vtools["vidiq_keyword_research"],
        ytools["youtube_get_video_analytics"],
    ]
