"""Redis-backed sliding window rate limiter."""
import time

from fastapi import HTTPException

from app.config import settings
from app.redis_store import redis_store


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def check(self, user_id: str) -> dict:
        now = time.time()
        key = f"rate:{user_id}"
        count = redis_store.sliding_window_count(key, now, self.window_seconds)
        remaining = max(0, self.max_requests - count)
        reset_at = int(now + self.window_seconds)

        if count > self.max_requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "retry_after_seconds": self.window_seconds,
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(self.window_seconds),
                },
            )

        return {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset_at": reset_at,
        }

    def get_stats(self, user_id: str) -> dict:
        now = time.time()
        count = redis_store.sorted_count(f"rate:{user_id}", now, self.window_seconds)
        return {
            "requests_in_window": count,
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - count),
        }


rate_limiter = RateLimiter(settings.rate_limit_per_minute, 60)
