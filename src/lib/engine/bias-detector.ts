/**
 * AGSPE Bias Detector - Detects media bias indicators,
 * flags pro-group language, and tracks source reliability over time.
 *
 * Ported from backend/app/models/bias_detector.py
 */

import { SOURCE_TIERS } from './types';
import type { SourceReliability, BiasAnalysisResult } from './types';

// Pro-group language patterns for detection
const PRO_GROUP_PHRASES = [
  'set to revolutionize',
  'game-changing',
  'unprecedented',
  'world-class',
  'visionary',
  'transformative',
  'groundbreaking',
  'trailblazing',
  'pioneering',
  'ambitious roadmap',
  'strongly denied',
  'categorically denied',
  'baseless allegations',
  'misleading reports',
  'speculative and misleading',
  'full compliance',
  'robust governance',
  'industry-leading',
  'market leader',
  'dominant position',
  'strategic advantage',
];

const NEGATIVE_PHRASES = [
  'controversial',
  'alleged',
  'scrutiny',
  'investigation',
  'wrongdoing',
  'fraud',
  'manipulation',
  'offshore',
  'shell companies',
  'conflict of interest',
  'regulatory violation',
  'governance concerns',
  'debt trap',
  'crony capitalism',
];

interface LanguageResult {
  bias_score: number;
  is_likely_promotional: boolean;
  detected_pro_phrases: string[];
  detected_neg_phrases: string[];
}

/**
 * Detect pro-group language patterns in text.
 * Ported from backend/app/utils/text_processing.py
 */
function detectProGroupLanguage(text: string): LanguageResult {
  const lowerText = text.toLowerCase();

  const detectedPro: string[] = [];
  const detectedNeg: string[] = [];

  for (const phrase of PRO_GROUP_PHRASES) {
    if (lowerText.includes(phrase.toLowerCase())) {
      detectedPro.push(phrase);
    }
  }

  for (const phrase of NEGATIVE_PHRASES) {
    if (lowerText.includes(phrase.toLowerCase())) {
      detectedNeg.push(phrase);
    }
  }

  // Calculate bias score
  const proScore = Math.min(detectedPro.length * 0.15, 0.6);
  const negScore = Math.min(detectedNeg.length * 0.1, 0.4);
  const biasScore = Math.max(proScore - negScore * 0.3, 0);

  return {
    bias_score: Math.round(biasScore * 1000) / 1000,
    is_likely_promotional: detectedPro.length > 1 || (detectedPro.length > 0 && detectedNeg.length === 0),
    detected_pro_phrases: detectedPro,
    detected_neg_phrases: detectedNeg,
  };
}

export class BiasDetector {
  private sourceReliability: Map<string, SourceReliability>;

  constructor() {
    this.sourceReliability = new Map();
    this.initDefaultSources();
  }

  private initDefaultSources(): void {
    const defaultSources: Array<[string, number]> = [
      ['Reuters', 1], ['AP News', 1], ['BBC', 1],
      ['Al Jazeera', 1], ['OCCRP', 1], ['Bloomberg', 1],
      ['Financial Times', 1],
      ['The Hindu', 2], ['Scroll.in', 2], ['The Wire', 2],
      ['Business Standard', 2],
      ['NDTV', 3], ['Times Now', 3], ['Republic TV', 3],
      ['Zee News', 3], ['Adani Group PR', 3],
    ];

    const avgValidationByTier: Record<number, number> = { 1: 0.85, 2: 0.70, 3: 0.35 };

    for (const [name, tier] of defaultSources) {
      this.sourceReliability.set(name, {
        name,
        tier,
        total_articles: 0,
        validated_articles: 0,
        retracted_articles: 0,
        average_validation_score: avgValidationByTier[tier] || 0.3,
        bias_incidents: 0,
        last_updated: new Date().toISOString(),
      });
    }
  }

  /**
   * Calculate reliability score for a source based on historical performance.
   */
  private getReliabilityScore(name: string): number {
    const rel = this.sourceReliability.get(name);
    if (!rel || rel.total_articles === 0) return 0.5;

    const validationRate = rel.validated_articles / rel.total_articles;
    const retractionPenalty = rel.retracted_articles * 0.1;
    const biasPenalty = rel.bias_incidents * 0.05;
    let score = validationRate * 0.6 + rel.average_validation_score * 0.4;
    score -= retractionPenalty + biasPenalty;

    return Math.max(0.0, Math.min(1.0, score));
  }

  /**
   * Analyze an article for bias indicators.
   */
  analyzeArticle(article: {
    id?: string;
    title?: string;
    content_snippet?: string;
    source?: string;
    source_tier?: number;
    validation_score?: number;
  }): BiasAnalysisResult {
    const text = `${article.title || ''} ${article.content_snippet || ''}`;
    const source = article.source || 'Unknown';
    const tier = article.source_tier || 3;

    // Detect pro-group language
    const languageResult = detectProGroupLanguage(text);

    // Calculate source bias factor
    const sourceBiasFactor = 1.0 - this.getReliabilityScore(source);

    // Combined bias score
    const tierWeightMap: Record<number, number> = { 1: 0.9, 2: 0.7, 3: 0.3 };
    const biasScore =
      languageResult.bias_score * 0.4 +
      sourceBiasFactor * 0.3 +
      (1.0 - (tierWeightMap[tier] || 0.3)) * 0.3;

    // Determine bias risk
    let biasRisk: 'Low' | 'Medium' | 'High';
    if (biasScore > 0.6) {
      biasRisk = 'High';
    } else if (biasScore > 0.3) {
      biasRisk = 'Medium';
    } else {
      biasRisk = 'Low';
    }

    // Add warnings for high-risk cases
    let warning: string | null = null;
    if (tier === 3 && languageResult.is_likely_promotional) {
      warning = 'BIAS_DETECTED: Pro-group language in Tier 3 source - requires Tier 1 corroboration';
    } else if (tier === 3) {
      warning = 'REQUIRES_VERIFICATION: Tier 3 source lacks independent corroboration';
    }

    const result: BiasAnalysisResult = {
      article_id: article.id || 'unknown',
      source,
      source_tier: tier,
      bias_score: Math.round(biasScore * 1000) / 1000,
      bias_risk_level: biasRisk,
      pro_group_language_detected: languageResult.is_likely_promotional,
      pro_group_indicators: languageResult.detected_pro_phrases,
      negative_indicators: languageResult.detected_neg_phrases,
      source_reliability_score: this.getReliabilityScore(source),
      warning,
    };

    // Update source reliability
    this.updateSourceReliability(source, article, result);

    return result;
  }

  private updateSourceReliability(
    source: string,
    article: { source_tier?: number; validation_score?: number },
    biasResult: BiasAnalysisResult
  ): void {
    if (!this.sourceReliability.has(source)) {
      this.sourceReliability.set(source, {
        name: source,
        tier: article.source_tier || 3,
        total_articles: 0,
        validated_articles: 0,
        retracted_articles: 0,
        average_validation_score: 0.5,
        bias_incidents: 0,
        last_updated: new Date().toISOString(),
      });
    }

    const rel = this.sourceReliability.get(source)!;
    rel.total_articles += 1;

    // Update average validation score
    const articleScore = article.validation_score || 0.5;
    rel.average_validation_score =
      (rel.average_validation_score * (rel.total_articles - 1) + articleScore) /
      rel.total_articles;

    if (biasResult.bias_risk_level === 'Low') {
      rel.validated_articles += 1;
    }
    if (biasResult.pro_group_language_detected) {
      rel.bias_incidents += 1;
    }

    rel.last_updated = new Date().toISOString();
  }

  /**
   * Get reliability report for all tracked sources.
   */
  getSourceReliabilityReport(): Array<{
    source: string;
    tier: number;
    reliability_score: number;
    total_articles: number;
    validated_articles: number;
    bias_incidents: number;
    average_validation_score: number;
  }> {
    const report: Array<{
      source: string;
      tier: number;
      reliability_score: number;
      total_articles: number;
      validated_articles: number;
      bias_incidents: number;
      average_validation_score: number;
    }> = [];

    for (const [name, rel] of this.sourceReliability.entries()) {
      report.push({
        source: name,
        tier: rel.tier,
        reliability_score: Math.round(this.getReliabilityScore(name) * 1000) / 1000,
        total_articles: rel.total_articles,
        validated_articles: rel.validated_articles,
        bias_incidents: rel.bias_incidents,
        average_validation_score: Math.round(rel.average_validation_score * 1000) / 1000,
      });
    }

    // Sort by reliability score descending
    report.sort((a, b) => b.reliability_score - a.reliability_score);

    return report;
  }
}
