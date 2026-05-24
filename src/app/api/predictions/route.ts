import { NextResponse } from 'next/server';
import { getData, initializeStore, isStoreStale } from '@/lib/data/store';

export async function GET() {
  try {
    // Initialize store if needed
    initializeStore();

    // If store is stale, we could trigger a refresh, but for predictions
    // we'll just return cached data to keep response fast
    const predictions = getData('predictions');

    return NextResponse.json({
      success: true,
      data: predictions,
      count: predictions.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    // Fallback to mock data
    const { predictions } = await import('@/lib/mock-data');
    return NextResponse.json({
      success: true,
      data: predictions,
      count: predictions.length,
      timestamp: new Date().toISOString(),
      fallback: true,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
