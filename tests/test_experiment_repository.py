from datetime import datetime, timezone

import pytest

from app.evaluation.experiments import ExperimentResult
from app.evaluation.regression import RegressionFailure, RegressionReport
from app.repository.experiments import ExperimentRecord, SQLiteExperimentStore


def make_record(experiment_id: str = "exp-1") -> ExperimentRecord:
    result = ExperimentResult(
        name="baseline",
        total_runs=4,
        passed_runs=3,
        pass_rate=0.75,
        average_confidence=0.8,
        average_duration_ms=120.0,
        scenario_pass_rates={"db": 1.0, "redis": 0.5},
    )
    regression = RegressionReport(
        passed=False,
        failures=(
            RegressionFailure(
                metric="pass_rate",
                actual=0.75,
                expected=1.0,
                direction="min",
                message="below threshold",
            ),
        ),
        pass_rate_interval_lower=0.3,
        pass_rate_interval_upper=0.95,
    )
    return ExperimentRecord(
        experiment_id=experiment_id,
        name="baseline",
        dataset_name="core",
        dataset_version="1",
        dataset_fingerprint="abc",
        result=result,
        regression=regression,
        created_at=datetime.now(timezone.utc),
    )


def test_experiment_store_round_trips_record(tmp_path) -> None:
    store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    original = make_record()
    store.save(original)

    loaded = store.get("exp-1")
    assert loaded is not None
    assert loaded.experiment_id == original.experiment_id
    assert loaded.result.scenario_pass_rates == {"db": 1.0, "redis": 0.5}
    assert loaded.regression is not None
    assert loaded.regression.failures[0].metric == "pass_rate"


def test_experiment_store_lists_newest_first(tmp_path) -> None:
    store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    first = make_record("first")
    second = make_record("second")
    store.save(first)
    store.save(second)

    records = store.list()
    assert {record.experiment_id for record in records} == {"first", "second"}


def test_experiment_store_replaces_same_id(tmp_path) -> None:
    store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    store.save(make_record())
    store.save(make_record())
    loaded = store.get("exp-1")
    assert loaded is not None
    assert loaded.name == "baseline"


def test_experiment_store_validates_limit(tmp_path) -> None:
    store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    with pytest.raises(ValueError, match="between"):
        store.list(0)


def test_experiment_store_missing_record_is_none(tmp_path) -> None:
    store = SQLiteExperimentStore(str(tmp_path / "experiments.db"))
    assert store.get("missing") is None


def test_experiment_store_supports_memory_database() -> None:
    store = SQLiteExperimentStore(":memory:")
    record = make_record()
    store.save(record)
    assert store.get(record.experiment_id) is not None
