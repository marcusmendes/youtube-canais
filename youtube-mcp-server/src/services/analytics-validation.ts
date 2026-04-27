/**
 * Date-window validation for YouTube Analytics API queries.
 *
 * Several dimensions, filters and metrics only have data starting from a
 * specific date. Querying earlier dates either returns empty rows silently or
 * fails with a 400. This utility centralises the cutoffs and adjusts the
 * request transparently while emitting warnings.
 *
 * References (verified against official docs, 2026):
 * - https://developers.google.com/youtube/analytics/dimensions
 * - https://developers.google.com/youtube/analytics/metrics
 */

export const FIELD_DATE_FLOORS: Record<string, string> = {
  // audienceType filter only supports dates >= 2013-09-25.
  // https://developers.google.com/youtube/analytics/dimensions#audienceType
  'audienceType': '2013-09-25',

  // creatorContentType dimension data available from 2019-01-01.
  // https://developers.google.com/youtube/analytics/dimensions
  'creatorContentType': '2019-01-01',

  // liveOrOnDemand dimension data available from 2014-04-01.
  'liveOrOnDemand': '2014-04-01',

  // youtubeProduct dimension data available from 2015-07-18.
  'youtubeProduct': '2015-07-18',

  // city dimension data available from 2022-01-01.
  'city': '2022-01-01',

  // videosAddedToPlaylists / videosRemovedFromPlaylists from 2014-10-01.
  'videosAddedToPlaylists': '2014-10-01',
  'videosRemovedFromPlaylists': '2014-10-01',
};

export type DateValidationPolicy = 'adjust' | 'remove' | 'error';

export interface DateValidationResult {
  adjustedStartDate: string;
  removedFields: string[];
  warnings: string[];
}

function isBefore(a: string, b: string): boolean {
  return a < b;
}

function maxDate(a: string, b: string): string {
  return a > b ? a : b;
}

/**
 * Validates that the requested startDate is compatible with the date floors
 * of every field in `fieldsUsed`. Adjusts the start date forward (or removes
 * fields, or throws) according to `policy`.
 */
export function validateDateWindow(
  startDate: string,
  fieldsUsed: string[],
  policy: DateValidationPolicy = 'adjust'
): DateValidationResult {
  const warnings: string[] = [];
  const removedFields: string[] = [];
  let adjustedStartDate = startDate;

  for (const field of fieldsUsed) {
    const floor = FIELD_DATE_FLOORS[field];
    if (!floor) continue;

    if (isBefore(startDate, floor)) {
      if (policy === 'error') {
        throw new Error(
          `Field "${field}" only has data from ${floor} onwards, ` +
          `but startDate=${startDate} was requested.`
        );
      }

      if (policy === 'remove') {
        removedFields.push(field);
        warnings.push(
          `Field "${field}" removed from query because data is only available from ${floor}.`
        );
        continue;
      }

      adjustedStartDate = maxDate(adjustedStartDate, floor);
      warnings.push(
        `startDate adjusted from ${startDate} to ${floor} because field "${field}" requires it.`
      );
    }
  }

  return { adjustedStartDate, removedFields, warnings };
}

const FIELD_PATTERN = /([a-zA-Z]+)/g;

/**
 * Extracts dimension/filter/metric names from a comma- or semicolon-separated
 * Analytics API parameter string. Used to feed `validateDateWindow`.
 */
export function extractFieldNames(...parameterStrings: Array<string | undefined | null>): string[] {
  const names = new Set<string>();
  for (const raw of parameterStrings) {
    if (!raw) continue;
    const matches = raw.match(FIELD_PATTERN) || [];
    for (const m of matches) {
      names.add(m);
    }
  }
  return Array.from(names);
}

const REVENUE_METRICS = new Set([
  'estimatedRevenue',
  'estimatedAdRevenue',
  'estimatedRedPartnerRevenue',
  'grossRevenue',
  'cpm',
  'playbackBasedCpm',
  'monetizedPlaybacks',
  'adImpressions',
]);

/**
 * Returns true if any of the supplied metric names requires the
 * yt-analytics-monetary.readonly OAuth scope.
 */
export function metricsRequireMonetaryScope(metricsCsv: string | undefined): boolean {
  if (!metricsCsv) return false;
  return metricsCsv
    .split(',')
    .map(m => m.trim())
    .some(m => REVENUE_METRICS.has(m));
}

/**
 * Returns the default end date (today) and start date (offsetDays ago) in
 * YYYY-MM-DD when not provided.
 */
export function defaultDateRange(
  startDate?: string,
  endDate?: string,
  offsetDays = 30
): { startDate: string; endDate: string } {
  const now = new Date();
  const past = new Date(now.getTime() - offsetDays * 24 * 60 * 60 * 1000);
  return {
    startDate: startDate || past.toISOString().split('T')[0],
    endDate: endDate || now.toISOString().split('T')[0],
  };
}

/**
 * Validates that #videos × #days <= 50,000 for traffic-source style queries.
 */
export function validateVideoDayProduct(
  videoCount: number,
  startDate: string,
  endDate: string,
  limit = 50_000
): void {
  const start = new Date(startDate).getTime();
  const end = new Date(endDate).getTime();
  const days = Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1);
  const product = videoCount * days;
  if (product > limit) {
    throw new Error(
      `Query exceeds API limit: ${videoCount} videos × ${days} days = ${product} > ${limit}. ` +
      `Reduce the date range or number of videos.`
    );
  }
}
