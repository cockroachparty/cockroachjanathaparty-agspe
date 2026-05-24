"""
AGSPE Bias Detector - Detects media bias indicators,
flags pro-group language, and tracks source reliability over time.
"""
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field

from ..utils.text_processing import detect_pro_group_language


@dataclass
class SourceReliability:
    """Track reliability metrics for a source over time."""
    name: str
    tier: int
    total_articles: int = 0
    validated_articles: int = 0
    retracted_articles: int = 0
    average_validation_score: float = 0.0
    bias_incidents: int = 0
    last_updated: Optional[datetime] = None

    @property
    def reliability_score(self) -> float:
        """Calculate reliability score based on historical performance."""
        if self.total_articles == 0:
            return 0.5
        validation_rate = self.validated_articles / self.total_articles
        retraction_penalty = self.retracted_articles * 0.1
        bias_penalty = self.bias_incidents * 0.05
        score = (validation_rate * 0.6 + self.average_validation_score * 0.4)
        score -= retraction_penalty + bias_penalty
        return max(0.0, min(1.0, score))


class BiasDetector:
    """
    Media Bias Detection Engine for AGSPE.

    Analyzes news articles and sources for bias indicators,
    pro-group language patterns, and reliability metrics.
    """

    def __init__(self):
        self.source_reliability: Dict[str, SourceReliability] = {}
        self._init_default_sources()

    def _init_default_sources(self) -> None:
        """Initialize reliability tracking for known sources."""
        default_sources = [
            ("Reuters", 1), ("AP News", 1), ("BBC", 1),
            ("Al Jazeera", 1), ("OCCRP", 1), ("Bloomberg", 1),
            ("Financial Times", 1),
            ("The Hindu", 2), ("Scroll.in", 2), ("The Wire", 2),
            ("Business Standard", 2),
            ("NDTV", 3), ("Times Now", 3), ("Republic TV", 3),
            ("Zee News", 3), ("Adani Group PR", 3),
        ]

        for name, tier in default_sources:
            self.source_reliability[name] = SourceReliability(
                name=name,
                tier=tier,
                total_articles=0,
                average_validation_score={1: 0.85, 2: 0.70, 3: 0.35}.get(tier, 0.3),
                last_updated=datetime.utcnow(),
            )

    def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze an article for bias indicators.

        Args:
            article: Dict with 'title', 'content_snippet', 'source', 'source_tier'

        Returns:
            Bias analysis result dictionary
        """
        text = f"{article.get('title', '')} {article.get('content_snippet', '')}"
        source = article.get("source", "Unknown")
        tier = article.get("source_tier", 3)

        # Detect pro-group language
        language_result = detect_pro_group_language(text)

        # Calculate source bias factor
        reliability = self.source_reliability.get(source)
        source_bias_factor = 0.0
        if reliability:
            source_bias_factor = 1.0 - reliability.reliability_score

        # Combined bias score
        bias_score = (
            language_result["bias_score"] * 0.4 +
            source_bias_factor * 0.3 +
            (1.0 - {1: 0.9, 2: 0.7, 3: 0.3}.get(tier, 0.3)) * 0.3
        )

        # Determine bias risk
        if bias_score > 0.6:
            bias_risk = "High"
        elif bias_score > 0.3:
            bias_risk = "Medium"
        else:
            bias_risk = "Low"

        result = {
            "article_id": article.get("id", "unknown"),
            "source": source,
            "source_tier": tier,
            "bias_score": round(bias_score, 3),
            "bias_risk_level": bias_risk,
            "pro_group_language_detected": language_result["is_likely_promotional"],
            "pro_group_indicators": language_result["detected_pro_phrases"],
            "negative_indicators": language_result["detected_neg_phrases"],
            "source_reliability_score": reliability.reliability_score if reliability else 0.5,
            "warning": None,
        }

        # Add warnings for high-risk cases
        if tier == 3 and language_result["is_likely_promotional"]:
            result["warning"] = "BIAS_DETECTED: Pro-group language in Tier 3 source - requires Tier 1 corroboration"
        elif tier == 3:
            result["warning"] = "REQUIRES_VERIFICATION: Tier 3 source lacks independent corroboration"

        # Update source reliability
        self._update_source_reliability(source, article, result)

        return result

    def _update_source_reliability(
        self, source: str, article: Dict, bias_result: Dict
    ) -> None:
        """Update source reliability tracking based on analysis."""
        if source not in self.source_reliability:
            self.source_reliability[source] = SourceReliability(
                name=source,
                tier=article.get("source_tier", 3),
                last_updated=datetime.utcnow(),
            )

        rel = self.source_reliability[source]
        rel.total_articles += 1

        # Update average validation score
        article_score = article.get("validation_score", 0.5)
        rel.average_validation_score = (
            (rel.average_validation_score * (rel.total_articles - 1) + article_score)
            / rel.total_articles
        )

        if bias_result["bias_risk_level"] == "Low":
            rel.validated_articles += 1
        if bias_result["pro_group_language_detected"]:
            rel.bias_incidents += 1

        rel.last_updated = datetime.utcnow()

    def get_source_reliability_report(self) -> List[Dict]:
        """Get reliability report for all tracked sources."""
        report = []
        for name, rel in sorted(
            self.source_reliability.items(), key=lambda x: x[1].reliability_score, reverse=True
        ):
            report.append({
                "source": name,
                "tier": rel.tier,
                "reliability_score": round(rel.reliability_score, 3),
                "total_articles": rel.total_articles,
                "validated_articles": rel.validated_articles,
                "bias_incidents": rel.bias_incidents,
                "average_validation_score": round(rel.average_validation_score, 3),
            })
        return report
