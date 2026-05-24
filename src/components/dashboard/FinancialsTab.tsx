'use client';

import { useState, useMemo, useEffect } from 'react';
import { financials as mockFinancials, type Financial } from '@/lib/mock-data';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  IndianRupee,
  DollarSign,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';

type SortField = keyof Financial;
type SortDirection = 'asc' | 'desc';

function formatNumber(num: number, currency: 'INR' | 'USD'): string {
  if (currency === 'INR') {
    if (num >= 100000) return `₹${(num / 100000).toFixed(2)}L Cr`;
    if (num >= 1000) return `₹${(num / 1000).toFixed(2)}K Cr`;
    return `₹${num}`;
  } else {
    if (num >= 1000) return `$${(num / 1000).toFixed(2)}B`;
    return `$${num}M`;
  }
}

function formatPrice(num: number, currency: 'INR' | 'USD'): string {
  if (currency === 'INR') return `₹${num.toLocaleString('en-IN')}`;
  return `$${num.toFixed(2)}`;
}

function getDEHeatmapClass(de: number): string {
  if (de <= 0.4) return 'de-low';
  if (de <= 0.8) return 'de-medium';
  if (de <= 1.5) return 'de-high';
  return 'de-very-high';
}

function getDELabel(de: number): string {
  if (de <= 0.4) return 'Low';
  if (de <= 0.8) return 'Moderate';
  if (de <= 1.5) return 'High';
  return 'Very High';
}

export default function FinancialsTab() {
  const [financials, setFinancials] = useState<Financial[]>(mockFinancials);
  const [currency, setCurrency] = useState<'INR' | 'USD'>('INR');
  const [sortField, setSortField] = useState<SortField>('market_cap_inr');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffect(() => {
    fetch('/api/financials')
      .then((r) => r.json())
      .then((d) => {
        if (d.data && Array.isArray(d.data) && d.data.length > 0) {
          setFinancials(d.data);
        }
      })
      .catch(() => {}); // Keep mock data on error
  }, []);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedFinancials = useMemo(() => {
    return [...financials].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      return sortDirection === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }, [financials, sortField, sortDirection]);

  const totalMarketCap = financials.reduce((s, f) => s + (currency === 'INR' ? f.market_cap_inr : f.market_cap_usd), 0);
  const avgDE = (financials.reduce((s, f) => s + f.debt_to_equity, 0) / financials.length).toFixed(2);

  const renderSortIcon = (field: SortField) => {
    if (sortField !== field) return <ArrowUpDown className="h-3 w-3 ml-1 opacity-30" />;
    return sortDirection === 'asc' ? (
      <ArrowUp className="h-3 w-3 ml-1 text-emerald-400" />
    ) : (
      <ArrowDown className="h-3 w-3 ml-1 text-emerald-400" />
    );
  };

  return (
    <div className="space-y-6">
      {/* Currency Toggle & Stats */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant={currency === 'INR' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setCurrency('INR')}
            className={currency === 'INR' ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'border-border/50'}
          >
            <IndianRupee className="h-4 w-4 mr-1" />
            INR
          </Button>
          <Button
            variant={currency === 'USD' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setCurrency('USD')}
            className={currency === 'USD' ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'border-border/50'}
          >
            <DollarSign className="h-4 w-4 mr-1" />
            USD
          </Button>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div>
            <span className="text-muted-foreground text-xs">Total MCap: </span>
            <span className="font-semibold">{formatNumber(totalMarketCap, currency)}</span>
          </div>
          <div>
            <span className="text-muted-foreground text-xs">Avg D/E: </span>
            <span className="font-semibold text-amber-400">{avgDE}</span>
          </div>
        </div>
      </div>

      {/* Financial Table */}
      <Card className="glass-card border-0">
        <CardContent className="p-0">
          <div className="overflow-x-auto custom-scrollbar">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent border-border/30">
                  <TableHead className="cursor-pointer select-none" onClick={() => handleSort('company_name')}>
                    <div className="flex items-center">Company {renderSortIcon('company_name')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none" onClick={() => handleSort('ticker')}>
                    <div className="flex items-center">Ticker {renderSortIcon('ticker')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none text-right" onClick={() => handleSort(currency === 'INR' ? 'market_cap_inr' : 'market_cap_usd')}>
                    <div className="flex items-center justify-end">Market Cap {renderSortIcon(currency === 'INR' ? 'market_cap_inr' : 'market_cap_usd')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none text-right" onClick={() => handleSort('debt_to_equity')}>
                    <div className="flex items-center justify-end">D/E Ratio {renderSortIcon('debt_to_equity')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none text-right" onClick={() => handleSort(currency === 'INR' ? 'stock_price' : 'stock_price_usd')}>
                    <div className="flex items-center justify-end">Price {renderSortIcon(currency === 'INR' ? 'stock_price' : 'stock_price_usd')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none text-right" onClick={() => handleSort('change_percent')}>
                    <div className="flex items-center justify-end">Change% {renderSortIcon('change_percent')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none text-right" onClick={() => handleSort('pe_ratio')}>
                    <div className="flex items-center justify-end">P/E {renderSortIcon('pe_ratio')}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer select-none" onClick={() => handleSort('sector')}>
                    <div className="flex items-center">Sector {renderSortIcon('sector')}</div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedFinancials.map((fin) => (
                  <TableRow key={fin.id} className="border-border/20 hover:bg-muted/20">
                    <TableCell className="font-medium text-sm">{fin.company_name}</TableCell>
                    <TableCell>
                      <code className="text-xs bg-muted/50 px-1.5 py-0.5 rounded">{fin.ticker}</code>
                    </TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      {formatNumber(currency === 'INR' ? fin.market_cap_inr : fin.market_cap_usd, currency)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium ${getDEHeatmapClass(fin.debt_to_equity)}`}>
                        {fin.debt_to_equity.toFixed(2)}
                        <span className="text-[9px] opacity-70">({getDELabel(fin.debt_to_equity)})</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right text-sm">
                      {formatPrice(currency === 'INR' ? fin.stock_price : fin.stock_price_usd, currency)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className={`inline-flex items-center gap-1 text-sm font-medium ${fin.change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {fin.change_percent >= 0 ? (
                          <TrendingUp className="h-3 w-3" />
                        ) : (
                          <TrendingDown className="h-3 w-3" />
                        )}
                        {fin.change_percent >= 0 ? '+' : ''}{fin.change_percent.toFixed(2)}%
                      </div>
                    </TableCell>
                    <TableCell className="text-right text-sm">{fin.pe_ratio.toFixed(1)}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[10px] border-border/30">
                        {fin.sector}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* D/E Ratio Heatmap Legend */}
      <Card className="glass-card border-0">
        <CardContent className="p-4">
          <h3 className="text-sm font-semibold mb-3">Debt-to-Equity Heatmap Legend</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded de-low" />
              <div>
                <p className="text-xs font-medium">Low Risk</p>
                <p className="text-[10px] text-muted-foreground">D/E ≤ 0.4</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded de-medium" />
              <div>
                <p className="text-xs font-medium">Moderate</p>
                <p className="text-[10px] text-muted-foreground">D/E 0.4 - 0.8</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded de-high" />
              <div>
                <p className="text-xs font-medium">High</p>
                <p className="text-[10px] text-muted-foreground">D/E 0.8 - 1.5</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded de-very-high" />
              <div>
                <p className="text-xs font-medium">Very High</p>
                <p className="text-[10px] text-muted-foreground">D/E &gt; 1.5</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
