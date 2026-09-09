from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from typing import Iterable


@dataclass(frozen=True)
class LatencySample:
    operation: str
    duration_ms: float
    occurred_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.operation.strip():
            raise ValueError("operation is required")
        if self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")


@dataclass(frozen=True)
class LatencySummary:
    operation: str
    count: int
    average_ms: float
    minimum_ms: float
    maximum_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float


def percentile(values: Iterable[float], percentile_rank: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("at least one latency sample is required")
    if not 0 <= percentile_rank <= 100:
        raise ValueError("percentile must be between 0 and 100")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile_rank / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize_latency(samples: Iterable[LatencySample]) -> LatencySummary:
    items = list(samples)
    if not items:
        raise ValueError("at least one latency sample is required")
    operation = items[0].operation
    if any(item.operation != operation for item in items):
        raise ValueError("latency samples must belong to one operation")
    values = [item.duration_ms for item in items]
    return LatencySummary(
        operation=operation,
        count=len(values),
        average_ms=mean(values),
        minimum_ms=min(values),
        maximum_ms=max(values),
        p50_ms=percentile(values, 50),
        p95_ms=percentile(values, 95),
        p99_ms=percentile(values, 99),
    )
