import { google, youtubereporting_v1 } from 'googleapis';
import { getAuthenticatedClient } from '../auth/oauth-client.js';
import {
  ReachByVideoParams,
  EnsureReportingJobParams,
  ReachAggregateBy,
} from '../types.js';
import { defaultDateRange } from './analytics-validation.js';

/**
 * YouTube Reporting API (bulk) service.
 *
 * The Reporting API publishes daily CSV "report jobs". Unlike Targeted
 * Queries, these reports are exhaustive but lag by ~24h. We use them as the
 * authoritative source for `videoThumbnailImpressions` /
 * `videoThumbnailImpressionsClickRate`, which Targeted Queries does not
 * reliably support today.
 *
 * Reference report types used:
 * - channel_basic_a2          (daily channel stats)
 * - channel_reach_basic_a1    (impressions, CTR by video × day)
 * - channel_reach_combined_a1 (impressions + traffic source segmentation)
 *
 * Verified against:
 * https://developers.google.com/youtube/reporting/v1/reports
 * https://developers.google.com/youtube/reporting/v1/reference/rest
 */

export const REACH_REPORT_TYPES = {
  reachBasic: 'channel_reach_basic_a1',
  reachCombined: 'channel_reach_combined_a1',
} as const;

export type ReachReportTypeId =
  (typeof REACH_REPORT_TYPES)[keyof typeof REACH_REPORT_TYPES];

export class ReportingService {
  private async client(): Promise<youtubereporting_v1.Youtubereporting> {
    const auth = await getAuthenticatedClient();
    return google.youtubereporting({ version: 'v1', auth });
  }

  // --- Report types -----------------------------------------------------

  async listReportTypes(): Promise<youtubereporting_v1.Schema$ReportType[]> {
    const c = await this.client();
    const res = await c.reportTypes.list({ pageSize: 200 });
    return res.data.reportTypes || [];
  }

  // --- Jobs -------------------------------------------------------------

  async listJobs(): Promise<youtubereporting_v1.Schema$Job[]> {
    const c = await this.client();
    const res = await c.jobs.list({ includeSystemManaged: true, pageSize: 200 });
    return res.data.jobs || [];
  }

  async findJob(reportTypeId: string): Promise<youtubereporting_v1.Schema$Job | null> {
    const jobs = await this.listJobs();
    return jobs.find(j => j.reportTypeId === reportTypeId) || null;
  }

  async ensureJob(
    reportTypeId: string,
    name?: string,
  ): Promise<{ job: youtubereporting_v1.Schema$Job; created: boolean }> {
    const existing = await this.findJob(reportTypeId);
    if (existing) return { job: existing, created: false };

    const c = await this.client();
    const res = await c.jobs.create({
      requestBody: {
        reportTypeId,
        name: name || `mcp-${reportTypeId}`,
      },
    });
    return { job: res.data, created: true };
  }

  // --- Reports ----------------------------------------------------------

  async listReportsForJob(
    jobId: string,
    opts: { startTimeAtOrAfter?: string; startTimeBefore?: string } = {},
  ): Promise<youtubereporting_v1.Schema$Report[]> {
    const c = await this.client();
    const reports: youtubereporting_v1.Schema$Report[] = [];
    let pageToken: string | undefined;
    do {
      const res = await c.jobs.reports.list({
        jobId,
        pageSize: 100,
        pageToken,
        startTimeAtOrAfter: opts.startTimeAtOrAfter,
        startTimeBefore: opts.startTimeBefore,
      });
      if (res.data.reports) reports.push(...res.data.reports);
      pageToken = res.data.nextPageToken || undefined;
    } while (pageToken);
    return reports;
  }

  async downloadCsv(downloadUrl: string): Promise<string> {
    const auth = await getAuthenticatedClient();
    const accessToken = (await auth.getAccessToken()).token;
    if (!accessToken) {
      throw new Error('Missing access token for Reporting download.');
    }

    const res = await fetch(downloadUrl, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!res.ok) {
      throw new Error(
        `Reporting download failed: ${res.status} ${res.statusText}`,
      );
    }
    return await res.text();
  }

  parseCsv(csv: string): Record<string, string>[] {
    const lines = csv.replace(/\r\n/g, '\n').split('\n').filter(l => l.length > 0);
    if (lines.length === 0) return [];

    const header = splitCsvLine(lines[0]);
    return lines.slice(1).map(line => {
      const cols = splitCsvLine(line);
      const obj: Record<string, string> = {};
      header.forEach((h, i) => {
        obj[h] = cols[i] ?? '';
      });
      return obj;
    });
  }

  /**
   * Convenience: enqueue/find a job, fetch all daily reports in window, and
   * concatenate parsed CSV rows. Designed for ad-hoc analytical reads.
   */
  async fetchReportRows(
    reportTypeId: ReachReportTypeId | string,
    opts: {
      startDate: string;
      endDate: string;
      autoCreateJob?: boolean;
    },
  ): Promise<{
    rows: Record<string, string>[];
    job: youtubereporting_v1.Schema$Job;
    reportCount: number;
    hasData: boolean;
    info: string[];
  }> {
    const info: string[] = [];

    let job = await this.findJob(reportTypeId);
    if (!job) {
      if (!opts.autoCreateJob) {
        throw new Error(
          `No reporting job found for reportTypeId="${reportTypeId}". ` +
          `Re-run with autoCreateJob=true or call reporting_ensureJob first. ` +
          `Note: data will only start populating ~24-48h after job creation.`,
        );
      }
      const created = await this.ensureJob(reportTypeId);
      job = created.job;
      info.push(
        `Reporting job auto-created (id=${job.id}). ` +
        `Reports usually appear ~24-48h later; previous days may be empty.`,
      );
    }

    if (!job.id) {
      throw new Error('Reporting job is missing id.');
    }

    const reports = await this.listReportsForJob(job.id, {
      startTimeAtOrAfter: `${opts.startDate}T00:00:00Z`,
      startTimeBefore: `${opts.endDate}T23:59:59Z`,
    });

    if (reports.length === 0) {
      info.push(
        `No reports yet for window ${opts.startDate}..${opts.endDate}. ` +
        `Either the window is too recent (Reporting lag) or no data is published.`,
      );
      return { rows: [], job, reportCount: 0, hasData: false, info };
    }

    const allRows: Record<string, string>[] = [];
    for (const report of reports) {
      if (!report.downloadUrl) continue;
      const csv = await this.downloadCsv(report.downloadUrl);
      const parsed = this.parseCsv(csv);
      allRows.push(...parsed);
    }

    return {
      rows: allRows,
      job,
      reportCount: reports.length,
      hasData: allRows.length > 0,
      info,
    };
  }

  // --- Tool 9: getReachByVideo -----------------------------------------

  async getReachByVideo(params: ReachByVideoParams) {
    const { startDate, endDate } = defaultDateRange(params.startDate, params.endDate);
    const aggregateBy: ReachAggregateBy = params.aggregateBy || 'video';
    const autoCreateJob = params.autoCreateJob !== false;

    if (params.videoId && params.videoIds && params.videoIds.length > 0) {
      throw new Error('Provide either videoId or videoIds, not both.');
    }

    const wantedIds = new Set<string>(
      params.videoId
        ? [params.videoId]
        : params.videoIds || [],
    );

    const fetched = await this.fetchReportRows(REACH_REPORT_TYPES.reachBasic, {
      startDate,
      endDate,
      autoCreateJob,
    });

    if (!fetched.hasData) {
      return {
        period: { startDate, endDate },
        scope: wantedIds.size === 0 ? 'channel' : Array.from(wantedIds),
        aggregateBy,
        reach: [],
        totals: {},
        meta: {
          apiSource: 'reporting-api',
          jobId: fetched.job.id,
          reportCount: fetched.reportCount,
          hasData: false,
          info: fetched.info,
        },
      };
    }

    const rows = wantedIds.size === 0
      ? fetched.rows
      : fetched.rows.filter(r => wantedIds.has(r['video_id']));

    const aggregated = aggregateReachRows(rows, aggregateBy);
    const totals = aggregateReachRows(rows, 'totals')[0] || {};

    return {
      period: { startDate, endDate },
      scope: wantedIds.size === 0 ? 'channel' : Array.from(wantedIds),
      aggregateBy,
      reach: aggregated,
      totals,
      meta: {
        apiSource: 'reporting-api',
        jobId: fetched.job.id,
        reportCount: fetched.reportCount,
        hasData: true,
        info: fetched.info,
      },
    };
  }

  // --- Tool 10: ensureJob ----------------------------------------------

  async ensureJobTool(params: EnsureReportingJobParams) {
    const { job, created } = await this.ensureJob(params.reportTypeId, params.name);
    return {
      created,
      job,
      info: created
        ? 'Job created. The first reports usually arrive 24-48h later.'
        : 'Job already existed; using it for subsequent calls.',
    };
  }
}

// --- helpers ------------------------------------------------------------

function splitCsvLine(line: string): string[] {
  const out: string[] = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"' && line[i + 1] === '"') {
        cur += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        cur += ch;
      }
      continue;
    }
    if (ch === '"') {
      inQuotes = true;
      continue;
    }
    if (ch === ',') {
      out.push(cur);
      cur = '';
      continue;
    }
    cur += ch;
  }
  out.push(cur);
  return out;
}

function aggregateReachRows(
  rows: Record<string, string>[],
  by: ReachAggregateBy | 'totals',
): Record<string, string | number>[] {
  if (rows.length === 0) return [];

  const numericFields = [
    'views',
    'video_thumbnail_impressions',
    'video_thumbnail_impressions_click_rate',
    'unique_viewers',
    'subscribers_gained',
    'subscribers_lost',
  ];

  const buckets = new Map<string, Record<string, number | string>>();
  for (const row of rows) {
    const key =
      by === 'video'
        ? row['video_id'] || 'unknown'
        : by === 'day'
        ? row['date'] || 'unknown'
        : by === 'videoAndDay'
        ? `${row['video_id']}|${row['date']}`
        : 'TOTAL';

    const cur = buckets.get(key) || {};
    if (by === 'video') cur['video_id'] = row['video_id'];
    if (by === 'day') cur['date'] = row['date'];
    if (by === 'videoAndDay') {
      cur['video_id'] = row['video_id'];
      cur['date'] = row['date'];
    }

    for (const field of numericFields) {
      if (row[field] === undefined) continue;
      const value = Number(row[field]);
      if (Number.isFinite(value)) {
        cur[field] = ((cur[field] as number) || 0) + value;
      }
    }

    buckets.set(key, cur);
  }

  const aggregated = Array.from(buckets.values());

  for (const row of aggregated) {
    const impressions = Number(row['video_thumbnail_impressions'] || 0);
    const ctr = Number(row['video_thumbnail_impressions_click_rate'] || 0);
    if (impressions > 0 && ctr > 0) {
      row['video_thumbnail_impressions_click_rate'] = ctr / Math.max(rows.length, 1);
    }
  }

  return aggregated;
}
