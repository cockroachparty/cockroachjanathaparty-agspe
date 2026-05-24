"""
AGSPE Validation Engine - Multi-Source Verification Algorithm

CRITICAL MODULE: Implements the multi-tier cross-source verification protocol
to mitigate media bias and ensure data reliability for predictions.

Algorithm:
1. Assign weights based on source trust tier (Tier 1=0.9, Tier 2=0.7, Tier 3=0.3)
2. Cross-Verification Rule: Tier 3 claim requires Tier 1 corroboration within 24h
3. Contradiction Detection: Tier 1 conflicts trigger manual review flag
4. Output: validation_score (0.0-1.0) and bias_risk_level (Low/Medium/High)
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import json
import os

from ..config import settings


# ── Source Tier Definitions ──

SOURCE_TIERS = {
    # Tier 1 - High Weight (0.9) - International / Highly Credible
    "Reuters": {"tier": 1, "weight": 0.9},
    "AP News": {"tier": 1, "weight": 0.9},
    "BBC": {"tier": 1, "weight": 0.9},
    "Al Jazeera": {"tier": 1, "weight": 0.9},
    "OCCRP": {"tier": 1, "weight": 0.9},
    "Bloomberg": {"tier": 1, "weight": 0.9},
    "Financial Times": {"tier": 1, "weight": 0.9},

    # Tier 2 - Medium Weight (0.7) - Independent Indian Media
    "The Hindu": {"tier": 2, "weight": 0.7},
    "Scroll.in": {"tier": 2, "weight": 0.7},
    "The Wire": {"tier": 2, "weight": 0.7},
    "Business Standard": {"tier": 2, "weight": 0.7},
    "Economic and Political Weekly": {"tier": 2, "weight": 0.7},
    "NDTV Profit": {"tier": 2, "weight": 0.7},

    # Tier 3 - Low Weight (0.3) - Pro-Group / Requires Verification
    "NDTV": {"tier": 3, "weight": 0.3, "tag": "Requires Verification"},
    "Times Now": {"tier": 3, "weight": 0.3, "tag": "Requires Verification"},
    "Republic TV": {"tier": 3, "weight": 0.3, "tag": "Requires Verification"},
    "Zee News": {"tier": 3, "weight": 0.3, "tag": "Requires Verification"},
    "Adani Group PR": {"tier": 3, "weight": 0.3, "tag": "Pro-Group"},
}


@dataclass
class ValidationFlags:
    """Flags raised during the validation process."""
    tier_3_only: bool = False
    no_tier_1_corroboration: bool = False
    tier_1_contradiction: bool = False
    manual_review_required: bool = False
    single_source: bool = False
    cross_verification_passed: bool = False
    insufficient_sources: bool = False
    pro_group_source_only: bool = False


@dataclass
class SourceInput:
    """Input source for validation."""
    name: str
    tier: int
    weight: float
    agrees: bool  # Does this source agree with the claim?
    timestamp: Optional[datetime] = None
    is_pro_group: bool = False


class ValidationEngine:
    """
    Multi-Source Verification Engine for AGSPE.

    Validates claims through a weighted, tiered source verification system
    that detects bias, requires cross-verification for low-tier sources,
    and flags contradictions between high-tier sources.

    Usage:
        engine = ValidationEngine()
        result = engine.validate_claim(
            claim="Adani Group wins new airport concession",
            sources=[
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True},
            ]
        )
    """

    def __init__(self):
        self.flags = ValidationFlags()
        self.audit_trail: List[Dict] = []

    def validate_claim(
        self,
        claim: str,
        sources: List[Dict],
        timestamps: Optional[Dict[str, datetime]] = None,
    ) -> Dict:
        """
        Validate a claim against multiple sources using the multi-tier algorithm.

        Args:
            claim: The claim text/event to validate
            sources: List of source metadata dicts:
                {name: str, tier: int, weight: float, agrees: bool, is_pro_group: bool}
            timestamps: Optional dict of source_name -> datetime for cross-verification timing

        Returns:
            Dict with:
                - validation_score: float (0.0 to 1.0)
                - bias_risk_level: str (Low/Medium/High)
                - flags: List[str]
                - cross_verification_status: str
                - tier_1_corroboration: bool
                - contradiction_detected: bool
        """
        self.flags = ValidationFlags()
        self.audit_trail = []

        if not sources:
            self.flags.insufficient_sources = True
            result = self._build_result(0.0, claim)
            self._log_decision("validate_claim", claim, 0.0, "No sources provided")
            return result

        # Parse source inputs
        source_inputs = self._parse_sources(sources, timestamps)

        # Step 1: Calculate weighted validation score
        raw_score = self._calculate_weighted_score(source_inputs)

        # Step 2: Check cross-verification requirements
        cross_verification = self._check_cross_verification(source_inputs, timestamps)

        # Step 3: Detect contradictions between Tier 1 sources
        contradiction = self._detect_contradictions(source_inputs)

        # Step 4: Check for special conditions
        self._check_special_conditions(source_inputs)

        # Step 5: Apply adjustments based on flags
        adjusted_score = self._apply_adjustments(raw_score)

        # Step 6: Determine bias risk level
        bias_risk = self._determine_bias_risk(adjusted_score)

        # Build final result
        result = self._build_result(adjusted_score, claim)

        # Log the decision
        self._log_decision(
            "validate_claim", claim, adjusted_score,
            f"raw={raw_score:.3f}, flags={[f for f in self._get_flag_list() if f]}"
        )

        return result

    def _parse_sources(
        self, sources: List[Dict], timestamps: Optional[Dict[str, datetime]]
    ) -> List[SourceInput]:
        """Parse raw source dicts into SourceInput objects."""
        parsed = []
        for src in sources:
            # Look up known source if name matches
            known = SOURCE_TIERS.get(src.get("name", ""), {})
            tier = src.get("tier", known.get("tier", 3))
            weight = src.get("weight", known.get("weight", 0.3))
            is_pro_group = src.get("is_pro_group", "tag" in known and known.get("tag") == "Pro-Group")

            ts = None
            if timestamps and src.get("name") in timestamps:
                ts = timestamps[src["name"]]

            parsed.append(SourceInput(
                name=src.get("name", "Unknown"),
                tier=tier,
                weight=weight,
                agrees=src.get("agrees", True),
                timestamp=ts,
                is_pro_group=is_pro_group,
            ))
        return parsed

    def _calculate_weighted_score(self, sources: List[SourceInput]) -> float:
        """
        Calculate weighted validation score based on source tiers and agreement.

        Formula:
        score = sum(weight * agrees_indicator) / sum(weight)

        Where agrees_indicator is 1.0 for agree, -0.5 for disagree, 0.0 for neutral.
        """
        total_weight = 0.0
        weighted_sum = 0.0

        for src in sources:
            weight = src.weight
            total_weight += weight

            if src.agrees:
                weighted_sum += weight * 1.0
            else:
                weighted_sum += weight * (-0.5)

        if total_weight == 0:
            return 0.0

        raw_score = weighted_sum / total_weight

        # Normalize to 0.0 - 1.0 range
        # Raw score can be negative (disagreement), map to 0-1
        normalized = (raw_score + 0.5) / 1.5
        normalized = max(0.0, min(1.0, normalized))

        return round(normalized, 4)

    def _check_cross_verification(
        self, sources: List[SourceInput], timestamps: Optional[Dict[str, datetime]]
    ) -> Dict:
        """
        Check if Tier 3 claims have Tier 1 corroboration within the verification window.

        Cross-Verification Rule: A claim from a Tier 3 source triggers a flag
        requiring confirmation from at least one Tier 1 source within 24 hours
        to be considered valid for prediction input.
        """
        tier_3_sources = [s for s in sources if s.tier == 3 and s.agrees]
        tier_1_sources = [s for s in sources if s.tier == 1 and s.agrees]

        result = {
            "required": len(tier_3_sources) > 0,
            "corroborated": False,
            "within_window": False,
        }

        if not tier_3_sources:
            # No Tier 3 sources requiring verification
            self.flags.cross_verification_passed = True
            result["corroborated"] = True
            return result

        if not tier_1_sources:
            # Tier 3 claim with NO Tier 1 corroboration
            self.flags.no_tier_1_corroboration = True
            self._log_decision(
                "cross_verification", "Tier 3 claim lacks Tier 1 corroboration",
                0, "Flagged as requiring verification"
            )
            return result

        # Check if Tier 1 corroboration exists within time window
        result["corroborated"] = True

        if timestamps:
            for t3 in tier_3_sources:
                if t3.timestamp:
                    for t1 in tier_1_sources:
                        if t1.timestamp:
                            time_diff = abs((t1.timestamp - t3.timestamp).total_seconds())
                            window = settings.CROSS_VERIFICATION_WINDOW_HOURS * 3600
                            if time_diff <= window:
                                result["within_window"] = True
                                break

            if result["within_window"]:
                self.flags.cross_verification_passed = True
            else:
                self.flags.no_tier_1_corroboration = True
        else:
            # Without timestamps, assume corroboration exists if Tier 1 source agrees
            self.flags.cross_verification_passed = True
            result["within_window"] = True

        return result

    def _detect_contradictions(self, sources: List[SourceInput]) -> Dict:
        """
        Detect if Tier 1 sources conflict on a claim.

        Contradiction Rule: If Tier 1 sources conflict, trigger a manual review
        flag and pause prediction confidence until resolved.
        """
        tier_1_sources = [s for s in sources if s.tier == 1]

        agrees = [s for s in tier_1_sources if s.agrees]
        disagrees = [s for s in tier_1_sources if not s.agrees]

        result = {
            "contradiction_detected": len(agrees) > 0 and len(disagrees) > 0,
            "agreeing_sources": [s.name for s in agrees],
            "disagreeing_sources": [s.name for s in disagrees],
        }

        if result["contradiction_detected"]:
            self.flags.tier_1_contradiction = True
            self.flags.manual_review_required = True
            self._log_decision(
                "contradiction_detection",
                f"Tier 1 conflict: {result['agreeing_sources']} vs {result['disagreeing_sources']}",
                0, "Manual review triggered, confidence paused"
            )

        return result

    def _check_special_conditions(self, sources: List[SourceInput]) -> None:
        """Check for special conditions that affect validation."""
        tier_counts = {1: 0, 2: 0, 3: 0}
        pro_group_count = 0

        for src in sources:
            tier_counts[src.tier] = tier_counts.get(src.tier, 0) + 1
            if src.is_pro_group:
                pro_group_count += 1

        # Only Tier 3 sources
        if tier_counts[1] == 0 and tier_counts[2] == 0 and tier_counts[3] > 0:
            self.flags.tier_3_only = True

        # Single source
        if len(sources) == 1:
            self.flags.single_source = True

        # Only pro-group sources
        if pro_group_count > 0 and pro_group_count == len(sources):
            self.flags.pro_group_source_only = True

    def _apply_adjustments(self, raw_score: float) -> float:
        """
        Apply score adjustments based on validation flags.

        Adjustments:
        - Tier 3 only, no Tier 1 corroboration: Cap score at 0.3
        - Tier 1 contradiction: Reduce score by 50%
        - Single source: Reduce score by 20%
        - Pro-group only: Cap score at 0.2
        """
        adjusted = raw_score

        # Pro-group sources only - hardest cap
        if self.flags.pro_group_source_only:
            adjusted = min(adjusted, 0.2)

        # Tier 3 only with no Tier 1 corroboration
        if self.flags.tier_3_only and self.flags.no_tier_1_corroboration:
            adjusted = min(adjusted, 0.3)

        # No Tier 1 corroboration for Tier 3 claim
        elif self.flags.no_tier_1_corroboration:
            adjusted = min(adjusted, 0.4)

        # Tier 1 contradiction - reduce by 50%
        if self.flags.tier_1_contradiction:
            adjusted *= 0.5

        # Single source penalty
        if self.flags.single_source:
            adjusted *= 0.8

        return round(max(0.0, min(1.0, adjusted)), 4)

    def _determine_bias_risk(self, score: float) -> str:
        """
        Determine bias risk level based on validation score and flags.

        - score >= 0.7: Low
        - 0.4 <= score < 0.7: Medium
        - score < 0.4: High
        """
        if self.flags.manual_review_required:
            return "High"
        if self.flags.tier_1_contradiction:
            return "High"
        if self.flags.pro_group_source_only:
            return "High"

        if score >= settings.VALIDATION_HIGH_THRESHOLD:
            return "Low"
        elif score >= settings.VALIDATION_MEDIUM_THRESHOLD:
            return "Medium"
        else:
            return "High"

    def _get_flag_list(self) -> List[str]:
        """Get list of active flag names."""
        flags = []
        if self.flags.tier_3_only:
            flags.append("TIER_3_ONLY")
        if self.flags.no_tier_1_corroboration:
            flags.append("NO_TIER_1_CORROBORATION")
        if self.flags.tier_1_contradiction:
            flags.append("TIER_1_CONTRADICTION")
        if self.flags.manual_review_required:
            flags.append("MANUAL_REVIEW_REQUIRED")
        if self.flags.single_source:
            flags.append("SINGLE_SOURCE")
        if self.flags.cross_verification_passed:
            flags.append("CROSS_VERIFICATION_PASSED")
        if self.flags.insufficient_sources:
            flags.append("INSUFFICIENT_SOURCES")
        if self.flags.pro_group_source_only:
            flags.append("PRO_GROUP_SOURCE_ONLY")
        return flags

    def _build_result(self, score: float, claim: str) -> Dict:
        """Build the final validation result dictionary."""
        bias_risk = self._determine_bias_risk(score)
        flag_list = self._get_flag_list()

        cross_verification_status = "Not Required"
        if self.flags.tier_3_only or self.flags.no_tier_1_corroboration:
            if self.flags.cross_verification_passed:
                cross_verification_status = "Passed - Tier 1 corroboration found"
            else:
                cross_verification_status = "Failed - Tier 1 corroboration required"
        elif self.flags.cross_verification_passed:
            cross_verification_status = "Passed"

        return {
            "validation_score": score,
            "bias_risk_level": bias_risk,
            "flags": flag_list,
            "cross_verification_status": cross_verification_status,
            "tier_1_corroboration": self.flags.cross_verification_passed,
            "contradiction_detected": self.flags.tier_1_contradiction,
            "claim": claim,
            "manual_review_required": self.flags.manual_review_required,
        }

    def _log_decision(self, step: str, detail: str, score: float, note: str) -> None:
        """Log an algorithmic decision for audit trail."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": step,
            "detail": detail,
            "score": score,
            "note": note,
        }
        self.audit_trail.append(entry)

    def get_audit_trail(self) -> List[Dict]:
        """Return the audit trail for this validation session."""
        return self.audit_trail

    def export_audit_trail(self, filepath: str) -> None:
        """Export the audit trail to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.audit_trail, f, indent=2, default=str)

    @staticmethod
    def get_source_tier(source_name: str) -> Dict:
        """Look up a source's tier information."""
        return SOURCE_TIERS.get(source_name, {"tier": 3, "weight": 0.3, "tag": "Unknown"})

    @staticmethod
    def get_all_sources() -> Dict:
        """Return all registered sources with their tier info."""
        return SOURCE_TIERS.copy()
