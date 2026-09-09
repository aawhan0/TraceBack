from __future__ import annotations

from dataclasses import dataclass, field

from app.evaluation.experiments import ExperimentResult
from app.evaluation.statistics import NumericSummary, proportion_interval, summarize


@dataclass(frozen=True)
class RegressionPolicy:
    """Explicit quality thresholds used to accept a benchmark result."""

    minimum_pass_rate: float = 1.0
    minimum_root_cause_accuracy: float = 1.0
    minimum_evidence_recall: float = 1.0
    minimum_evidence_precision: float = 1.0
    maximum_average_duration_ms: float | None = None
    minimum_average_confidence: float | None = None
    minimum_scenario_pass_rate: float = 1.0

    def __post_init__(self) -> None:
        bounded = (
            self.minimum_pass_rate,
            self.minimum_root_cause_accuracy,
            self.minimum_evidence_recall,
            self.minimum_evidence_precision,
            self.minimum_scenario_pass_rate,
        )
        if any(not 0 <= value <= 1 for value in bounded):
            raise ValueError("quality thresholds must be between 0 and 1")
        if self.maximum_average_duration_ms is not None and self.maximum_average_duration_ms < 0:
            raise ValueError("maximum_average_duration_ms cannot be negative")
        if self.minimum_average_confidence is not None and not 0 <= self.minimum_average_confidence <= 1:
            raise ValueError("minimum_average_confidence must be between 0 and 1")


@dataclass(frozen=True)
class RegressionFailure:
    metric: str
    actual: float
    expected: float
    direction: str
    message: str


@dataclass(frozen=True)
class RegressionReport:
    passed: bool
    failures: tuple[RegressionFailure, ...]
    pass_rate_interval_lower: float
    pass_rate_interval_upper: float
    latency: NumericSummary | None = None

    @property
    def failure_count(self) -> int:
        return len(self.failures)


@dataclass(frozen=True)
class ExperimentMetrics:
    """Metrics needed to make a regression decision."""

    pass_rate: float
    root_cause_accuracy: float
    evidence_recall: float
    evidence_precision: float
    average_confidence: float
    average_duration_ms: float
    scenario_pass_rates: dict[str, float] = field(default_factory=dict)


def evaluate_regression(
    metrics: ExperimentMetrics,
    policy: RegressionPolicy,
    *,
    passed_runs: int,
    total_runs: int,
) -> RegressionReport:
    failures: list[RegressionFailure] = []

    _require_minimum(
        failures, "pass_rate", metrics.pass_rate, policy.minimum_pass_rate
    )
    _require_minimum(
        failures,
        "root_cause_accuracy",
        metrics.root_cause_accuracy,
        policy.minimum_root_cause_accuracy,
    )
    _require_minimum(
        failures,
        "evidence_recall",
        metrics.evidence_recall,
        policy.minimum_evidence_recall,
    )
    _require_minimum(
        failures,
        "evidence_precision",
        metrics.evidence_precision,
        policy.minimum_evidence_precision,
    )
    _require_minimum(
        failures,
        "average_confidence",
        metrics.average_confidence,
        policy.minimum_average_confidence,
        enabled=policy.minimum_average_confidence is not None,
    )
    if (
        policy.maximum_average_duration_ms is not None
        and metrics.average_duration_ms > policy.maximum_average_duration_ms
    ):
        failures.append(
            RegressionFailure(
                "average_duration_ms",
                metrics.average_duration_ms,
                policy.maximum_average_duration_ms,
                "max",
                "average duration exceeds the configured ceiling",
            )
        )

    for scenario_id, pass_rate in sorted(metrics.scenario_pass_rates.items()):
        _require_minimum(
            failures,
            f"scenario:{scenario_id}",
            pass_rate,
            policy.minimum_scenario_pass_rate,
        )

    interval = proportion_interval(passed_runs, total_runs)
    latency = None
    if metrics.average_duration_ms >= 0:
        latency = NumericSummary(
            count=1,
            minimum=metrics.average_duration_ms,
            maximum=metrics.average_duration_ms,
            mean=metrics.average_duration_ms,
            median=metrics.average_duration_ms,
            p95=metrics.average_duration_ms,
        )
    return RegressionReport(
        passed=not failures,
        failures=tuple(failures),
        pass_rate_interval_lower=interval.lower,
        pass_rate_interval_upper=interval.upper,
        latency=latency,
    )


def _require_minimum(
    failures: list[RegressionFailure],
    metric: str,
    actual: float,
    expected: float | None,
    *,
    enabled: bool = True,
) -> None:
    if not enabled or expected is None:
        return
    if actual < expected:
        failures.append(
            RegressionFailure(
                metric,
                actual,
                expected,
                "min",
                f"{metric} is below the configured minimum",
            )
        )


def metrics_from_experiment(
    result: ExperimentResult,
    *,
    root_cause_accuracy: float | None = None,
    evidence_recall: float | None = None,
    evidence_precision: float | None = None,
) -> ExperimentMetrics:
    """Adapt the compact experiment result to the richer regression contract."""
    return ExperimentMetrics(
        pass_rate=result.pass_rate,
        root_cause_accuracy=result.pass_rate if root_cause_accuracy is None else root_cause_accuracy,
        evidence_recall=1.0 if evidence_recall is None else evidence_recall,
        evidence_precision=1.0 if evidence_precision is None else evidence_precision,
        average_confidence=result.average_confidence,
        average_duration_ms=result.average_duration_ms,
        scenario_pass_rates=dict(result.scenario_pass_rates),
    )


def summarize_durations(values: list[float]) -> NumericSummary:
    """Expose duration summaries for reporting layers."""
    return summarize(values)
