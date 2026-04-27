/**
 * Post-processors for YouTube Analytics API responses.
 *
 * These helpers transform the raw `reports.query` output (rows + columnHeaders)
 * into shapes that are easier for downstream consumers (LLMs, dashboards) to
 * interpret.
 */

export interface ColumnHeader {
  name?: string | null;
  columnType?: string | null;
  dataType?: string | null;
}

export type AnalyticsRow = Array<string | number | null>;

function indexOfColumn(headers: ColumnHeader[], name: string): number {
  return headers.findIndex(h => h?.name === name);
}

/**
 * Converts a row-based response (rows + columnHeaders) into an array of
 * objects keyed by column name. Faster to consume from JSON.
 */
export function rowsToObjects(
  rows: AnalyticsRow[] | null | undefined,
  headers: ColumnHeader[] | null | undefined
): Record<string, string | number | null>[] {
  if (!rows || !headers) return [];
  return rows.map(row => {
    const obj: Record<string, string | number | null> = {};
    headers.forEach((h, i) => {
      const key = h?.name || `col_${i}`;
      obj[key] = row[i] ?? null;
    });
    return obj;
  });
}

/**
 * Normalises a viewerPercentage (or any percentage-shaped) metric grouped by
 * a bucket dimension so each bucket sums to 100%. Returns the rebucketed rows
 * along with the bucket totals.
 *
 * Example: subscribedStatus + ageGroup + gender ⇒ percentages are computed
 * within each subscribedStatus bucket, not across all rows.
 */
export function normalizeByBucket(
  rows: AnalyticsRow[],
  headers: ColumnHeader[],
  bucketDimension: string,
  metricName = 'viewerPercentage'
): {
  rows: AnalyticsRow[];
  bucketTotals: Record<string, number>;
  injectedColumn: string;
} {
  const bucketIdx = indexOfColumn(headers, bucketDimension);
  const valueIdx = indexOfColumn(headers, metricName);

  if (bucketIdx === -1 || valueIdx === -1) {
    return { rows, bucketTotals: {}, injectedColumn: '' };
  }

  const bucketTotals: Record<string, number> = {};
  for (const row of rows) {
    const bucket = String(row[bucketIdx] ?? '');
    const value = Number(row[valueIdx] ?? 0);
    bucketTotals[bucket] = (bucketTotals[bucket] || 0) + value;
  }

  const injectedColumn = `${metricName}NormalizedByBucket`;
  const newRows: AnalyticsRow[] = rows.map(row => {
    const bucket = String(row[bucketIdx] ?? '');
    const value = Number(row[valueIdx] ?? 0);
    const total = bucketTotals[bucket] || 0;
    const normalized = total > 0 ? (value / total) * 100 : 0;
    return [...row, normalized];
  });

  return { rows: newRows, bucketTotals, injectedColumn };
}

/**
 * Sums one numeric column across all rows. Useful for computing
 * "totalViews" given a per-source breakdown.
 */
export function sumColumn(
  rows: AnalyticsRow[],
  headers: ColumnHeader[],
  columnName: string
): number {
  const idx = indexOfColumn(headers, columnName);
  if (idx === -1) return 0;
  return rows.reduce((acc, row) => acc + Number(row[idx] ?? 0), 0);
}

/**
 * Computes a per-row share percentage of a given metric over the column total.
 * Returns rows enriched with `${metricName}SharePercentage`.
 */
export function withSharePercentage(
  rows: AnalyticsRow[],
  headers: ColumnHeader[],
  metricName: string
): { rows: AnalyticsRow[]; injectedColumn: string; total: number } {
  const idx = indexOfColumn(headers, metricName);
  if (idx === -1) return { rows, injectedColumn: '', total: 0 };

  const total = rows.reduce((acc, row) => acc + Number(row[idx] ?? 0), 0);
  const injectedColumn = `${metricName}SharePercentage`;
  const newRows: AnalyticsRow[] = rows.map(row => {
    const value = Number(row[idx] ?? 0);
    const share = total > 0 ? (value / total) * 100 : 0;
    return [...row, share];
  });
  return { rows: newRows, injectedColumn, total };
}

/**
 * Adds a clock-style timestamp (mm:ss) to each row of an audience retention
 * curve given the elapsedVideoTimeRatio column and the total video duration.
 */
export function addTimestampsFromRatio(
  rows: AnalyticsRow[],
  headers: ColumnHeader[],
  videoDurationSeconds: number,
  ratioColumn = 'elapsedVideoTimeRatio'
): { rows: AnalyticsRow[]; injectedColumns: string[] } {
  const idx = indexOfColumn(headers, ratioColumn);
  if (idx === -1) return { rows, injectedColumns: [] };

  const injectedColumns = ['timestampSeconds', 'timestampLabel'];
  const newRows: AnalyticsRow[] = rows.map(row => {
    const ratio = Number(row[idx] ?? 0);
    const seconds = ratio * videoDurationSeconds;
    const mm = Math.floor(seconds / 60);
    const ss = Math.floor(seconds % 60);
    const label = `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
    return [...row, Math.round(seconds * 100) / 100, label];
  });
  return { rows: newRows, injectedColumns };
}
