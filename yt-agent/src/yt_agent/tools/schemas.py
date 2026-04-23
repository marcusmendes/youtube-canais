"""Pydantic response schemas for VidIQ and YouTube API wrappers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import datetime

# ---------------------------------------------------------------------------
# VidIQ response schemas
# ---------------------------------------------------------------------------


class VidIQKeywordMetrics(BaseModel):
    keyword: str
    volume: float | None = None
    competition: float | None = None
    overall: float | None = None
    estimated_monthly_search: float | None = Field(None, alias="estimatedMonthlySearch")
    calibrated_total_searches_30d: float | None = Field(None, alias="calibratedTotalSearches30d")
    growth_percentage: float | None = Field(None, alias="growthPercentage")


class VidIQKeywordResult(BaseModel):
    seed_keyword: VidIQKeywordMetrics = Field(alias="seedKeyword")
    related_keywords: list[VidIQKeywordMetrics] = Field(
        default_factory=list, alias="relatedKeywords"
    )


class VidIQOutlierVideo(BaseModel):
    video_id: str = Field(alias="videoId")
    title: str = ""
    channel_title: str | None = Field(None, alias="channelTitle")
    channel_id: str | None = Field(None, alias="channelId")
    view_count: int | None = Field(None, alias="viewCount")
    breakout_score: float | None = Field(None, alias="breakoutScore")
    score: float | None = None
    tags: list[str] = Field(default_factory=list)
    published_at: str | None = Field(None, alias="publishedAt")
    thumbnail: str | None = None


class VidIQOutlierResult(BaseModel):
    videos: list[VidIQOutlierVideo]
    keyword: str | None = None


class VidIQTrendingVideo(BaseModel):
    video_id: str = Field(alias="videoId")
    video_title: str = Field(alias="videoTitle")
    video_published_at: str | None = Field(None, alias="videoPublishedAt")
    video_duration: str | None = Field(None, alias="videoDuration")
    channel_id: str | None = Field(None, alias="channelId")
    channel_title: str | None = Field(None, alias="channelTitle")
    view_count: int | None = Field(None, alias="viewCount")
    engagement_rate: float | None = Field(None, alias="engagementRate")
    vph: float | None = None
    video_tags: list[str] = Field(default_factory=list, alias="videoTags")


class VidIQTranscriptResult(BaseModel):
    video_id: str = Field(alias="videoId")
    transcription: str
    language: str | None = None


class VidIQComment(BaseModel):
    author: str = ""
    author_channel_url: str | None = Field(None, alias="authorChannelUrl")
    text: str = ""
    like_count: int = Field(0, alias="likeCount")
    published_at: str | None = Field(None, alias="publishedAt")


class VidIQCommentThread(BaseModel):
    top_comment: VidIQComment = Field(alias="topComment")
    reply_count: int = Field(0, alias="replyCount")
    replies: list[VidIQComment] = Field(default_factory=list)


class VidIQCommentsResult(BaseModel):
    comments: list[VidIQCommentThread]
    video_id: str | None = Field(None, alias="videoId")


class VidIQVideoStatPoint(BaseModel):
    timestamp: str
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    vph: float | None = None


class VidIQVideoStatsResult(BaseModel):
    video_id: str = Field(alias="videoId")
    data: list[VidIQVideoStatPoint]


class VidIQChannel(BaseModel):
    channel_id: str = Field(alias="channelId")


class VidIQChannelVideo(BaseModel):
    video_id: str = Field(alias="videoId")
    title: str = ""
    published_at: str | None = Field(None, alias="publishedAt")
    thumbnail: str | None = None


class VidIQChannelVideosResult(BaseModel):
    channel_id: str = Field(alias="channelId")
    channel_title: str | None = Field(None, alias="channelTitle")
    video_format: str = Field(alias="videoFormat")
    popular: bool = True
    videos: list[VidIQChannelVideo]


class VidIQColumnHeader(BaseModel):
    name: str
    data_type: str = Field(alias="dataType")
    column_type: str = Field(alias="columnType")


class VidIQAnalyticsResult(BaseModel):
    channel_id: str = Field(alias="channelId")
    start_date: str = Field(alias="startDate")
    end_date: str = Field(alias="endDate")
    column_headers: list[VidIQColumnHeader] = Field(alias="columnHeaders")
    rows: list[list[str | int | float | None]]


class VidIQTrendPoint(BaseModel):
    minutes_since_publication: int = Field(alias="minutesSincePublication")
    views: dict[str, float | None]


class VidIQPerformanceTrendsResult(BaseModel):
    channel_id: str = Field(alias="channelId")
    trends: list[VidIQTrendPoint]
    created_at: str | None = Field(None, alias="createdAt")


class VidIQCurrentStats(BaseModel):
    subscribers: int | None = None
    views: int | None = None
    videos: int | None = None


class VidIQGrowth(BaseModel):
    subscribers_gained: int | None = Field(None, alias="subscribersGained")
    views_gained: int | None = Field(None, alias="viewsGained")
    videos_published: int | None = Field(None, alias="videosPublished")


class VidIQDailyStat(BaseModel):
    date: str
    subscribers: int | None = None
    views: int | None = None
    videos: int | None = None


class VidIQChannelStatsResult(BaseModel):
    channel_id: str = Field(alias="channelId")
    title: str | None = None
    thumbnail: str | None = None
    country: str | None = None
    default_language: str | None = Field(None, alias="defaultLanguage")
    published_at: str | None = Field(None, alias="publishedAt")
    topics: list[str] = Field(default_factory=list)
    current_stats: VidIQCurrentStats = Field(alias="currentStats")
    growth: VidIQGrowth
    daily_stats: list[VidIQDailyStat] = Field(default_factory=list, alias="dailyStats")


# ---------------------------------------------------------------------------
# YouTube response schemas
# ---------------------------------------------------------------------------


class YouTubeSearchResult(BaseModel):
    video_id: str
    title: str = ""
    channel_title: str | None = None
    published_at: str | None = None
    description: str = ""


class YouTubeVideoDetail(BaseModel):
    video_id: str
    title: str = ""
    description: str = ""
    channel_id: str | None = None
    channel_title: str | None = None
    published_at: str | None = None
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    duration: str | None = None
    tags: list[str] = Field(default_factory=list)


class YouTubeOwnVideo(BaseModel):
    video_id: str
    title: str = ""
    status: str = ""
    published_at: str | None = None


class YouTubeAnalytics(BaseModel):
    rows: list[list[str | int | float | None]] = Field(default_factory=list)
    column_headers: list[dict[str, str]] = Field(default_factory=list)


class YouTubeTopVideo(BaseModel):
    video_id: str
    title: str = ""
    views: int = 0
    estimated_minutes_watched: float = 0.0
    likes: int = 0


class YouTubeChannelInfo(BaseModel):
    channel_id: str
    title: str = ""
    description: str = ""
    subscriber_count: int | None = None
    view_count: int | None = None
    video_count: int | None = None
    published_at: datetime | None = None
