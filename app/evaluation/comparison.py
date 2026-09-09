from __future__ import annotations

from dataclasses import dataclass

from app.evaluation.experiments import ExperimentResult
from app.evaluation.provenance import BenchmarkProvenance
from app.repository.experiments import ExperimentRecord


@dataclass(frozen=True)
class ScenarioComparison:
    """Per-scenario quality delta between two compatible experiments."""

    scenario_id: str
    baseline_pass_rate: float
    candidate_pass_rate: float
    pass_rate_delta: float


@dataclass(frozen=True)
class BenchmarkComparison:
    """Structured comparison of two persisted benchmark experiments."""

    baseline_experiment_id: str
    candidate_experiment_id: str
    dataset_name: str
    dataset_version: str
    dataset_fingerprint: str
    baseline_pass_rate: float
    candidate_pass_rate: float
    pass_rate_delta: float
    baseline_confidence: float
    candidate_confidence: float
    confidence_delta: float
    baseline_duration_ms: float
    candidate_duration_ms: float
    duration_delta_ms: float
    scenario_comparisons: tuple[ScenarioComparison, ...]
    baseline_provider: str | None
    candidate_provider: str | None
    baseline_model: str | None
    candidate_model: str | None

    @property
    def improved(self) -> bool:
        return self.pass_rate_delta > 0

    @property
    def regressed(self) -> bool:
        return self.pass_rate_delta < 0

    @property
    def unchanged(self) -> bool:
        return self.pass_rate_delta == 0

    @property
    def verdict(self) -> str:
        if self.improved:
            return "improved"
        if self.regressed:
            return "regressed"
        return "unchanged"


class IncompatibleBenchmarkError(ValueError):
    """Raised when two experiments cannot be meaningfully compared."""


def compare_experiment_results(
    baseline: ExperimentResult,
    candidate: ExperimentResult,
) -> tuple[float, float, float, tuple[ScenarioComparison, ...]]:
    """Compare the measurable result portion of two compatible experiments."""
    baseline_scenarios = set(baseline.scenario_pass_rates)
    candidate_scenarios = set(candidate.scenario_pass_rates)
    if baseline_scenarios != candidate_scenarios:
        missing = sorted(baseline_scenarios - candidate_scenarios)
        extra = sorted(candidate_scenarios - baseline_scenarios)
        raise IncompatibleBenchmarkError(
            f"scenario sets differ (missing={missing}, extra={extra})"
        )

    scenarios = tuple(
        ScenarioComparison(
            scenario_id=scenario_id,
            baseline_pass_rate=baseline.scenario_pass_rates[scenario_id],
            candidate_pass_rate=candidate.scenario_pass_rates[scenario_id],
            pass_rate_delta=(
                candidate.scenario_pass_rates[scenario_id]
                - baseline.scenario_pass_rates[scenario_id]
            ),
        )
        for scenario_id in sorted(baseline_scenarios)
    )
    return (
        candidate.pass_rate - baseline.pass_rate,
        candidate.average_confidence - baseline.average_confidence,
        candidate.average_duration_ms - baseline.average_duration_ms,
        scenarios,
    )


def compare_experiments(
    baseline: ExperimentRecord,
    candidate: ExperimentRecord,
) -> BenchmarkComparison:
    """Compare persisted experiments while enforcing dataset compatibility."""
    if baseline.dataset_name != candidate.dataset_name:
        raise IncompatibleBenchmarkError("experiments use different dataset names")
    if baseline.dataset_version != candidate.dataset_version:
        raise IncompatibleBenchmarkError("experiments use different dataset versions")
    if baseline.dataset_fingerprint != candidate.dataset_fingerprint:
        raise IncompatibleBenchmarkError(
            "experiments use different dataset fingerprints; compare matching datasets"
        )

    pass_delta, confidence_delta, duration_delta, scenarios = compare_experiment_results(
        baseline.result,
        candidate.result,
    )
    baseline_provenance: BenchmarkProvenance | None = baseline.provenance
    candidate_provenance: BenchmarkProvenance | None = candidate.provenance

    return BenchmarkComparison(
        baseline_experiment_id=baseline.experiment_id,
        candidate_experiment_id=candidate.experiment_id,
        dataset_name=baseline.dataset_name,
        dataset_version=baseline.dataset_version,
        dataset_fingerprint=baseline.dataset_fingerprint,
        baseline_pass_rate=baseline.result.pass_rate,
        candidate_pass_rate=candidate.result.pass_rate,
        pass_rate_delta=pass_delta,
        baseline_confidence=baseline.result.average_confidence,
        candidate_confidence=candidate.result.average_confidence,
        confidence_delta=confidence_delta,
        baseline_duration_ms=baseline.result.average_duration_ms,
        candidate_duration_ms=candidate.result.average_duration_ms,
        duration_delta_ms=duration_delta,
        scenario_comparisons=scenarios,
        baseline_provider=baseline_provenance.provider if baseline_provenance else None,
        candidate_provider=candidate_provenance.provider if candidate_provenance else None,
        baseline_model=baseline_provenance.model if baseline_provenance else None,
        candidate_model=candidate_provenance.model if candidate_provenance else None,
    )


def comparison_to_dict(comparison: BenchmarkComparison) -> dict[str, object]:
    """Return a JSON-safe representation for API and CLI consumers."""
    return {
        "baseline_experiment_id": comparison.baseline_experiment_id,
        "candidate_experiment_id": comparison.candidate_experiment_id,
        "dataset": {
            "name": comparison.dataset_name,
            "version": comparison.dataset_version,
            "fingerprint": comparison.dataset_fingerprint,
        },
        "metrics": {
            "pass_rate": {
                "baseline": comparison.baseline_pass_rate,
                "candidate": comparison.candidate_pass_rate,
                "delta": comparison.pass_rate_delta,
            },
            "average_confidence": {
                "baseline": comparison.baseline_confidence,
                "candidate": comparison.candidate_confidence,
                "delta": comparison.confidence_delta,
            },
            "average_duration_ms": {
                "baseline": comparison.baseline_duration_ms,
                "candidate": comparison.candidate_duration_ms,
                "delta": comparison.duration_delta_ms,
            },
        },
        "verdict": comparison.verdict,
        "providers": {
            "baseline": comparison.baseline_provider,
            "candidate": comparison.candidate_provider,
        },
        "models": {
            "baseline": comparison.baseline_model,
            "candidate": comparison.candidate_model,
        },
        "scenarios": [
            {
                "scenario_id": item.scenario_id,
                "baseline_pass_rate": item.baseline_pass_rate,
                "candidate_pass_rate": item.candidate_pass_rate,
                "pass_rate_delta": item.pass_rate_delta,
            }
            for item in comparison.scenario_comparisons
        ],
    }
