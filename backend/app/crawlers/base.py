"""
AGSPE Base Crawler - Abstract base class with rate limiting,
proxy rotation, and error handling for all data scrapers.
"""
import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class BaseCrawler(ABC):
    """
    Abstract base crawler with rate limiting and proxy rotation.

    All scrapers inherit from this class and implement the `crawl` method.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        rate_limit_seconds: float = 2.0,
        max_retries: int = 3,
        proxy_rotator_url: Optional[str] = None,
    ):
        self.name = name
        self.base_url = base_url
        self.rate_limit_seconds = rate_limit_seconds
        self.max_retries = max_retries
        self.proxy_rotator_url = proxy_rotator_url
        self.last_request_time: float = 0.0
        self.request_count: int = 0
        self.error_count: int = 0
        self.results: List[Dict] = []

    @abstractmethod
    def crawl(self, query: Optional[str] = None, **kwargs) -> List[Dict]:
        """
        Crawl data from the source.

        Args:
            query: Optional search query
            **kwargs: Additional crawl parameters

        Returns:
            List of crawled data items
        """
        pass

    def rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_seconds:
            sleep_time = self.rate_limit_seconds - elapsed
            # Add small random jitter to avoid thundering herd
            sleep_time += random.uniform(0, 0.5)
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def get_headers(self) -> Dict[str, str]:
        """Generate request headers with random user agent."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
        }

    def get_proxy(self) -> Optional[Dict]:
        """Get proxy configuration if proxy rotator is configured."""
        if not self.proxy_rotator_url:
            return None
        return {"http": self.proxy_rotator_url, "https": self.proxy_rotator_url}

    def should_respect_robots_txt(self, url: str) -> bool:
        """Check if the URL's robots.txt should be respected (always True for compliance)."""
        return True

    def handle_error(self, error: Exception, url: str) -> None:
        """Handle and log crawl errors."""
        self.error_count += 1
        logger.error(f"[{self.name}] Error crawling {url}: {str(error)}")

    def get_stats(self) -> Dict:
        """Return crawler statistics."""
        return {
            "name": self.name,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "result_count": len(self.results),
            "last_request_time": datetime.fromtimestamp(self.last_request_time).isoformat() if self.last_request_time > 0 else None,
        }
