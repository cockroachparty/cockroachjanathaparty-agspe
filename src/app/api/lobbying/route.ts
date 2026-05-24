import { NextResponse } from 'next/server';
import { getData, initializeStore } from '@/lib/data/store';

export async function GET() {
  try {
    initializeStore();
    const lobbying = getData('lobbying');

    return NextResponse.json({
      success: true,
      data: lobbying,
      count: lobbying.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    const { lobbyingRecords } = await import('@/lib/mock-data');
    return NextResponse.json({
      success: true,
      data: lobbyingRecords,
      count: lobbyingRecords.length,
      timestamp: new Date().toISOString(),
      fallback: true,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
