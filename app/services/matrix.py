from __future__ import annotations

from dataclasses import dataclass

from app.evaluation.dataset import DatasetManifest
from app.evaluation.matrix import ExperimentConfiguration, ExperimentMatrixRunner, MatrixResult
from app.evaluation.regression import RegressionPolicy
from app.models.domain import IncidentScenario
from app.services.benchmark import BenchmarkService


@dataclass(frozen=True)
class MatrixRequest:
    matrix_id: str
    dataset: DatasetManifest
    configurations: tuple[ExperimentConfiguration, ...]
    repetitions: int = 1
    policy: RegressionPolicy = RegressionPolicy()


class MatrixService:
    """Application service for reproducible multi-configuration benchmarks."""

    def __init__(self, benchmark_service: BenchmarkService | None = None) -> None:
        self.runner = ExperimentMatrixRunner(benchmark_service)

    def run(
        self,
        request: MatrixRequest,
        catalog: dict[str, IncidentScenario],
    ) -> MatrixResult:
        return self.runner.run(
            request.matrix_id,
            request.dataset,
            catalog,
            request.configurations,
            repetitions=request.repetitions,
            policy=request.policy,
        )
