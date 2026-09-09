from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable


@dataclass(frozen=True)
class CalibrationBucket:
    """One confidence bucket in a reliability diagram."""

    lower_bound: float
    upper_bound: float
    observations: int
    average_confidence: float
    observed_success_rate: float

    @property
    def calibration_gap(self) -> float:
        return abs(self.average_confidence - self.observed_success_rate)


@dataclass(frozen=True)
class CalibrationReport:
    """Confidence quality summary for an experiment."""

    observations: int
    brier_score: float
    expected_calibration_error: float
    maximum_calibration_error: float
    buckets: tuple[CalibrationBucket, ...]


def calibration_report(
    predictions: Iterable[tuple[float, bool]],
    *,
    bucket_count: int = 10,
) -> CalibrationReport:
    """Measure whether reported confidence tracks actual success."""
    values = [(float(confidence), bool(success)) for confidence, success in predictions]
    if not values:
        raise ValueError("At least one prediction is required")
    if bucket_count < 1 or bucket_count > 100:
        raise ValueError("bucket_count must be between 1 and 100")
    if any(not 0 <= confidence <= 1 for confidence, _ in values):
        raise ValueError("confidence must be between 0 and 1")

    buckets: list[CalibrationBucket] = []
    ece = 0.0
    mce = 0.0
    total = len(values)
    for index in range(bucket_count):
        lower = index / bucket_count
        upper = (index + 1) / bucket_count
        members = [
            (confidence, success)
            for confidence, success in values
            if lower <= confidence < upper
            or (index == bucket_count - 1 and confidence == upper)
        ]
        if not members:
            continue
        average_confidence = sum(item[0] for item in members) / len(members)
        success_rate = sum(item[1] for item in members) / len(members)
        bucket = CalibrationBucket(
            lower_bound=lower,
            upper_bound=upper,
            observations=len(members),
            average_confidence=average_confidence,
            observed_success_rate=success_rate,
        )
        buckets.append(bucket)
        gap = bucket.calibration_gap
        ece += len(members) / total * gap
        mce = max(mce, gap)

    brier = sum((confidence - float(success)) ** 2 for confidence, success in values) / total
    return CalibrationReport(
        observations=total,
        brier_score=brier,
        expected_calibration_error=ece,
        maximum_calibration_error=mce,
        buckets=tuple(buckets),
    )


def confidence_standard_error(confidences: Iterable[float]) -> float:
    """Return the standard error of the mean confidence."""
    values = [float(value) for value in confidences]
    if not values:
        raise ValueError("At least one confidence value is required")
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("confidence must be between 0 and 1")
    if len(values) == 1:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance / len(values))
