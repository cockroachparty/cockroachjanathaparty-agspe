import { NextResponse } from 'next/server';
import { getStoreStatus, initializeStore } from '@/lib/data/store';

export async function GET() {
  try {
    initializeStore();
    const status = getStoreStatus();

    return NextResponse.json({
      success: true,
      status: 'operational',
      lastRefresh: status.lastRefresh,
      dataCounts: status.dataCounts,
      systemStatus: status.systemStatus,
      uptime: status.uptime,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json({
      success: true,
      status: 'degraded',
      lastRefresh: null,
      dataCounts: {},
      systemStatus: 'error',
      uptime: 'unknown',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
