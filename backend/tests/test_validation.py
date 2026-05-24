"""
AGSPE Validation Engine Tests
Tests for the Multi-Source Verification Algorithm.
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.validation import ValidationEngine, SOURCE_TIERS


class TestValidationEngine:
    """Test suite for the Validation Engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ValidationEngine()

    # ── Basic Validation Tests ──

    def test_empty_sources_returns_zero(self):
        """Claim with no sources should return score 0.0."""
        result = self.engine.validate_claim("Test claim", sources=[])
        assert result["validation_score"] == 0.0
        assert result["bias_risk_level"] == "High"
        assert "INSUFFICIENT_SOURCES" in result["flags"]

    def test_single_tier1_source_agree(self):
        """Single Tier 1 source that agrees should return reasonable score."""
        result = self.engine.validate_claim(
            "Adani wins port concession",
            sources=[{"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True}],
        )
        assert result["validation_score"] > 0.5
        assert "SINGLE_SOURCE" in result["flags"]

    def test_single_tier1_source_disagree(self):
        """Single Tier 1 source that disagrees should return lower score."""
        result = self.engine.validate_claim(
            "Adani wins port concession",
            sources=[{"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": False}],
        )
        assert result["validation_score"] < 0.5

    def test_multiple_tier1_sources_agree(self):
        """Multiple Tier 1 sources agreeing should return high score."""
        result = self.engine.validate_claim(
            "Adani wins port concession",
            sources=[
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "BBC", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "Bloomberg", "tier": 1, "weight": 0.9, "agrees": True},
            ],
        )
        assert result["validation_score"] >= 0.8
        assert result["bias_risk_level"] == "Low"
        assert result["tier_1_corroboration"] is True

    # ── Tier 3 Cross-Verification Tests ──

    def test_ndtv_only_story_low_confidence(self):
        """
        CRITICAL: NDTV-only story should be flagged as low confidence.
        This is a key requirement from the specification.
        """
        result = self.engine.validate_claim(
            "Adani Group set to revolutionize Indian aviation",
            sources=[{"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True}],
        )
        assert result["validation_score"] <= 0.3
        assert result["bias_risk_level"] == "High"
        assert "TIER_3_ONLY" in result["flags"]
        assert "NO_TIER_1_CORROBORATION" in result["flags"]

    def test_ndtv_with_tier1_corroboration(self):
        """NDTV story with Reuters confirmation should have higher confidence."""
        result = self.engine.validate_claim(
            "Adani Group wins airport bid",
            sources=[
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True},
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
            ],
        )
        assert result["validation_score"] > 0.3
        assert result["tier_1_corroboration"] is True
        assert result["bias_risk_level"] in ["Low", "Medium"]

    def test_ndtv_without_tier1_corroboration(self):
        """NDTV story without Tier 1 confirmation should be capped."""
        result = self.engine.validate_claim(
            "Adani Group expanding operations",
            sources=[
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True},
                {"name": "Times Now", "tier": 3, "weight": 0.3, "agrees": True},
            ],
        )
        assert result["validation_score"] <= 0.4
        assert "NO_TIER_1_CORROBORATION" in result["flags"]

    # ── Contradiction Detection Tests ──

    def test_tier1_contradiction_triggers_manual_review(self):
        """Contradicting Tier 1 sources should trigger manual review."""
        result = self.engine.validate_claim(
            "Adani Group under investigation",
            sources=[
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "BBC", "tier": 1, "weight": 0.9, "agrees": False},
            ],
        )
        assert "TIER_1_CONTRADICTION" in result["flags"]
        assert "MANUAL_REVIEW_REQUIRED" in result["flags"]
        assert result["bias_risk_level"] == "High"

    def test_tier1_tier2_agreement_no_contradiction(self):
        """Tier 1 and Tier 2 agreeing should not trigger contradiction."""
        result = self.engine.validate_claim(
            "Adani Power commissions new plant",
            sources=[
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "The Hindu", "tier": 2, "weight": 0.7, "agrees": True},
            ],
        )
        assert "TIER_1_CONTRADICTION" not in result["flags"]
        assert "MANUAL_REVIEW_REQUIRED" not in result["flags"]

    # ── Pro-Group Source Tests ──

    def test_pro_group_only_sources(self):
        """Only pro-group sources should have very low confidence cap."""
        result = self.engine.validate_claim(
            "Adani Group achieves record growth",
            sources=[
                {"name": "Adani Group PR", "tier": 3, "weight": 0.3, "agrees": True, "is_pro_group": True},
            ],
        )
        assert result["validation_score"] <= 0.2
        assert result["bias_risk_level"] == "High"
        assert "PRO_GROUP_SOURCE_ONLY" in result["flags"]

    # ── Bias Risk Level Tests ──

    def test_high_score_low_risk(self):
        """High validation score should result in Low bias risk."""
        result = self.engine.validate_claim(
            "Government announces infrastructure budget",
            sources=[
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "BBC", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "The Hindu", "tier": 2, "weight": 0.7, "agrees": True},
            ],
        )
        assert result["bias_risk_level"] == "Low"

    def test_low_score_high_risk(self):
        """Low validation score should result in High bias risk."""
        result = self.engine.validate_claim(
            "Adani to acquire major company",
            sources=[{"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True}],
        )
        assert result["bias_risk_level"] == "High"

    # ── Cross-Verification with Timestamps ──

    def test_cross_verification_within_window(self):
        """Tier 1 corroboration within 24h should pass cross-verification."""
        now = datetime.utcnow()
        result = self.engine.validate_claim(
            "Adani Green announces solar project",
            sources=[
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True},
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
            ],
            timestamps={
                "NDTV": now - timedelta(hours=3),
                "Reuters": now - timedelta(hours=1),
            },
        )
        assert result["cross_verification_status"] in [
            "Passed", "Passed - Tier 1 corroboration found"
        ]

    def test_cross_verification_outside_window(self):
        """Tier 1 corroboration beyond 24h should flag verification needed."""
        now = datetime.utcnow()
        result = self.engine.validate_claim(
            "Adani Green announces solar project",
            sources=[
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True},
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
            ],
            timestamps={
                "NDTV": now - timedelta(hours=48),
                "Reuters": now - timedelta(hours=1),
            },
        )
        # Tier 1 exists but timing is outside window, so cross-verification fails
        # The score should be capped since Tier 3 claim lacks timely corroboration
        assert result["tier_1_corroboration"] is False
        assert "NO_TIER_1_CORROBORATION" in result["flags"]

    # ── Source Lookup Tests ──

    def test_get_source_tier_known(self):
        """Known source should return correct tier info."""
        info = ValidationEngine.get_source_tier("Reuters")
        assert info["tier"] == 1
        assert info["weight"] == 0.9

    def test_get_source_tier_unknown(self):
        """Unknown source should default to Tier 3."""
        info = ValidationEngine.get_source_tier("Unknown Source")
        assert info["tier"] == 3
        assert info["weight"] == 0.3

    def test_get_all_sources(self):
        """All sources should be returned."""
        sources = ValidationEngine.get_all_sources()
        assert "Reuters" in sources
        assert "NDTV" in sources
        assert "The Hindu" in sources

    # ── Audit Trail Tests ──

    def test_audit_trail_populated(self):
        """Validation should populate audit trail."""
        self.engine.validate_claim(
            "Test claim",
            sources=[{"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True}],
        )
        assert len(self.engine.get_audit_trail()) > 0

    def test_audit_trail_export(self, tmp_path):
        """Audit trail should be exportable to JSON."""
        self.engine.validate_claim(
            "Test claim",
            sources=[{"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True}],
        )
        filepath = str(tmp_path / "test_audit.json")
        self.engine.export_audit_trail(filepath)
        assert os.path.exists(filepath)


class TestValidationEngineIntegration:
    """Integration tests for the Validation Engine with realistic scenarios."""

    def setup_method(self):
        self.engine = ValidationEngine()

    def test_hindenburg_report_scenario(self):
        """Test validation of a Hindenburg report claim."""
        result = self.engine.validate_claim(
            "Adani Group offshore entities used for stock manipulation",
            sources=[
                {"name": "OCCRP", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "BBC", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "Reuters", "tier": 1, "weight": 0.9, "agrees": True},
                {"name": "The Hindu", "tier": 2, "weight": 0.7, "agrees": True},
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": False},
                {"name": "Adani Group PR", "tier": 3, "weight": 0.3, "agrees": False, "is_pro_group": True},
            ],
        )
        # Should have reasonable score due to multiple Tier 1 sources
        assert result["validation_score"] >= 0.5
        # Contradiction from Tier 3 should not trigger Tier 1 contradiction
        assert "TIER_1_CONTRADICTION" not in result["flags"]

    def test_airport_bid_scenario(self):
        """Test validation of an airport bid claim from mixed sources."""
        result = self.engine.validate_claim(
            "Adani Group preparing bids for three new airports",
            sources=[
                {"name": "NDTV", "tier": 3, "weight": 0.3, "agrees": True},
                {"name": "Times Now", "tier": 3, "weight": 0.3, "agrees": True},
            ],
        )
        # Tier 3 only should be flagged
        assert result["validation_score"] <= 0.4
        assert result["bias_risk_level"] == "High"
        assert "REQUIRES VERIFICATION" in result["cross_verification_status"] or "Failed" in result["cross_verification_status"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
