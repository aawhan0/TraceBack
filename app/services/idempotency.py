from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class CachedOperation(Generic[T]):
    key: str
    value: T
    expires_at: float


class IdempotencyStore(Generic[T]):
    """Bounded process-local idempotency store for retry-safe operations."""

    def __init__(self, ttl_seconds: float = 300.0, max_entries: int = 10_000):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._items: dict[str, CachedOperation[T]] = {}
        self._lock = Lock()

    def get(self, key: str) -> T | None:
        if not key.strip():
            raise ValueError("idempotency key is required")
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            if item.expires_at <= monotonic():
                del self._items[key]
                return None
            return item.value

    def put(self, key: str, value: T) -> None:
        if not key.strip():
            raise ValueError("idempotency key is required")
        with self._lock:
            now = monotonic()
            expired = [k for k, item in self._items.items() if item.expires_at <= now]
            for item_key in expired:
                del self._items[item_key]
            if len(self._items) >= self.max_entries:
                oldest = min(self._items, key=lambda k: self._items[k].expires_at)
                del self._items[oldest]
            self._items[key] = CachedOperation(key, value, now + self.ttl_seconds)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
