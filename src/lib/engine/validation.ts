/**
 * AGSPE Validation Engine - Multi-Source Verification Algorithm
 *
 * Ported from backend/app/models/validation.py
 *
 * CRITICAL MODULE: Implements the multi-tier cross-source verification protocol
 * to mitigate media bias and ensure data reliability for predictions.
 *
 * Algorithm:
 * 1. Assign weights based on source trust tier (Tier 1=0.9, Tier 2=0.7, Tier 3=0.3)
 * 2. Cross-Verification Rule: Tier 3 claim requires Tier 1 corroboration within 24h
 * 3. Contradiction Detection: Tier 1 conflicts trigger manual review flag
 * 4. Output: validation_score (0.0-1.0) and bias_risk_level (Low/Medium/High)
 */

import {
  SOURCE_TIERS,
  VALIDATION_CONFIG,
  type SourceInput,
  type ValidationFlags,
  type ValidationResult,
} from './types';

interface AuditEntry {
  timestamp: string;
  step: string;
  detail: string;
  score: number;
  note: string;
}

export class ValidationEngine {
  private flags: ValidationFlags;
  private auditTrail: AuditEntry[];

  constructor() {
    this.flags = this.createEmptyFlags();
    this.auditTrail = [];
  }

  private createEmptyFlags(): ValidationFlags {
    return {
      tier_3_only: false,
      no_tier_1_corroboration: false,
      tier_1_contradiction: false,
      manual_review_required: false,
      single_source: false,
      cross_verification_passed: false,
      insufficient_sources: false,
      pro_group_source_only: false,
    };
  }

  /**
   * Validate a claim against multiple sources using the multi-tier algorithm.
   */
  validateClaim(
    claim: string,
    sources: Array<{
      name: string;
      tier?: number;
      weight?: number;
      agrees?: boolean;
      is_pro_group?: boolean;
      timestamp?: Date;
    }>,
    timestamps?: Record<string, Date>
  ): ValidationResult {
    this.flags = this.createEmptyFlags();
    this.auditTrail = [];

    if (!sources || sources.length === 0) {
      this.flags.insufficient_sources = true;
      const result = this.buildResult(0.0, claim);
      this.logDecision('validate_claim', claim, 0.0, 'No sources provided');
      return result;
    }

    // Parse source inputs
    const sourceInputs = this.parseSources(sources, timestamps);

    // Step 1: Calculate weighted validation score
    const rawScore = this.calculateWeightedScore(sourceInputs);

    // Step 2: Check cross-verification requirements
    this.checkCrossVerification(sourceInputs, timestamps);

    // Step 3: Detect contradictions between Tier 1 sources
    this.detectContradictions(sourceInputs);

    // Step 4: Check for special conditions
    this.checkSpecialConditions(sourceInputs);

    // Step 5: Apply adjustments based on flags
    const adjustedScore = this.applyAdjustments(rawScore);

    // Build final result
    const result = this.buildResult(adjustedScore, claim);

    // Log the decision
    this.logDecision(
      'validate_claim',
      claim,
      adjustedScore,
      `raw=${rawScore.toFixed(3)}, flags=${this.getFlagList().filter((f) => f).join(', ')}`
    );

    return result;
  }

  private parseSources(
    sources: Array<{
      name: string;
      tier?: number;
      weight?: number;
      agrees?: boolean;
      is_pro_group?: boolean;
      timestamp?: Date;
    }>,
    timestamps?: Record<string, Date>
  ): SourceInput[] {
    return sources.map((src) => {
      const known = SOURCE_TIERS[src.name] || {};
      const tier = src.tier ?? known.tier ?? 3;
      const weight = src.weight ?? known.weight ?? 0.3;
      const is_pro_group =
        src.is_pro_group ??
        ('tag' in known && (known as { tag?: string }).tag === 'Pro-Group');
      const ts =
        timestamps && src.name in timestamps ? timestamps[src.name] : undefined;

      return {
        name: src.name || 'Unknown',
        tier,
        weight,
        agrees: src.agrees ?? true,
        timestamp: ts,
        is_pro_group,
      };
    });
  }

  /**
   * Calculate weighted validation score based on source tiers and agreement.
   *
   * Formula:
   * score = sum(weight * agrees_indicator) / sum(weight)
   *
   * Where agrees_indicator is 1.0 for agree, -0.5 for disagree.
   */
  private calculateWeightedScore(sources: SourceInput[]): number {
    let totalWeight = 0.0;
    let weightedSum = 0.0;

    for (const src of sources) {
      totalWeight += src.weight;
      if (src.agrees) {
        weightedSum += src.weight * 1.0;
      } else {
        weightedSum += src.weight * -0.5;
      }
    }

    if (totalWeight === 0) return 0.0;

    const rawScore = weightedSum / totalWeight;

    // Normalize to 0.0 - 1.0 range
    // Raw score can be negative (disagreement), map to 0-1
    let normalized = (rawScore + 0.5) / 1.5;
    normalized = Math.max(0.0, Math.min(1.0, normalized));

    return Math.round(normalized * 10000) / 10000;
  }

  /**
   * Check if Tier 3 claims have Tier 1 corroboration within the verification window.
   */
  private checkCrossVerification(
    sources: SourceInput[],
    timestamps?: Record<string, Date>
  ): void {
    const tier3Sources = sources.filter((s) => s.tier === 3 && s.agrees);
    const tier1Sources = sources.filter((s) => s.tier === 1 && s.agrees);

    if (tier3Sources.length === 0) {
      // No Tier 3 sources requiring verification
      this.flags.cross_verification_passed = true;
      return;
    }

    if (tier1Sources.length === 0) {
      // Tier 3 claim with NO Tier 1 corroboration
      this.flags.no_tier_1_corroboration = true;
      this.logDecision(
        'cross_verification',
        'Tier 3 claim lacks Tier 1 corroboration',
        0,
        'Flagged as requiring verification'
      );
      return;
    }

    // Check if Tier 1 corroboration exists within time window
    if (timestamps) {
      let withinWindow = false;
      for (const t3 of tier3Sources) {
        if (t3.timestamp) {
          for (const t1 of tier1Sources) {
            if (t1.timestamp) {
              const timeDiff = Math.abs(
                t1.timestamp.getTime() - t3.timestamp.getTime()
              );
              const window =
                VALIDATION_CONFIG.cross_verification_window_hours * 3600 * 1000;
              if (timeDiff <= window) {
                withinWindow = true;
                break;
              }
            }
          }
        }
      }

      if (withinWindow) {
        this.flags.cross_verification_passed = true;
      } else {
        this.flags.no_tier_1_corroboration = true;
      }
    } else {
      // Without timestamps, assume corroboration exists if Tier 1 source agrees
      this.flags.cross_verification_passed = true;
    }
  }

  /**
   * Detect if Tier 1 sources conflict on a claim.
   */
  private detectContradictions(sources: SourceInput[]): void {
    const tier1Sources = sources.filter((s) => s.tier === 1);
    const agrees = tier1Sources.filter((s) => s.agrees);
    const disagrees = tier1Sources.filter((s) => !s.agrees);

    if (agrees.length > 0 && disagrees.length > 0) {
      this.flags.tier_1_contradiction = true;
      this.flags.manual_review_required = true;
      this.logDecision(
        'contradiction_detection',
        `Tier 1 conflict: [${agrees.map((s) => s.name).join(', ')}] vs [${disagrees.map((s) => s.name).join(', ')}]`,
        0,
        'Manual review triggered, confidence paused'
      );
    }
  }

  /**
   * Check for special conditions that affect validation.
   */
  private checkSpecialConditions(sources: SourceInput[]): void {
    const tierCounts: Record<number, number> = { 1: 0, 2: 0, 3: 0 };
    let proGroupCount = 0;

    for (const src of sources) {
      tierCounts[src.tier] = (tierCounts[src.tier] || 0) + 1;
      if (src.is_pro_group) proGroupCount++;
    }

    // Only Tier 3 sources
    if (tierCounts[1] === 0 && tierCounts[2] === 0 && tierCounts[3] > 0) {
      this.flags.tier_3_only = true;
    }

    // Single source
    if (sources.length === 1) {
      this.flags.single_source = true;
    }

    // Only pro-group sources
    if (proGroupCount > 0 && proGroupCount === sources.length) {
      this.flags.pro_group_source_only = true;
    }
  }

  /**
   * Apply score adjustments based on validation flags.
   *
   * Adjustments:
   * - Pro-group sources only: Cap score at 0.2
   * - Tier 3 only, no Tier 1 corroboration: Cap score at 0.3
   * - No Tier 1 corroboration (mixed tiers): Cap score at 0.4
   * - Tier 1 contradiction: Reduce score by 50%
   * - Single source: Reduce score by 20%
   */
  private applyAdjustments(rawScore: number): number {
    let adjusted = rawScore;

    // Pro-group sources only - hardest cap
    if (this.flags.pro_group_source_only) {
      adjusted = Math.min(adjusted, VALIDATION_CONFIG.pro_group_max_score);
    }

    // Tier 3 only with no Tier 1 corroboration
    if (this.flags.tier_3_only && this.flags.no_tier_1_corroboration) {
      adjusted = Math.min(
        adjusted,
        VALIDATION_CONFIG.tier_3_max_score_without_tier1
      );
    }
    // No Tier 1 corroboration for Tier 3 claim
    else if (this.flags.no_tier_1_corroboration) {
      adjusted = Math.min(adjusted, 0.4);
    }

    // Tier 1 contradiction - reduce by 50%
    if (this.flags.tier_1_contradiction) {
      adjusted *= VALIDATION_CONFIG.contradiction_confidence_reduction;
    }

    // Single source penalty
    if (this.flags.single_source) {
      adjusted *= VALIDATION_CONFIG.single_source_reduction;
    }

    return Math.round(Math.max(0.0, Math.min(1.0, adjusted)) * 10000) / 10000;
  }

  /**
   * Determine bias risk level based on validation score and flags.
   */
  private determineBiasRisk(score: number): 'Low' | 'Medium' | 'High' {
    if (this.flags.manual_review_required) return 'High';
    if (this.flags.tier_1_contradiction) return 'High';
    if (this.flags.pro_group_source_only) return 'High';

    if (score >= VALIDATION_CONFIG.high_risk_threshold) return 'Low';
    if (score >= VALIDATION_CONFIG.medium_risk_threshold) return 'Medium';
    return 'High';
  }

  private getFlagList(): string[] {
    const flags: string[] = [];
    if (this.flags.tier_3_only) flags.push('TIER_3_ONLY');
    if (this.flags.no_tier_1_corroboration) flags.push('NO_TIER_1_CORROBORATION');
    if (this.flags.tier_1_contradiction) flags.push('TIER_1_CONTRADICTION');
    if (this.flags.manual_review_required) flags.push('MANUAL_REVIEW_REQUIRED');
    if (this.flags.single_source) flags.push('SINGLE_SOURCE');
    if (this.flags.cross_verification_passed) flags.push('CROSS_VERIFICATION_PASSED');
    if (this.flags.insufficient_sources) flags.push('INSUFFICIENT_SOURCES');
    if (this.flags.pro_group_source_only) flags.push('PRO_GROUP_SOURCE_ONLY');
    return flags;
  }

  private buildResult(score: number, claim: string): ValidationResult {
    const biasRisk = this.determineBiasRisk(score);
    const flagList = this.getFlagList();

    let crossVerificationStatus = 'Not Required';
    if (this.flags.tier_3_only || this.flags.no_tier_1_corroboration) {
      if (this.flags.cross_verification_passed) {
        crossVerificationStatus = 'Passed - Tier 1 corroboration found';
      } else {
        crossVerificationStatus = 'Failed - Tier 1 corroboration required';
      }
    } else if (this.flags.cross_verification_passed) {
      crossVerificationStatus = 'Passed';
    }

    return {
      validation_score: score,
      bias_risk_level: biasRisk,
      flags: flagList,
      cross_verification_status: crossVerificationStatus,
      tier_1_corroboration: this.flags.cross_verification_passed,
      contradiction_detected: this.flags.tier_1_contradiction,
      claim,
      manual_review_required: this.flags.manual_review_required,
    };
  }

  private logDecision(
    step: string,
    detail: string,
    score: number,
    note: string
  ): void {
    this.auditTrail.push({
      timestamp: new Date().toISOString(),
      step,
      detail,
      score,
      note,
    });
  }

  getAuditTrail(): AuditEntry[] {
    return this.auditTrail;
  }

  /**
   * Look up a source's tier information.
   */
  static getSourceTier(sourceName: string): { tier: number; weight: number; tag?: string } {
    return SOURCE_TIERS[sourceName] || { tier: 3, weight: 0.3, tag: 'Unknown' };
  }

  /**
   * Return all registered sources with their tier info.
   */
  static getAllSources(): Record<string, { tier: number; weight: number; tag?: string }> {
    return { ...SOURCE_TIERS };
  }
}
