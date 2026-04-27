import { createServer as createHttpServer, IncomingMessage, ServerResponse } from 'node:http';
import { randomUUID } from 'node:crypto';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { VideoService } from './services/video.js';
import { TranscriptService } from './services/transcript.js';
import { PlaylistService } from './services/playlist.js';
import { ChannelService } from './services/channel.js';
import { AnalyticsService } from './services/analytics.js';
import { ReportingService } from './services/reporting.js';
import { StudioService } from './services/studio.js';
import {
    hasOAuthCredentials,
    isAuthenticated,
    authenticate,
    hasMonetaryScope,
    getGrantedScopes,
    reauthenticate,
} from './auth/oauth-client.js';
import {
    VideoParams,
    SearchParams,
    TranscriptParams,
    ChannelParams,
    ChannelsParams,
    ChannelSearchParams,
    ChannelVideosParams,
    CreatorDiscoveryParams,
    PlaylistParams,
    PlaylistItemsParams,
    ListChannelPlaylistsParams,
    VideoAnalyticsParams,
    ChannelAnalyticsParams,
    TopVideosParams,
    ListOwnVideosParams,
    UpdateVideoParams,
    ListCommentsParams,
    ListChannelCommentsParams,
    AddCommentParams,
    ReplyToCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    ModerateCommentParams,
    RetentionCurveParams,
    TrafficSourcesParams,
    TrafficSourceDetailParams,
    CardPerformanceParams,
    DemographicsParams,
    DeviceAndPlaybackParams,
    AnalyticsQueryParams,
    RevenueParams,
    ReachByVideoParams,
    EnsureReportingJobParams,
    ReauthenticateParams,
} from './types.js';

function safeSerialize(value: unknown, maxLength = 4000) {
    try {
        const serialized = JSON.stringify(value);
        if (!serialized) {
            return String(value);
        }

        return serialized.length > maxLength
            ? `${serialized.slice(0, maxLength)}... [truncated ${serialized.length - maxLength} chars]`
            : serialized;
    } catch (error) {
        return `[unserializable: ${error instanceof Error ? error.message : String(error)}]`;
    }
}

function summarizeResult(result: unknown) {
    if (Array.isArray(result)) {
        return `array(length=${result.length})`;
    }

    if (result && typeof result === 'object') {
        const record = result as Record<string, unknown>;
        const keys = Object.keys(record);

        if (Array.isArray(record.transcript)) {
            return `object(keys=${keys.join(',')}; transcript=${record.transcript.length})`;
        }

        if (Array.isArray(record.timestampedTranscript)) {
            return `object(keys=${keys.join(',')}; timestampedTranscript=${record.timestampedTranscript.length})`;
        }

        return `object(keys=${keys.join(',')})`;
    }

    return `${typeof result}(${String(result)})`;
}

function createMcpServer() {
    const server = new Server(
        {
            name: 'zubeid-youtube-mcp-server',
            version: '1.0.0',
        },
        {
            capabilities: {
                tools: {},
            },
        }
    );

    const videoService = new VideoService();
    const transcriptService = new TranscriptService();
    const playlistService = new PlaylistService();
    const channelService = new ChannelService();
    const analyticsService = new AnalyticsService();
    const reportingService = new ReportingService();
    const studioService = new StudioService();

    server.setRequestHandler(ListToolsRequestSchema, async () => {
        console.error('[MCP] list_tools requested');
        return {
            tools: [
                {
                    name: 'videos_getVideo',
                    description: 'Get detailed information about a YouTube video',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: {
                                type: 'string',
                                description: 'The YouTube video ID',
                            },
                            parts: {
                                type: 'array',
                                description: 'Parts of the video to retrieve',
                                items: {
                                    type: 'string',
                                },
                            },
                        },
                        required: ['videoId'],
                    },
                },
                {
                    name: 'videos_searchVideos',
                    description: 'Search for videos on YouTube',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            query: {
                                type: 'string',
                                description: 'Search query',
                            },
                            maxResults: {
                                type: 'number',
                                description: 'Maximum number of results to return',
                            },
                            order: {
                                type: 'string',
                                description: 'Sort order for results, such as relevance or date',
                            },
                            publishedAfter: {
                                type: 'string',
                                description: 'Only include videos published after this ISO 8601 date',
                            },
                            publishedBefore: {
                                type: 'string',
                                description: 'Only include videos published before this ISO 8601 date',
                            },
                            channelId: {
                                type: 'string',
                                description: 'Restrict results to a specific channel ID',
                            },
                            videoDuration: {
                                type: 'string',
                                description: 'Filter by duration: "short" (< 4 min), "medium" (4-20 min), "long" (> 20 min), or "any" (default)',
                            },
                            uniqueChannels: {
                                type: 'boolean',
                                description: 'Return only one matched video per unique channel',
                            },
                            channelMinSubscribers: {
                                type: 'number',
                                description: 'Minimum subscriber count for the matched video channel',
                            },
                            channelMaxSubscribers: {
                                type: 'number',
                                description: 'Maximum subscriber count for the matched video channel',
                            },
                            channelLastUploadAfter: {
                                type: 'string',
                                description: 'Only include videos whose channel latest upload is after this ISO 8601 date',
                            },
                            channelLastUploadBefore: {
                                type: 'string',
                                description: 'Only include videos whose channel latest upload is before this ISO 8601 date',
                            },
                            creatorOnly: {
                                type: 'boolean',
                                description: 'Only include channels heuristically classified as creators',
                            },
                            sortBy: {
                                type: 'string',
                                description: 'Optional ranking mode such as relevance, indie_priority, subscribers_asc, subscribers_desc, or recent_activity',
                            },
                        },
                        required: ['query'],
                    },
                },
                {
                    name: 'transcripts_getTranscript',
                    description: 'Get the transcript of a YouTube video',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: {
                                type: 'string',
                                description: 'The YouTube video ID',
                            },
                            language: {
                                type: 'string',
                                description: 'Language code for the transcript',
                            },
                        },
                        required: ['videoId'],
                    },
                },
                {
                    name: 'channels_getChannel',
                    description: 'Get information about a YouTube channel',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            channelId: {
                                type: 'string',
                                description: 'The YouTube channel ID',
                            },
                        },
                        required: ['channelId'],
                    },
                },
                {
                    name: 'channels_getChannels',
                    description: 'Get information about multiple YouTube channels',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            channelIds: {
                                type: 'array',
                                description: 'A list of YouTube channel IDs',
                                items: {
                                    type: 'string',
                                },
                            },
                            parts: {
                                type: 'array',
                                description: 'Parts of the channel resource to retrieve',
                                items: {
                                    type: 'string',
                                },
                            },
                            includeLatestUpload: {
                                type: 'boolean',
                                description: 'Whether to include the latestVideoPublishedAt enrichment field',
                            },
                        },
                        required: ['channelIds'],
                    },
                },
                {
                    name: 'channels_searchChannels',
                    description: 'Search for YouTube channels by handle, name, or query',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            query: {
                                type: 'string',
                                description: 'Channel search query or handle',
                            },
                            maxResults: {
                                type: 'number',
                                description: 'Maximum number of results to return',
                            },
                            order: {
                                type: 'string',
                                description: 'Sort order for results, such as relevance',
                            },
                            channelType: {
                                type: 'string',
                                description: 'Restrict to channel type such as any or show',
                            },
                            minSubscribers: {
                                type: 'number',
                                description: 'Minimum subscriber count for returned channels',
                            },
                            maxSubscribers: {
                                type: 'number',
                                description: 'Maximum subscriber count for returned channels',
                            },
                            lastUploadAfter: {
                                type: 'string',
                                description: 'Only include channels whose latest upload is after this ISO 8601 date',
                            },
                            lastUploadBefore: {
                                type: 'string',
                                description: 'Only include channels whose latest upload is before this ISO 8601 date',
                            },
                            creatorOnly: {
                                type: 'boolean',
                                description: 'Only include channels heuristically classified as creators',
                            },
                            sortBy: {
                                type: 'string',
                                description: 'Optional ranking mode such as relevance, indie_priority, subscribers_asc, subscribers_desc, or recent_activity',
                            },
                        },
                        required: ['query'],
                    },
                },
                {
                    name: 'channels_findCreators',
                    description: 'Find creator channels from video mentions with subscriber band and recent activity filters in one call',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            query: {
                                type: 'string',
                                description: 'Search query such as a game name or topic mention',
                            },
                            maxResults: {
                                type: 'number',
                                description: 'Maximum number of video matches to scan before channel enrichment',
                            },
                            order: {
                                type: 'string',
                                description: 'Search ordering such as relevance or date',
                            },
                            videoPublishedAfter: {
                                type: 'string',
                                description: 'Only include matched videos published after this ISO 8601 date',
                            },
                            videoPublishedBefore: {
                                type: 'string',
                                description: 'Only include matched videos published before this ISO 8601 date',
                            },
                            channelMinSubscribers: {
                                type: 'number',
                                description: 'Minimum subscriber count for returned creator channels',
                            },
                            channelMaxSubscribers: {
                                type: 'number',
                                description: 'Maximum subscriber count for returned creator channels',
                            },
                            channelLastUploadAfter: {
                                type: 'string',
                                description: 'Only include channels whose latest upload is after this ISO 8601 date',
                            },
                            channelLastUploadBefore: {
                                type: 'string',
                                description: 'Only include channels whose latest upload is before this ISO 8601 date',
                            },
                            creatorOnly: {
                                type: 'boolean',
                                description: 'Only include channels heuristically classified as creators',
                            },
                            sortBy: {
                                type: 'string',
                                description: 'Optional ranking mode such as relevance, indie_priority, subscribers_asc, subscribers_desc, or recent_activity',
                            },
                            sampleVideosPerChannel: {
                                type: 'number',
                                description: 'How many matched video samples to include per returned channel',
                            },
                        },
                        required: ['query'],
                    },
                },
                {
                    name: 'channels_listVideos',
                    description: 'Get videos from a specific channel',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            channelId: {
                                type: 'string',
                                description: 'The YouTube channel ID',
                            },
                            maxResults: {
                                type: 'number',
                                description: 'Maximum number of results to return',
                            },
                        },
                        required: ['channelId'],
                    },
                },
                {
                    name: 'playlists_getPlaylist',
                    description: 'Get information about a YouTube playlist',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            playlistId: {
                                type: 'string',
                                description: 'The YouTube playlist ID',
                            },
                        },
                        required: ['playlistId'],
                    },
                },
                {
                    name: 'playlists_getPlaylistItems',
                    description: 'Get videos in a YouTube playlist',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            playlistId: {
                                type: 'string',
                                description: 'The YouTube playlist ID',
                            },
                            maxResults: {
                                type: 'number',
                                description: 'Maximum number of results to return',
                            },
                        },
                        required: ['playlistId'],
                    },
                },

                {
                    name: 'playlists_listByChannel',
                    description: 'List all playlists of a YouTube channel',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            channelId: { type: 'string', description: 'The YouTube channel ID' },
                            maxResults: { type: 'number', description: 'Maximum number of playlists to return (default 50)' },
                            pageToken: { type: 'string', description: 'Page token for pagination' },
                        },
                        required: ['channelId'],
                    },
                },

                // --- OAuth 2.0 tools ---

                {
                    name: 'auth_status',
                    description: 'Check OAuth 2.0 authentication status. Shows whether credentials are configured and whether the user is authenticated.',
                    inputSchema: { type: 'object', properties: {} },
                },
                {
                    name: 'auth_authenticate',
                    description: 'Start the OAuth 2.0 authentication flow. Opens the browser for Google authorization. Required before using analytics, studio, or comment tools.',
                    inputSchema: { type: 'object', properties: {} },
                },
                {
                    name: 'analytics_getVideoAnalytics',
                    description: 'Get analytics for a specific video on your channel (views, watch time, retention, likes, shares, etc). Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'The YouTube video ID' },
                            startDate: { type: 'string', description: 'Start date in YYYY-MM-DD format (defaults to 30 days ago)' },
                            endDate: { type: 'string', description: 'End date in YYYY-MM-DD format (defaults to today)' },
                            metrics: { type: 'string', description: 'Comma-separated metrics (defaults to views,estimatedMinutesWatched,averageViewDuration,likes,dislikes,comments,shares,subscribersGained,subscribersLost,averageViewPercentage)' },
                        },
                        required: ['videoId'],
                    },
                },
                {
                    name: 'analytics_getChannelAnalytics',
                    description: 'Get analytics for your entire channel (views, watch time, subscribers gained/lost, etc). Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            startDate: { type: 'string', description: 'Start date in YYYY-MM-DD format (defaults to 30 days ago)' },
                            endDate: { type: 'string', description: 'End date in YYYY-MM-DD format (defaults to today)' },
                            metrics: { type: 'string', description: 'Comma-separated metrics (defaults to views,estimatedMinutesWatched,averageViewDuration,likes,dislikes,comments,shares,subscribersGained,subscribersLost)' },
                            dimensions: { type: 'string', description: 'Comma-separated dimensions: day, month, country, video, etc (defaults to day)' },
                        },
                    },
                },
                {
                    name: 'analytics_getTopVideos',
                    description: 'Get your top-performing videos ranked by a metric. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            startDate: { type: 'string', description: 'Start date in YYYY-MM-DD format (defaults to 30 days ago)' },
                            endDate: { type: 'string', description: 'End date in YYYY-MM-DD format (defaults to today)' },
                            maxResults: { type: 'number', description: 'Number of videos to return (default 10)' },
                            sortBy: { type: 'string', description: 'Metric to sort by: views, estimatedMinutesWatched, likes, comments, shares (default views)' },
                        },
                    },
                },
                {
                    name: 'analytics_getRetentionCurve',
                    description: 'Get the audience retention curve (audienceWatchRatio + relativeRetentionPerformance) for a video, with granular start/stop counts. Adjusts the date window automatically when audienceType is incompatible with pre-2013-09-25 dates. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'The YouTube video ID' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (defaults to 30 days ago, auto-adjusted to >=2013-09-25 when audienceType is set)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (defaults to today)' },
                            audienceType: { type: 'string', enum: ['ORGANIC', 'AD_INSTREAM', 'AD_INDISPLAY', 'ALL'], description: 'Filter by audience type. ALL removes the filter. Default ORGANIC.' },
                            onIncompatibleDate: { type: 'string', enum: ['adjust', 'remove', 'error'], description: 'Behaviour when startDate < 2013-09-25 and audienceType is set. Default adjust.' },
                            includeGranularStats: { type: 'boolean', description: 'Include startedWatching/stoppedWatching/totalSegmentImpressions metrics. Default true.' },
                            videoDurationSeconds: { type: 'number', description: 'If provided, injects timestampSeconds and timestampLabel columns into the curve.' },
                        },
                        required: ['videoId'],
                    },
                },
                {
                    name: 'analytics_getTrafficSources',
                    description: 'Aggregate traffic-source breakdown (insightTrafficSourceType) for a video, list of videos, or the whole channel. Returns shares of views and watch time. Validates videos × days <= 50000. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'Single video ID. Mutually exclusive with videoIds.' },
                            videoIds: { type: 'array', items: { type: 'string' }, description: 'Up to 500 video IDs. Mutually exclusive with videoId.' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                            groupByDay: { type: 'boolean', description: 'Add day as the first dimension. Default false.' },
                            country: { type: 'string', description: 'ISO-3166-1 alpha-2 country filter (e.g. BR, US).' },
                            creatorContentType: { type: 'string', enum: ['LIVE_STREAM', 'SHORTS', 'VIDEO_ON_DEMAND', 'STORY'], description: 'Filter by content type (data from 2019-01-01).' },
                            includeEngagedViews: { type: 'boolean', description: 'Include engagedViews metric. Default true.' },
                        },
                    },
                },
                {
                    name: 'analytics_getTrafficSourceDetail',
                    description: 'Drill into a specific traffic source for one video — e.g. exact YouTube search keywords, related videos, or external URLs. maxResults capped at 25 by the API. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'The YouTube video ID' },
                            trafficSourceType: { type: 'string', enum: ['ADVERTISING', 'CAMPAIGN_CARD', 'END_SCREEN', 'EXT_URL', 'HASHTAGS', 'NOTIFICATION', 'RELATED_VIDEO', 'SOUND_PAGE', 'SUBSCRIBER', 'YT_CHANNEL', 'YT_OTHER_PAGE', 'YT_SEARCH', 'VIDEO_REMIXES'], description: 'Source type to drill into.' },
                            maxResults: { type: 'number', description: 'Max details to return (default 25, capped at 25).' },
                            sortBy: { type: 'string', enum: ['views', 'estimatedMinutesWatched'], description: 'Sort metric (default views).' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                        },
                        required: ['videoId', 'trafficSourceType'],
                    },
                },
                {
                    name: 'analytics_getCardPerformance',
                    description: 'Get info-card impressions, clicks and CTR for a video, multiple videos, or the channel. Optionally grouped by day and/or video. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'Restrict to one video. Omit to aggregate across the channel.' },
                            groupByVideo: { type: 'boolean', description: 'When videoId is omitted, break down by video. Default false.' },
                            groupByDay: { type: 'boolean', description: 'Break down by day. Default false.' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                        },
                    },
                },
                {
                    name: 'analytics_getDemographics',
                    description: 'Demographics (ageGroup × gender) with viewerPercentage normalised per subscribed bucket. When subscribedStatus=BOTH (default) returns three pre-normalised result sets (subscribed, unsubscribed, overall) so percentages always sum to 100% within their bucket. creatorContentType data starts 2019-01-01. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                            country: { type: 'string', description: 'ISO-3166-1 alpha-2 country filter.' },
                            videoId: { type: 'string', description: 'Restrict to a specific video.' },
                            subscribedStatus: { type: 'string', enum: ['SUBSCRIBED', 'UNSUBSCRIBED', 'BOTH'], description: 'BOTH returns 3 normalised sets. Default BOTH.' },
                        },
                    },
                },
                {
                    name: 'analytics_getDeviceAndPlayback',
                    description: 'Breakdown by deviceType, operatingSystem, deviceAndOs, playbackLocation, subscribedStatus, creatorContentType or youtubeProduct. Auto-adjusts the date window for dimension date floors. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            groupBy: { type: 'string', enum: ['deviceType', 'operatingSystem', 'deviceAndOs', 'playbackLocation', 'subscribedStatus', 'creatorContentType', 'youtubeProduct'], description: 'Dimension(s) to group by.' },
                            videoId: { type: 'string', description: 'Restrict to one video.' },
                            country: { type: 'string', description: 'ISO-3166-1 alpha-2 country filter.' },
                            creatorContentType: { type: 'string', enum: ['LIVE_STREAM', 'SHORTS', 'VIDEO_ON_DEMAND', 'STORY'], description: 'Filter by content type.' },
                            metrics: { type: 'string', description: 'Comma-separated metrics override.' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                        },
                        required: ['groupBy'],
                    },
                },
                {
                    name: 'analytics_query',
                    description: 'Power-user escape hatch: run an arbitrary YouTube Analytics query against your channel. Validates date floors and enforces the monetary scope automatically when revenue metrics are requested. Requires OAuth.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            metrics: { type: 'string', description: 'Comma-separated list of metrics.' },
                            dimensions: { type: 'string', description: 'Comma-separated list of dimensions.' },
                            filters: { type: 'string', description: 'Filter string (e.g. video==VID;country==BR).' },
                            sort: { type: 'string', description: 'Sort spec (prefix with - for desc).' },
                            maxResults: { type: 'number', description: 'Cap on result rows.' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                            currency: { type: 'string', description: 'Three-letter currency code for revenue metrics.' },
                        },
                        required: ['metrics'],
                    },
                },
                {
                    name: 'analytics_getRevenue',
                    description: 'Revenue metrics (estimatedRevenue, monetizedPlaybacks, cpm, etc) for the channel or specific videos. Requires the yt-analytics-monetary.readonly OAuth scope (run auth_reauthenticate first if it is missing).',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            scope: { type: 'string', enum: ['channel', 'video'], description: 'channel-wide or per-video aggregation.' },
                            videoId: { type: 'string', description: 'Required when scope=video and only one video is targeted.' },
                            videoIds: { type: 'array', items: { type: 'string' }, description: 'Multiple video IDs (mutually exclusive with videoId).' },
                            groupBy: { type: 'string', enum: ['day', 'month', 'country', 'video', 'adType'], description: 'Optional dimension for grouping.' },
                            country: { type: 'string', description: 'ISO-3166-1 alpha-2 country filter.' },
                            currency: { type: 'string', description: 'Currency code (default USD).' },
                            metrics: { type: 'string', description: 'Comma-separated revenue metrics override.' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                        },
                        required: ['scope'],
                    },
                },
                {
                    name: 'reporting_getReachByVideo',
                    description: 'Pulls thumbnail impressions and click-through rate via the YouTube Reporting API (channel_reach_basic_a1). The Reporting API lags ~24-48h; the first call may auto-create the job and report nothing until the next pipeline run.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'Restrict to a single video.' },
                            videoIds: { type: 'array', items: { type: 'string' }, description: 'Multiple video IDs (mutually exclusive with videoId).' },
                            startDate: { type: 'string', description: 'YYYY-MM-DD (default 30 days ago)' },
                            endDate: { type: 'string', description: 'YYYY-MM-DD (default today)' },
                            aggregateBy: { type: 'string', enum: ['video', 'videoAndDay', 'day'], description: 'How to aggregate the parsed CSV rows (default video).' },
                            autoCreateJob: { type: 'boolean', description: 'Auto-create the reporting job when missing (default true).' },
                        },
                    },
                },
                {
                    name: 'reporting_ensureJob',
                    description: 'Administrative helper: ensure a YouTube Reporting API job exists for the given reportTypeId. Returns the job and a flag indicating whether it was just created (data lags 24-48h after creation).',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            reportTypeId: { type: 'string', description: 'Reporting API report type, e.g. channel_reach_basic_a1.' },
                            name: { type: 'string', description: 'Optional display name for the job.' },
                        },
                        required: ['reportTypeId'],
                    },
                },
                {
                    name: 'reporting_listJobs',
                    description: 'List all Reporting API jobs (including system-managed ones) for the authenticated channel.',
                    inputSchema: { type: 'object', properties: {} },
                },
                {
                    name: 'auth_reauthenticate',
                    description: 'Clear stored OAuth tokens and run the consent flow again, so newly added scopes (such as yt-analytics-monetary.readonly) are granted. Pass confirm=true to actually proceed.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            confirm: { type: 'boolean', description: 'Must be true to clear tokens and start the flow.' },
                        },
                        required: ['confirm'],
                    },
                },
                {
                    name: 'studio_getOwnChannel',
                    description: 'Get detailed information about your own YouTube channel. Requires OAuth authentication.',
                    inputSchema: { type: 'object', properties: {} },
                },
                {
                    name: 'studio_listOwnVideos',
                    description: 'List your own videos including private and unlisted ones, with full statistics. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            maxResults: { type: 'number', description: 'Maximum number of videos to return (default 20)' },
                            status: { type: 'string', description: 'Filter by privacy status: public, private, or unlisted' },
                            pageToken: { type: 'string', description: 'Page token for pagination' },
                        },
                    },
                },
                {
                    name: 'studio_updateVideo',
                    description: 'Update a video on your channel (title, description, tags, privacy, etc). Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'The YouTube video ID to update' },
                            title: { type: 'string', description: 'New video title' },
                            description: { type: 'string', description: 'New video description' },
                            tags: { type: 'array', items: { type: 'string' }, description: 'New video tags' },
                            categoryId: { type: 'string', description: 'YouTube category ID' },
                            privacyStatus: { type: 'string', description: 'Privacy status: public, private, or unlisted' },
                            defaultLanguage: { type: 'string', description: 'Default language code (e.g. pt, en)' },
                        },
                        required: ['videoId'],
                    },
                },
                {
                    name: 'studio_listOwnPlaylists',
                    description: 'List all playlists on your own channel (including private ones). Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            maxResults: { type: 'number', description: 'Maximum number of playlists to return (default 50)' },
                            pageToken: { type: 'string', description: 'Page token for pagination' },
                        },
                    },
                },
                {
                    name: 'studio_listComments',
                    description: 'List comments on a video (with replies). Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'The YouTube video ID' },
                            maxResults: { type: 'number', description: 'Maximum number of comment threads (default 20)' },
                            order: { type: 'string', description: 'Sort order: relevance or time (default relevance)' },
                        },
                        required: ['videoId'],
                    },
                },
                {
                    name: 'studio_listChannelComments',
                    description: 'List all comments across your entire channel (all videos). Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            channelId: { type: 'string', description: 'The YouTube channel ID' },
                            maxResults: { type: 'number', description: 'Maximum number of comment threads (default 20)' },
                            order: { type: 'string', description: 'Sort order: relevance or time (default relevance)' },
                        },
                        required: ['channelId'],
                    },
                },
                {
                    name: 'studio_addComment',
                    description: 'Add a new top-level comment on a video. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            videoId: { type: 'string', description: 'The YouTube video ID to comment on' },
                            text: { type: 'string', description: 'Comment text' },
                        },
                        required: ['videoId', 'text'],
                    },
                },
                {
                    name: 'studio_replyToComment',
                    description: 'Reply to a comment on one of your videos. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            commentId: { type: 'string', description: 'The comment ID to reply to' },
                            text: { type: 'string', description: 'Reply text' },
                        },
                        required: ['commentId', 'text'],
                    },
                },
                {
                    name: 'studio_updateComment',
                    description: 'Edit the text of an existing comment or reply you authored. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            commentId: { type: 'string', description: 'The comment ID to update' },
                            text: { type: 'string', description: 'New comment text' },
                        },
                        required: ['commentId', 'text'],
                    },
                },
                {
                    name: 'studio_deleteComment',
                    description: 'Delete a comment or reply. Only the comment author or channel owner can delete. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            commentId: { type: 'string', description: 'The comment ID to delete' },
                        },
                        required: ['commentId'],
                    },
                },
                {
                    name: 'studio_moderateComment',
                    description: 'Set the moderation status of a comment (publish, reject, or hold for review). Channel owner only. Requires OAuth authentication.',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            commentId: { type: 'string', description: 'The comment ID to moderate' },
                            moderationStatus: { type: 'string', description: 'Status: published, rejected, or heldForReview' },
                            banAuthor: { type: 'boolean', description: 'If rejecting, also ban the author from commenting (default false)' },
                        },
                        required: ['commentId', 'moderationStatus'],
                    },
                },
            ],
        };
    });

    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;
        const startedAt = Date.now();

        console.error(`[MCP] tool.start name=${name} args=${safeSerialize(args)}`);

        try {
            let result: unknown;

            switch (name) {
                case 'videos_getVideo':
                    result = await videoService.getVideo(args as unknown as VideoParams);
                    break;
                case 'videos_searchVideos':
                    result = await videoService.searchVideos(args as unknown as SearchParams);
                    break;
                case 'transcripts_getTranscript':
                    result = await transcriptService.getTranscript(args as unknown as TranscriptParams);
                    break;
                case 'channels_getChannel':
                    result = await channelService.getChannel(args as unknown as ChannelParams);
                    break;
                case 'channels_getChannels':
                    result = await channelService.getChannels(args as unknown as ChannelsParams);
                    break;
                case 'channels_searchChannels':
                    result = await channelService.searchChannels(args as unknown as ChannelSearchParams);
                    break;
                case 'channels_findCreators':
                    result = await channelService.findCreators(args as unknown as CreatorDiscoveryParams);
                    break;
                case 'channels_listVideos':
                    result = await channelService.listVideos(args as unknown as ChannelVideosParams);
                    break;
                case 'playlists_getPlaylist':
                    result = await playlistService.getPlaylist(args as unknown as PlaylistParams);
                    break;
                case 'playlists_getPlaylistItems':
                    result = await playlistService.getPlaylistItems(args as unknown as PlaylistItemsParams);
                    break;
                case 'playlists_listByChannel':
                    result = await playlistService.listByChannel(args as unknown as ListChannelPlaylistsParams);
                    break;

                // OAuth tools
                case 'auth_status':
                    result = {
                        credentialsConfigured: hasOAuthCredentials(),
                        authenticated: isAuthenticated(),
                        hasMonetaryScope: hasMonetaryScope(),
                        grantedScopes: getGrantedScopes(),
                    };
                    break;
                case 'auth_authenticate':
                    result = await authenticate();
                    break;
                case 'auth_reauthenticate': {
                    const { confirm } = args as unknown as ReauthenticateParams;
                    if (!confirm) {
                        result = {
                            confirmed: false,
                            warning: 'Pass confirm=true to clear current tokens and re-run the OAuth flow.',
                            currentScopes: getGrantedScopes(),
                        };
                    } else {
                        result = await reauthenticate();
                    }
                    break;
                }
                case 'analytics_getVideoAnalytics':
                    result = await analyticsService.getVideoAnalytics(args as unknown as VideoAnalyticsParams);
                    break;
                case 'analytics_getChannelAnalytics':
                    result = await analyticsService.getChannelAnalytics(args as unknown as ChannelAnalyticsParams);
                    break;
                case 'analytics_getTopVideos':
                    result = await analyticsService.getTopVideos(args as unknown as TopVideosParams);
                    break;
                case 'analytics_getRetentionCurve':
                    result = await analyticsService.getRetentionCurve(args as unknown as RetentionCurveParams);
                    break;
                case 'analytics_getTrafficSources':
                    result = await analyticsService.getTrafficSources(args as unknown as TrafficSourcesParams);
                    break;
                case 'analytics_getTrafficSourceDetail':
                    result = await analyticsService.getTrafficSourceDetail(args as unknown as TrafficSourceDetailParams);
                    break;
                case 'analytics_getCardPerformance':
                    result = await analyticsService.getCardPerformance(args as unknown as CardPerformanceParams);
                    break;
                case 'analytics_getDemographics':
                    result = await analyticsService.getDemographics(args as unknown as DemographicsParams);
                    break;
                case 'analytics_getDeviceAndPlayback':
                    result = await analyticsService.getDeviceAndPlayback(args as unknown as DeviceAndPlaybackParams);
                    break;
                case 'analytics_query':
                    result = await analyticsService.query(args as unknown as AnalyticsQueryParams);
                    break;
                case 'analytics_getRevenue':
                    result = await analyticsService.getRevenue(args as unknown as RevenueParams);
                    break;
                case 'reporting_getReachByVideo':
                    result = await reportingService.getReachByVideo(args as unknown as ReachByVideoParams);
                    break;
                case 'reporting_ensureJob':
                    result = await reportingService.ensureJobTool(args as unknown as EnsureReportingJobParams);
                    break;
                case 'reporting_listJobs':
                    result = await reportingService.listJobs();
                    break;
                case 'studio_getOwnChannel':
                    result = await studioService.getOwnChannel();
                    break;
                case 'studio_listOwnVideos':
                    result = await studioService.listOwnVideos(args as unknown as ListOwnVideosParams);
                    break;
                case 'studio_updateVideo':
                    result = await studioService.updateVideo(args as unknown as UpdateVideoParams);
                    break;
                case 'studio_listOwnPlaylists':
                    result = await studioService.listOwnPlaylists(args as unknown as { maxResults?: number; pageToken?: string });
                    break;
                case 'studio_listComments':
                    result = await studioService.listComments(args as unknown as ListCommentsParams);
                    break;
                case 'studio_listChannelComments':
                    result = await studioService.listChannelComments(args as unknown as ListChannelCommentsParams);
                    break;
                case 'studio_addComment':
                    result = await studioService.addComment(args as unknown as AddCommentParams);
                    break;
                case 'studio_replyToComment':
                    result = await studioService.replyToComment(args as unknown as ReplyToCommentParams);
                    break;
                case 'studio_updateComment':
                    result = await studioService.updateComment(args as unknown as UpdateCommentParams);
                    break;
                case 'studio_deleteComment':
                    result = await studioService.deleteComment(args as unknown as DeleteCommentParams);
                    break;
                case 'studio_moderateComment':
                    result = await studioService.moderateComment(args as unknown as ModerateCommentParams);
                    break;

                default:
                    throw new Error(`Unknown tool: ${name}`);
            }

            console.error(
                `[MCP] tool.success name=${name} durationMs=${Date.now() - startedAt} summary=${summarizeResult(result)}`
            );

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(result, null, 2)
                }]
            };
        } catch (error) {
            console.error(
                `[MCP] tool.error name=${name} durationMs=${Date.now() - startedAt} error=${error instanceof Error ? error.stack || error.message : String(error)}`
            );
            return {
                content: [{
                    type: 'text',
                    text: `Error: ${error instanceof Error ? error.message : String(error)}`
                }],
                isError: true
            };
        }
    });

    return server;
}

async function readJsonBody(req: IncomingMessage): Promise<unknown> {
    const chunks: Buffer[] = [];

    for await (const chunk of req) {
        chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    }

    if (chunks.length === 0) {
        return undefined;
    }

    const raw = Buffer.concat(chunks).toString('utf8').trim();

    if (!raw) {
        return undefined;
    }

    return JSON.parse(raw);
}

function writeJson(res: ServerResponse, statusCode: number, payload: unknown) {
    res.statusCode = statusCode;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(payload));
}

async function startStdioServer() {
    const server = createMcpServer();
    const transport = new StdioServerTransport();

    await server.connect(transport);
    
    // Log the server info
    console.error(`YouTube MCP Server v1.0.0 started successfully`);
    console.error(`Server will validate YouTube API key when tools are called`);
    
    return server;
}

async function startHttpMcpServer() {
    const host = process.env.MCP_HOST || '0.0.0.0';
    const port = Number(process.env.MCP_PORT || '8088');
    const stateless = process.env.MCP_STATELESS !== 'false';

    const httpServer = createHttpServer(async (req, res) => {
        const requestStartedAt = Date.now();
        const origin = `http://${req.headers.host || `${host}:${port}`}`;
        const url = new URL(req.url || '/', origin);

        res.on('finish', () => {
            console.log(
                `[HTTP] ${req.method} ${url.pathname} status=${res.statusCode} durationMs=${Date.now() - requestStartedAt}`
            );
        });

        if (url.pathname === '/ready') {
            writeJson(res, 200, {
                status: 'ok',
                transport: 'http',
                stateless,
            });
            return;
        }

        if (url.pathname !== '/mcp') {
            writeJson(res, 404, {
                error: 'Not found',
            });
            return;
        }

        let parsedBody: unknown;

        if (req.method === 'POST') {
            try {
                parsedBody = await readJsonBody(req);
                console.log(`[HTTP] request.body method=${req.method} path=${url.pathname} body=${safeSerialize(parsedBody)}`);
            } catch (error) {
                writeJson(res, 400, {
                    jsonrpc: '2.0',
                    error: {
                        code: -32700,
                        message: `Invalid JSON body: ${error instanceof Error ? error.message : String(error)}`,
                    },
                    id: null,
                });
                return;
            }
        }

        const server = createMcpServer();
        const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: stateless ? undefined : () => randomUUID(),
            enableJsonResponse: stateless,
        });

        res.on('close', () => {
            transport.close().catch(() => undefined);
            server.close().catch(() => undefined);
        });

        try {
            await server.connect(transport);
            await transport.handleRequest(req, res, parsedBody);
        } catch (error) {
            console.error('Error handling HTTP MCP request:', error);

            if (!res.headersSent) {
                writeJson(res, 500, {
                    jsonrpc: '2.0',
                    error: {
                        code: -32603,
                        message: error instanceof Error ? error.message : 'Internal server error',
                    },
                    id: null,
                });
            }
        }
    });

    await new Promise<void>((resolve, reject) => {
        httpServer.once('error', reject);
        httpServer.listen(port, host, () => {
            httpServer.off('error', reject);
            resolve();
        });
    });

    console.log('YouTube MCP Server v1.0.0 started successfully over HTTP');
    console.log(`Listening on http://${host}:${port}/mcp`);
    console.log(`Readiness endpoint available at http://${host}:${port}/ready`);
    console.log('Server will validate YouTube API key when tools are called');

    return httpServer;
}

export async function startMcpServer() {
    const transport = (process.env.MCP_TRANSPORT || 'stdio').toLowerCase();

    if (transport === 'http') {
        return startHttpMcpServer();
    }

    return startStdioServer();
}
