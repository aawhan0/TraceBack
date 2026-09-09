from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True)
class MetricSnapshot:
    counters: dict[str, int]
    timings: dict[str, tuple[int, float, float]]


class MetricsRegistry:
    """Dependency-free metrics registry for request and investigation telemetry."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._timings: dict[str, list[float]] = {}
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        if not name.strip():
            raise ValueError("metric name is required")
        if value < 0:
            raise ValueError("metric increment cannot be negative")
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def observe(self, name: str, duration_seconds: float) -> None:
        if not name.strip():
            raise ValueError("metric name is required")
        if duration_seconds < 0:
            raise ValueError("duration cannot be negative")
        with self._lock:
            self._timings.setdefault(name, []).append(duration_seconds)

    def time(self, name: str) -> "_Timer":
        return _Timer(self, name)

    def snapshot(self) -> MetricSnapshot:
        with self._lock:
            timings = {
                name: (len(values), min(values), max(values))
                for name, values in self._timings.items()
                if values
            }
            return MetricSnapshot(dict(self._counters), timings)

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._timings.clear()


class _Timer:
    def __init__(self, registry: MetricsRegistry, name: str) -> None:
        self.registry = registry
        self.name = name
        self.started = 0.0

    def __enter__(self) -> "_Timer":
        self.started = monotonic()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.registry.observe(self.name, monotonic() - self.started)
        return False
