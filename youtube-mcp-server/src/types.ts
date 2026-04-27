/**
 * Video details parameters
 */
export interface VideoParams {
  videoId: string;
  parts?: string[];
}

/**
 * Search videos parameters
 */
export interface SearchParams {
  query: string;
  maxResults?: number;
  order?: string;
  publishedAfter?: string;
  publishedBefore?: string;
  channelId?: string;
  videoDuration?: 'any' | 'short' | 'medium' | 'long';
  uniqueChannels?: boolean;
  channelMinSubscribers?: number;
  channelMaxSubscribers?: number;
  channelLastUploadAfter?: string;
  channelLastUploadBefore?: string;
  creatorOnly?: boolean;
  sortBy?: 'relevance' | 'date' | 'subscribers_asc' | 'subscribers_desc' | 'indie_priority' | 'recent_activity';
}

/**
 * Trending videos parameters
 */
export interface TrendingParams {
  regionCode?: string;
  maxResults?: number;
  videoCategoryId?: string;
}

/**
 * Related videos parameters
 */
export interface RelatedVideosParams {
  videoId: string;
  maxResults?: number;
}

/**
 * Transcript parameters
 */
export interface TranscriptParams {
  videoId: string;
  language?: string;
}

/**
 * Search transcript parameters
 */
export interface SearchTranscriptParams {
  videoId: string;
  query: string;
  language?: string;
}

/**
 * Channel parameters
 */
export interface ChannelParams {
  channelId: string;
}

/**
 * Channel lookup parameters
 */
export interface ChannelsParams {
  channelIds: string[];
  parts?: string[];
  includeLatestUpload?: boolean;
}

/**
 * Channel search parameters
 */
export interface ChannelSearchParams {
  query: string;
  maxResults?: number;
  order?: string;
  channelType?: string;
  minSubscribers?: number;
  maxSubscribers?: number;
  lastUploadAfter?: string;
  lastUploadBefore?: string;
  creatorOnly?: boolean;
  sortBy?: 'relevance' | 'subscribers_asc' | 'subscribers_desc' | 'indie_priority' | 'recent_activity';
}

/**
 * Creator discovery parameters
 */
export interface CreatorDiscoveryParams {
  query: string;
  maxResults?: number;
  order?: string;
  videoPublishedAfter?: string;
  videoPublishedBefore?: string;
  channelMinSubscribers?: number;
  channelMaxSubscribers?: number;
  channelLastUploadAfter?: string;
  channelLastUploadBefore?: string;
  creatorOnly?: boolean;
  sortBy?: 'relevance' | 'subscribers_asc' | 'subscribers_desc' | 'indie_priority' | 'recent_activity';
  sampleVideosPerChannel?: number;
}

/**
 * Channel videos parameters
 */
export interface ChannelVideosParams {
  channelId: string;
  maxResults?: number;
}

/**
 * Playlist parameters
 */
export interface PlaylistParams {
  playlistId: string;
}

/**
 * Playlist items parameters
 */
export interface PlaylistItemsParams {
  playlistId: string;
  maxResults?: number;
}

export interface ListChannelPlaylistsParams {
  channelId: string;
  maxResults?: number;
  pageToken?: string;
}

// --- OAuth-authenticated tool params ---

export interface VideoAnalyticsParams {
  videoId: string;
  startDate?: string;
  endDate?: string;
  metrics?: string;
}

export interface ChannelAnalyticsParams {
  startDate?: string;
  endDate?: string;
  metrics?: string;
  dimensions?: string;
}

export interface TopVideosParams {
  startDate?: string;
  endDate?: string;
  maxResults?: number;
  sortBy?: string;
}

// --- Analytics v2: new tools (Targeted Queries) ---

export type AudienceType = 'ORGANIC' | 'AD_INSTREAM' | 'AD_INDISPLAY' | 'ALL';
export type DateValidationPolicy = 'adjust' | 'remove' | 'error';
export type CreatorContentType = 'LIVE_STREAM' | 'SHORTS' | 'VIDEO_ON_DEMAND' | 'STORY';

export interface RetentionCurveParams {
  videoId: string;
  startDate?: string;
  endDate?: string;
  audienceType?: AudienceType;
  onIncompatibleDate?: DateValidationPolicy;
  includeGranularStats?: boolean;
  videoDurationSeconds?: number;
}

export interface TrafficSourcesParams {
  videoId?: string;
  videoIds?: string[];
  startDate?: string;
  endDate?: string;
  groupByDay?: boolean;
  country?: string;
  creatorContentType?: CreatorContentType;
  includeEngagedViews?: boolean;
}

export type TrafficSourceTypeForDetail =
  | 'ADVERTISING'
  | 'CAMPAIGN_CARD'
  | 'END_SCREEN'
  | 'EXT_URL'
  | 'HASHTAGS'
  | 'NOTIFICATION'
  | 'RELATED_VIDEO'
  | 'SOUND_PAGE'
  | 'SUBSCRIBER'
  | 'YT_CHANNEL'
  | 'YT_OTHER_PAGE'
  | 'YT_SEARCH'
  | 'VIDEO_REMIXES';

export interface TrafficSourceDetailParams {
  videoId: string;
  trafficSourceType: TrafficSourceTypeForDetail;
  maxResults?: number;
  sortBy?: 'views' | 'estimatedMinutesWatched';
  startDate?: string;
  endDate?: string;
}

export interface CardPerformanceParams {
  videoId?: string;
  groupByVideo?: boolean;
  groupByDay?: boolean;
  startDate?: string;
  endDate?: string;
}

export interface DemographicsParams {
  startDate?: string;
  endDate?: string;
  country?: string;
  subscribedStatus?: 'SUBSCRIBED' | 'UNSUBSCRIBED' | 'BOTH';
  videoId?: string;
}

export type DeviceAndPlaybackGroupBy =
  | 'deviceType'
  | 'operatingSystem'
  | 'deviceAndOs'
  | 'playbackLocation'
  | 'subscribedStatus'
  | 'creatorContentType'
  | 'youtubeProduct';

export interface DeviceAndPlaybackParams {
  groupBy: DeviceAndPlaybackGroupBy;
  videoId?: string;
  country?: string;
  creatorContentType?: CreatorContentType;
  metrics?: string;
  startDate?: string;
  endDate?: string;
}

export interface AnalyticsQueryParams {
  metrics: string;
  dimensions?: string;
  filters?: string;
  sort?: string;
  maxResults?: number;
  startDate?: string;
  endDate?: string;
  currency?: string;
}

// --- Analytics v2: revenue (monetary scope) ---

export type RevenueGroupBy = 'day' | 'month' | 'country' | 'video' | 'adType';

export interface RevenueParams {
  scope: 'channel' | 'video';
  videoId?: string;
  videoIds?: string[];
  groupBy?: RevenueGroupBy;
  country?: string;
  currency?: string;
  metrics?: string;
  startDate?: string;
  endDate?: string;
}

// --- Reporting API (bulk) ---

export type ReachAggregateBy = 'video' | 'videoAndDay' | 'day';

export interface ReachByVideoParams {
  videoId?: string;
  videoIds?: string[];
  startDate?: string;
  endDate?: string;
  aggregateBy?: ReachAggregateBy;
  autoCreateJob?: boolean;
}

export interface EnsureReportingJobParams {
  reportTypeId: string;
  name?: string;
}

export interface ReauthenticateParams {
  confirm: boolean;
}

export interface ListOwnVideosParams {
  maxResults?: number;
  status?: string;
  pageToken?: string;
}

export interface UpdateVideoParams {
  videoId: string;
  title?: string;
  description?: string;
  tags?: string[];
  categoryId?: string;
  privacyStatus?: string;
  defaultLanguage?: string;
}

export interface ListCommentsParams {
  videoId: string;
  maxResults?: number;
  order?: string;
}

export interface ListChannelCommentsParams {
  channelId: string;
  maxResults?: number;
  order?: string;
}

export interface AddCommentParams {
  videoId: string;
  text: string;
}

export interface ReplyToCommentParams {
  commentId: string;
  text: string;
}

export interface UpdateCommentParams {
  commentId: string;
  text: string;
}

export interface DeleteCommentParams {
  commentId: string;
}

export interface ModerateCommentParams {
  commentId: string;
  moderationStatus: 'published' | 'rejected' | 'heldForReview';
  banAuthor?: boolean;
}
