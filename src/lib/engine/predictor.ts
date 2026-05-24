/**
 * AGSPE Prediction Engine - Hybrid Logic Engine
 *
 * Ported from backend/app/models/predictor.py
 *
 * Combines statistical trends and heuristic rules to generate
 * probabilistic predictions on Adani Group future business moves
 * with confidence intervals and timelines.
 */

import type {
  AcquisitionPattern,
  PolicyCorrelation,
  Prediction,
} from './types';

// ── Known Patterns ──

export const ACQUISITION_PATTERNS: Record<string, AcquisitionPattern> = {
  standard_acquisition: {
    name: 'Standard Acquisition Cycle',
    stages: [
      'Fragmented Sector',
      'Large Acquisition',
      'Consolidation',
      'Listing/Demerger',
    ],
    typical_duration_months: 18,
    confidence_base: 0.7,
  },
  green_energy_expansion: {
    name: 'Green Energy Expansion',
    stages: [
      'Government Renewable Target Announced',
      'Policy Incentives Released',
      'Adani Green Capacity Announcement',
      'JV/Partnership Formation',
      'Project Commissioning',
    ],
    typical_duration_months: 24,
    confidence_base: 0.75,
  },
  port_infrastructure: {
    name: 'Port & Infrastructure Play',
    stages: [
      'Government Infrastructure Push',
      'Bid Preparation/Consortium',
      'Concession Win',
      'Capacity Expansion',
    ],
    typical_duration_months: 12,
    confidence_base: 0.8,
  },
  distressed_asset_acquisition: {
    name: 'Distressed Asset Acquisition',
    stages: [
      'IBCP/NCLT Proceedings',
      'Asset Valuation',
      'Adani Bid Submission',
      'Creditor Approval',
      'Takeover & Restructuring',
    ],
    typical_duration_months: 15,
    confidence_base: 0.65,
  },
};

export const POLICY_CORRELATIONS: Record<string, PolicyCorrelation> = {
  infrastructure_push: {
    trigger: 'BJP/NDA announces infrastructure push',
    predicted_action: 'Adani port/airport bid win',
    base_probability: 0.82,
    evidence: [
      'Historical correlation: 2019-2026 infrastructure budgets',
      'Adani Ports won 6 of 8 major port concessions since 2019',
      'Airport privatization aligned with Adani wins',
    ],
  },
  renewable_target: {
    trigger: 'Government raises renewable energy target',
    predicted_action: 'Adani Green capacity expansion / JV',
    base_probability: 0.78,
    evidence: [
      '500 GW renewable target by 2030',
      'Adani Green committed 45 GW by 2030',
      'TotalEnergies JV expansion pattern',
    ],
  },
  defense_policy: {
    trigger: 'Defense procurement policy announced',
    predicted_action: 'Adani Defense contract win',
    base_probability: 0.65,
    evidence: [
      'Make in India defense push',
      'Adani Defense & Aerospace established 2015',
      'DRDO partnerships pattern',
    ],
  },
  cement_consolidation: {
    trigger: 'Infrastructure/housing policy boost',
    predicted_action: 'Ambuja/ACC capacity expansion or acquisition',
    base_probability: 0.72,
    evidence: [
      'Post-ACC/Ambuja acquisition consolidation',
      '140 MTPA target by 2028',
      'Greenfield plant announcements',
    ],
  },
};

interface PatternMatch {
  name: string;
  predicted_action: string;
  category: string;
  confidence_base: number;
  evidence: string[];
  sources: string[];
}

interface FinancialSignals {
  composite: number;
  debt_signal: number;
  capex_signal: number;
  volatility_signal: number;
  growth_signal: number;
}

export class PredictionEngine {
  private financialWeight = 0.35;
  private politicalWeight = 0.35;
  private patternWeight = 0.30;

  /**
   * Generate probabilistic predictions for Adani Group business moves.
   */
  generatePredictions(
    financialData?: Array<Record<string, unknown>>,
    politicalEvents?: Array<Record<string, unknown>>,
    historicalAcquisitions?: Array<Record<string, unknown>>,
    currentContext?: Record<string, unknown>
  ): Prediction[] {
    const predictions: Prediction[] = [];

    // Use provided data or defaults
    const finData = financialData || this.getDefaultFinancialData();
    const polEvents = politicalEvents || this.getDefaultPoliticalEvents();
    const acquisitions =
      historicalAcquisitions || this.getDefaultAcquisitions();
    const context = currentContext || {
      date: new Date().toISOString(),
      market_condition: 'normal',
    };

    // Calculate component signals
    const financialSignals = this.calculateFinancialSignal(finData);
    const politicalAlignment = this.calculatePoliticalAlignment(polEvents);
    const patternMatches = this.matchAcquisitionPatterns(acquisitions, context);

    // Generate predictions from each pattern match
    for (const pattern of patternMatches) {
      const timeline = this.generateTimeline(
        financialSignals.composite,
        politicalAlignment,
        pattern.confidence_base
      );

      const confidence = this.calculateConfidence(
        financialSignals.composite,
        politicalAlignment,
        pattern.confidence_base
      );

      const id = `pred-${predictions.length + 1}`.padStart(7, '0');

      predictions.push({
        id,
        likely_action: pattern.predicted_action,
        category: pattern.category,
        timeline_start: timeline[0],
        timeline_end: timeline[1],
        confidence_score: Math.round(confidence * 1000) / 10,
        supporting_evidence: pattern.evidence,
        risk_factors: this.identifyRiskFactors(
          financialSignals,
          politicalAlignment
        ),
        financial_signal: financialSignals.composite,
        political_alignment: politicalAlignment,
        pattern_match: pattern.name,
        validation_score: Math.min(confidence, 1.0),
      });
    }

    // Add policy-correlation predictions
    for (const [corrKey, corr] of Object.entries(POLICY_CORRELATIONS)) {
      const confidence = this.calculateConfidence(
        financialSignals.composite,
        politicalAlignment,
        corr.base_probability
      );

      const timeline = this.generateTimeline(
        financialSignals.composite,
        politicalAlignment,
        corr.base_probability
      );

      predictions.push({
        id: `pred-policy-${corrKey}`,
        likely_action: corr.predicted_action,
        category: 'Policy Correlation',
        timeline_start: timeline[0],
        timeline_end: timeline[1],
        confidence_score: Math.round(confidence * 1000) / 10,
        supporting_evidence: corr.evidence,
        risk_factors: this.identifyRiskFactors(
          financialSignals,
          politicalAlignment
        ),
        financial_signal: financialSignals.composite,
        political_alignment: politicalAlignment,
        pattern_match: corr.trigger,
        validation_score: Math.min(confidence, 1.0),
      });
    }

    // Sort by confidence score descending
    predictions.sort((a, b) => b.confidence_score - a.confidence_score);

    return predictions;
  }

  /**
   * Analyze financial indicators to generate prediction signals.
   */
  private calculateFinancialSignal(
    financialData: Array<Record<string, unknown>>
  ): FinancialSignals {
    if (!financialData || financialData.length === 0) {
      return {
        composite: 0.5,
        debt_signal: 0.5,
        capex_signal: 0.5,
        volatility_signal: 0.5,
        growth_signal: 0.5,
      };
    }

    const totalMarketCap = financialData.reduce(
      (sum, f) => sum + ((f.market_cap_inr as number) || 0),
      0
    );
    const safeTotalMarketCap = totalMarketCap || 1;

    // Weighted average debt-to-equity (by market cap)
    const weightedDTE =
      financialData.reduce(
        (sum, f) =>
          sum +
          ((f.debt_to_equity as number) || 1.0) *
            ((f.market_cap_inr as number) || 0),
        0
      ) / safeTotalMarketCap;

    // Debt signal: Lower D/E is better (inverse relationship)
    const debtSignal = Math.max(0.0, Math.min(1.0, 1.0 - weightedDTE / 5.0));

    // Capex signal: Higher capex commitment suggests expansion intent
    const totalCapex = financialData.reduce(
      (sum, f) => sum + ((f.capex_commitment_inr as number) || 0),
      0
    );
    const capexSignal =
      totalCapex > 0 ? Math.min(1.0, totalCapex / 200000) : 0.3;

    // Volatility signal: Lower volatility = more stable = higher confidence
    const avgVolatility =
      financialData.reduce(
        (sum, f) => sum + ((f.stock_volatility_30d as number) || 30),
        0
      ) / financialData.length;
    const volatilitySignal = Math.max(
      0.0,
      Math.min(1.0, 1.0 - avgVolatility / 60.0)
    );

    // Revenue growth signal
    const avgGrowth =
      financialData.reduce(
        (sum, f) => sum + ((f.revenue_growth_yoy as number) || 0.1),
        0
      ) / financialData.length;
    const growthSignal = Math.min(1.0, Math.max(0.0, avgGrowth / 0.3));

    // Composite financial signal
    const composite =
      debtSignal * 0.25 +
      capexSignal * 0.3 +
      volatilitySignal * 0.2 +
      growthSignal * 0.25;

    return {
      composite: Math.round(composite * 10000) / 10000,
      debt_signal: Math.round(debtSignal * 10000) / 10000,
      capex_signal: Math.round(capexSignal * 10000) / 10000,
      volatility_signal: Math.round(volatilitySignal * 10000) / 10000,
      growth_signal: Math.round(growthSignal * 10000) / 10000,
    };
  }

  /**
   * Calculate political alignment score based on proximity to
   * government announcements and policy initiatives.
   */
  private calculatePoliticalAlignment(
    events: Array<Record<string, unknown>>
  ): number {
    if (!events || events.length === 0) return 0.5;

    let weightedSum = 0.0;
    let totalWeight = 0.0;

    const tierWeightMap: Record<number, number> = { 1: 1.0, 2: 0.7, 3: 0.3 };

    for (const event of events) {
      const relevance = (event.relevance_score as number) || 0.5;
      const tier = (event.source_tier as number) || 3;
      const tierWeight = tierWeightMap[tier] || 0.3;
      const weight = relevance * tierWeight;

      // Positive events increase alignment, negative decrease
      const impact = (event.impact as number) || 0.5;
      weightedSum += weight * impact;
      totalWeight += weight;
    }

    if (totalWeight === 0) return 0.5;

    const alignment = weightedSum / totalWeight;
    return Math.round(Math.max(0.0, Math.min(1.0, alignment)) * 10000) / 10000;
  }

  /**
   * Match current market state to known acquisition/pattern templates.
   */
  private matchAcquisitionPatterns(
    acquisitions: Array<Record<string, unknown>>,
    _context: Record<string, unknown>
  ): PatternMatch[] {
    const matches: PatternMatch[] = [];

    // Analyze sector distribution of recent acquisitions
    const sectorCounts: Record<string, number> = {};
    for (const acq of acquisitions) {
      const sector = (acq.sector as string) || 'Unknown';
      sectorCounts[sector] = (sectorCounts[sector] || 0) + 1;
    }

    // Port/Infrastructure pattern
    if (
      (sectorCounts['Ports'] || 0) + (sectorCounts['Infrastructure'] || 0) >=
      3
    ) {
      matches.push({
        name: ACQUISITION_PATTERNS.port_infrastructure.name,
        predicted_action: 'New Port or Airport Concession Win',
        category: 'Infrastructure',
        confidence_base: ACQUISITION_PATTERNS.port_infrastructure.confidence_base,
        evidence: [
          'Multiple infrastructure acquisitions in recent years',
          'Government privatization pipeline active',
          'Adani Ports dominant market position',
        ],
        sources: ['Acquisition pattern analysis', 'Infrastructure sector data'],
      });
    }

    // Green Energy pattern
    if (
      (sectorCounts['Green Energy'] || 0) +
        (sectorCounts['Renewable'] || 0) +
        (sectorCounts['Renewable Energy'] || 0) >=
      2
    ) {
      matches.push({
        name: ACQUISITION_PATTERNS.green_energy_expansion.name,
        predicted_action: 'Green Hydrogen JV or Solar Capacity Expansion',
        category: 'Green Energy',
        confidence_base:
          ACQUISITION_PATTERNS.green_energy_expansion.confidence_base,
        evidence: [
          'Government 500 GW renewable target',
          'Adani Green 45 GW target by 2030',
          'TotalEnergies partnership expansion',
        ],
        sources: ['Green energy sector data', 'Policy correlation'],
      });
    }

    // Distressed asset pattern
    if (
      (sectorCounts['Cement'] || 0) + (sectorCounts['Metals'] || 0) >=
      2
    ) {
      matches.push({
        name: ACQUISITION_PATTERNS.distressed_asset_acquisition.name,
        predicted_action: 'Distressed Asset Bid in Cement or Metals',
        category: 'M&A',
        confidence_base:
          ACQUISITION_PATTERNS.distressed_asset_acquisition.confidence_base,
        evidence: [
          'Track record of distressed asset acquisitions (ACC, Ambuja)',
          'NCLT pipeline active with stressed assets',
          'Consolidation strategy in cement sector',
        ],
        sources: ['M&A pattern analysis', 'NCLT proceedings data'],
      });
    }

    // Digital/Telecom pattern (emerging)
    if (
      (sectorCounts['Digital'] || 0) +
        (sectorCounts['Technology'] || 0) +
        (sectorCounts['Digital / Technology'] || 0) >=
      1
    ) {
      matches.push({
        name: 'Digital Expansion',
        predicted_action: 'Data Center or Digital Infrastructure Investment',
        category: 'Digital Infrastructure',
        confidence_base: 0.55,
        evidence: [
          'Adani Data Network license acquired',
          'Growing data center demand in India',
          '5G rollout creating new opportunities',
        ],
        sources: ['Digital sector analysis', 'Telecom licensing data'],
      });
    }

    // If no specific pattern matched, add a general expansion prediction
    if (matches.length === 0) {
      matches.push({
        name: ACQUISITION_PATTERNS.standard_acquisition.name,
        predicted_action: 'Sector Expansion or New Acquisition',
        category: 'General',
        confidence_base: 0.5,
        evidence: [
          'Historical expansion pattern continues',
          'Group diversification strategy ongoing',
        ],
        sources: ['General pattern analysis'],
      });
    }

    return matches;
  }

  /**
   * Generate a confidence interval timeline for a prediction.
   */
  private generateTimeline(
    financialSignal: number,
    politicalAlignment: number,
    patternConfidence: number
  ): [string, string] {
    const combinedSignal =
      (financialSignal + politicalAlignment + patternConfidence) / 3;

    // Calculate months from now
    const minMonths = Math.max(3, Math.floor(12 * (1 - combinedSignal)));
    const maxMonths = minMonths + Math.max(3, Math.floor(6 * (1 - combinedSignal)));

    const now = new Date();
    const startDate = new Date(
      now.getTime() + minMonths * 30 * 24 * 60 * 60 * 1000
    );
    const endDate = new Date(
      now.getTime() + maxMonths * 30 * 24 * 60 * 60 * 1000
    );

    return [this.dateToQuarter(startDate), this.dateToQuarter(endDate)];
  }

  /**
   * Calculate overall prediction confidence score.
   */
  private calculateConfidence(
    financialSignal: number,
    politicalAlignment: number,
    patternConfidence: number
  ): number {
    let confidence =
      financialSignal * this.financialWeight +
      politicalAlignment * this.politicalWeight +
      patternConfidence * this.patternWeight;

    // Add small random variation for realism (±5%)
    const variation = (Math.random() - 0.5) * 0.1;
    confidence = Math.max(0.0, Math.min(1.0, confidence + variation));

    return Math.round(confidence * 10000) / 10000;
  }

  /**
   * Identify risk factors that could affect prediction accuracy.
   */
  private identifyRiskFactors(
    financialSignals: FinancialSignals,
    politicalAlignment: number
  ): string[] {
    const risks: string[] = [];

    if (financialSignals.debt_signal < 0.4) {
      risks.push('High debt-to-equity ratio across group companies');
    }
    if (financialSignals.volatility_signal < 0.4) {
      risks.push('Elevated stock price volatility');
    }
    if (politicalAlignment < 0.4) {
      risks.push('Weakening political alignment score');
    }
    if (politicalAlignment > 0.8) {
      risks.push('Over-reliance on political connections - regulatory risk');
    }

    risks.push('Regulatory scrutiny risk (SEBI/Hindenburg aftermath)');
    risks.push('Global commodity price fluctuation risk');
    risks.push('Currency risk (INR depreciation impact on USD debt)');

    return risks;
  }

  /**
   * Convert a date to quarter string format (e.g., 'Q3 2026').
   */
  private dateToQuarter(date: Date): string {
    const quarter = Math.floor(date.getMonth() / 3) + 1;
    return `Q${quarter} ${date.getFullYear()}`;
  }

  private getDefaultFinancialData(): Array<Record<string, unknown>> {
    return [
      {
        company: 'Adani Enterprises',
        debt_to_equity: 1.2,
        capex_commitment_inr: 55000,
        stock_volatility_30d: 25,
        revenue_growth_yoy: 0.18,
        market_cap_inr: 280000,
      },
      {
        company: 'Adani Ports & SEZ',
        debt_to_equity: 0.9,
        capex_commitment_inr: 30000,
        stock_volatility_30d: 18,
        revenue_growth_yoy: 0.22,
        market_cap_inr: 310000,
      },
      {
        company: 'Adani Green Energy',
        debt_to_equity: 2.1,
        capex_commitment_inr: 75000,
        stock_volatility_30d: 35,
        revenue_growth_yoy: 0.35,
        market_cap_inr: 220000,
      },
      {
        company: 'Adani Total Gas',
        debt_to_equity: 0.5,
        capex_commitment_inr: 15000,
        stock_volatility_30d: 20,
        revenue_growth_yoy: 0.12,
        market_cap_inr: 260000,
      },
      {
        company: 'Adani Power',
        debt_to_equity: 1.8,
        capex_commitment_inr: 40000,
        stock_volatility_30d: 30,
        revenue_growth_yoy: 0.25,
        market_cap_inr: 180000,
      },
    ];
  }

  private getDefaultPoliticalEvents(): Array<Record<string, unknown>> {
    return [
      {
        event_type: 'policy',
        description: 'Union Budget 2026 infrastructure allocation',
        relevance_score: 0.9,
        source_tier: 1,
        impact: 0.85,
      },
      {
        event_type: 'regulation',
        description: 'SEBI enhanced disclosure requirements',
        relevance_score: 0.8,
        source_tier: 1,
        impact: 0.3,
      },
      {
        event_type: 'policy',
        description: 'Green hydrogen policy incentives',
        relevance_score: 0.85,
        source_tier: 1,
        impact: 0.8,
      },
      {
        event_type: 'political',
        description: 'State election outcomes affecting project approvals',
        relevance_score: 0.6,
        source_tier: 2,
        impact: 0.65,
      },
      {
        event_type: 'regulation',
        description: 'Airport privatization Phase 3 announced',
        relevance_score: 0.9,
        source_tier: 1,
        impact: 0.9,
      },
    ];
  }

  private getDefaultAcquisitions(): Array<Record<string, unknown>> {
    return [
      { company_acquired: 'ACC Ltd', sector: 'Cement', year: 2022 },
      { company_acquired: 'Ambuja Cements', sector: 'Cement', year: 2022 },
      {
        company_acquired: 'Jaypee Infratech',
        sector: 'Infrastructure',
        year: 2023,
      },
      { company_acquired: 'DB Power', sector: 'Power', year: 2023 },
      {
        company_acquired: 'Warora-Hingoni MW',
        sector: 'Power',
        year: 2024,
      },
      {
        company_acquired: 'ITD Cementation',
        sector: 'Infrastructure',
        year: 2024,
      },
      { company_acquired: 'NDTV', sector: 'Media', year: 2022 },
      {
        company_acquired: 'Haigreeva Inc',
        sector: 'Green Energy',
        year: 2025,
      },
    ];
  }
}
