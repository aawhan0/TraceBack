from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import uuid4

from app.agent.baseline import BaselineInvestigator
from app.agent.llm import LLMInvestigator
from app.evaluation.dataset import DatasetManifest
from app.evaluation.experiments import ExperimentResult, ExperimentRunner, ExperimentSpec
from app.evaluation.provenance import BenchmarkProvenance
from app.evaluation.regression import (
    RegressionPolicy,
    RegressionReport,
    evaluate_regression,
    metrics_from_experiment,
)
from app.config import Settings
from app.models.domain import IncidentScenario
from app.observability.events import TraceContext, TraceSpan
from app.providers.ollama import OllamaProvider
from app.repository.experiments import ExperimentRecord, ExperimentStore, SQLiteExperimentStore
from app.repository.runs import utc_now
from app.services.investigation import InvestigationService


@dataclass(frozen=True)
class BenchmarkRequest:
    """High-level request for one reproducible benchmark."""

    name: str
    dataset: DatasetManifest
    repetitions: int = 1
    policy: RegressionPolicy = RegressionPolicy()
    mode: Literal["baseline", "llm"] = "baseline"
    model: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("benchmark name is required")
        if self.repetitions < 1 or self.repetitions > 100:
            raise ValueError("repetitions must be between 1 and 100")
        if self.mode == "baseline" and self.model is not None:
            raise ValueError("baseline benchmarks cannot declare a model")
        if self.mode == "llm" and not (self.model or "").strip():
            raise ValueError("LLM benchmarks require a model")

    def provenance(self) -> BenchmarkProvenance:
        return BenchmarkProvenance.from_environment(
            provider="baseline" if self.mode == "baseline" else "ollama",
            model=self.model,
        )


@dataclass(frozen=True)
class BenchmarkResult:
    experiment_id: str
    result: ExperimentResult
    regression: RegressionReport
    dataset_name: str
    dataset_version: str
    dataset_fingerprint: str
    provenance: BenchmarkProvenance | None = None


class BenchmarkService:
    """Coordinates datasets, experiment execution, regression gates, and persistence."""

    def __init__(
        self,
        investigation_service: InvestigationService | None = None,
        experiment_store: ExperimentStore | None = None,
    ) -> None:
        self.investigation_service = investigation_service or InvestigationService()
        self.experiment_store = experiment_store or SQLiteExperimentStore()

    def run(
        self,
        request: BenchmarkRequest,
        catalog: dict[str, IncidentScenario],
        *,
        trace: TraceContext | None = None,
    ) -> BenchmarkResult:
        context = trace or TraceContext.create()
        scenarios = request.dataset.scenarios(catalog)
        spec = ExperimentSpec(
            request.name,
            tuple(scenario.id for scenario in scenarios),
            request.repetitions,
        )
        runner = ExperimentRunner(self.investigation_service)
        provenance = request.provenance()
        investigator_factory = self._investigator_factory(request)
        with TraceSpan(
            context,
            "benchmark",
            benchmark=request.name,
            dataset=request.dataset.name,
            version=request.dataset.version,
            mode=request.mode,
            provider=provenance.provider,
            model=provenance.model or "",
            git_revision=provenance.git_revision,
        ):
            result = runner.run(spec, catalog, investigator_factory=investigator_factory)
            metrics = metrics_from_experiment(result)
            regression = evaluate_regression(
                metrics,
                request.policy,
                passed_runs=result.passed_runs,
                total_runs=result.total_runs,
            )
            experiment_id = str(uuid4())
            record = ExperimentRecord(
                experiment_id=experiment_id,
                name=request.name,
                dataset_name=request.dataset.name,
                dataset_version=request.dataset.version,
                dataset_fingerprint=request.dataset.fingerprint,
                result=result,
                regression=regression,
                created_at=utc_now(),
                provenance=provenance,
            )
            self.experiment_store.save(record)
        return BenchmarkResult(
            experiment_id=experiment_id,
            result=result,
            regression=regression,
            dataset_name=request.dataset.name,
            dataset_version=request.dataset.version,
            dataset_fingerprint=request.dataset.fingerprint,
            provenance=provenance,
        )

    @staticmethod
    def _investigator_factory(request: BenchmarkRequest):
        if request.mode == "baseline":
            return lambda scenario: BaselineInvestigator(scenario)

        settings = Settings.from_environment()
        provider = OllamaProvider(
            model=request.model or settings.model,
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout,
        )
        return lambda scenario: LLMInvestigator(scenario, provider)

    def get(self, experiment_id: str) -> ExperimentRecord | None:
        return self.experiment_store.get(experiment_id)

    def list(self, limit: int = 50) -> list[ExperimentRecord]:
        return self.experiment_store.list(limit)


def default_dataset(
    catalog: dict[str, IncidentScenario],
    *,
    name: str = "core-scenarios",
    version: str = "1",
) -> DatasetManifest:
    """Build a stable dataset from the currently registered scenarios."""
    from app.evaluation.dataset import build_manifest

    return build_manifest(
        name,
        version,
        tuple(catalog.values()),
        description="All version-controlled Traceback incident scenarios.",
    )


def assert_regression(result: BenchmarkResult) -> BenchmarkResult:
    """Fail fast for CI callers while retaining the persisted report."""
    if not result.regression.passed:
        details = "; ".join(
            f"{failure.metric}: {failure.actual:.4f} < {failure.expected:.4f}"
            for failure in result.regression.failures
            if failure.direction == "min"
        )
        raise RuntimeError(f"Benchmark regression gate failed: {details}")
    return result
