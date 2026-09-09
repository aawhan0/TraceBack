from dataclasses import dataclass
from statistics import fmean

from app.models.domain import IncidentScenario
from app.services.investigation import InvestigationResult, InvestigationService


@dataclass(frozen=True)
class ExperimentSpec:
    """Configuration for a repeatable investigation experiment."""

    name: str
    scenario_ids: tuple[str, ...]
    repetitions: int = 1

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Experiment name is required")
        if not self.scenario_ids:
            raise ValueError("At least one scenario is required")
        if self.repetitions < 1 or self.repetitions > 100:
            raise ValueError("repetitions must be between 1 and 100")


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    total_runs: int
    passed_runs: int
    pass_rate: float
    average_confidence: float
    average_duration_ms: float
    scenario_pass_rates: dict[str, float]


@dataclass(frozen=True)
class RegressionGate:
    """A minimum acceptable pass rate for a new experiment."""

    minimum_pass_rate: float = 1.0

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_pass_rate <= 1:
            raise ValueError("minimum_pass_rate must be between 0 and 1")

    def check(self, result: ExperimentResult) -> bool:
        return result.pass_rate >= self.minimum_pass_rate


class ExperimentRunner:
    """Runs investigations repeatedly under one configuration."""

    def __init__(self, service: InvestigationService | None = None) -> None:
        self.service = service or InvestigationService()

    def run(
        self,
        spec: ExperimentSpec,
        scenarios: dict[str, IncidentScenario],
        investigator_factory=None,
    ) -> ExperimentResult:
        missing = [scenario_id for scenario_id in spec.scenario_ids if scenario_id not in scenarios]
        if missing:
            raise KeyError(f"Unknown scenarios: {', '.join(missing)}")

        results: list[InvestigationResult] = []
        for scenario_id in spec.scenario_ids:
            scenario = scenarios[scenario_id]
            for _ in range(spec.repetitions):
                investigator = investigator_factory(scenario) if investigator_factory else None
                results.append(self.service.investigate(scenario, investigator=investigator))

        return summarize_experiment(spec.name, results)


def summarize_experiment(name: str, results: list[InvestigationResult]) -> ExperimentResult:
    if not results:
        raise ValueError("At least one investigation result is required")

    total = len(results)
    passed = sum(result.evaluation.passed for result in results)
    by_scenario: dict[str, list[bool]] = {}
    for result in results:
        by_scenario.setdefault(result.scenario_id, []).append(result.evaluation.passed)

    return ExperimentResult(
        name=name,
        total_runs=total,
        passed_runs=passed,
        pass_rate=passed / total,
        average_confidence=fmean(result.diagnosis.confidence for result in results),
        average_duration_ms=fmean(result.duration_ms for result in results),
        scenario_pass_rates={
            scenario_id: sum(values) / len(values) for scenario_id, values in by_scenario.items()
        },
    )


def compare_experiments(
    baseline: ExperimentResult, candidate: ExperimentResult
) -> dict[str, float]:
    return {
        "pass_rate_delta": candidate.pass_rate - baseline.pass_rate,
        "average_confidence_delta": candidate.average_confidence - baseline.average_confidence,
        "average_duration_ms_delta": candidate.average_duration_ms - baseline.average_duration_ms,
    }
