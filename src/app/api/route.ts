import { NextResponse } from 'next/server';
import { getStoreStatus, initializeStore } from '@/lib/data/store';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    initializeStore();
    const status = getStoreStatus();

    return NextResponse.json({
      name: 'AGSPE',
      version: '2.0.0',
      repository: 'https://github.com/cockroachparty/cockroachjanathaparty-agspe',
      status: 'operational',
      lastRefresh: status.lastRefresh,
      dataCounts: status.dataCounts,
      systemStatus: status.systemStatus,
      disclaimer: 'For informational purposes only. Not financial or investment advice.',
    });
  } catch {
    return NextResponse.json({
      name: 'AGSPE',
      version: '2.0.0',
      repository: 'https://github.com/cockroachparty/cockroachjanathaparty-agspe',
      status: 'degraded',
      lastRefresh: null,
      disclaimer: 'For informational purposes only. Not financial or investment advice.',
    });
  }
}
