import { google } from 'googleapis';
import { getAuthenticatedClient, requireMonetaryScope } from '../auth/oauth-client.js';
import {
  VideoAnalyticsParams,
  ChannelAnalyticsParams,
  TopVideosParams,
  RetentionCurveParams,
  TrafficSourcesParams,
  TrafficSourceDetailParams,
  CardPerformanceParams,
  DemographicsParams,
  DeviceAndPlaybackParams,
  AnalyticsQueryParams,
  RevenueParams,
} from '../types.js';
import {
  defaultDateRange,
  validateDateWindow,
  validateVideoDayProduct,
  metricsRequireMonetaryScope,
  extractFieldNames,
} from './analytics-validation.js';
import {
  rowsToObjects,
  normalizeByBucket,
  withSharePercentage,
  addTimestampsFromRatio,
  ColumnHeader,
  AnalyticsRow,
} from './analytics-postprocess.js';

interface QueryEnvelope {
  columnHeaders: ColumnHeader[];
  rows: AnalyticsRow[];
}

export class AnalyticsService {
  private async getAnalyticsClient() {
    const auth = await getAuthenticatedClient();
    return google.youtubeAnalytics({ version: 'v2', auth });
  }

  private async getOwnChannelId(): Promise<string> {
    const auth = await getAuthenticatedClient();
    const youtube = google.youtube({ version: 'v3', auth });
    const response = await youtube.channels.list({ part: ['id'], mine: true });

    const channelId = response.data.items?.[0]?.id;
    if (!channelId) {
      throw new Error('Could not determine your channel ID. Make sure you have a YouTube channel.');
    }
    return channelId;
  }

  // --- Existing tools (unchanged contract) -------------------------------

  async getVideoAnalytics({
    videoId,
    startDate: rawStart,
    endDate: rawEnd,
    metrics: rawMetrics,
  }: VideoAnalyticsParams) {
    const analytics = await this.getAnalyticsClient();
    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(rawStart, rawEnd);
    const metrics = rawMetrics ||
      'views,estimatedMinutesWatched,averageViewDuration,likes,dislikes,comments,shares,subscribersGained,subscribersLost,averageViewPercentage';

    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      filters: `video==${videoId}`,
      dimensions: 'day',
      sort: '-day',
    });

    return {
      videoId,
      period: { startDate, endDate },
      columnHeaders: response.data.columnHeaders,
      rows: response.data.rows,
    };
  }

  async getChannelAnalytics({
    startDate: rawStart,
    endDate: rawEnd,
    metrics: rawMetrics,
    dimensions: rawDimensions,
  }: ChannelAnalyticsParams) {
    const analytics = await this.getAnalyticsClient();
    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(rawStart, rawEnd);
    const metrics = rawMetrics ||
      'views,estimatedMinutesWatched,averageViewDuration,likes,dislikes,comments,shares,subscribersGained,subscribersLost';
    const dimensions = rawDimensions || 'day';

    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      dimensions,
      sort: `-${dimensions.split(',')[0]}`,
    });

    return {
      channelId,
      period: { startDate, endDate },
      columnHeaders: response.data.columnHeaders,
      rows: response.data.rows,
    };
  }

  async getTopVideos({
    startDate: rawStart,
    endDate: rawEnd,
    maxResults = 10,
    sortBy = 'views',
  }: TopVideosParams) {
    const analytics = await this.getAnalyticsClient();
    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(rawStart, rawEnd);

    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics:
        'views,estimatedMinutesWatched,averageViewDuration,likes,comments,shares,subscribersGained,averageViewPercentage',
      dimensions: 'video',
      sort: `-${sortBy}`,
      maxResults,
    });

    return {
      channelId,
      period: { startDate, endDate },
      columnHeaders: response.data.columnHeaders,
      rows: response.data.rows,
    };
  }

  // --- Tool 1: getRetentionCurve ----------------------------------------

  async getRetentionCurve(params: RetentionCurveParams) {
    const {
      videoId,
      audienceType = 'ORGANIC',
      onIncompatibleDate = 'adjust',
      includeGranularStats = true,
      videoDurationSeconds,
    } = params;

    const channelId = await this.getOwnChannelId();
    const range = defaultDateRange(params.startDate, params.endDate);

    let appliedAudienceType: string | null = audienceType === 'ALL' ? null : audienceType;
    const fieldsUsed = appliedAudienceType ? ['audienceType'] : [];

    let validation = validateDateWindow(range.startDate, fieldsUsed, onIncompatibleDate);

    if (onIncompatibleDate === 'remove' && validation.removedFields.includes('audienceType')) {
      appliedAudienceType = null;
    }

    const startDate = validation.adjustedStartDate;
    const { endDate } = range;

    const baseMetrics = ['audienceWatchRatio', 'relativeRetentionPerformance'];
    const granular = ['startedWatching', 'stoppedWatching', 'totalSegmentImpressions'];
    const metrics = (includeGranularStats ? [...baseMetrics, ...granular] : baseMetrics).join(',');

    const filters = appliedAudienceType
      ? `video==${videoId};audienceType==${appliedAudienceType}`
      : `video==${videoId}`;

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      filters,
      dimensions: 'elapsedVideoTimeRatio',
      sort: 'elapsedVideoTimeRatio',
    });

    const headers = (response.data.columnHeaders || []) as ColumnHeader[];
    let rows = (response.data.rows || []) as AnalyticsRow[];

    let injectedColumns: string[] = [];
    if (videoDurationSeconds && videoDurationSeconds > 0) {
      const ts = addTimestampsFromRatio(rows, headers, videoDurationSeconds);
      rows = ts.rows;
      injectedColumns = ts.injectedColumns;
    }

    return {
      videoId,
      period: { startDate, endDate },
      appliedFilters: { audienceType: appliedAudienceType },
      curve: rowsToObjects(rows, [
        ...headers,
        ...injectedColumns.map(name => ({ name } as ColumnHeader)),
      ]),
      meta: {
        apiSource: 'targeted-query',
        columnHeaders: [...headers, ...injectedColumns.map(n => ({ name: n }))],
        rowCount: rows.length,
        injectedColumns,
      },
      _warnings: validation.warnings,
    };
  }

  // --- Tool 2: getTrafficSources ----------------------------------------

  async getTrafficSources(params: TrafficSourcesParams) {
    const {
      videoId,
      videoIds,
      groupByDay = false,
      country,
      creatorContentType,
      includeEngagedViews = true,
    } = params;

    if (videoId && videoIds && videoIds.length > 0) {
      throw new Error('Provide either videoId or videoIds, not both.');
    }

    const ids: string[] | null = videoId ? [videoId] : videoIds && videoIds.length > 0 ? videoIds : null;
    if (ids && ids.length > 500) {
      throw new Error('videoIds is limited to 500 IDs per the Analytics API.');
    }

    const channelId = await this.getOwnChannelId();
    const range = defaultDateRange(params.startDate, params.endDate);

    const fieldsUsed = extractFieldNames(creatorContentType ? 'creatorContentType' : '');
    const validation = validateDateWindow(range.startDate, fieldsUsed, 'adjust');
    const startDate = validation.adjustedStartDate;
    const endDate = range.endDate;

    if (ids) {
      validateVideoDayProduct(ids.length, startDate, endDate);
    }

    const filterParts: string[] = [];
    if (ids) filterParts.push(`video==${ids.join(',')}`);
    if (country) filterParts.push(`country==${country}`);
    if (creatorContentType) filterParts.push(`creatorContentType==${creatorContentType}`);
    const filters = filterParts.length > 0 ? filterParts.join(';') : undefined;

    const dimensions = groupByDay ? 'day,insightTrafficSourceType' : 'insightTrafficSourceType';
    const metricsList = ['views', 'estimatedMinutesWatched', 'averageViewDuration'];
    if (includeEngagedViews) metricsList.unshift('engagedViews');
    const metrics = metricsList.join(',');

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      dimensions,
      filters,
      sort: '-views',
    });

    const headers = (response.data.columnHeaders || []) as ColumnHeader[];
    let rows = (response.data.rows || []) as AnalyticsRow[];

    const sharing = withSharePercentage(rows, headers, 'views');
    rows = sharing.rows;
    const allHeaders: ColumnHeader[] = [
      ...headers,
      ...(sharing.injectedColumn ? [{ name: sharing.injectedColumn } as ColumnHeader] : []),
    ];

    return {
      scope: ids ? { videoIds: ids } : { videoIds: 'channel' as const },
      period: { startDate, endDate },
      appliedFilters: { country, creatorContentType },
      trafficSources: rowsToObjects(rows, allHeaders),
      totals: {
        views: sharing.total,
      },
      meta: {
        apiSource: 'targeted-query',
        columnHeaders: allHeaders,
        rowCount: rows.length,
      },
      _warnings: validation.warnings,
    };
  }

  // --- Tool 3: getTrafficSourceDetail -----------------------------------

  async getTrafficSourceDetail(params: TrafficSourceDetailParams) {
    const {
      videoId,
      trafficSourceType,
      maxResults = 25,
      sortBy = 'views',
    } = params;

    if (maxResults > 25) {
      throw new Error('maxResults capped at 25 per Analytics API constraint for detail reports.');
    }

    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(params.startDate, params.endDate);

    const filters = `video==${videoId};insightTrafficSourceType==${trafficSourceType}`;

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics: 'views,estimatedMinutesWatched,averageViewDuration',
      dimensions: 'insightTrafficSourceDetail',
      filters,
      sort: `-${sortBy}`,
      maxResults,
    });

    const headers = (response.data.columnHeaders || []) as ColumnHeader[];
    const rows = (response.data.rows || []) as AnalyticsRow[];

    return {
      videoId,
      trafficSourceType,
      period: { startDate, endDate },
      details: rowsToObjects(rows, headers),
      meta: {
        apiSource: 'targeted-query',
        columnHeaders: headers,
        rowCount: rows.length,
      },
    };
  }

  // --- Tool 4: getCardPerformance ---------------------------------------

  async getCardPerformance(params: CardPerformanceParams) {
    const { videoId, groupByVideo = false, groupByDay = false } = params;
    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(params.startDate, params.endDate);

    const dimensionParts: string[] = [];
    if (groupByDay) dimensionParts.push('day');
    if (!videoId && groupByVideo) dimensionParts.push('video');
    const dimensions = dimensionParts.length > 0 ? dimensionParts.join(',') : undefined;

    const filters = videoId ? `video==${videoId}` : undefined;

    const metrics = [
      'cardImpressions',
      'cardClicks',
      'cardClickRate',
      'cardTeaserImpressions',
      'cardTeaserClicks',
      'cardTeaserClickRate',
    ].join(',');

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      dimensions,
      filters,
    });

    const headers = (response.data.columnHeaders || []) as ColumnHeader[];
    const rows = (response.data.rows || []) as AnalyticsRow[];

    return {
      scope: videoId ? { videoId } : { videoId: 'channel' as const },
      period: { startDate, endDate },
      cardStats: rowsToObjects(rows, headers),
      meta: {
        apiSource: 'targeted-query',
        columnHeaders: headers,
        rowCount: rows.length,
      },
    };
  }

  // --- Tool 5: getDemographics ------------------------------------------

  private async runDemographicsQuery(opts: {
    channelId: string;
    startDate: string;
    endDate: string;
    country?: string;
    videoId?: string;
    subscribedStatus?: 'SUBSCRIBED' | 'UNSUBSCRIBED';
  }): Promise<QueryEnvelope> {
    const filterParts: string[] = [];
    if (opts.videoId) filterParts.push(`video==${opts.videoId}`);
    if (opts.country) filterParts.push(`country==${opts.country}`);
    if (opts.subscribedStatus) filterParts.push(`subscribedStatus==${opts.subscribedStatus}`);
    const filters = filterParts.length > 0 ? filterParts.join(';') : undefined;

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${opts.channelId}`,
      startDate: opts.startDate,
      endDate: opts.endDate,
      metrics: 'viewerPercentage',
      dimensions: 'ageGroup,gender',
      filters,
      sort: 'gender,ageGroup',
    });

    return {
      columnHeaders: (response.data.columnHeaders || []) as ColumnHeader[],
      rows: (response.data.rows || []) as AnalyticsRow[],
    };
  }

  async getDemographics(params: DemographicsParams) {
    const { country, subscribedStatus = 'BOTH', videoId } = params;
    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(params.startDate, params.endDate);

    if (subscribedStatus === 'SUBSCRIBED' || subscribedStatus === 'UNSUBSCRIBED') {
      const env = await this.runDemographicsQuery({
        channelId,
        startDate,
        endDate,
        country,
        videoId,
        subscribedStatus,
      });
      return {
        period: { startDate, endDate },
        bucket: subscribedStatus,
        rows: rowsToObjects(env.rows, env.columnHeaders),
        meta: {
          apiSource: 'targeted-query',
          columnHeaders: env.columnHeaders,
          rowCount: env.rows.length,
          queries: 1,
        },
      };
    }

    const [subscribed, unsubscribed, overall] = await Promise.all([
      this.runDemographicsQuery({
        channelId,
        startDate,
        endDate,
        country,
        videoId,
        subscribedStatus: 'SUBSCRIBED',
      }),
      this.runDemographicsQuery({
        channelId,
        startDate,
        endDate,
        country,
        videoId,
        subscribedStatus: 'UNSUBSCRIBED',
      }),
      this.runDemographicsQuery({
        channelId,
        startDate,
        endDate,
        country,
        videoId,
      }),
    ]);

    const subSum = subscribed.rows.reduce((acc, r) => acc + Number(r[2] ?? 0), 0);
    const unsubSum = unsubscribed.rows.reduce((acc, r) => acc + Number(r[2] ?? 0), 0);
    const totalRaw = subSum + unsubSum;

    return {
      period: { startDate, endDate },
      subscribed: {
        rows: rowsToObjects(subscribed.rows, subscribed.columnHeaders),
        note: 'Percentages normalized within SUBSCRIBED bucket (sums to 100%)',
      },
      unsubscribed: {
        rows: rowsToObjects(unsubscribed.rows, unsubscribed.columnHeaders),
        note: 'Percentages normalized within UNSUBSCRIBED bucket (sums to 100%)',
      },
      overall: {
        rows: rowsToObjects(overall.rows, overall.columnHeaders),
        bucketSplit: totalRaw > 0
          ? {
            SUBSCRIBED: (subSum / totalRaw) * 100,
            UNSUBSCRIBED: (unsubSum / totalRaw) * 100,
          }
          : { SUBSCRIBED: 0, UNSUBSCRIBED: 0 },
        note: 'Aggregated demographics (no subscribedStatus split)',
      },
      meta: { apiSource: 'targeted-query', queries: 3 },
    };
  }

  // --- Tool 6: getDeviceAndPlayback -------------------------------------

  async getDeviceAndPlayback(params: DeviceAndPlaybackParams) {
    const { groupBy, videoId, country, creatorContentType, metrics: rawMetrics } = params;
    const channelId = await this.getOwnChannelId();
    const range = defaultDateRange(params.startDate, params.endDate);

    let dimensions: string;
    switch (groupBy) {
      case 'deviceAndOs':
        dimensions = 'deviceType,operatingSystem';
        break;
      case 'playbackLocation':
        dimensions = 'insightPlaybackLocationType';
        break;
      default:
        dimensions = groupBy;
    }

    const fieldsUsed = extractFieldNames(
      dimensions,
      creatorContentType ? 'creatorContentType' : '',
    );
    const validation = validateDateWindow(range.startDate, fieldsUsed, 'adjust');
    const startDate = validation.adjustedStartDate;
    const endDate = range.endDate;

    const filterParts: string[] = [];
    if (videoId) filterParts.push(`video==${videoId}`);
    if (country) filterParts.push(`country==${country}`);
    if (creatorContentType) filterParts.push(`creatorContentType==${creatorContentType}`);
    const filters = filterParts.length > 0 ? filterParts.join(';') : undefined;

    const metrics = rawMetrics ||
      'views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage';

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      dimensions,
      filters,
      sort: '-views',
    });

    const headers = (response.data.columnHeaders || []) as ColumnHeader[];
    let rows = (response.data.rows || []) as AnalyticsRow[];

    const sharing = withSharePercentage(rows, headers, 'views');
    rows = sharing.rows;
    const allHeaders: ColumnHeader[] = [
      ...headers,
      ...(sharing.injectedColumn ? [{ name: sharing.injectedColumn } as ColumnHeader] : []),
    ];

    return {
      groupBy,
      period: { startDate, endDate },
      appliedFilters: { videoId, country, creatorContentType },
      breakdown: rowsToObjects(rows, allHeaders),
      totals: { views: sharing.total },
      meta: {
        apiSource: 'targeted-query',
        columnHeaders: allHeaders,
        rowCount: rows.length,
      },
      _warnings: validation.warnings,
    };
  }

  // --- Tool 7: query (escape hatch) -------------------------------------

  async query(params: AnalyticsQueryParams) {
    const { metrics, dimensions, filters, sort, maxResults, currency } = params;

    if (metricsRequireMonetaryScope(metrics)) {
      requireMonetaryScope();
    }

    const channelId = await this.getOwnChannelId();
    const range = defaultDateRange(params.startDate, params.endDate);

    const fieldsUsed = extractFieldNames(dimensions, filters, metrics);
    const validation = validateDateWindow(range.startDate, fieldsUsed, 'adjust');
    const startDate = validation.adjustedStartDate;
    const endDate = range.endDate;

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      dimensions,
      filters,
      sort,
      maxResults,
      currency,
    });

    return {
      period: { startDate, endDate },
      query: { metrics, dimensions, filters, sort, maxResults, currency },
      columnHeaders: response.data.columnHeaders,
      rows: response.data.rows,
      _warnings: validation.warnings,
    };
  }

  // --- Tool 8: getRevenue (monetary scope) ------------------------------

  async getRevenue(params: RevenueParams) {
    requireMonetaryScope();

    const {
      scope,
      videoId,
      videoIds,
      groupBy,
      country,
      currency = 'USD',
      metrics: rawMetrics,
    } = params;

    if (scope === 'video' && !videoId && (!videoIds || videoIds.length === 0)) {
      throw new Error('scope=video requires videoId or videoIds.');
    }

    const channelId = await this.getOwnChannelId();
    const { startDate, endDate } = defaultDateRange(params.startDate, params.endDate);

    const ids = videoId ? [videoId] : videoIds && videoIds.length > 0 ? videoIds : null;
    if (scope === 'video' && ids) {
      validateVideoDayProduct(ids.length, startDate, endDate);
    }

    const metrics = rawMetrics ||
      'estimatedRevenue,estimatedAdRevenue,grossRevenue,cpm,playbackBasedCpm,monetizedPlaybacks,adImpressions';

    const filterParts: string[] = [];
    if (scope === 'video' && ids) filterParts.push(`video==${ids.join(',')}`);
    if (country) filterParts.push(`country==${country}`);
    const filters = filterParts.length > 0 ? filterParts.join(';') : undefined;

    const dimensions = groupBy;

    const analytics = await this.getAnalyticsClient();
    const response = await analytics.reports.query({
      ids: `channel==${channelId}`,
      startDate,
      endDate,
      metrics,
      dimensions,
      filters,
      sort: dimensions ? `-${metrics.split(',')[0]}` : undefined,
      currency,
    });

    const headers = (response.data.columnHeaders || []) as ColumnHeader[];
    const rows = (response.data.rows || []) as AnalyticsRow[];

    return {
      scope,
      period: { startDate, endDate },
      currency,
      appliedFilters: { country, videoIds: ids },
      groupBy: groupBy || 'aggregated',
      revenue: rowsToObjects(rows, headers),
      meta: {
        apiSource: 'targeted-query',
        columnHeaders: headers,
        rowCount: rows.length,
      },
    };
  }
}
