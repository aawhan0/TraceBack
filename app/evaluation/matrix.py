from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.evaluation.comparison import BenchmarkComparison, compare_experiments
from app.evaluation.dataset import DatasetManifest
from app.evaluation.regression import RegressionPolicy
from app.repository.experiments import ExperimentRecord
from app.services.benchmark import BenchmarkRequest, BenchmarkResult, BenchmarkService


@dataclass(frozen=True)
class ExperimentConfiguration:
    """One model/provider configuration in a benchmark matrix."""

    name: str
    mode: Literal["baseline", "llm"] = "baseline"
    model: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("configuration name is required")
        if self.mode == "baseline" and self.model is not None:
            raise ValueError("baseline configurations cannot declare a model")
        if self.mode == "llm" and not (self.model or "").strip():
            raise ValueError("LLM configurations require a model")


@dataclass(frozen=True)
class MatrixResult:
    """Persisted results produced by every configuration in one matrix."""

    matrix_id: str
    dataset_name: str
    dataset_version: str
    dataset_fingerprint: str
    results: tuple[BenchmarkResult, ...]
    comparisons: tuple[BenchmarkComparison, ...]
    best_experiment_id: str

    @property
    def experiment_ids(self) -> tuple[str, ...]:
        return tuple(item.experiment_id for item in self.results)


class ExperimentMatrixRunner:
    """Run several benchmark configurations against one immutable dataset."""

    def __init__(self, service: BenchmarkService | None = None) -> None:
        self.service = service or BenchmarkService()

    def run(
        self,
        matrix_id: str,
        dataset: DatasetManifest,
        catalog,
        configurations: tuple[ExperimentConfiguration, ...],
        *,
        repetitions: int = 1,
        policy: RegressionPolicy = RegressionPolicy(),
    ) -> MatrixResult:
        if not matrix_id.strip():
            raise ValueError("matrix id is required")
        if not configurations:
            raise ValueError("at least one configuration is required")
        if len(configurations) > 20:
            raise ValueError("matrix cannot contain more than 20 configurations")

        results: list[BenchmarkResult] = []
        names: set[str] = set()
        for configuration in configurations:
            if configuration.name in names:
                raise ValueError(f"duplicate configuration name: {configuration.name}")
            names.add(configuration.name)
            results.append(
                self.service.run(
                    BenchmarkRequest(
                        configuration.name,
                        dataset,
                        repetitions,
                        policy,
                        mode=configuration.mode,
                        model=configuration.model,
                    ),
                    catalog,
                )
            )

        comparisons: list[BenchmarkComparison] = []
        baseline = results[0]
        for candidate in results[1:]:
            comparisons.append(
                compare_experiments(
                    self.service.get(baseline.experiment_id),
                    self.service.get(candidate.experiment_id),
                )
            )

        best = max(
            results,
            key=lambda item: (
                item.result.pass_rate,
                item.result.average_confidence,
                -item.result.average_duration_ms,
            ),
        )
        return MatrixResult(
            matrix_id=matrix_id,
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            dataset_fingerprint=dataset.fingerprint,
            results=tuple(results),
            comparisons=tuple(comparisons),
            best_experiment_id=best.experiment_id,
        )
