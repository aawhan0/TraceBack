import pytest

from app.evaluation.compare import IncompatibleBenchmarkError, compare_experiments
from app.evaluation.experiments import ExperimentResult
from app.evaluation.provenance import BenchmarkProvenance
from app.repository.experiments import ExperimentRecord
from datetime import datetime, timezone


def make_record(
    experiment_id: str,
    *,
    fingerprint: str = "same",
    pass_rate: float = 1.0,
    scenarios: dict[str, float] | None = None,
    provider: str = "baseline",
    model: str | None = None,
) -> ExperimentRecord:
    result = ExperimentResult(
        name=experiment_id,
        total_runs=2,
        passed_runs=int(pass_rate * 2),
        pass_rate=pass_rate,
        average_confidence=0.8,
        average_duration_ms=100.0,
        scenario_pass_rates=scenarios or {"database-pool-exhaustion": pass_rate},
    )
    return ExperimentRecord(
        experiment_id=experiment_id,
        name=experiment_id,
        dataset_name="core-scenarios",
        dataset_version="1",
        dataset_fingerprint=fingerprint,
        result=result,
        regression=None,
        created_at=datetime.now(timezone.utc),
        provenance=BenchmarkProvenance(
            application_version="0.1.0",
            git_revision="test",
            python_version="3.12",
            environment="test",
            provider=provider,
            model=model,
        ),
    )


def test_compare_experiments_reports_metric_and_scenario_deltas() -> None:
    baseline = make_record("base", pass_rate=0.5)
    candidate = make_record("candidate", pass_rate=1.0, provider="ollama", model="llama3.2")

    comparison = compare_experiments(baseline, candidate)

    assert comparison.pass_rate_delta == 0.5
    assert comparison.verdict == "improved"
    assert comparison.candidate_provider == "ollama"
    assert comparison.candidate_model == "llama3.2"
    assert comparison.scenario_comparisons[0].pass_rate_delta == 0.5


def test_compare_experiments_rejects_different_dataset_fingerprint() -> None:
    with pytest.raises(IncompatibleBenchmarkError, match="fingerprints"):
        compare_experiments(make_record("base"), make_record("candidate", fingerprint="different"))


def test_compare_experiments_rejects_different_scenario_sets() -> None:
    with pytest.raises(IncompatibleBenchmarkError, match="scenario sets"):
        compare_experiments(
            make_record("base"),
            make_record("candidate", scenarios={"redis-connectivity-failure": 1.0}),
        )


def test_comparison_detects_regression_and_unchanged_results() -> None:
    assert compare_experiments(make_record("base", pass_rate=1.0), make_record("candidate", pass_rate=0.5)).regressed
    assert compare_experiments(make_record("base"), make_record("candidate")).unchanged
