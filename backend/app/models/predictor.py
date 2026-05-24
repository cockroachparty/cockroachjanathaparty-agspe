"""
AGSPE Prediction Engine - Hybrid Logic Engine

Combines statistical trends and heuristic rules to generate
probabilistic predictions on Adani Group future business moves
with confidence intervals and timelines.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import math
import random


# ── Known Patterns ──

ACQUISITION_PATTERNS = {
    "standard_acquisition": {
        "name": "Standard Acquisition Cycle",
        "stages": [
            "Fragmented Sector",
            "Large Acquisition",
            "Consolidation",
            "Listing/Demerger",
        ],
        "typical_duration_months": 18,
        "confidence_base": 0.7,
    },
    "green_energy_expansion": {
        "name": "Green Energy Expansion",
        "stages": [
            "Government Renewable Target Announced",
            "Policy Incentives Released",
            "Adani Green Capacity Announcement",
            "JV/Partnership Formation",
            "Project Commissioning",
        ],
        "typical_duration_months": 24,
        "confidence_base": 0.75,
    },
    "port_infrastructure": {
        "name": "Port & Infrastructure Play",
        "stages": [
            "Government Infrastructure Push",
            "Bid Preparation/Consortium",
            "Concession Win",
            "Capacity Expansion",
        ],
        "typical_duration_months": 12,
        "confidence_base": 0.8,
    },
    "distressed_asset_acquisition": {
        "name": "Distressed Asset Acquisition",
        "stages": [
            "IBCP/NCLT Proceedings",
            "Asset Valuation",
            "Adani Bid Submission",
            "Creditor Approval",
            "Takeover & Restructuring",
        ],
        "typical_duration_months": 15,
        "confidence_base": 0.65,
    },
}

POLICY_CORRELATIONS = {
    "infrastructure_push": {
        "trigger": "BJP/NDA announces infrastructure push",
        "predicted_action": "Adani port/airport bid win",
        "base_probability": 0.82,
        "evidence": [
            "Historical correlation: 2019-2026 infrastructure budgets",
            "Adani Ports won 6 of 8 major port concessions since 2019",
            "Airport privatization aligned with Adani wins",
        ],
    },
    "renewable_target": {
        "trigger": "Government raises renewable energy target",
        "predicted_action": "Adani Green capacity expansion / JV",
        "base_probability": 0.78,
        "evidence": [
            "500 GW renewable target by 2030",
            "Adani Green committed 45 GW by 2030",
            "TotalEnergies JV expansion pattern",
        ],
    },
    "defense_policy": {
        "trigger": "Defense procurement policy announced",
        "predicted_action": "Adani Defense contract win",
        "base_probability": 0.65,
        "evidence": [
            "Make in India defense push",
            "Adani Defense & Aerospace established 2015",
            "DRDO partnerships pattern",
        ],
    },
    "cement_consolidation": {
        "trigger": "Infrastructure/housing policy boost",
        "predicted_action": "Ambuja/ACC capacity expansion or acquisition",
        "base_probability": 0.72,
        "evidence": [
            "Post-ACC/Ambuja acquisition consolidation",
            "140 MTPA target by 2028",
            "Greenfield plant announcements",
        ],
    },
}


@dataclass
class FinancialIndicators:
    """Financial data for a company or group."""
    debt_to_equity: float = 0.0
    capex_commitment_inr: float = 0.0
    stock_volatility_30d: float = 0.0
    revenue_growth_yoy: float = 0.0
    profit_margin: float = 0.0
    market_cap_inr: float = 0.0
    free_cash_flow_inr: float = 0.0


@dataclass
class PoliticalEvent:
    """A political/policy event relevant to predictions."""
    event_type: str
    description: str
    date: datetime
    relevance_score: float = 0.5  # 0-1, how relevant to Adani Group
    source_tier: int = 3


@dataclass
class PredictionOutput:
    """Output of a prediction generation."""
    id: str
    likely_action: str
    category: str
    timeline_start: str
    timeline_end: str
    confidence_score: float
    supporting_evidence: List[str]
    risk_factors: List[str]
    financial_signal: float = 0.0
    political_alignment: float = 0.0
    pattern_match: str = ""
    data_sources: List[str] = field(default_factory=list)


class PredictionEngine:
    """
    Hybrid Prediction Engine for AGSPE.

    Combines:
    1. Financial Indicators Analysis (Debt-to-Equity, Capex, Volatility)
    2. Political Alignment Scoring (Government proximity)
    3. Pattern Recognition (Acquisition cycles, Policy correlations)

    Generates probabilistic predictions with timelines and confidence scores.
    """

    def __init__(self):
        self.financial_weight = 0.35
        self.political_weight = 0.35
        self.pattern_weight = 0.30

    def generate_predictions(
        self,
        financial_data: Optional[List[Dict]] = None,
        political_events: Optional[List[Dict]] = None,
        historical_acquisitions: Optional[List[Dict]] = None,
        current_context: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Generate probabilistic predictions for Adani Group business moves.

        Args:
            financial_data: List of company financial data dicts
            political_events: List of political/policy event dicts
            historical_acquisitions: List of past acquisition dicts
            current_context: Additional context (date, market conditions, etc.)

        Returns:
            List of prediction dictionaries with confidence scores and timelines
        """
        predictions = []

        # Use provided data or defaults
        fin_data = financial_data or self._get_default_financial_data()
        pol_events = political_events or self._get_default_political_events()
        acquisitions = historical_acquisitions or self._get_default_acquisitions()
        context = current_context or {"date": datetime.utcnow(), "market_condition": "normal"}

        # Calculate component signals
        financial_signals = self._calculate_financial_signal(fin_data)
        political_alignment = self._calculate_political_alignment(pol_events)
        pattern_matches = self._match_acquisition_patterns(acquisitions, context)

        # Generate predictions from each pattern match
        for pattern in pattern_matches:
            timeline = self._generate_timeline(
                financial_signals.get("composite", 0.5),
                political_alignment,
                pattern["confidence_base"],
            )

            confidence = self._calculate_confidence(
                financial_signals.get("composite", 0.5),
                political_alignment,
                pattern["confidence_base"],
            )

            prediction = PredictionOutput(
                id=f"pred-{len(predictions)+1:03d}",
                likely_action=pattern["predicted_action"],
                category=pattern["category"],
                timeline_start=timeline[0],
                timeline_end=timeline[1],
                confidence_score=round(confidence * 100, 1),
                supporting_evidence=pattern.get("evidence", []),
                risk_factors=self._identify_risk_factors(financial_signals, political_alignment),
                financial_signal=financial_signals.get("composite", 0.0),
                political_alignment=political_alignment,
                pattern_match=pattern["name"],
                data_sources=pattern.get("sources", []),
            )
            predictions.append(self._prediction_to_dict(prediction))

        # Add policy-correlation predictions
        for corr_key, corr in POLICY_CORRELATIONS.items():
            confidence = self._calculate_confidence(
                financial_signals.get("composite", 0.5),
                political_alignment,
                corr["base_probability"],
            )

            timeline = self._generate_timeline(
                financial_signals.get("composite", 0.5),
                political_alignment,
                corr["base_probability"],
            )

            prediction = PredictionOutput(
                id=f"pred-policy-{corr_key}",
                likely_action=corr["predicted_action"],
                category="Policy Correlation",
                timeline_start=timeline[0],
                timeline_end=timeline[1],
                confidence_score=round(confidence * 100, 1),
                supporting_evidence=corr.get("evidence", []),
                risk_factors=self._identify_risk_factors(financial_signals, political_alignment),
                financial_signal=financial_signals.get("composite", 0.0),
                political_alignment=political_alignment,
                pattern_match=corr["trigger"],
                data_sources=["Policy correlation analysis"],
            )
            predictions.append(self._prediction_to_dict(prediction))

        # Sort by confidence score descending
        predictions.sort(key=lambda x: x["confidence_score"], reverse=True)

        return predictions

    def _calculate_financial_signal(self, financial_data: List[Dict]) -> Dict:
        """
        Analyze financial indicators to generate prediction signals.

        Returns composite score and individual component scores.
        """
        if not financial_data:
            return {"composite": 0.5, "debt_signal": 0.5, "capex_signal": 0.5, "volatility_signal": 0.5}

        total_market_cap = sum(f.get("market_cap_inr", 0) for f in financial_data)
        if total_market_cap == 0:
            total_market_cap = 1  # Avoid division by zero

        # Weighted average debt-to-equity (by market cap)
        weighted_dte = sum(
            f.get("debt_to_equity", 1.0) * f.get("market_cap_inr", 0)
            for f in financial_data
        ) / total_market_cap

        # Debt signal: Lower D/E is better (inverse relationship)
        debt_signal = max(0.0, min(1.0, 1.0 - (weighted_dte / 5.0)))

        # Capex signal: Higher capex commitment suggests expansion intent
        total_capex = sum(f.get("capex_commitment_inr", 0) for f in financial_data)
        capex_signal = min(1.0, total_capex / 200000) if total_capex > 0 else 0.3

        # Volatility signal: Lower volatility = more stable = higher confidence
        avg_volatility = sum(f.get("stock_volatility_30d", 30) for f in financial_data) / len(financial_data)
        volatility_signal = max(0.0, min(1.0, 1.0 - (avg_volatility / 60.0)))

        # Revenue growth signal
        avg_growth = sum(f.get("revenue_growth_yoy", 0.1) for f in financial_data) / len(financial_data)
        growth_signal = min(1.0, max(0.0, avg_growth / 0.3))

        # Composite financial signal
        composite = (
            debt_signal * 0.25 +
            capex_signal * 0.30 +
            volatility_signal * 0.20 +
            growth_signal * 0.25
        )

        return {
            "composite": round(composite, 4),
            "debt_signal": round(debt_signal, 4),
            "capex_signal": round(capex_signal, 4),
            "volatility_signal": round(volatility_signal, 4),
            "growth_signal": round(growth_signal, 4),
        }

    def _calculate_political_alignment(self, events: List[Dict]) -> float:
        """
        Calculate political alignment score based on proximity to
        government announcements and policy initiatives.
        """
        if not events:
            return 0.5

        weighted_sum = 0.0
        total_weight = 0.0

        for event in events:
            relevance = event.get("relevance_score", 0.5)
            tier = event.get("source_tier", 3)
            # Higher tier sources contribute more weight
            tier_weight = {1: 1.0, 2: 0.7, 3: 0.3}.get(tier, 0.3)
            weight = relevance * tier_weight

            # Positive events increase alignment, negative decrease
            impact = event.get("impact", 0.5)  # 0=very negative, 1=very positive
            weighted_sum += weight * impact
            total_weight += weight

        if total_weight == 0:
            return 0.5

        alignment = weighted_sum / total_weight
        return round(max(0.0, min(1.0, alignment)), 4)

    def _match_acquisition_patterns(
        self, acquisitions: List[Dict], context: Dict
    ) -> List[Dict]:
        """
        Match current market state to known acquisition/pattern templates.

        Identifies which pattern stage the group is likely in and
        generates predictions for the next stage.
        """
        matches = []

        # Analyze sector distribution of recent acquisitions
        sector_counts: Dict[str, int] = {}
        for acq in acquisitions:
            sector = acq.get("sector", "Unknown")
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        # Port/Infrastructure pattern
        if sector_counts.get("Ports", 0) + sector_counts.get("Infrastructure", 0) >= 3:
            matches.append({
                "name": ACQUISITION_PATTERNS["port_infrastructure"]["name"],
                "predicted_action": "New Port or Airport Concession Win",
                "category": "Infrastructure",
                "confidence_base": ACQUISITION_PATTERNS["port_infrastructure"]["confidence_base"],
                "evidence": [
                    "Multiple infrastructure acquisitions in recent years",
                    "Government privatization pipeline active",
                    "Adani Ports dominant market position",
                ],
                "sources": ["Acquisition pattern analysis", "Infrastructure sector data"],
            })

        # Green Energy pattern
        if sector_counts.get("Green Energy", 0) + sector_counts.get("Renewable", 0) >= 2:
            matches.append({
                "name": ACQUISITION_PATTERNS["green_energy_expansion"]["name"],
                "predicted_action": "Green Hydrogen JV or Solar Capacity Expansion",
                "category": "Green Energy",
                "confidence_base": ACQUISITION_PATTERNS["green_energy_expansion"]["confidence_base"],
                "evidence": [
                    "Government 500 GW renewable target",
                    "Adani Green 45 GW target by 2030",
                    "TotalEnergies partnership expansion",
                ],
                "sources": ["Green energy sector data", "Policy correlation"],
            })

        # Distressed asset pattern
        if sector_counts.get("Cement", 0) + sector_counts.get("Metals", 0) >= 2:
            matches.append({
                "name": ACQUISITION_PATTERNS["distressed_asset_acquisition"]["name"],
                "predicted_action": "Distressed Asset Bid in Cement or Metals",
                "category": "M&A",
                "confidence_base": ACQUISITION_PATTERNS["distressed_asset_acquisition"]["confidence_base"],
                "evidence": [
                    "Track record of distressed asset acquisitions (ACC, Ambuja)",
                    "NCLT pipeline active with stressed assets",
                    "Consolidation strategy in cement sector",
                ],
                "sources": ["M&A pattern analysis", "NCLT proceedings data"],
            })

        # Digital/Telecom pattern (emerging)
        if sector_counts.get("Digital", 0) + sector_counts.get("Telecom", 0) >= 1:
            matches.append({
                "name": "Digital Expansion",
                "predicted_action": "Data Center or Digital Infrastructure Investment",
                "category": "Digital Infrastructure",
                "confidence_base": 0.55,
                "evidence": [
                    "Adani Data Network license acquired",
                    "Growing data center demand in India",
                    "5G rollout creating new opportunities",
                ],
                "sources": ["Digital sector analysis", "Telecom licensing data"],
            })

        # If no specific pattern matched, add a general expansion prediction
        if not matches:
            matches.append({
                "name": ACQUISITION_PATTERNS["standard_acquisition"]["name"],
                "predicted_action": "Sector Expansion or New Acquisition",
                "category": "General",
                "confidence_base": 0.5,
                "evidence": [
                    "Historical expansion pattern continues",
                    "Group diversification strategy ongoing",
                ],
                "sources": ["General pattern analysis"],
            })

        return matches

    def _generate_timeline(
        self, financial_signal: float, political_alignment: float, pattern_confidence: float
    ) -> Tuple[str, str]:
        """
        Generate a confidence interval timeline for a prediction.

        Returns (timeline_start, timeline_end) as quarter strings.
        """
        # Base timeline: 6-18 months from now
        # Stronger signals = shorter timeline (more imminent)
        combined_signal = (financial_signal + political_alignment + pattern_confidence) / 3

        # Calculate months from now
        now = datetime.utcnow()
        min_months = max(3, int(12 * (1 - combined_signal)))
        max_months = min_months + max(3, int(6 * (1 - combined_signal)))

        start_date = now + timedelta(days=min_months * 30)
        end_date = now + timedelta(days=max_months * 30)

        return (
            self._date_to_quarter(start_date),
            self._date_to_quarter(end_date),
        )

    def _calculate_confidence(
        self, financial_signal: float, political_alignment: float, pattern_confidence: float
    ) -> float:
        """Calculate overall prediction confidence score."""
        confidence = (
            financial_signal * self.financial_weight +
            political_alignment * self.political_weight +
            pattern_confidence * self.pattern_weight
        )
        # Add small random variation for realism (±5%)
        variation = random.uniform(-0.05, 0.05)
        confidence = max(0.0, min(1.0, confidence + variation))
        return round(confidence, 4)

    def _identify_risk_factors(
        self, financial_signals: Dict, political_alignment: float
    ) -> List[str]:
        """Identify risk factors that could affect prediction accuracy."""
        risks = []

        if financial_signals.get("debt_signal", 0.5) < 0.4:
            risks.append("High debt-to-equity ratio across group companies")
        if financial_signals.get("volatility_signal", 0.5) < 0.4:
            risks.append("Elevated stock price volatility")
        if political_alignment < 0.4:
            risks.append("Weakening political alignment score")
        if political_alignment > 0.8:
            risks.append("Over-reliance on political connections - regulatory risk")

        risks.append("Regulatory scrutiny risk (SEBI/Hindenburg aftermath)")
        risks.append("Global commodity price fluctuation risk")
        risks.append("Currency risk (INR depreciation impact on USD debt")

        return risks

    def _date_to_quarter(self, date: datetime) -> str:
        """Convert a date to quarter string format (e.g., 'Q3 2026')."""
        quarter = (date.month - 1) // 3 + 1
        return f"Q{quarter} {date.year}"

    def _prediction_to_dict(self, pred: PredictionOutput) -> Dict:
        """Convert PredictionOutput to dictionary."""
        return {
            "id": pred.id,
            "likely_action": pred.likely_action,
            "category": pred.category,
            "timeline_start": pred.timeline_start,
            "timeline_end": pred.timeline_end,
            "confidence_score": pred.confidence_score,
            "supporting_evidence": pred.supporting_evidence,
            "risk_factors": pred.risk_factors,
            "financial_signal": pred.financial_signal,
            "political_alignment": pred.political_alignment,
            "pattern_match": pred.pattern_match,
            "data_sources": pred.data_sources,
            "created_at": datetime.utcnow().isoformat(),
            "validation_score": min(pred.confidence_score / 100, 1.0),
        }

    def _get_default_financial_data(self) -> List[Dict]:
        """Return default financial data for demo purposes."""
        return [
            {"company": "Adani Enterprises", "debt_to_equity": 1.2, "capex_commitment_inr": 55000,
             "stock_volatility_30d": 25, "revenue_growth_yoy": 0.18, "market_cap_inr": 280000},
            {"company": "Adani Ports & SEZ", "debt_to_equity": 0.9, "capex_commitment_inr": 30000,
             "stock_volatility_30d": 18, "revenue_growth_yoy": 0.22, "market_cap_inr": 310000},
            {"company": "Adani Green Energy", "debt_to_equity": 2.1, "capex_commitment_inr": 75000,
             "stock_volatility_30d": 35, "revenue_growth_yoy": 0.35, "market_cap_inr": 220000},
            {"company": "Adani Total Gas", "debt_to_equity": 0.5, "capex_commitment_inr": 15000,
             "stock_volatility_30d": 20, "revenue_growth_yoy": 0.12, "market_cap_inr": 260000},
            {"company": "Adani Power", "debt_to_equity": 1.8, "capex_commitment_inr": 40000,
             "stock_volatility_30d": 30, "revenue_growth_yoy": 0.25, "market_cap_inr": 180000},
        ]

    def _get_default_political_events(self) -> List[Dict]:
        """Return default political events for demo purposes."""
        return [
            {"event_type": "policy", "description": "Union Budget 2026 infrastructure allocation",
             "relevance_score": 0.9, "source_tier": 1, "impact": 0.85},
            {"event_type": "regulation", "description": "SEBI enhanced disclosure requirements",
             "relevance_score": 0.8, "source_tier": 1, "impact": 0.3},
            {"event_type": "policy", "description": "Green hydrogen policy incentives",
             "relevance_score": 0.85, "source_tier": 1, "impact": 0.8},
            {"event_type": "political", "description": "State election outcomes affecting project approvals",
             "relevance_score": 0.6, "source_tier": 2, "impact": 0.65},
            {"event_type": "regulation", "description": "Airport privatization Phase 3 announced",
             "relevance_score": 0.9, "source_tier": 1, "impact": 0.9},
        ]

    def _get_default_acquisitions(self) -> List[Dict]:
        """Return default acquisition history for demo purposes."""
        return [
            {"company_acquired": "ACC Ltd", "sector": "Cement", "year": 2022},
            {"company_acquired": "Ambuja Cements", "sector": "Cement", "year": 2022},
            {"company_acquired": "Jaypee Infratech", "sector": "Infrastructure", "year": 2023},
            {"company_acquired": "DB Power", "sector": "Power", "year": 2023},
            {"company_acquired": "Warora-Hingoni MW", "sector": "Power", "year": 2024},
            {"company_acquired": "ITD Cementation", "sector": "Infrastructure", "year": 2024},
            {"company_acquired": "NDTV", "sector": "Media", "year": 2022},
            {"company_acquired": "Haigreeva Inc", "sector": "Green Energy", "year": 2025},
        ]
