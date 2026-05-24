"""
AGSPE Rate Limiter - Token bucket rate limiting for web scrapers
with proxy rotation support.
"""
import time
import threading
from typing import Optional, Dict
from collections import defaultdict


class TokenBucket:
    """Token bucket rate limiter implementation."""

    def __init__(self, rate: float = 0.5, capacity: int = 10):
        """
        Args:
            rate: Tokens added per second
            capacity: Maximum burst capacity
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if successful."""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_and_consume(self, tokens: int = 1) -> None:
        """Wait until tokens are available, then consume."""
        while not self.consume(tokens):
            time.sleep(0.1)

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now


class RateLimiter:
    """
    Global rate limiter with per-domain and global limits.
    Supports proxy rotation and request scheduling.
    """

    def __init__(
        self,
        requests_per_minute: int = 30,
        burst_capacity: int = 5,
    ):
        self.global_bucket = TokenBucket(
            rate=requests_per_minute / 60.0,
            capacity=burst_capacity,
        )
        self.domain_buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(rate=0.5, capacity=3)
        )
        self.proxy_list: list = []
        self.current_proxy_index: int = 0

    def add_proxy(self, proxy_url: str) -> None:
        """Add a proxy to the rotation pool."""
        self.proxy_list.append(proxy_url)

    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in rotation."""
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy

    def acquire(self, domain: str = "global") -> None:
        """Acquire rate limit permission for a request."""
        self.global_bucket.wait_and_consume()
        if domain != "global":
            self.domain_buckets[domain].wait_and_consume()

    def get_wait_time(self, domain: str = "global") -> float:
        """Estimate wait time before next request is allowed."""
        global_wait = max(0, 1.0 - self.global_bucket.tokens) / self.global_bucket.rate if self.global_bucket.rate > 0 else 0
        domain_wait = 0
        if domain != "global":
            bucket = self.domain_buckets[domain]
            domain_wait = max(0, 1.0 - bucket.tokens) / bucket.rate if bucket.rate > 0 else 0
        return max(global_wait, domain_wait)
