from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor, sqrt
from statistics import fmean, median
from typing import Iterable


@dataclass(frozen=True)
class NumericSummary:
    """Descriptive statistics for a finite collection of measurements."""

    count: int
    minimum: float
    maximum: float
    mean: float
    median: float
    p95: float


@dataclass(frozen=True)
class ProportionInterval:
    """Wilson score interval for a binary proportion."""

    successes: int
    observations: int
    proportion: float
    lower: float
    upper: float


def summarize(values: Iterable[float]) -> NumericSummary:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("At least one value is required")
    return NumericSummary(
        count=len(ordered),
        minimum=ordered[0],
        maximum=ordered[-1],
        mean=fmean(ordered),
        median=median(ordered),
        p95=_percentile(ordered, 0.95),
    )


def _percentile(ordered: list[float], quantile: float) -> float:
    if not ordered:
        raise ValueError("At least one value is required")
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be between 0 and 1")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * quantile
    lower = floor(position)
    upper = ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def proportion_interval(successes: int, observations: int, z: float = 1.96) -> ProportionInterval:
    """Return a Wilson interval without requiring a statistics dependency."""
    if observations < 1:
        raise ValueError("observations must be positive")
    if not 0 <= successes <= observations:
        raise ValueError("successes must be within observations")
    if z <= 0:
        raise ValueError("z must be positive")

    p = successes / observations
    denominator = 1 + z**2 / observations
    center = (p + z**2 / (2 * observations)) / denominator
    margin = (
        z
        * sqrt(
            p * (1 - p) / observations
            + z**2 / (4 * observations**2)
        )
        / denominator
    )
    return ProportionInterval(
        successes=successes,
        observations=observations,
        proportion=p,
        lower=max(0.0, center - margin),
        upper=min(1.0, center + margin),
    )


def pass_rate_interval(passed: int, total: int) -> ProportionInterval:
    """Convenience wrapper for experiment pass rates."""
    return proportion_interval(passed, total)


def percentile(values: Iterable[float], quantile: float) -> float:
    """Calculate a linearly interpolated percentile."""
    return _percentile(sorted(float(value) for value in values), quantile)
