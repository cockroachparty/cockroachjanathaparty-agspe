"""
AGSPE News Crawler - Aggregates news from tiered sources
with bias detection and validation metadata.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from .base import BaseCrawler
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Source tier definitions
SOURCE_TIERS = {
    # Tier 1 - High Weight (0.9)
    "reuters": {"tier": 1, "weight": 0.9, "name": "Reuters", "base_url": "https://www.reuters.com"},
    "ap_news": {"tier": 1, "weight": 0.9, "name": "AP News", "base_url": "https://apnews.com"},
    "bbc": {"tier": 1, "weight": 0.9, "name": "BBC", "base_url": "https://www.bbc.com"},
    "al_jazeera": {"tier": 1, "weight": 0.9, "name": "Al Jazeera", "base_url": "https://www.aljazeera.com"},
    "occrp": {"tier": 1, "weight": 0.9, "name": "OCCRP", "base_url": "https://www.occrp.org"},
    "bloomberg": {"tier": 1, "weight": 0.9, "name": "Bloomberg", "base_url": "https://www.bloomberg.com"},
    "financial_times": {"tier": 1, "weight": 0.9, "name": "Financial Times", "base_url": "https://www.ft.com"},

    # Tier 2 - Medium Weight (0.7)
    "the_hindu": {"tier": 2, "weight": 0.7, "name": "The Hindu", "base_url": "https://www.thehindu.com"},
    "scroll_in": {"tier": 2, "weight": 0.7, "name": "Scroll.in", "base_url": "https://scroll.in"},
    "the_wire": {"tier": 2, "weight": 0.7, "name": "The Wire", "base_url": "https://thewire.in"},
    "business_standard": {"tier": 2, "weight": 0.7, "name": "Business Standard", "base_url": "https://www.business-standard.com"},

    # Tier 3 - Low Weight (0.3) - "Requires Verification"
    "ndtv": {"tier": 3, "weight": 0.3, "name": "NDTV", "base_url": "https://www.ndtv.com", "tag": "Requires Verification"},
    "times_now": {"tier": 3, "weight": 0.3, "name": "Times Now", "base_url": "https://www.timesnownews.com", "tag": "Requires Verification"},
    "republic_tv": {"tier": 3, "weight": 0.3, "name": "Republic TV", "base_url": "https://www.republicworld.com", "tag": "Requires Verification"},
    "zee_news": {"tier": 3, "weight": 0.3, "name": "Zee News", "base_url": "https://zeenews.india.com", "tag": "Requires Verification"},
}


class NewsCrawler(BaseCrawler):
    """
    News aggregator crawler that collects articles from
    multiple tiered sources with proper validation metadata.
    """

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="news_aggregator",
            base_url="",
            rate_limit_seconds=2.0,
            proxy_rotator_url=proxy_rotator_url,
        )
        self.rate_limiter = RateLimiter(requests_per_minute=30)
        self.source_tiers = SOURCE_TIERS

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """
        Crawl news from all configured sources.

        In production, this would make actual HTTP requests.
        For the demo, returns pre-configured sample data.

        Args:
            query: Search query (e.g., "Adani Group")
            sources: Optional list of specific source keys to crawl
            tier_filter: Optional tier number to filter by (1, 2, or 3)

        Returns:
            List of news article dictionaries
        """
        sources = kwargs.get("sources", None)
        tier_filter = kwargs.get("tier_filter", None)

        # In demo mode, return sample data
        articles = self._get_sample_articles(query)

        # Filter by source if specified
        if sources:
            articles = [a for a in articles if a.get("source_key") in sources]

        # Filter by tier if specified
        if tier_filter:
            articles = [a for a in articles if a.get("source_tier") == tier_filter]

        self.results.extend(articles)
        self.request_count += 1

        return articles

    def get_source_tier_info(self, source_key: str) -> Dict:
        """Get tier information for a specific source."""
        return self.source_tiers.get(source_key, {"tier": 3, "weight": 0.3, "name": "Unknown"})

    def _get_sample_articles(self, query: Optional[str] = None) -> List[Dict]:
        """Generate sample news articles for demo purposes."""
        now = datetime.utcnow()

        articles = [
            {
                "id": "news-001",
                "title": "Adani Ports Wins Vizhinjam International Terminal Concession",
                "source": "Reuters",
                "source_key": "reuters",
                "source_tier": 1,
                "url": "https://www.reuters.com/example/adani-ports-vizhinjam",
                "published_at": (now - timedelta(hours=2)).isoformat(),
                "content_snippet": "Adani Ports and Special Economic Zone has been awarded the concession to operate the Vizhinjam International Transhipment Terminal, marking a significant expansion of India's largest private port operator.",
                "validation_score": 0.92,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Ports & SEZ", "Adani Enterprises"],
                "keywords": ["ports", "concession", "infrastructure", "Vizhinjam"],
            },
            {
                "id": "news-002",
                "title": "Adani Green Energy Announces 10 GW Solar Project in Rajasthan",
                "source": "Bloomberg",
                "source_key": "bloomberg",
                "source_tier": 1,
                "url": "https://www.bloomberg.com/example/adani-green-solar",
                "published_at": (now - timedelta(hours=5)).isoformat(),
                "content_snippet": "Adani Green Energy Ltd has announced plans to develop a 10 GW solar power project in Rajasthan, aligning with India's renewable energy targets and the company's 45 GW goal by 2030.",
                "validation_score": 0.88,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Green Energy"],
                "keywords": ["solar", "renewable", "Rajasthan", "green energy"],
            },
            {
                "id": "news-003",
                "title": "SEBI Tightens Disclosure Norms for Conglomerates with Multiple Listed Entities",
                "source": "The Hindu",
                "source_key": "the_hindu",
                "source_tier": 2,
                "url": "https://www.thehindu.com/example/sebi-disclosure-norms",
                "published_at": (now - timedelta(hours=8)).isoformat(),
                "content_snippet": "The Securities and Exchange Board of India has proposed enhanced disclosure requirements for business groups with more than five listed entities, which could impact the Adani Group's reporting obligations.",
                "validation_score": 0.78,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Enterprises", "Adani Ports & SEZ", "Adani Green Energy"],
                "keywords": ["SEBI", "regulation", "disclosure", "compliance"],
            },
            {
                "id": "news-004",
                "title": "Adani Group Set to Revolutionize Indian Aviation with New Airport Bids",
                "source": "NDTV",
                "source_key": "ndtv",
                "source_tier": 3,
                "url": "https://www.ndtv.com/example/adani-airport-bids",
                "published_at": (now - timedelta(hours=3)).isoformat(),
                "content_snippet": "The Adani Group is reportedly preparing bids for three new airport concessions under the government's Phase 3 privatization program, which could further consolidate its position as India's largest private airport operator.",
                "validation_score": 0.32,
                "bias_risk_level": "High",
                "tag": "Requires Verification",
                "related_companies": ["Adani Enterprises", "Adani Airports"],
                "keywords": ["airport", "privatization", "aviation", "bids"],
            },
            {
                "id": "news-005",
                "title": "Adani Total Gas Expands CNG Network to 50 New Districts",
                "source": "AP News",
                "source_key": "ap_news",
                "source_tier": 1,
                "url": "https://apnews.com/example/adani-total-gas-cng",
                "published_at": (now - timedelta(hours=12)).isoformat(),
                "content_snippet": "Adani Total Gas Ltd has announced the expansion of its compressed natural gas distribution network to 50 new districts across India, as part of its city gas distribution growth strategy.",
                "validation_score": 0.85,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Total Gas"],
                "keywords": ["CNG", "gas distribution", "expansion"],
            },
            {
                "id": "news-006",
                "title": "Hindenburg Research Publishes Follow-Up Report on Adani Group Debt Structure",
                "source": "OCCRP",
                "source_key": "occrp",
                "source_tier": 1,
                "url": "https://www.occrp.org/example/hindenburg-follow-up",
                "published_at": (now - timedelta(hours=24)).isoformat(),
                "content_snippet": "OCCRP and investigative partners have published findings examining the Adani Group's offshore debt structures and related-party transactions, raising questions about governance and transparency.",
                "validation_score": 0.91,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Enterprises", "Adani Group"],
                "keywords": ["Hindenburg", "debt", "offshore", "governance"],
            },
            {
                "id": "news-007",
                "title": "Adani Group Unveils Green Hydrogen Roadmap at RE-Invest 2026",
                "source": "Times Now",
                "source_key": "times_now",
                "source_tier": 3,
                "url": "https://www.timesnownews.com/example/adani-green-hydrogen",
                "published_at": (now - timedelta(hours=6)).isoformat(),
                "content_snippet": "Gautam Adani announced an ambitious green hydrogen production roadmap targeting 1 million tonnes per annum by 2030, with an investment commitment of USD 50 billion over the next decade.",
                "validation_score": 0.28,
                "bias_risk_level": "High",
                "tag": "Requires Verification",
                "related_companies": ["Adani Green Energy", "Adani Enterprises"],
                "keywords": ["green hydrogen", "investment", "renewable"],
            },
            {
                "id": "news-008",
                "title": "India's Union Budget 2026-27 Allocates Record Infrastructure Spending",
                "source": "BBC",
                "source_key": "bbc",
                "source_tier": 1,
                "url": "https://www.bbc.com/example/india-budget-infrastructure",
                "published_at": (now - timedelta(hours=48)).isoformat(),
                "content_snippet": "India's Finance Minister announced a record infrastructure allocation of INR 15 lakh crore in the Union Budget 2026-27, with significant focus on ports, airports, and renewable energy sectors.",
                "validation_score": 0.95,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Ports & SEZ", "Adani Enterprises", "Adani Green Energy"],
                "keywords": ["budget", "infrastructure", "spending", "policy"],
            },
            {
                "id": "news-009",
                "title": "Adani Defense Wins UAV Supply Contract from Indian Army",
                "source": "Business Standard",
                "source_key": "business_standard",
                "source_tier": 2,
                "url": "https://www.business-standard.com/example/adani-defense-uav",
                "published_at": (now - timedelta(hours=16)).isoformat(),
                "content_snippet": "Adani Defense Systems & Technologies has secured a contract to supply medium-altitude long-endurance UAVs to the Indian Army, marking its entry into the defense manufacturing supply chain.",
                "validation_score": 0.75,
                "bias_risk_level": "Medium",
                "tag": "Unverified",
                "related_companies": ["Adani Enterprises"],
                "keywords": ["defense", "UAV", "military", "contract"],
            },
            {
                "id": "news-010",
                "title": "Adani Data Centers Plans 1 GW Capacity Expansion Across India",
                "source": "Financial Times",
                "source_key": "financial_times",
                "source_tier": 1,
                "url": "https://www.ft.com/example/adani-data-centers",
                "published_at": (now - timedelta(hours=20)).isoformat(),
                "content_snippet": "Adani Data Centers, a unit of Adani Enterprises, is planning a massive expansion to 1 GW of data center capacity across six Indian cities, riding the AI and cloud computing wave in the subcontinent.",
                "validation_score": 0.87,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Enterprises"],
                "keywords": ["data center", "AI", "cloud", "digital infrastructure"],
            },
            {
                "id": "news-011",
                "title": "Electoral Bond Data Reveals Corporate Donation Patterns in India",
                "source": "Scroll.in",
                "source_key": "scroll_in",
                "source_tier": 2,
                "url": "https://scroll.in/example/electoral-bonds-corporate",
                "published_at": (now - timedelta(hours=72)).isoformat(),
                "content_snippet": "Analysis of released electoral bond data shows significant corporate donations to ruling party, with infrastructure and energy companies among the top contributors.",
                "validation_score": 0.72,
                "bias_risk_level": "Medium",
                "tag": "Verified",
                "related_companies": ["Adani Group"],
                "keywords": ["electoral bonds", "donations", "political", "transparency"],
            },
            {
                "id": "news-012",
                "title": "Adani Wilmar Reports Strong Q4 FY26 Results, Market Share Gains",
                "source": "Reuters",
                "source_key": "reuters",
                "source_tier": 1,
                "url": "https://www.reuters.com/example/adani-wilmar-q4",
                "published_at": (now - timedelta(hours=10)).isoformat(),
                "content_snippet": "Adani Wilmar reported a 34% increase in net profit for Q4 FY26, driven by volume growth in edible oils and packaged foods, gaining market share from competitors.",
                "validation_score": 0.90,
                "bias_risk_level": "Low",
                "tag": "Verified",
                "related_companies": ["Adani Wilmar"],
                "keywords": ["results", "FMCG", "edible oil", "profit"],
            },
        ]

        # Filter by query if provided
        if query and query.lower() != "adani":
            query_lower = query.lower()
            articles = [
                a for a in articles
                if query_lower in a["title"].lower() or query_lower in a["content_snippet"].lower()
            ]

        return articles
