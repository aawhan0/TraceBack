from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from app.evaluation.experiments import ExperimentResult
from app.evaluation.statistics import pass_rate_interval


@dataclass(frozen=True)
class QualitySnapshot:
    """Compact quality view suitable for dashboards and release notes."""

    generated_at: datetime
    total_runs: int
    passed_runs: int
    pass_rate: float
    pass_rate_lower_bound: float
    pass_rate_upper_bound: float
    average_confidence: float
    average_duration_ms: float
    healthy: bool


def quality_snapshot(result: ExperimentResult, minimum_pass_rate: float = 1.0) -> QualitySnapshot:
    if not 0 <= minimum_pass_rate <= 1:
        raise ValueError("minimum_pass_rate must be between 0 and 1")
    interval = pass_rate_interval(result.passed_runs, result.total_runs)
    return QualitySnapshot(
        generated_at=datetime.now(timezone.utc),
        total_runs=result.total_runs,
        passed_runs=result.passed_runs,
        pass_rate=result.pass_rate,
        pass_rate_lower_bound=interval.lower,
        pass_rate_upper_bound=interval.upper,
        average_confidence=result.average_confidence,
        average_duration_ms=result.average_duration_ms,
        healthy=result.pass_rate >= minimum_pass_rate,
    )


def weighted_pass_rate(results: Iterable[tuple[bool, float]]) -> float:
    """Calculate a weighted pass rate from (passed, positive weight) pairs."""
    pairs = list(results)
    if not pairs:
        raise ValueError("At least one result is required")
    total_weight = sum(weight for _, weight in pairs)
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")
    return sum(weight for passed, weight in pairs if passed) / total_weight
