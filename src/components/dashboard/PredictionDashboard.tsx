'use client';

import { useState, useEffect, useMemo } from 'react';
import { predictions as mockPredictions, type Prediction } from '@/lib/mock-data';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  TrendingUp,
  Shield,
  Target,
  Activity,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Zap,
} from 'lucide-react';

function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    Infrastructure: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    'Green Energy': 'bg-green-500/20 text-green-400 border-green-500/30',
    'M&A': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    'Digital Infrastructure': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    Defense: 'bg-red-500/20 text-red-400 border-red-500/30',
  };
  return colors[category] || 'bg-slate-500/20 text-slate-400 border-slate-500/30';
}

function getConfidenceColor(score: number): string {
  if (score >= 75) return 'bg-emerald-500';
  if (score >= 60) return 'bg-amber-500';
  return 'bg-red-500';
}

function getRiskLevel(score: number): { label: string; color: string; pulse: string } {
  if (score >= 0.75) return { label: 'LOW RISK', color: 'text-emerald-400', pulse: 'bg-emerald-400' };
  if (score >= 0.6) return { label: 'MODERATE RISK', color: 'text-amber-400', pulse: 'bg-amber-400' };
  return { label: 'HIGH RISK', color: 'text-red-400', pulse: 'bg-red-400' };
}

export default function PredictionDashboard() {
  const [predictions, setPredictions] = useState<Prediction[]>(mockPredictions);

  useEffect(() => {
    fetch('/api/predictions')
      .then((r) => r.json())
      .then((d) => {
        if (d.data && Array.isArray(d.data) && d.data.length > 0) {
          setPredictions(d.data);
        }
      })
      .catch(() => {}); // Keep mock data on error
  }, []);

  const topPredictions = useMemo(() => predictions.slice(0, 5), [predictions]);
  const totalPredictions = predictions.length;
  const highConfidence = useMemo(() => predictions.filter((p) => p.confidence_score >= 70).length, [predictions]);
  const avgConfidence = useMemo(() => Math.round(predictions.reduce((s, p) => s + p.confidence_score, 0) / predictions.length), [predictions]);
  const totalMarketCap = 16450000;

  const politicalRiskScore = 0.72;
  const riskLevel = getRiskLevel(politicalRiskScore);

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="glass-card border-0">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/15">
                <Target className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Predictions</p>
                <p className="text-2xl font-bold gradient-text-emerald">{totalPredictions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-0">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-500/15">
                <Shield className="h-5 w-5 text-amber-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">High Confidence</p>
                <p className="text-2xl font-bold gradient-text-amber">{highConfidence}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-0">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/15">
                <BarChart3 className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Avg Confidence</p>
                <p className="text-2xl font-bold">{avgConfidence}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card border-0">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-cyan-500/15">
                <TrendingUp className="h-5 w-5 text-cyan-400" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Group Market Cap</p>
                <p className="text-lg font-bold">₹{((totalMarketCap) / 100).toFixed(1)}L Cr</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Political Risk Indicator */}
      <Card className="glass-card border-0">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className={`w-3 h-3 rounded-full ${riskLevel.pulse} animate-pulse-glow`} style={{ color: riskLevel.pulse === 'bg-emerald-400' ? '#34d399' : riskLevel.pulse === 'bg-amber-400' ? '#fbbf24' : '#f87171' }} />
              </div>
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wider">Political Risk Indicator</h3>
                <p className={`text-lg font-bold ${riskLevel.color}`}>{riskLevel.label}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 w-full sm:w-auto">
              <div className="flex-1 sm:w-48">
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>Alignment Score</span>
                  <span>{(politicalRiskScore * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all confidence-bar-animated ${politicalRiskScore >= 0.75 ? 'bg-emerald-500' : politicalRiskScore >= 0.5 ? 'bg-amber-500' : 'bg-red-500'}`}
                    style={{ width: `${politicalRiskScore * 100}%` }}
                  />
                </div>
              </div>
              <Badge variant="outline" className="border-amber-500/30 text-amber-400 bg-amber-500/10 text-xs">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Elevated
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Top 5 High-Probability Moves */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Zap className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold">Top 5 High-Probability Moves</h2>
        </div>
        <div className="grid gap-4">
          {topPredictions.map((pred, index) => (
            <Card key={pred.id} className="glass-card glass-card-hover border-0 transition-all duration-300">
              <CardContent className="p-4">
                <div className="flex flex-col gap-4">
                  {/* Header */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center text-emerald-400 font-bold text-sm">
                        #{index + 1}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-sm sm:text-base leading-tight">{pred.likely_action}</h3>
                        <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                          <Badge className={`text-[10px] px-2 py-0 border ${getCategoryColor(pred.category)}`}>
                            {pred.category}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {pred.timeline_start} → {pred.timeline_end}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex-shrink-0 text-right">
                      <div className="text-2xl font-bold" style={{ color: pred.confidence_score >= 75 ? '#34d399' : pred.confidence_score >= 60 ? '#fbbf24' : '#f87171' }}>
                        {pred.confidence_score}%
                      </div>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Confidence</p>
                    </div>
                  </div>

                  {/* Confidence Bar */}
                  <div>
                    <Progress
                      value={pred.confidence_score}
                      className="h-2"
                    />
                  </div>

                  {/* Signal Metrics */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="text-center p-2 rounded-lg bg-muted/30">
                      <p className="text-[10px] text-muted-foreground uppercase">Financial</p>
                      <p className="text-sm font-semibold">{(pred.financial_signal * 100).toFixed(0)}%</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-muted/30">
                      <p className="text-[10px] text-muted-foreground uppercase">Political</p>
                      <p className="text-sm font-semibold">{(pred.political_alignment * 100).toFixed(0)}%</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-muted/30">
                      <p className="text-[10px] text-muted-foreground uppercase">Validation</p>
                      <p className="text-sm font-semibold">{(pred.validation_score * 100).toFixed(0)}%</p>
                    </div>
                  </div>

                  {/* Evidence & Risks */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-emerald-400 mb-1.5 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" /> Supporting Evidence
                      </p>
                      <ul className="space-y-1">
                        {pred.supporting_evidence.map((ev, i) => (
                          <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                            <span className="text-emerald-500 mt-0.5">•</span>
                            {ev}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-amber-400 mb-1.5 flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" /> Risk Factors
                      </p>
                      <ul className="space-y-1">
                        {pred.risk_factors.map((rf, i) => (
                          <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                            <span className="text-amber-500 mt-0.5">•</span>
                            {rf}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Pattern Match */}
                  <div className="flex items-center gap-2 pt-1 border-t border-border/50">
                    <Activity className="h-3 w-3 text-muted-foreground" />
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Pattern:</span>
                    <span className="text-xs font-medium text-foreground">{pred.pattern_match}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Timeline Forecast */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Activity className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold">Timeline Forecast</h2>
        </div>
        <Card className="glass-card border-0">
          <CardContent className="p-4">
            <div className="overflow-x-auto custom-scrollbar">
              <div className="min-w-[700px]">
                {/* Quarter Headers */}
                <div className="grid grid-cols-8 gap-0 mb-3">
                  <div className="text-[10px] text-muted-foreground uppercase tracking-wider text-center">
                    Prediction
                  </div>
                  {['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026', 'Q1 2027', 'Q2 2027', 'Q3 2027'].map((q) => (
                    <div key={q} className="text-[10px] text-muted-foreground uppercase tracking-wider text-center">
                      {q}
                    </div>
                  ))}
                </div>

                {/* Timeline Bars */}
                {predictions.map((pred) => {
                  const quarters = ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026', 'Q1 2027', 'Q2 2027', 'Q3 2027'];
                  const startIdx = quarters.indexOf(pred.timeline_start);
                  const endIdx = quarters.indexOf(pred.timeline_end);
                  const barColor = pred.confidence_score >= 75
                    ? 'bg-emerald-500/40 border-emerald-500/60'
                    : pred.confidence_score >= 60
                      ? 'bg-amber-500/40 border-amber-500/60'
                      : 'bg-red-500/40 border-red-500/60';

                  return (
                    <div key={pred.id} className="grid grid-cols-8 gap-0 mb-2 items-center">
                      <div className="text-[11px] text-foreground truncate pr-2" title={pred.likely_action}>
                        {pred.likely_action.length > 28 ? pred.likely_action.substring(0, 28) + '…' : pred.likely_action}
                      </div>
                      {quarters.map((q, idx) => {
                        const isActive = idx >= startIdx && idx <= endIdx;
                        const isStart = idx === startIdx;
                        const isEnd = idx === endIdx;
                        return (
                          <div key={q} className="flex items-center justify-center h-8 relative">
                            {isActive && (
                              <div
                                className={`h-5 w-full ${barColor} border ${
                                  isStart ? 'rounded-l-md ml-1' : ''
                                } ${isEnd ? 'rounded-r-md mr-1' : ''} ${!isStart && !isEnd ? 'border-l-0 border-r-0' : ''}`}
                              />
                            )}
                            {isStart && (
                              <div className="absolute left-1 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-emerald-400" />
                            )}
                            {isEnd && (
                              <div className="absolute right-1 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-amber-400" />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  );
                })}

                {/* Legend */}
                <div className="flex items-center gap-4 mt-4 pt-3 border-t border-border/50">
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded bg-emerald-500/40 border border-emerald-500/60" />
                    <span className="text-[10px] text-muted-foreground">High Confidence (≥75%)</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded bg-amber-500/40 border border-amber-500/60" />
                    <span className="text-[10px] text-muted-foreground">Medium (60-74%)</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded bg-red-500/40 border border-red-500/60" />
                    <span className="text-[10px] text-muted-foreground">Low (&lt;60%)</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
