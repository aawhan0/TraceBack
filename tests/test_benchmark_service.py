import pytest

from app.evaluation.dataset import build_manifest
from app.evaluation.experiments import ExperimentResult
from app.evaluation.regression import RegressionFailure, RegressionPolicy, RegressionReport
from app.models.domain import Diagnosis
from app.observability.events import InMemoryEventSink, TraceContext
from app.repository.experiments import SQLiteExperimentStore
from app.repository.runs import SQLiteRunStore
from app.scenarios.catalog import SCENARIOS
from app.services.benchmark import (
    BenchmarkRequest,
    BenchmarkResult,
    BenchmarkService,
    assert_regression,
    default_dataset,
)
from app.services.investigation import InvestigationService


class InMemoryRunService(InvestigationService):
    def __init__(self, store) -> None:
        self.store = store

    def investigate(self, scenario, investigator=None, provider=None, run_store=None):
        return super().investigate(
            scenario,
            investigator=investigator,
            provider=provider,
            run_store=self.store,
        )


def test_benchmark_request_validates_name_and_repetitions() -> None:
    dataset = build_manifest("core", "1", SCENARIOS[:1])
    with pytest.raises(ValueError):
        BenchmarkRequest("", dataset)
    with pytest.raises(ValueError):
        BenchmarkRequest("core", dataset, repetitions=0)


def test_default_dataset_covers_catalog() -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    dataset = default_dataset(catalog)
    assert dataset.case_count == len(SCENARIOS)
    assert dataset.name == "core-scenarios"


def test_benchmark_service_persists_result(tmp_path) -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    run_store = SQLiteRunStore(str(tmp_path / "runs.db"))
    experiment_store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    service = BenchmarkService(
        InMemoryRunService(run_store),
        experiment_store,
    )
    dataset = build_manifest("smoke", "1", SCENARIOS[:2])
    result = service.run(
        BenchmarkRequest("smoke", dataset, repetitions=2),
        catalog,
    )

    assert result.result.total_runs == 4
    assert result.result.pass_rate == 1.0
    assert result.regression.passed
    assert experiment_store.get(result.experiment_id) is not None


def test_benchmark_service_emits_trace_events(tmp_path) -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    run_store = SQLiteRunStore(str(tmp_path / "runs.db"))
    experiment_store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    service = BenchmarkService(InMemoryRunService(run_store), experiment_store)
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    dataset = build_manifest("smoke", "1", SCENARIOS[:1])

    service.run(BenchmarkRequest("smoke", dataset), catalog, trace=context)
    names = [event.name for event in sink.events(context.trace_id)]
    assert names == ["benchmark.started", "benchmark.completed"]


def test_assert_regression_returns_successful_result(tmp_path) -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    service = BenchmarkService(
        InMemoryRunService(SQLiteRunStore(str(tmp_path / "runs.db"))),
        SQLiteExperimentStore(str(tmp_path / "experiments.db")),
    )
    dataset = build_manifest("smoke", "1", SCENARIOS[:1])
    result = service.run(BenchmarkRequest("smoke", dataset), catalog)
    assert assert_regression(result) is result


def test_assert_regression_raises_on_failed_gate() -> None:
    result = BenchmarkResult(
        experiment_id="exp-1",
        result=ExperimentResult("smoke", 1, 0, 0.0, 0.2, 10.0, {"db": 0.0}),
        regression=RegressionReport(
            passed=False,
            failures=(
                RegressionFailure(
                    "pass_rate",
                    0.0,
                    1.0,
                    "min",
                    "below threshold",
                ),
            ),
            pass_rate_interval_lower=0.0,
            pass_rate_interval_upper=0.0,
        ),
        dataset_name="core",
        dataset_version="1",
        dataset_fingerprint="abc",
    )
    with pytest.raises(RuntimeError, match="regression gate failed"):
        assert_regression(result)
