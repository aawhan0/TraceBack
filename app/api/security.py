from __future__ import annotations

from collections import deque
from threading import Lock
from time import monotonic


class RateLimiter:
    """Small process-local sliding-window limiter for protecting public endpoints."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        if not key:
            raise ValueError("rate-limit key cannot be empty")
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._requests.setdefault(key, deque())
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
