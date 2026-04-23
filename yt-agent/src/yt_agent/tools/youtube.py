"""Async wrapper for the YouTube MCP server — calls tools via MCP protocol."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from yt_agent.tools.mcp_client import _extract_text, _parse_result

if TYPE_CHECKING:
    from mcp import ClientSession
from yt_agent.tools.schemas import (
    YouTubeAnalytics,
    YouTubeChannelInfo,
    YouTubeOwnVideo,
    YouTubeSearchResult,
    YouTubeTopVideo,
    YouTubeVideoDetail,
)

logger = logging.getLogger(__name__)


class YouTubeClient:
    """Typed async client that proxies YouTube MCP tools.

    Each method calls the corresponding MCP tool on the YouTube server
    and returns a validated Pydantic model.
    """

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def _call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any] | list[Any]:
        logger.debug("YouTube MCP call: %s(%s)", tool_name, arguments)
        result = await self._session.call_tool(tool_name, arguments=arguments)
        return _parse_result(result)

    # -- Search Videos ------------------------------------------------------

    async def search_videos(
        self,
        query: str,
        *,
        duration: str | None = None,
        published_after: str | None = None,
        max_results: int = 10,
    ) -> list[YouTubeSearchResult]:
        args: dict[str, Any] = {"query": query, "maxResults": max_results}
        if duration:
            args["videoDuration"] = duration
        if published_after:
            args["publishedAfter"] = published_after
        data = await self._call("videos_searchVideos", args)
        items = data.get("items", data.get("videos", [])) if isinstance(data, dict) else data
        results: list[YouTubeSearchResult] = []
        for item in items:
            raw_id = item.get("id")
            vid = (
                raw_id.get("videoId") if isinstance(raw_id, dict) else item.get("videoId")
            )
            if not vid:
                continue
            snippet = item.get("snippet", item)
            results.append(
                YouTubeSearchResult(
                    video_id=vid,
                    title=snippet.get("title", ""),
                    channel_title=snippet.get("channelTitle"),
                    published_at=snippet.get("publishedAt"),
                    description=snippet.get("description", ""),
                )
            )
        return results

    # -- Get Video ----------------------------------------------------------

    async def get_video(self, video_id: str) -> YouTubeVideoDetail:
        data = await self._call("videos_getVideo", {"videoId": video_id})
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
            if not items:
                msg = f"Video {video_id!r} not found"
                raise ValueError(msg)
            item = items[0]
        else:
            item = data

        snippet = item.get("snippet", item)
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        return YouTubeVideoDetail(
            video_id=video_id,
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            channel_id=snippet.get("channelId"),
            channel_title=snippet.get("channelTitle"),
            published_at=snippet.get("publishedAt"),
            view_count=int(stats["viewCount"]) if "viewCount" in stats else None,
            like_count=int(stats["likeCount"]) if "likeCount" in stats else None,
            comment_count=int(stats["commentCount"]) if "commentCount" in stats else None,
            duration=content.get("duration"),
            tags=snippet.get("tags", []),
        )

    # -- Get Transcript -----------------------------------------------------

    async def get_transcript(
        self,
        video_id: str,
        *,
        language: str | None = None,
    ) -> str:
        args: dict[str, Any] = {"videoId": video_id}
        if language:
            args["language"] = language
        result = await self._session.call_tool("transcripts_getTranscript", arguments=args)
        return _extract_text(result)

    # -- List Own Videos (Studio) -------------------------------------------

    async def list_own_videos(
        self,
        *,
        status: str | None = None,
        max_results: int = 20,
    ) -> list[YouTubeOwnVideo]:
        args: dict[str, Any] = {"maxResults": max_results}
        if status:
            args["status"] = status
        data = await self._call("studio_listOwnVideos", args)
        items = data.get("items", data.get("videos", [])) if isinstance(data, dict) else data
        return [
            YouTubeOwnVideo(
                video_id=item.get("videoId", item.get("id", {}).get("videoId", "")),
                title=item.get("title", item.get("snippet", {}).get("title", "")),
                status=item.get("status", item.get("privacyStatus", "public")),
                published_at=item.get("publishedAt", item.get("snippet", {}).get("publishedAt")),
            )
            for item in items
        ]

    # -- Video Analytics ----------------------------------------------------

    async def get_video_analytics(
        self,
        video_id: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        metrics: str = "views,estimatedMinutesWatched,likes,comments",
    ) -> YouTubeAnalytics:
        args: dict[str, Any] = {"videoId": video_id, "metrics": metrics}
        if start_date:
            args["startDate"] = start_date
        if end_date:
            args["endDate"] = end_date
        data = await self._call("analytics_getVideoAnalytics", args)
        return YouTubeAnalytics(
            rows=data.get("rows", []),
            column_headers=data.get("columnHeaders", []),
        )

    # -- Channel Analytics --------------------------------------------------

    async def get_channel_analytics(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        metrics: str = "views,estimatedMinutesWatched,subscribersGained",
        dimensions: str = "day",
    ) -> YouTubeAnalytics:
        args: dict[str, Any] = {"metrics": metrics, "dimensions": dimensions}
        if start_date:
            args["startDate"] = start_date
        if end_date:
            args["endDate"] = end_date
        data = await self._call("analytics_getChannelAnalytics", args)
        return YouTubeAnalytics(
            rows=data.get("rows", []),
            column_headers=data.get("columnHeaders", []),
        )

    # -- Top Videos ---------------------------------------------------------

    async def get_top_videos(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        max_results: int = 10,
        sort_by: str = "views",
    ) -> list[YouTubeTopVideo]:
        args: dict[str, Any] = {"maxResults": max_results, "sortBy": sort_by}
        if start_date:
            args["startDate"] = start_date
        if end_date:
            args["endDate"] = end_date
        data = await self._call("analytics_getTopVideos", args)
        rows = data.get("rows", []) if isinstance(data, dict) else data
        return [
            YouTubeTopVideo(
                video_id=row[0] if row else "",
                title="",
                views=int(row[1]) if len(row) > 1 else 0,
                estimated_minutes_watched=float(row[2]) if len(row) > 2 else 0.0,
                likes=int(row[3]) if len(row) > 3 else 0,
            )
            for row in rows
        ]

    # -- Get Channel --------------------------------------------------------

    async def get_channel(self, channel_id: str) -> YouTubeChannelInfo:
        data = await self._call("channels_getChannel", {"channelId": channel_id})
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
            if not items:
                msg = f"Channel {channel_id!r} not found"
                raise ValueError(msg)
            item = items[0]
        else:
            item = data

        snippet = item.get("snippet", item)
        stats = item.get("statistics", {})
        return YouTubeChannelInfo(
            channel_id=channel_id,
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            subscriber_count=(
                int(stats["subscriberCount"]) if "subscriberCount" in stats else None
            ),
            view_count=int(stats["viewCount"]) if "viewCount" in stats else None,
            video_count=int(stats["videoCount"]) if "videoCount" in stats else None,
            published_at=snippet.get("publishedAt"),
        )
