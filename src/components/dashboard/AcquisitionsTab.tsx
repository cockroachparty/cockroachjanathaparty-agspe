'use client';

import { useState, useMemo, useEffect } from 'react';
import { acquisitions as mockAcquisitions, type Acquisition } from '@/lib/mock-data';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Search,
  Building2,
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';

function getStatusStyle(status: Acquisition['status']): string {
  switch (status) {
    case 'Active':
      return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    case 'Integrated':
      return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
    case 'Demerged':
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    case 'Pending Litigation':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
}

type SortField = 'company_acquired' | 'year' | 'valuation_inr' | 'sector';
type SortDirection = 'asc' | 'desc';

export default function AcquisitionsTab() {
  const [acquisitions, setAcquisitions] = useState<Acquisition[]>(mockAcquisitions);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('year');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffect(() => {
    fetch('/api/acquisitions')
      .then((r) => r.json())
      .then((d) => {
        if (d.data && Array.isArray(d.data) && d.data.length > 0) {
          setAcquisitions(d.data);
        }
      })
      .catch(() => {}); // Keep mock data on error
  }, []);

  const sectors = useMemo(() => Array.from(new Set(acquisitions.map((a) => a.sector))).sort(), [acquisitions]);
  const statuses: Acquisition['status'][] = ['Active', 'Integrated', 'Demerged', 'Pending Litigation'];
  const allYears = useMemo(() => Array.from(new Set(acquisitions.map((a) => a.year))).sort(), [acquisitions]);

  const [yearRange, setYearRange] = useState<[number, number]>([
    allYears.length > 0 ? Math.min(...allYears) : 2019,
    allYears.length > 0 ? Math.max(...allYears) : 2025,
  ]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection(field === 'year' ? 'desc' : 'asc');
    }
  };

  const filteredAcquisitions = useMemo(() => {
    return acquisitions
      .filter((acq) => {
        if (selectedSector !== 'all' && acq.sector !== selectedSector) return false;
        if (selectedStatus !== 'all' && acq.status !== selectedStatus) return false;
        if (acq.year < yearRange[0] || acq.year > yearRange[1]) return false;
        if (searchQuery) {
          const q = searchQuery.toLowerCase();
          return (
            acq.company_acquired.toLowerCase().includes(q) ||
            acq.acquirer.toLowerCase().includes(q) ||
            acq.sector.toLowerCase().includes(q)
          );
        }
        return true;
      })
      .sort((a, b) => {
        const aVal = a[sortField];
        const bVal = b[sortField];
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
        }
        return sortDirection === 'asc'
          ? String(aVal).localeCompare(String(bVal))
          : String(bVal).localeCompare(String(aVal));
      });
  }, [acquisitions, searchQuery, selectedSector, selectedStatus, yearRange, sortField, sortDirection]);

  // Summary stats
  const totalValuationINR = filteredAcquisitions.reduce((s, a) => s + a.valuation_inr, 0);
  const totalValuationUSD = filteredAcquisitions.reduce((s, a) => s + a.valuation_usd, 0);

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
      {/* Filter Bar */}
      <Card className="glass-card border-0">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Filter className="h-4 w-4 text-emerald-400" />
            <h3 className="text-sm font-semibold">Filter Acquisitions</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="relative lg:col-span-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search companies, acquirers, sectors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-muted/20 border-border/30 h-9 text-sm"
              />
            </div>

            {/* Sector Filter */}
            <Select value={selectedSector} onValueChange={setSelectedSector}>
              <SelectTrigger className="bg-muted/20 border-border/30 h-9 text-sm w-full">
                <SelectValue placeholder="Sector" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sectors</SelectItem>
                {sectors.map((sector) => (
                  <SelectItem key={sector} value={sector}>
                    {sector}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Status Filter */}
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="bg-muted/20 border-border/30 h-9 text-sm w-full">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {statuses.map((status) => (
                  <SelectItem key={status} value={status}>
                    {status}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Year Range */}
            <Select
              value={`${yearRange[0]}-${yearRange[1]}`}
              onValueChange={(v) => {
                const [min, max] = v.split('-').map(Number);
                setYearRange([min, max]);
              }}
            >
              <SelectTrigger className="bg-muted/20 border-border/30 h-9 text-sm w-full">
                <SelectValue placeholder="Year Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={`${allYears.length > 0 ? Math.min(...allYears) : 2019}-${allYears.length > 0 ? Math.max(...allYears) : 2025}`}>All Years</SelectItem>
                <SelectItem value="2019-2021">2019 - 2021</SelectItem>
                <SelectItem value="2022-2023">2022 - 2023</SelectItem>
                <SelectItem value="2024-2025">2024 - 2025</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
            <span>Showing {filteredAcquisitions.length} of {acquisitions.length} acquisitions</span>
            <div className="flex items-center gap-3">
              <span>Total: ₹{(totalValuationINR / 1000).toFixed(1)}K Cr (${(totalValuationUSD / 1000).toFixed(1)}B)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Acquisitions Table */}
      <Card className="glass-card border-0">
        <CardContent className="p-0">
          <div className="overflow-x-auto custom-scrollbar">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent border-border/30">
                  <TableHead className="cursor-pointer select-none" onClick={() => handleSort('company_acquired')}>
                    <div className="flex items-center">Company Acquired {renderSortIcon('company_acquired')}</div>
                  </TableHead>
                  <TableHead>Acquirer</TableHead>
                  <TableHead className="cursor-pointer select-none text-center" onClick={() => handleSort('year')}>
                    <div className="flex items-center justify-center">Year {renderSortIcon('year')}</div>
                  </TableHead>
                  <TableHead className="text-right">Valuation (INR)</TableHead>
                  <TableHead className="text-right hidden sm:table-cell">Valuation (USD)</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="cursor-pointer select-none hidden md:table-cell" onClick={() => handleSort('sector')}>
                    <div className="flex items-center">Sector {renderSortIcon('sector')}</div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAcquisitions.map((acq) => (
                  <TableRow key={acq.id} className="border-border/20 hover:bg-muted/20">
                    <TableCell className="font-medium text-sm max-w-[200px]">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                        <span className="truncate">{acq.company_acquired}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground max-w-[150px] truncate">
                      {acq.acquirer}
                    </TableCell>
                    <TableCell className="text-center">
                      <span className="text-sm font-mono">{acq.year}</span>
                    </TableCell>
                    <TableCell className="text-right text-sm">
                      {acq.valuation_inr > 0 ? (
                        <span>₹{acq.valuation_inr.toLocaleString('en-IN')} Cr</span>
                      ) : (
                        <span className="text-muted-foreground">Concession</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right text-sm hidden sm:table-cell">
                      {acq.valuation_usd > 0 ? (
                        <span>${acq.valuation_usd}M</span>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={`text-[9px] px-2 py-0 border ${getStatusStyle(acq.status)}`}>
                        {acq.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      <Badge variant="outline" className="text-[9px] border-border/30">
                        {acq.sector}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Status Legend */}
      <Card className="glass-card border-0">
        <CardContent className="p-4">
          <h3 className="text-sm font-semibold mb-3">Status Legend</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
              <div>
                <p className="text-xs font-medium">Active</p>
                <p className="text-[10px] text-muted-foreground">Currently operating</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-cyan-500" />
              <div>
                <p className="text-xs font-medium">Integrated</p>
                <p className="text-[10px] text-muted-foreground">Merged into parent</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-slate-500" />
              <div>
                <p className="text-xs font-medium">Demerged</p>
                <p className="text-[10px] text-muted-foreground">Spun off / separated</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div>
                <p className="text-xs font-medium">Pending Litigation</p>
                <p className="text-[10px] text-muted-foreground">Legal disputes active</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
