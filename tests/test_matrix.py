import pytest

from app.evaluation.dataset import build_manifest
from app.evaluation.matrix import ExperimentConfiguration, ExperimentMatrixRunner
from app.repository.experiments import SQLiteExperimentStore
from app.repository.runs import SQLiteRunStore
from app.services.benchmark import BenchmarkService
from app.services.investigation import InvestigationService
from app.scenarios.catalog import SCENARIOS


class InMemoryRunService(InvestigationService):
    def __init__(self, store):
        self.store = store

    def investigate(self, scenario, investigator=None, provider=None, run_store=None):
        return super().investigate(
            scenario, investigator=investigator, provider=provider, run_store=self.store
        )


def test_configuration_contract() -> None:
    with pytest.raises(ValueError):
        ExperimentConfiguration("")
    with pytest.raises(ValueError):
        ExperimentConfiguration("bad", model="llama3.2")
    with pytest.raises(ValueError):
        ExperimentConfiguration("bad", mode="llm")


def test_matrix_runs_all_configurations_on_same_dataset(tmp_path) -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    benchmark = BenchmarkService(
        InMemoryRunService(SQLiteRunStore(str(tmp_path / "runs.db"))),
        SQLiteExperimentStore(str(tmp_path / "experiments.db")),
    )
    dataset = build_manifest("core-scenarios", "1", SCENARIOS[:2])
    result = ExperimentMatrixRunner(benchmark).run(
        "smoke-matrix",
        dataset,
        catalog,
        (
            ExperimentConfiguration("baseline"),
            ExperimentConfiguration("second-baseline"),
        ),
        repetitions=2,
    )
    assert len(result.results) == 2
    assert len(result.comparisons) == 1
    assert all(item.dataset_fingerprint == dataset.fingerprint for item in result.results)
    assert result.best_experiment_id in result.experiment_ids


def test_matrix_rejects_duplicate_names(tmp_path) -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    benchmark = BenchmarkService(
        InMemoryRunService(SQLiteRunStore(str(tmp_path / "runs.db"))),
        SQLiteExperimentStore(str(tmp_path / "experiments.db")),
    )
    dataset = build_manifest("core-scenarios", "1", SCENARIOS[:1])
    with pytest.raises(ValueError, match="duplicate"):
        ExperimentMatrixRunner(benchmark).run(
            "matrix", dataset, catalog,
            (ExperimentConfiguration("same"), ExperimentConfiguration("same")),
        )
