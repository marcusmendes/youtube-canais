"""Async wrapper for the VidIQ MCP server — calls tools via MCP protocol."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from yt_agent.tools.mcp_client import _parse_result

if TYPE_CHECKING:
    from mcp import ClientSession
from yt_agent.tools.schemas import (
    VidIQAnalyticsResult,
    VidIQChannel,
    VidIQChannelStatsResult,
    VidIQChannelVideosResult,
    VidIQCommentsResult,
    VidIQKeywordResult,
    VidIQOutlierResult,
    VidIQPerformanceTrendsResult,
    VidIQTranscriptResult,
    VidIQTrendingVideo,
    VidIQVideoStatsResult,
)

logger = logging.getLogger(__name__)

_GRANULARITY_MAP: dict[str, str] = {
    "hour": "hourly",
    "hourly": "hourly",
    "day": "daily",
    "daily": "daily",
    "month": "monthly",
    "monthly": "monthly",
}

_VIDEO_FORMAT_MAP: dict[str, str] = {
    "long": "long",
    "long-form": "long",
    "video": "long",
    "short": "short",
    "shorts": "short",
    "live": "live",
    "stream": "live",
    "all": "long",
}


class VidIQClient:
    """Typed async client that proxies VidIQ MCP tools.

    Each method calls the corresponding MCP tool on the VidIQ server
    and returns a validated Pydantic model.

    When *channel_handle* is provided, every method that accepts a
    ``channel_id`` will silently replace whatever value the LLM passed
    with the configured handle — preventing misidentification.
    """

    def __init__(
        self,
        session: ClientSession,
        *,
        channel_handle: str | None = None,
    ) -> None:
        self._session = session
        self._channel_handle = channel_handle

    def _resolve_channel(self, channel_id: str) -> str:
        if self._channel_handle:
            if channel_id != self._channel_handle:
                logger.warning(
                    "Overriding channel_id %r → %r",
                    channel_id,
                    self._channel_handle,
                )
            return self._channel_handle
        return channel_id

    async def _call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any] | list[Any]:
        logger.debug("VidIQ MCP call: %s(%s)", tool_name, arguments)
        result = await self._session.call_tool(tool_name, arguments=arguments)
        return _parse_result(result)

    # -- Keyword Research ---------------------------------------------------

    async def keyword_research(
        self,
        keyword: str,
        *,
        include_related: bool = True,
    ) -> VidIQKeywordResult:
        data = await self._call(
            "vidiq_keyword_research",
            {"keyword": keyword, "includeRelated": include_related},
        )
        return VidIQKeywordResult.model_validate(data)

    # -- Outliers -----------------------------------------------------------

    async def outliers(
        self,
        *,
        keyword: str | None = None,
        content_type: Literal["all", "long", "short"] = "all",
        published_within: str | None = None,
        sort: str | None = None,
        limit: int = 20,
    ) -> VidIQOutlierResult:
        args: dict[str, Any] = {"limit": limit, "contentType": content_type}
        if keyword:
            args["keyword"] = keyword
        if published_within:
            args["publishedWithin"] = published_within
        if sort:
            args["sort"] = sort
        data = await self._call("vidiq_outliers", args)
        return VidIQOutlierResult.model_validate(data)

    # -- Trending Videos ----------------------------------------------------

    async def trending_videos(
        self,
        video_format: str,
        *,
        title_query: str | None = None,
        sort_by: str = "relevance",
        limit: int = 10,
    ) -> list[VidIQTrendingVideo]:
        normalized_fmt = _VIDEO_FORMAT_MAP.get(video_format.lower(), "long")
        args: dict[str, Any] = {
            "videoFormat": normalized_fmt,
            "sortBy": sort_by,
            "limit": limit,
        }
        if title_query:
            args["titleQuery"] = title_query
        data = await self._call("vidiq_trending_videos", args)
        videos = data.get("videos", []) if isinstance(data, dict) else data
        return [VidIQTrendingVideo.model_validate(v) for v in videos]

    # -- Video Transcript ---------------------------------------------------

    async def video_transcript(
        self,
        video_id: str,
        *,
        language: str | None = None,
    ) -> VidIQTranscriptResult:
        args: dict[str, Any] = {"videoId": video_id}
        if language:
            args["language"] = language
        data = await self._call("vidiq_video_transcript", args)
        return VidIQTranscriptResult.model_validate(data)

    # -- Video Comments -----------------------------------------------------

    async def video_comments(
        self,
        video_id: str,
        *,
        order: Literal["time", "relevance"] = "relevance",
        max_result: int = 20,
    ) -> VidIQCommentsResult:
        data = await self._call(
            "vidiq_video_comments",
            {"videoId": video_id, "order": order, "maxResult": max_result},
        )
        return VidIQCommentsResult.model_validate(data)

    # -- Video Stats --------------------------------------------------------

    async def video_stats(
        self,
        video_id: str,
        granularity: str,
        *,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> VidIQVideoStatsResult:
        normalized = _GRANULARITY_MAP.get(granularity.lower(), "daily")
        args: dict[str, Any] = {"videoId": video_id, "granularity": normalized}
        if from_date:
            args["from"] = from_date
        if to_date:
            args["to"] = to_date
        data = await self._call("vidiq_video_stats", args)
        return VidIQVideoStatsResult.model_validate(data)

    # -- User Channels ------------------------------------------------------

    async def user_channels(self) -> list[VidIQChannel]:
        data = await self._call("vidiq_user_channels", {})
        channels = data.get("channels", []) if isinstance(data, dict) else data
        return [VidIQChannel.model_validate(c) for c in channels]

    # -- Channel Videos -----------------------------------------------------

    async def channel_videos(
        self,
        channel_id: str,
        video_format: str,
        *,
        popular: bool = True,
    ) -> VidIQChannelVideosResult:
        normalized_fmt = _VIDEO_FORMAT_MAP.get(video_format.lower(), "long")
        data = await self._call(
            "vidiq_channel_videos",
            {
                "channelId": self._resolve_channel(channel_id),
                "videoFormat": normalized_fmt,
                "popular": popular,
            },
        )
        return VidIQChannelVideosResult.model_validate(data)

    # -- Channel Analytics --------------------------------------------------

    async def channel_analytics(
        self,
        channel_id: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
        filters: str | None = None,
    ) -> VidIQAnalyticsResult:
        args: dict[str, Any] = {"channelId": self._resolve_channel(channel_id)}
        if start_date:
            args["startDate"] = start_date
        if end_date:
            args["endDate"] = end_date
        if metrics:
            args["metrics"] = metrics
        if dimensions:
            args["dimensions"] = dimensions
        if filters:
            args["filters"] = filters
        data = await self._call("vidiq_channel_analytics", args)
        return VidIQAnalyticsResult.model_validate(data)

    # -- Channel Performance Trends -----------------------------------------

    async def channel_performance_trends(
        self,
        channel_id: str,
    ) -> VidIQPerformanceTrendsResult:
        data = await self._call(
            "vidiq_channel_performance_trends",
            {"channelId": self._resolve_channel(channel_id)},
        )
        return VidIQPerformanceTrendsResult.model_validate(data)

    # -- Channel Stats ------------------------------------------------------

    async def channel_stats(
        self,
        channel_id: str,
        *,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> VidIQChannelStatsResult:
        args: dict[str, Any] = {"channelId": self._resolve_channel(channel_id)}
        if from_date:
            args["from"] = from_date
        if to_date:
            args["to"] = to_date
        data = await self._call("vidiq_channel_stats", args)
        return VidIQChannelStatsResult.model_validate(data)
