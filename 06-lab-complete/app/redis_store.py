"""Redis-backed storage with a local fallback for development."""
import time
from collections import defaultdict

import redis

from app.config import settings


class RedisStore:
    def __init__(self, url: str):
        self.enabled = False
        self._memory: dict[str, tuple[float | None, object]] = {}
        self._sorted_memory: dict[str, list[float]] = defaultdict(list)
        self.client = None
        if url:
            try:
                self.client = redis.from_url(url, decode_responses=True)
                self.client.ping()
                self.enabled = True
            except Exception:
                self.client = None

    def ping(self) -> bool:
        if not self.enabled or self.client is None:
            return False
        try:
            return bool(self.client.ping())
        except Exception:
            self.enabled = False
            return False

    def incrbyfloat(self, key: str, amount: float, ttl_seconds: int) -> float:
        if self.enabled and self.client is not None:
            pipe = self.client.pipeline()
            pipe.incrbyfloat(key, amount)
            pipe.expire(key, ttl_seconds)
            value, _ = pipe.execute()
            return float(value)

        expires_at, current = self._memory.get(key, (None, 0.0))
        if expires_at and expires_at < time.time():
            current = 0.0
        value = float(current) + amount
        self._memory[key] = (time.time() + ttl_seconds, value)
        return value

    def get_float(self, key: str) -> float:
        if self.enabled and self.client is not None:
            value = self.client.get(key)
            return float(value or 0.0)

        expires_at, current = self._memory.get(key, (None, 0.0))
        if expires_at and expires_at < time.time():
            self._memory.pop(key, None)
            return 0.0
        return float(current or 0.0)

    def sliding_window_count(self, key: str, now: float, window_seconds: int) -> int:
        cutoff = now - window_seconds
        if self.enabled and self.client is not None:
            pipe = self.client.pipeline()
            pipe.zremrangebyscore(key, 0, cutoff)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window_seconds)
            pipe.zcard(key)
            _, _, _, count = pipe.execute()
            return int(count)

        values = [item for item in self._sorted_memory[key] if item >= cutoff]
        values.append(now)
        self._sorted_memory[key] = values
        return len(values)

    def sorted_count(self, key: str, now: float, window_seconds: int) -> int:
        cutoff = now - window_seconds
        if self.enabled and self.client is not None:
            self.client.zremrangebyscore(key, 0, cutoff)
            return int(self.client.zcard(key))

        values = [item for item in self._sorted_memory[key] if item >= cutoff]
        self._sorted_memory[key] = values
        return len(values)


redis_store = RedisStore(settings.redis_url)
