"""
AGSPE Crawler Tests
Tests for news, regulatory, and political crawlers.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers.news import NewsCrawler, SOURCE_TIERS
from app.crawlers.regulatory import SEBICrawler, SECEdgarCrawler, MCACrawler
from app.crawlers.political import ElectionCommissionCrawler, OpenSecretsCrawler
from app.crawlers.rate_limiter import RateLimiter, TokenBucket


class TestNewsCrawler:
    """Tests for the News Crawler."""

    def setup_method(self):
        self.crawler = NewsCrawler()

    def test_crawl_returns_articles(self):
        """Crawling should return a list of articles."""
        articles = self.crawler.crawl()
        assert isinstance(articles, list)
        assert len(articles) > 0

    def test_articles_have_required_fields(self):
        """Each article should have required fields."""
        articles = self.crawler.crawl()
        required = ["id", "title", "source", "source_tier", "validation_score"]
        for article in articles:
            for field in required:
                assert field in article, f"Missing field: {field}"

    def test_source_tiers_correct(self):
        """Articles should have correct source tiers."""
        articles = self.crawler.crawl()
        for article in articles:
            assert article["source_tier"] in [1, 2, 3]

    def test_tier_3_flagged(self):
        """Tier 3 articles should be flagged as requiring verification."""
        articles = self.crawler.crawl()
        tier_3_articles = [a for a in articles if a["source_tier"] == 3]
        for article in tier_3_articles:
            assert article["tag"] == "Requires Verification"
            assert article["validation_score"] < 0.5

    def test_source_tier_lookup(self):
        """Source tier lookup should return correct info."""
        info = self.crawler.get_source_tier_info("reuters")
        assert info["tier"] == 1
        assert info["weight"] == 0.9

    def test_crawler_stats(self):
        """Crawler should track statistics."""
        self.crawler.crawl()
        stats = self.crawler.get_stats()
        assert stats["request_count"] > 0
        assert stats["name"] == "news_aggregator"


class TestRegulatoryCrawlers:
    """Tests for Regulatory Crawlers."""

    def test_sebi_crawler(self):
        """SEBI crawler should return filings."""
        crawler = SEBICrawler()
        filings = crawler.crawl()
        assert len(filings) > 0
        assert all(f["source"] == "SEBI" for f in filings)

    def test_sec_edgar_crawler(self):
        """SEC EDGAR crawler should return filings."""
        crawler = SECEdgarCrawler()
        filings = crawler.crawl()
        assert len(filings) > 0
        assert all(f["source"] == "SEC EDGAR" for f in filings)

    def test_mca_crawler(self):
        """MCA crawler should return filings."""
        crawler = MCACrawler()
        filings = crawler.crawl()
        assert len(filings) > 0
        assert all(f["source"] == "MCA India" for f in filings)


class TestPoliticalCrawlers:
    """Tests for Political/Lobbying Crawlers."""

    def test_election_commission_crawler(self):
        """ECI crawler should return records."""
        crawler = ElectionCommissionCrawler()
        records = crawler.crawl()
        assert len(records) > 0

    def test_opensecrets_crawler(self):
        """OpenSecrets crawler should return lobbying records."""
        crawler = OpenSecretsCrawler()
        records = crawler.crawl()
        assert len(records) > 0
        for record in records:
            assert record["source"] == "OpenSecrets"
            assert "amount_usd" in record


class TestRateLimiter:
    """Tests for the Rate Limiter."""

    def test_token_bucket_basic(self):
        """Token bucket should allow consumption when tokens available."""
        bucket = TokenBucket(rate=10, capacity=5)
        assert bucket.consume(1) is True

    def test_token_bucket_capacity(self):
        """Token bucket should respect capacity."""
        bucket = TokenBucket(rate=1, capacity=2)
        assert bucket.consume(1) is True
        assert bucket.consume(1) is True
        # Should be out of tokens
        assert bucket.consume(1) is False

    def test_rate_limiter_acquire(self):
        """Rate limiter should allow requests within limits."""
        limiter = RateLimiter(requests_per_minute=60, burst_capacity=5)
        # Should not raise
        limiter.acquire("test.com")

    def test_rate_limiter_no_proxy(self):
        """Rate limiter without proxies should return None."""
        limiter = RateLimiter()
        assert limiter.get_next_proxy() is None

    def test_rate_limiter_with_proxy(self):
        """Rate limiter with proxies should rotate through them."""
        limiter = RateLimiter()
        limiter.add_proxy("http://proxy1:8080")
        limiter.add_proxy("http://proxy2:8080")

        p1 = limiter.get_next_proxy()
        p2 = limiter.get_next_proxy()
        p3 = limiter.get_next_proxy()

        assert p1 == "http://proxy1:8080"
        assert p2 == "http://proxy2:8080"
        assert p3 == "http://proxy1:8080"  # Should rotate back


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
