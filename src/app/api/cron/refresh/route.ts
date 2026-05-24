import { NextResponse } from 'next/server';
import { refreshData, initializeStore } from '@/lib/data/store';

/**
 * Cron refresh endpoint for Vercel cron jobs.
 *
 * Must:
 * 1. Call refreshData() from the store
 * 2. Log results
 * 3. Return JSON with refresh status, counts, timestamp
 * 4. Handle CRON_SECRET env var for security (optional)
 * 5. Never fail - always return 200 with error details if something goes wrong
 */
export async function GET(request: Request) {
  try {
    // Check CRON_SECRET if set
    const cronSecret = process.env.CRON_SECRET;
    if (cronSecret) {
      const authHeader = request.headers.get('authorization');
      if (authHeader !== `Bearer ${cronSecret}`) {
        return NextResponse.json(
          {
            success: false,
            error: 'Unauthorized - invalid CRON_SECRET',
            timestamp: new Date().toISOString(),
          },
          { status: 401 }
        );
      }
    }

    // Initialize store if needed
    initializeStore();

    // Run the data refresh
    const result = await refreshData();

    console.log('[AGSPE Cron] Data refresh completed:', {
      sources_fetched: result.sources_fetched,
      articles_count: result.articles_count,
      duration_ms: result.duration_ms,
      errors: result.errors.length,
    });

    // Always return 200 - even with errors, report them in the response
    return NextResponse.json({
      success: true,
      message: 'Data refresh completed',
      refresh: {
        timestamp: result.timestamp,
        sources_fetched: result.sources_fetched,
        articles_count: result.articles_count,
        duration_ms: result.duration_ms,
        errors: result.errors,
      },
    });
  } catch (error) {
    // Never fail - always return 200 with error details
    console.error('[AGSPE Cron] Data refresh failed:', error);

    return NextResponse.json({
      success: false,
      message: 'Data refresh encountered an error',
      refresh: {
        timestamp: new Date().toISOString(),
        sources_fetched: 0,
        articles_count: 0,
        duration_ms: 0,
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      },
    });
  }
}
