import { NextResponse } from 'next/server';
import { getData, initializeStore } from '@/lib/data/store';

export async function GET() {
  try {
    initializeStore();
    const financials = getData('financials');

    return NextResponse.json({
      success: true,
      data: financials,
      count: financials.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    const { financials } = await import('@/lib/mock-data');
    return NextResponse.json({
      success: true,
      data: financials,
      count: financials.length,
      timestamp: new Date().toISOString(),
      fallback: true,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
