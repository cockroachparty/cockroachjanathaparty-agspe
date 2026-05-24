/**
 * AGSPE Data Store - Caching data store for serverless environment
 *
 * Uses module-level variables that survive within a serverless function
 * instance lifecycle. Falls back to mock data if anything goes wrong.
 */

import {
  predictions as mockPredictions,
  financials as mockFinancials,
  newsArticles as mockNews,
  lobbyingRecords as mockLobbying,
  acquisitions as mockAcquisitions,
  type Prediction,
  type Financial,
  type NewsArticle,
  type LobbyingRecord,
  type Acquisition,
} from '@/lib/mock-data';
import type { DataCache, StoreStatus, DataRefreshResult } from '@/lib/engine/types';

// ── Module-level cache (survives within serverless function instance lifecycle) ──

let dataCache: DataCache | null = null;
let isRefreshing = false;
let initializedAt: string | null = null;
let lastRefreshResult: DataRefreshResult | null = null;

/**
 * Initialize the store with mock data on first call.
 */
export function initializeStore(): void {
  if (dataCache) return;

  dataCache = {
    predictions: [...mockPredictions],
    financials: [...mockFinancials],
    news: [...mockNews],
    lobbying: [...mockLobbying],
    acquisitions: [...mockAcquisitions],
    lastRefresh: new Date().toISOString(),
  };

  initializedAt = new Date().toISOString();
}

/**
 * Refresh data from external sources, run through engines, update cache.
 * This is called by the cron job endpoint.
 *
 * NEVER throws - always returns a result, even on error.
 */
export async function refreshData(): Promise<DataRefreshResult> {
  // Prevent concurrent refreshes
  if (isRefreshing) {
    return {
      timestamp: new Date().toISOString(),
      sources_fetched: 0,
      articles_count: 0,
      errors: ['Refresh already in progress'],
      duration_ms: 0,
    };
  }

  isRefreshing = true;

  try {
    // Ensure store is initialized
    if (!dataCache) {
      initializeStore();
    }

    // Import data fetcher dynamically to avoid circular deps
    const { refreshAllData } = await import('@/lib/engine/data-fetcher');
    const result = await refreshAllData();

    // Now fetch individual data types to update cache
    const { fetchDataByType } = await import('@/lib/engine/data-fetcher');

    try {
      const newsResult = await fetchDataByType('news');
      if (newsResult.data.length > 0) {
        dataCache!.news = newsResult.data as NewsArticle[];
      }
    } catch { /* keep existing cache */ }

    try {
      const finResult = await fetchDataByType('financials');
      if (finResult.data.length > 0) {
        dataCache!.financials = finResult.data as Financial[];
      }
    } catch { /* keep existing cache */ }

    try {
      const lobResult = await fetchDataByType('lobbying');
      if (lobResult.data.length > 0) {
        dataCache!.lobbying = lobResult.data as LobbyingRecord[];
      }
    } catch { /* keep existing cache */ }

    try {
      const acqResult = await fetchDataByType('acquisitions');
      if (acqResult.data.length > 0) {
        dataCache!.acquisitions = acqResult.data as Acquisition[];
      }
    } catch { /* keep existing cache */ }

    try {
      const predResult = await fetchDataByType('predictions');
      if (predResult.data.length > 0) {
        dataCache!.predictions = predResult.data as Prediction[];
      }
    } catch { /* keep existing cache */ }

    dataCache!.lastRefresh = new Date().toISOString();
    lastRefreshResult = result;

    return result;
  } catch (error) {
    // Never fail - return error details
    const errorResult: DataRefreshResult = {
      timestamp: new Date().toISOString(),
      sources_fetched: 0,
      articles_count: dataCache?.predictions.length ?? 0 + dataCache?.news.length ?? 0,
      errors: [`Refresh error: ${error instanceof Error ? error.message : 'Unknown error'}`],
      duration_ms: 0,
    };
    lastRefreshResult = errorResult;
    return errorResult;
  } finally {
    isRefreshing = false;
  }
}

/**
 * Get cached data for a given type.
 * Initializes the store if not yet initialized.
 */
export function getData(
  type: 'predictions' | 'financials' | 'news' | 'lobbying' | 'acquisitions'
): Prediction[] | Financial[] | NewsArticle[] | LobbyingRecord[] | Acquisition[] {
  if (!dataCache) {
    initializeStore();
  }

  return dataCache![type];
}

/**
 * Get the current store status.
 */
export function getStoreStatus(): StoreStatus {
  if (!dataCache) {
    initializeStore();
  }

  const systemStatus: 'operational' | 'degraded' | 'error' =
    lastRefreshResult && lastRefreshResult.errors.length > 2
      ? 'degraded'
      : 'operational';

  // Calculate uptime
  let uptime = 'unknown';
  if (initializedAt) {
    const uptimeMs = Date.now() - new Date(initializedAt).getTime();
    const hours = Math.floor(uptimeMs / 3600000);
    const minutes = Math.floor((uptimeMs % 3600000) / 60000);
    uptime = `${hours}h ${minutes}m`;
  }

  return {
    lastRefresh: dataCache!.lastRefresh,
    dataCounts: {
      predictions: dataCache!.predictions.length,
      financials: dataCache!.financials.length,
      news: dataCache!.news.length,
      lobbying: dataCache!.lobbying.length,
      acquisitions: dataCache!.acquisitions.length,
    },
    systemStatus,
    uptime,
  };
}

/**
 * Check if the store is stale (older than 1 hour) and needs refresh.
 */
export function isStoreStale(maxAgeMs: number = 3600000): boolean {
  if (!dataCache || !dataCache.lastRefresh) return true;
  const age = Date.now() - new Date(dataCache.lastRefresh).getTime();
  return age > maxAgeMs;
}
