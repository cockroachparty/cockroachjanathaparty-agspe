'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import PredictionDashboard from '@/components/dashboard/PredictionDashboard';
import FinancialsTab from '@/components/dashboard/FinancialsTab';
import LobbyingTab from '@/components/dashboard/LobbyingTab';
import IntelligenceFeed from '@/components/dashboard/IntelligenceFeed';
import AcquisitionsTab from '@/components/dashboard/AcquisitionsTab';
import {
  Rocket,
  TrendingUp,
  Vote,
  Newspaper,
  Building2,
  Shield,
  RefreshCw,
} from 'lucide-react';

interface HealthData {
  success: boolean;
  status: string;
  lastRefresh: string | null;
  systemStatus: string;
  uptime: string;
  dataCounts: Record<string, number>;
}

export default function Home() {
  const [healthData, setHealthData] = useState<HealthData | null>(null);

  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then((d) => setHealthData(d))
      .catch(() => {});
  }, []);

  const formatLastRefresh = (timestamp: string | null): string => {
    if (!timestamp) return 'Loading...';
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#060b16' }}>
      {/* Header */}
      <header className="border-b border-white/5 px-4 sm:px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Shield className="h-8 w-8 text-emerald-400" />
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold tracking-tight">
                <span className="gradient-text-emerald">AGSPE</span>
              </h1>
              <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] leading-none">
                Adani Group Strategic Prediction Engine
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              System Active
            </div>
            <div className="text-xs text-muted-foreground/50">|</div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <RefreshCw className="h-3 w-3" />
              Last Refresh: {formatLastRefresh(healthData?.lastRefresh ?? null)}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-4 sm:px-6 py-4 sm:py-6 max-w-7xl mx-auto w-full">
        <Tabs defaultValue="predictions" className="space-y-4 sm:space-y-6">
          <TabsList className="bg-white/5 border border-white/5 h-auto p-1 flex flex-wrap gap-1">
            <TabsTrigger
              value="predictions"
              className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400 data-[state=active]:border-emerald-500/30 text-xs sm:text-sm gap-1.5 border border-transparent rounded-md px-2 sm:px-3 py-1.5"
            >
              <Rocket className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Predictions</span>
              <span className="sm:hidden">Pred</span>
            </TabsTrigger>
            <TabsTrigger
              value="financials"
              className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400 data-[state=active]:border-emerald-500/30 text-xs sm:text-sm gap-1.5 border border-transparent rounded-md px-2 sm:px-3 py-1.5"
            >
              <TrendingUp className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Financials</span>
              <span className="sm:hidden">Fin</span>
            </TabsTrigger>
            <TabsTrigger
              value="lobbying"
              className="data-[state=active]:bg-amber-500/20 data-[state=active]:text-amber-400 data-[state=active]:border-amber-500/30 text-xs sm:text-sm gap-1.5 border border-transparent rounded-md px-2 sm:px-3 py-1.5"
            >
              <Vote className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Lobbying</span>
              <span className="sm:hidden">Lob</span>
            </TabsTrigger>
            <TabsTrigger
              value="intelligence"
              className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400 data-[state=active]:border-cyan-500/30 text-xs sm:text-sm gap-1.5 border border-transparent rounded-md px-2 sm:px-3 py-1.5"
            >
              <Newspaper className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Intelligence</span>
              <span className="sm:hidden">Intel</span>
            </TabsTrigger>
            <TabsTrigger
              value="acquisitions"
              className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400 data-[state=active]:border-emerald-500/30 text-xs sm:text-sm gap-1.5 border border-transparent rounded-md px-2 sm:px-3 py-1.5"
            >
              <Building2 className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Acquisitions</span>
              <span className="sm:hidden">Acq</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="predictions">
            <PredictionDashboard />
          </TabsContent>
          <TabsContent value="financials">
            <FinancialsTab />
          </TabsContent>
          <TabsContent value="lobbying">
            <LobbyingTab />
          </TabsContent>
          <TabsContent value="intelligence">
            <IntelligenceFeed />
          </TabsContent>
          <TabsContent value="acquisitions">
            <AcquisitionsTab />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 px-4 sm:px-6 py-3 mt-auto">
        <div className="max-w-7xl mx-auto">
          <p className="text-[10px] sm:text-xs text-muted-foreground text-center">
            For informational purposes only. Not financial or investment advice. Data based on publicly available records.
          </p>
        </div>
      </footer>
    </div>
  );
}
