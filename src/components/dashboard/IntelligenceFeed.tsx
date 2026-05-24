'use client';

import { useState, useMemo, useEffect } from 'react';
import { newsArticles as mockNews, type NewsArticle } from '@/lib/mock-data';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Search,
  ShieldCheck,
  AlertTriangle,
  Filter,
  ExternalLink,
  Newspaper,
} from 'lucide-react';

function getTagStyle(tag: NewsArticle['tag']): string {
  switch (tag) {
    case 'Verified':
      return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    case 'Unverified':
      return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    case 'Requires Verification':
      return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    case 'Pro-Group':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
}

function getTierColor(tier: number): string {
  switch (tier) {
    case 1:
      return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    case 2:
      return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    case 3:
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
}

function getBiasColor(level: string): string {
  switch (level) {
    case 'Low':
      return 'text-emerald-400';
    case 'Medium':
      return 'text-amber-400';
    case 'High':
      return 'text-red-400';
    default:
      return 'text-muted-foreground';
  }
}

function getValidationColor(score: number): string {
  if (score >= 0.8) return 'bg-emerald-500';
  if (score >= 0.6) return 'bg-amber-500';
  return 'bg-red-500';
}

export default function IntelligenceFeed() {
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>(mockNews);
  const [searchQuery, setSearchQuery] = useState('');
  const [validationThreshold, setValidationThreshold] = useState(0.8);
  const [selectedTier, setSelectedTier] = useState<string>('all');
  const [selectedTag, setSelectedTag] = useState<string>('all');

  useEffect(() => {
    fetch('/api/news')
      .then((r) => r.json())
      .then((d) => {
        if (d.data && Array.isArray(d.data) && d.data.length > 0) {
          setNewsArticles(d.data);
        }
      })
      .catch(() => {}); // Keep mock data on error
  }, []);

  const filteredArticles = useMemo(() => {
    return newsArticles.filter((article) => {
      if (article.validation_score < validationThreshold) return false;
      if (selectedTier !== 'all' && article.source_tier !== parseInt(selectedTier)) return false;
      if (selectedTag !== 'all' && article.tag !== selectedTag) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          article.title.toLowerCase().includes(q) ||
          article.source.toLowerCase().includes(q) ||
          article.keywords.some((k) => k.toLowerCase().includes(q)) ||
          article.related_companies.some((c) => c.toLowerCase().includes(q))
        );
      }
      return true;
    });
  }, [newsArticles, searchQuery, validationThreshold, selectedTier, selectedTag]);

  return (
    <div className="space-y-6">
      {/* Filter Bar */}
      <Card className="glass-card border-0">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Filter className="h-4 w-4 text-emerald-400" />
            <h3 className="text-sm font-semibold">Filter Intelligence</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search articles, keywords, companies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-muted/20 border-border/30 h-9 text-sm"
              />
            </div>

            {/* Validation Score Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">Validation ≥ </span>
                <span className="font-medium">{(validationThreshold * 100).toFixed(0)}%</span>
              </div>
              <Slider
                value={[validationThreshold]}
                onValueChange={(v) => setValidationThreshold(v[0])}
                min={0}
                max={1}
                step={0.05}
                className="w-full"
              />
            </div>

            {/* Source Tier */}
            <Select value={selectedTier} onValueChange={setSelectedTier}>
              <SelectTrigger className="bg-muted/20 border-border/30 h-9 text-sm w-full">
                <SelectValue placeholder="Source Tier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tiers</SelectItem>
                <SelectItem value="1">Tier 1 - International Wire</SelectItem>
                <SelectItem value="2">Tier 2 - National Media</SelectItem>
                <SelectItem value="3">Tier 3 - Local/Partisan</SelectItem>
              </SelectContent>
            </Select>

            {/* Tag Filter */}
            <Select value={selectedTag} onValueChange={setSelectedTag}>
              <SelectTrigger className="bg-muted/20 border-border/30 h-9 text-sm w-full">
                <SelectValue placeholder="Tag" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tags</SelectItem>
                <SelectItem value="Verified">✓ Verified</SelectItem>
                <SelectItem value="Unverified">? Unverified</SelectItem>
                <SelectItem value="Requires Verification">⚠ Requires Verification</SelectItem>
                <SelectItem value="Pro-Group">⚡ Pro-Group</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="mt-3 text-xs text-muted-foreground">
            Showing {filteredArticles.length} of {newsArticles.length} articles
          </div>
        </CardContent>
      </Card>

      {/* Articles Feed */}
      <div className="space-y-3">
        {filteredArticles.map((article) => {
          const hasTier1Corroboration = article.source_tier === 1;
          const showBiasWarning = article.bias_risk_level === 'High' || !hasTier1Corroboration;

          return (
            <Card
              key={article.id}
              className="glass-card glass-card-hover border-0 transition-all duration-300"
            >
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Title & Source */}
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="font-semibold text-sm leading-tight flex-1">
                        {article.title}
                      </h3>
                      <Button variant="ghost" size="sm" className="h-7 w-7 p-0 flex-shrink-0">
                        <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <Newspaper className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">{article.source}</span>
                      <span className="text-xs text-muted-foreground">•</span>
                      <span className="text-xs text-muted-foreground">{article.published_at}</span>
                    </div>
                  </div>

                  {/* Tags & Badges */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge className={`text-[9px] px-2 py-0 border ${getTagStyle(article.tag)}`}>
                      {article.tag === 'Verified' && <ShieldCheck className="h-2.5 w-2.5 mr-0.5" />}
                      {article.tag}
                    </Badge>
                    <Badge className={`text-[9px] px-2 py-0 border ${getTierColor(article.source_tier)}`}>
                      Tier {article.source_tier}
                    </Badge>
                    {showBiasWarning && (
                      <Badge className="text-[9px] px-2 py-0 border bg-red-500/20 text-red-400 border-red-500/30">
                        <AlertTriangle className="h-2.5 w-2.5 mr-0.5" />
                        Bias Detected
                      </Badge>
                    )}
                    <Badge
                      variant="outline"
                      className={`text-[9px] px-2 py-0 border ${getBiasColor(article.bias_risk_level)}`}
                    >
                      Risk: {article.bias_risk_level}
                    </Badge>
                  </div>

                  {/* Validation Score Bar */}
                  <div>
                    <div className="flex justify-between text-[10px] mb-1">
                      <span className="text-muted-foreground">Validation Score</span>
                      <span className="font-medium">{(article.validation_score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted/30 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${getValidationColor(article.validation_score)}`}
                        style={{ width: `${article.validation_score * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Content Snippet */}
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {article.content_snippet}
                  </p>

                  {/* Related Companies & Keywords */}
                  <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-border/30">
                    {article.related_companies.map((company) => (
                      <Badge key={company} variant="outline" className="text-[9px] border-emerald-500/20 text-emerald-400">
                        {company}
                      </Badge>
                    ))}
                    {article.keywords.map((kw) => (
                      <span key={kw} className="text-[9px] text-muted-foreground bg-muted/30 px-1.5 py-0.5 rounded">
                        #{kw}
                      </span>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}

        {filteredArticles.length === 0 && (
          <Card className="glass-card border-0">
            <CardContent className="p-8 text-center">
              <Search className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">No articles match your filters</p>
              <p className="text-xs text-muted-foreground mt-1">Try adjusting the validation threshold or changing filters</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
