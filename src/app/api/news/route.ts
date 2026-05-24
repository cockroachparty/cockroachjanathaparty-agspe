import { NextResponse } from 'next/server';
import { getData, initializeStore } from '@/lib/data/store';

export async function GET() {
  try {
    initializeStore();
    const news = getData('news');

    return NextResponse.json({
      success: true,
      data: news,
      count: news.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    const { newsArticles } = await import('@/lib/mock-data');
    return NextResponse.json({
      success: true,
      data: newsArticles,
      count: newsArticles.length,
      timestamp: new Date().toISOString(),
      fallback: true,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
