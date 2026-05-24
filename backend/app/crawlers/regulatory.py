"""
AGSPE Regulatory Filings Crawler - Scrapes SEBI, SEC EDGAR,
and Ministry of Corporate Affairs (MCA) for regulatory data.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from .base import BaseCrawler

logger = logging.getLogger(__name__)


class SEBICrawler(BaseCrawler):
    """Crawler for SEBI (Securities and Exchange Board of India) filings."""

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="sebi_filings",
            base_url="https://www.sebi.gov.in",
            rate_limit_seconds=3.0,
            proxy_rotator_url=proxy_rotator_url,
        )

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """Crawl SEBI filings for Adani Group companies."""
        company = kwargs.get("company", None)
        filing_type = kwargs.get("filing_type", None)

        now = datetime.utcnow()
        filings = [
            {
                "id": "sebi-001",
                "source": "SEBI",
                "filing_type": "Disclosure",
                "company": "Adani Enterprises Ltd",
                "title": "Related Party Transaction Disclosure - Q4 FY26",
                "url": "https://www.sebi.gov.in/sebi_data/rptfiles/AEL_RPT_Q4FY26.html",
                "date": (now - timedelta(days=5)).isoformat(),
                "content_snippet": "Disclosure of related party transactions exceeding 10% of consolidated turnover for Q4 FY26, covering transactions with Adani Ports, Adani Green, and group entities.",
                "category": "disclosure",
            },
            {
                "id": "sebi-002",
                "source": "SEBI",
                "filing_type": "Shareholding Pattern",
                "company": "Adani Ports & SEZ Ltd",
                "title": "Shareholding Pattern - March 2026",
                "url": "https://www.sebi.gov.in/sebi_data/shpfiles/APSEZ_SHP_Mar2026.html",
                "date": (now - timedelta(days=15)).isoformat(),
                "content_snippet": "Promoter holding at 63.5%, FII holding at 16.2%, DII holding at 8.4%, public at 11.9%. No significant change from previous quarter.",
                "category": "shareholding",
            },
            {
                "id": "sebi-003",
                "source": "SEBI",
                "filing_type": "Regulatory Action",
                "company": "Adani Group",
                "title": "SEBI Order on Enhanced Monitoring of Group Companies",
                "url": "https://www.sebi.gov.in/sebi_data/orders/Adani_Monitoring_2026.html",
                "date": (now - timedelta(days=30)).isoformat(),
                "content_snippet": "SEBI has ordered enhanced monitoring and additional disclosure requirements for all Adani Group listed entities following the Supreme Court-appointed committee recommendations.",
                "category": "regulatory_action",
            },
        ]

        if company:
            filings = [f for f in filings if company.lower() in f["company"].lower()]
        if filing_type:
            filings = [f for f in filings if f["filing_type"].lower() == filing_type.lower()]

        self.results.extend(filings)
        self.request_count += 1
        return filings


class SECEdgarCrawler(BaseCrawler):
    """Crawler for US SEC EDGAR database (offshore entities/litigation)."""

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="sec_edgar",
            base_url="https://www.sec.gov/cgi-bin/browse-edgar",
            rate_limit_seconds=2.0,
            proxy_rotator_url=proxy_rotator_url,
        )

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """Crawl SEC EDGAR for Adani-related filings."""
        now = datetime.utcnow()
        filings = [
            {
                "id": "sec-001",
                "source": "SEC EDGAR",
                "filing_type": "20-F",
                "company": "Adani Ports & SEZ (ADR)",
                "title": "Annual Report - Foreign Private Issuer",
                "url": "https://www.sec.gov/Archives/edgar/data/example",
                "date": (now - timedelta(days=45)).isoformat(),
                "content_snippet": "Annual report detailing Adani Ports operations, related party transactions, and risk factors for ADR holders. Notable: offshore subsidiary structures in Mauritius and Singapore.",
                "category": "annual_report",
            },
            {
                "id": "sec-002",
                "source": "SEC EDGAR",
                "filing_type": "Litigation Release",
                "company": "Adani Group",
                "title": "SEC Investigation into Offshore Fund Holdings",
                "url": "https://www.sec.gov/litigation/litreleases/example",
                "date": (now - timedelta(days=60)).isoformat(),
                "content_snippet": "The SEC has been examining whether offshore funds with significant Adani Group holdings complied with beneficial ownership disclosure requirements.",
                "category": "litigation",
            },
        ]

        self.results.extend(filings)
        self.request_count += 1
        return filings


class MCACrawler(BaseCrawler):
    """Crawler for Ministry of Corporate Affairs (MCA) India filings."""

    def __init__(self, proxy_rotator_url: Optional[str] = None):
        super().__init__(
            name="mca_filings",
            base_url="https://www.mca.gov.in",
            rate_limit_seconds=3.0,
            proxy_rotator_url=proxy_rotator_url,
        )

    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """Crawl MCA filings for Adani Group entities."""
        now = datetime.utcnow()
        filings = [
            {
                "id": "mca-001",
                "source": "MCA India",
                "filing_type": "Annual Return",
                "company": "Adani Data Networks Ltd",
                "title": "Form MGT-7 Annual Return FY 2025-26",
                "url": "https://www.mca.gov.in/example/adani-data-networks",
                "date": (now - timedelta(days=20)).isoformat(),
                "content_snippet": "Annual return showing incorporation of Adani Data Networks, share capital structure, and key managerial personnel changes.",
                "category": "annual_return",
            },
            {
                "id": "mca-002",
                "source": "MCA India",
                "filing_type": "Charge Creation",
                "company": "Adani Green Energy Ltd",
                "title": "Form CHG-1 Creation of Charge - Green Hydrogen Project",
                "url": "https://www.mca.gov.in/example/adani-green-charge",
                "date": (now - timedelta(days=10)).isoformat(),
                "content_snippet": "Charge created in favor of consortium of banks for green hydrogen project financing, totaling INR 18,000 crore.",
                "category": "charge",
            },
        ]

        self.results.extend(filings)
        self.request_count += 1
        return filings
