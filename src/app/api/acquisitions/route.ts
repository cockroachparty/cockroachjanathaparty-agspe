import { NextResponse } from 'next/server';
import { getData, initializeStore } from '@/lib/data/store';

export async function GET() {
  try {
    initializeStore();
    const acquisitions = getData('acquisitions');

    return NextResponse.json({
      success: true,
      data: acquisitions,
      count: acquisitions.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    const { acquisitions } = await import('@/lib/mock-data');
    return NextResponse.json({
      success: true,
      data: acquisitions,
      count: acquisitions.length,
      timestamp: new Date().toISOString(),
      fallback: true,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
