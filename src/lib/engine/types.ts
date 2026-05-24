/**
 * AGSPE Engine Types - Shared types for the prediction engine system
 *
 * Reuses types from mock-data.ts where possible and adds engine-specific types.
 */

// Re-export data model types from mock-data
export type {
  Prediction,
  Financial,
  NewsArticle,
  LobbyingRecord,
  Acquisition,
} from '@/lib/mock-data';

// ── Source Trust Tier Definitions ──

export interface SourceTierInfo {
  tier: number;
  weight: number;
  tag?: string;
}

export type SourceTrustTier = 1 | 2 | 3;

export const SOURCE_TIERS: Record<string, SourceTierInfo> = {
  // Tier 1 - High Weight (0.9) - International / Highly Credible
  Reuters: { tier: 1, weight: 0.9 },
  'AP News': { tier: 1, weight: 0.9 },
  BBC: { tier: 1, weight: 0.9 },
  'Al Jazeera': { tier: 1, weight: 0.9 },
  OCCRP: { tier: 1, weight: 0.9 },
  Bloomberg: { tier: 1, weight: 0.9 },
  'Financial Times': { tier: 1, weight: 0.9 },

  // Tier 2 - Medium Weight (0.7) - Independent Indian Media
  'The Hindu': { tier: 2, weight: 0.7 },
  'Scroll.in': { tier: 2, weight: 0.7 },
  'The Wire': { tier: 2, weight: 0.7 },
  'Business Standard': { tier: 2, weight: 0.7 },
  'Economic and Political Weekly': { tier: 2, weight: 0.7 },
  'NDTV Profit': { tier: 2, weight: 0.7 },

  // Tier 3 - Low Weight (0.3) - Pro-Group / Requires Verification
  NDTV: { tier: 3, weight: 0.3, tag: 'Requires Verification' },
  'Times Now': { tier: 3, weight: 0.3, tag: 'Requires Verification' },
  'Republic TV': { tier: 3, weight: 0.3, tag: 'Requires Verification' },
  'Zee News': { tier: 3, weight: 0.3, tag: 'Requires Verification' },
  'Adani Group PR': { tier: 3, weight: 0.3, tag: 'Pro-Group' },
};

// Tier weight constants
export const TIER_WEIGHTS: Record<SourceTrustTier, number> = {
  1: 0.9,
  2: 0.7,
  3: 0.3,
};

// ── Validation Types ──

export interface SourceInput {
  name: string;
  tier: number;
  weight: number;
  agrees: boolean;
  timestamp?: Date;
  is_pro_group: boolean;
}

export interface ValidationFlags {
  tier_3_only: boolean;
  no_tier_1_corroboration: boolean;
  tier_1_contradiction: boolean;
  manual_review_required: boolean;
  single_source: boolean;
  cross_verification_passed: boolean;
  insufficient_sources: boolean;
  pro_group_source_only: boolean;
}

export interface ValidationResult {
  validation_score: number;
  bias_risk_level: 'Low' | 'Medium' | 'High';
  flags: string[];
  cross_verification_status: string;
  tier_1_corroboration: boolean;
  contradiction_detected: boolean;
  claim: string;
  manual_review_required: boolean;
}

// ── Prediction Types ──

export interface FinancialIndicators {
  debt_to_equity: number;
  capex_commitment_inr: number;
  stock_volatility_30d: number;
  revenue_growth_yoy: number;
  profit_margin: number;
  market_cap_inr: number;
  free_cash_flow_inr: number;
}

export interface PoliticalEvent {
  event_type: string;
  description: string;
  date: string;
  relevance_score: number;
  source_tier: number;
  impact?: number;
}

export interface PredictionInput {
  financial_data: Record<string, unknown>[];
  political_events: PoliticalEvent[];
  historical_acquisitions: Record<string, unknown>[];
  current_context: Record<string, unknown>;
}

export interface AcquisitionPattern {
  name: string;
  stages: string[];
  typical_duration_months: number;
  confidence_base: number;
}

export interface PolicyCorrelation {
  trigger: string;
  predicted_action: string;
  base_probability: number;
  evidence: string[];
}

// ── Bias Detection Types ──

export interface SourceReliability {
  name: string;
  tier: number;
  total_articles: number;
  validated_articles: number;
  retracted_articles: number;
  average_validation_score: number;
  bias_incidents: number;
  last_updated: string | null;
}

export interface BiasAnalysisResult {
  article_id: string;
  source: string;
  source_tier: number;
  bias_score: number;
  bias_risk_level: 'Low' | 'Medium' | 'High';
  pro_group_language_detected: boolean;
  pro_group_indicators: string[];
  negative_indicators: string[];
  source_reliability_score: number;
  warning: string | null;
}

// ── Data Fetcher Types ──

export interface DataRefreshResult {
  timestamp: string;
  sources_fetched: number;
  articles_count: number;
  errors: string[];
  duration_ms: number;
}

// ── Data Store Types ──

export interface DataCache {
  predictions: import('@/lib/mock-data').Prediction[];
  financials: import('@/lib/mock-data').Financial[];
  news: import('@/lib/mock-data').NewsArticle[];
  lobbying: import('@/lib/mock-data').LobbyingRecord[];
  acquisitions: import('@/lib/mock-data').Acquisition[];
  lastRefresh: string | null;
}

export interface StoreStatus {
  lastRefresh: string | null;
  dataCounts: {
    predictions: number;
    financials: number;
    news: number;
    lobbying: number;
    acquisitions: number;
  };
  systemStatus: 'operational' | 'degraded' | 'error';
  uptime: string;
}

// ── Validation Config ──

export const VALIDATION_CONFIG = {
  cross_verification_window_hours: 24,
  tier_3_max_score_without_tier1: 0.3,
  pro_group_max_score: 0.2,
  contradiction_confidence_reduction: 0.5,
  single_source_reduction: 0.8,
  high_risk_threshold: 0.7,
  medium_risk_threshold: 0.4,
} as const;
