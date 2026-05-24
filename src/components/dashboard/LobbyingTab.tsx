'use client';

import { useState, useMemo, useEffect } from 'react';
import { lobbyingRecords as mockLobbying, type LobbyingRecord } from '@/lib/mock-data';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Globe,
  Building2,
  Scale,
  Landmark,
  DollarSign,
} from 'lucide-react';

function formatUSD(amount: number): string {
  if (amount >= 1000000) return `$${(amount / 1000000).toFixed(2)}M`;
  if (amount >= 1000) return `$${(amount / 1000).toFixed(0)}K`;
  return `$${amount}`;
}

const countryFlags: Record<string, string> = {
  India: '🇮🇳',
  USA: '🇺🇸',
  Australia: '🇦🇺',
  Israel: '🇮🇱',
  Tanzania: '🇹🇿',
};

const countryColors: Record<string, string> = {
  India: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  USA: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  Australia: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  Israel: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  Tanzania: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
};

export default function LobbyingTab() {
  const [lobbyingRecords, setLobbyingRecords] = useState<LobbyingRecord[]>(mockLobbying);

  useEffect(() => {
    fetch('/api/lobbying')
      .then((r) => r.json())
      .then((d) => {
        if (d.data && Array.isArray(d.data) && d.data.length > 0) {
          setLobbyingRecords(d.data);
        }
      })
      .catch(() => {}); // Keep mock data on error
  }, []);

  // Group by country for global interests
  const countrySummary = useMemo(() => {
    const summary: Record<string, { total: number; count: number; types: Set<string> }> = {};
    lobbyingRecords.forEach((rec) => {
      if (!summary[rec.country]) {
        summary[rec.country] = { total: 0, count: 0, types: new Set() };
      }
      summary[rec.country].total += rec.amount_usd;
      summary[rec.country].count += 1;
      summary[rec.country].types.add(rec.disclosure_type);
    });
    return summary;
  }, [lobbyingRecords]);

  // Electoral bond data for bar chart
  const electoralBonds = useMemo(() => {
    return lobbyingRecords
      .filter((r) => r.disclosure_type === 'Electoral Bond')
      .sort((a, b) => a.year - b.year || a.quarter.localeCompare(b.quarter));
  }, [lobbyingRecords]);

  const maxBondAmount = Math.max(...electoralBonds.map((b) => b.amount_usd));

  // Lobbying spend by quarter
  const lobbyingSpend = useMemo(() => {
    return lobbyingRecords
      .filter((r) => r.disclosure_type !== 'Electoral Bond')
      .sort((a, b) => b.year - a.year || b.quarter.localeCompare(a.quarter));
  }, [lobbyingRecords]);

  // Law firms
  const lawFirms = useMemo(() => {
    const firms = new Map<string, { country: string; amount: number; descriptions: string[] }>();
    lobbyingRecords.forEach((rec) => {
      if (rec.law_firm && rec.law_firm !== '—' && rec.law_firm !== 'Local Counsel' && rec.law_firm !== 'Government Relations Counsel') {
        if (!firms.has(rec.law_firm)) {
          firms.set(rec.law_firm, { country: rec.country, amount: 0, descriptions: [] });
        }
        const firm = firms.get(rec.law_firm)!;
        firm.amount += rec.amount_usd;
        if (!firm.descriptions.includes(rec.description)) {
          firm.descriptions.push(rec.description);
        }
      }
    });
    return Array.from(firms.entries()).map(([name, data]) => ({ name, ...data }));
  }, [lobbyingRecords]);

  return (
    <div className="space-y-6">
      {/* Global Interests */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Globe className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold">Global Interests</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {Object.entries(countrySummary).map(([country, data]) => (
            <Card key={country} className="glass-card glass-card-hover border-0 transition-all duration-300">
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-1">{countryFlags[country] || '🌍'}</div>
                <p className="font-semibold text-sm">{country}</p>
                <Badge className={`text-[9px] mt-1 border ${countryColors[country] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
                  {data.count} {data.count === 1 ? 'Record' : 'Records'}
                </Badge>
                <p className="text-lg font-bold mt-2">{formatUSD(data.total)}</p>
                <p className="text-[10px] text-muted-foreground">Total Spend</p>
                <div className="mt-2 flex flex-wrap gap-1 justify-center">
                  {Array.from(data.types).map((type) => (
                    <span key={type} className="text-[9px] bg-muted/40 px-1.5 py-0.5 rounded">
                      {type.replace('Lobbying - ', '')}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Electoral Bond Donation Tracker */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Landmark className="h-5 w-5 text-amber-400" />
          <h2 className="text-lg font-semibold">Electoral Bond Donation Tracker</h2>
        </div>
        <Card className="glass-card border-0">
          <CardContent className="p-4">
            <div className="space-y-3">
              {electoralBonds.map((bond) => (
                <div key={bond.id} className="flex items-center gap-3">
                  <div className="w-20 text-xs text-muted-foreground text-right flex-shrink-0">
                    {bond.quarter} {bond.year}
                  </div>
                  <div className="flex-1 h-8 bg-muted/30 rounded-md overflow-hidden relative">
                    <div
                      className="h-full rounded-md transition-all duration-700 ease-out"
                      style={{
                        width: `${(bond.amount_usd / maxBondAmount) * 100}%`,
                        background: 'linear-gradient(90deg, rgba(245,158,11,0.4), rgba(245,158,11,0.7))',
                      }}
                    />
                    <div className="absolute inset-0 flex items-center px-3">
                      <span className="text-xs font-semibold text-amber-300">
                        {formatUSD(bond.amount_usd)}
                      </span>
                    </div>
                  </div>
                  <div className="w-28 text-xs text-muted-foreground flex-shrink-0 hidden sm:block">
                    {bond.description}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-border/50 flex items-center gap-4">
              <div className="text-sm">
                <span className="text-muted-foreground">Total Electoral Bonds: </span>
                <span className="font-bold text-amber-400">
                  {formatUSD(electoralBonds.reduce((s, b) => s + b.amount_usd, 0))}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lobbying Spend Log */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <DollarSign className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold">Lobbying Spend Log</h2>
        </div>
        <Card className="glass-card border-0">
          <CardContent className="p-0">
            <div className="overflow-x-auto custom-scrollbar">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent border-border/30">
                    <TableHead>Entity</TableHead>
                    <TableHead>Country</TableHead>
                    <TableHead>Quarter</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="hidden md:table-cell">Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lobbyingSpend.map((rec) => (
                    <TableRow key={rec.id} className="border-border/20 hover:bg-muted/20">
                      <TableCell className="font-medium text-sm max-w-[200px] truncate">
                        {rec.entity}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1.5">
                          <span>{countryFlags[rec.country]}</span>
                          <span className="text-sm">{rec.country}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{rec.quarter} {rec.year}</TableCell>
                      <TableCell className="text-right text-sm font-medium text-emerald-400">
                        {formatUSD(rec.amount_usd)}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`text-[9px] border ${
                            rec.disclosure_type.includes('Federal')
                              ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                              : rec.disclosure_type.includes('State')
                                ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                                : rec.disclosure_type.includes('Foreign')
                                  ? 'bg-red-500/15 text-red-400 border-red-500/30'
                                  : 'bg-slate-500/15 text-slate-400 border-slate-500/30'
                          }`}
                        >
                          {rec.disclosure_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="hidden md:table-cell text-xs text-muted-foreground max-w-[250px] truncate">
                        {rec.description}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Law Firm Engagements */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Scale className="h-5 w-5 text-cyan-400" />
          <h2 className="text-lg font-semibold">Law Firm Engagements</h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {lawFirms.map((firm) => (
            <Card key={firm.name} className="glass-card glass-card-hover border-0 transition-all duration-300">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-cyan-500/15">
                    <Building2 className="h-4 w-4 text-cyan-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-sm">{firm.name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">{countryFlags[firm.country]} {firm.country}</span>
                      <span className="text-xs font-medium text-emerald-400">{formatUSD(firm.amount)}</span>
                    </div>
                    <div className="mt-2 space-y-1">
                      {firm.descriptions.map((desc, i) => (
                        <p key={i} className="text-[11px] text-muted-foreground">
                          • {desc}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
