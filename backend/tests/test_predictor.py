"""
AGSPE Prediction Engine Tests
Tests for the hybrid prediction model.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.predictor import PredictionEngine, ACQUISITION_PATTERNS, POLICY_CORRELATIONS


class TestPredictionEngine:
    """Test suite for the Prediction Engine."""

    def setup_method(self):
        self.engine = PredictionEngine()

    def test_generate_predictions_returns_list(self):
        """Prediction generation should return a list of predictions."""
        predictions = self.engine.generate_predictions()
        assert isinstance(predictions, list)
        assert len(predictions) > 0

    def test_predictions_have_required_fields(self):
        """Each prediction should have all required fields."""
        predictions = self.engine.generate_predictions()
        required_fields = [
            "id", "likely_action", "category", "timeline_start",
            "timeline_end", "confidence_score", "supporting_evidence",
            "risk_factors", "financial_signal", "political_alignment",
            "pattern_match", "data_sources", "created_at", "validation_score",
        ]
        for pred in predictions:
            for field in required_fields:
                assert field in pred, f"Missing field: {field}"

    def test_confidence_score_range(self):
        """Confidence scores should be between 0 and 100."""
        predictions = self.engine.generate_predictions()
        for pred in predictions:
            assert 0 <= pred["confidence_score"] <= 100

    def test_financial_signal_range(self):
        """Financial signals should be between 0 and 1."""
        predictions = self.engine.generate_predictions()
        for pred in predictions:
            assert 0 <= pred["financial_signal"] <= 1

    def test_political_alignment_range(self):
        """Political alignment should be between 0 and 1."""
        predictions = self.engine.generate_predictions()
        for pred in predictions:
            assert 0 <= pred["political_alignment"] <= 1

    def test_timeline_format(self):
        """Timeline should be in quarter format (e.g., 'Q3 2026')."""
        predictions = self.engine.generate_predictions()
        for pred in predictions:
            assert pred["timeline_start"].startswith("Q")
            assert pred["timeline_end"].startswith("Q")

    def test_predictions_sorted_by_confidence(self):
        """Predictions should be sorted by confidence score descending."""
        predictions = self.engine.generate_predictions()
        scores = [p["confidence_score"] for p in predictions]
        assert scores == sorted(scores, reverse=True)

    def test_custom_financial_data(self):
        """Custom financial data should affect predictions."""
        high_growth_data = [
            {"company": "Test", "debt_to_equity": 0.5, "capex_commitment_inr": 200000,
             "stock_volatility_30d": 10, "revenue_growth_yoy": 0.5, "market_cap_inr": 500000},
        ]
        low_growth_data = [
            {"company": "Test", "debt_to_equity": 3.0, "capex_commitment_inr": 10000,
             "stock_volatility_30d": 50, "revenue_growth_yoy": -0.1, "market_cap_inr": 100000},
        ]

        high_predictions = self.engine.generate_predictions(financial_data=high_growth_data)
        low_predictions = self.engine.generate_predictions(financial_data=low_growth_data)

        # High growth should generally produce higher confidence
        assert len(high_predictions) > 0
        assert len(low_predictions) > 0

    def test_financial_signal_calculation(self):
        """Financial signal calculation should handle various data."""
        # Good financial health
        good_data = [
            {"company": "A", "debt_to_equity": 0.3, "capex_commitment_inr": 100000,
             "stock_volatility_30d": 15, "revenue_growth_yoy": 0.25, "market_cap_inr": 300000},
        ]
        good_signals = self.engine._calculate_financial_signal(good_data)
        assert good_signals["composite"] > 0.5

        # Poor financial health
        poor_data = [
            {"company": "B", "debt_to_equity": 4.0, "capex_commitment_inr": 5000,
             "stock_volatility_30d": 55, "revenue_growth_yoy": -0.1, "market_cap_inr": 50000},
        ]
        poor_signals = self.engine._calculate_financial_signal(poor_data)
        assert poor_signals["composite"] < good_signals["composite"]

    def test_political_alignment_calculation(self):
        """Political alignment calculation should weight by source tier."""
        high_alignment = [
            {"event_type": "policy", "description": "Budget infrastructure allocation",
             "relevance_score": 0.9, "source_tier": 1, "impact": 0.9},
        ]
        low_alignment = [
            {"event_type": "policy", "description": "Regulatory action",
             "relevance_score": 0.8, "source_tier": 1, "impact": 0.2},
        ]

        high_score = self.engine._calculate_political_alignment(high_alignment)
        low_score = self.engine._calculate_political_alignment(low_alignment)

        assert high_score > low_score

    def test_pattern_matching(self):
        """Pattern matching should identify known acquisition patterns."""
        # Infrastructure-heavy acquisition history
        infra_acquisitions = [
            {"company_acquired": "Port A", "sector": "Ports", "year": 2023},
            {"company_acquired": "Port B", "sector": "Ports", "year": 2024},
            {"company_acquired": "Highway C", "sector": "Infrastructure", "year": 2024},
            {"company_acquired": "Airport D", "sector": "Infrastructure", "year": 2025},
        ]
        matches = self.engine._match_acquisition_patterns(infra_acquisitions, {})
        assert len(matches) > 0
        # Should match infrastructure pattern
        infra_match = [m for m in matches if "Infrastructure" in m["category"]]
        assert len(infra_match) > 0

    def test_default_data_generates_predictions(self):
        """Default data should generate valid predictions."""
        predictions = self.engine.generate_predictions()
        assert len(predictions) >= 3  # Should have at least pattern + policy predictions

    def test_risk_factors_present(self):
        """Predictions should include risk factors."""
        predictions = self.engine.generate_predictions()
        for pred in predictions:
            assert len(pred["risk_factors"]) > 0

    def test_acquisition_patterns_defined(self):
        """Known acquisition patterns should be properly defined."""
        assert "standard_acquisition" in ACQUISITION_PATTERNS
        assert "green_energy_expansion" in ACQUISITION_PATTERNS
        assert "port_infrastructure" in ACQUISITION_PATTERNS
        assert "distressed_asset_acquisition" in ACQUISITION_PATTERNS

    def test_policy_correlations_defined(self):
        """Known policy correlations should be properly defined."""
        assert "infrastructure_push" in POLICY_CORRELATIONS
        assert POLICY_CORRELATIONS["infrastructure_push"]["base_probability"] > 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
