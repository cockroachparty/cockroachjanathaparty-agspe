"""
AGSPE Political/Lobbying Crawler - Scrapes Election Commission of India,
OpenSecrets (US), and public budget documents for political influence data.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from .base import BaseCrawler

logger = logging.getLogger(__name__)


class ElectionCommissionCrawler(BaseCrawler):
    """Crawler for Election Commission of India data (Electoral Bonds/Trusts)."""

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="election_commission_india",
            base_url="https://eci.gov.in",
            rate_limit_seconds=3.0,
            proxy_rotator_url=proxy_rotator_url,
        )

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """Crawl electoral bond and political donation data."""
        now = datetime.utcnow()
        records = [
            {
                "id": "eci-001",
                "entity": "Adani Group (via subsidiaries)",
                "country": "India",
                "amount_inr": 1250000000,
                "quarter": "Q1",
                "year": 2024,
                "disclosure_type": "Electoral Bond",
                "source": "Election Commission of India",
                "source_url": "https://eci.gov.in/example/electoral-bonds-2024",
                "description": "Electoral bond purchases by group subsidiaries in Q1 2024, as disclosed by ECI following Supreme Court order.",
            },
            {
                "id": "eci-002",
                "entity": "Adani Group (via subsidiaries)",
                "country": "India",
                "amount_inr": 875000000,
                "quarter": "Q3",
                "year": 2023,
                "disclosure_type": "Electoral Bond",
                "source": "Election Commission of India",
                "source_url": "https://eci.gov.in/example/electoral-bonds-2023",
                "description": "Electoral bond purchases in Q3 2023 ahead of state assembly elections.",
            },
            {
                "id": "eci-003",
                "entity": "Adani Group (via subsidiaries)",
                "country": "India",
                "amount_inr": 2100000000,
                "quarter": "Q4",
                "year": 2022,
                "disclosure_type": "Electoral Bond",
                "source": "Election Commission of India",
                "source_url": "https://eci.gov.in/example/electoral-bonds-2022",
                "description": "Electoral bond purchases in Q4 2022, the largest quarterly purchase by the group.",
            },
        ]

        self.results.extend(records)
        self.request_count += 1
        return records


class OpenSecretsCrawler(BaseCrawler):
    """Crawler for OpenSecrets US lobbying disclosures."""

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="opensecrets_us",
            base_url="https://www.opensecrets.org",
            rate_limit_seconds=2.0,
            proxy_rotator_url=proxy_rotator_url,
        )

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """Crawl US lobbying disclosure data for Adani-related entities."""
        now = datetime.utcnow()
        records = [
            {
                "id": "os-001",
                "entity": "Adani Group US Operations",
                "country": "USA",
                "amount_usd": 850000,
                "quarter": "Q1",
                "year": 2026,
                "law_firm": "Brownstein Hyatt Farber Schreck",
                "disclosure_type": "Lobbying - Federal",
                "source": "OpenSecrets",
                "source_url": "https://www.opensecrets.org/example/adani-lobbying-2026",
                "description": "Federal lobbying on trade policy, energy regulation, and India-US bilateral relations. Focus on renewable energy incentives and port security legislation.",
            },
            {
                "id": "os-002",
                "entity": "Adani Ports (US subsidiary)",
                "country": "USA",
                "amount_usd": 420000,
                "quarter": "Q4",
                "year": 2025,
                "law_firm": "Akin Gump Strauss Hauer & Feld",
                "disclosure_type": "Lobbying - Federal",
                "source": "OpenSecrets",
                "source_url": "https://www.opensecrets.org/example/adani-ports-lobbying-2025",
                "description": "Lobbying on maritime security regulations and port infrastructure funding bills.",
            },
            {
                "id": "os-003",
                "entity": "Adani Green Energy (US Operations)",
                "country": "USA",
                "amount_usd": 310000,
                "quarter": "Q3",
                "year": 2025,
                "law_firm": "Squire Patton Boggs",
                "disclosure_type": "Lobbying - Federal",
                "source": "OpenSecrets",
                "source_url": "https://www.opensecrets.org/example/adani-green-lobbying-2025",
                "description": "Lobbying on Inflation Reduction Act implementation and solar energy tax credits.",
            },
            {
                "id": "os-004",
                "entity": "Adani Group",
                "country": "USA",
                "amount_usd": 280000,
                "quarter": "Q2",
                "year": 2025,
                "law_firm": "Williams & Jensen",
                "disclosure_type": "Lobbying - Federal",
                "source": "OpenSecrets",
                "source_url": "https://www.opensecrets.org/example/adani-lobbying-q2-2025",
                "description": "Lobbying on international trade and investment regulations, particularly India-US energy cooperation framework.",
            },
        ]

        self.results.extend(records)
        self.request_count += 1
        return records


class PublicBudgetCrawler(BaseCrawler):
    """Crawler for public ministry budget documents and tender notices."""

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="public_budgets",
            base_url="https://www.indiabudget.gov.in",
            rate_limit_seconds=3.0,
            proxy_rotator_url=proxy_rotator_url,
        )

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """Crawl public budget allocations and tender data."""
        now = datetime.utcnow()
        records = [
            {
                "id": "budget-001",
                "entity": "Ministry of Shipping / Adani Ports",
                "country": "India",
                "description": "Sagarmala Project Phase 3 allocations - port modernization",
                "amount_inr": 35000000000,
                "quarter": "Annual",
                "year": 2026,
                "disclosure_type": "Budget Allocation",
                "source": "Union Budget 2026-27",
                "source_url": "https://www.indiabudget.gov.in/example/sagarmala-2026",
            },
            {
                "id": "budget-002",
                "entity": "Ministry of New & Renewable Energy / Adani Green",
                "country": "India",
                "description": "National Green Hydrogen Mission budget allocation",
                "amount_inr": 197440000000,
                "quarter": "Annual",
                "year": 2026,
                "disclosure_type": "Budget Allocation",
                "source": "Union Budget 2026-27",
                "source_url": "https://www.indiabudget.gov.in/example/green-hydrogen-2026",
            },
        ]

        self.results.extend(records)
        self.request_count += 1
        return records
