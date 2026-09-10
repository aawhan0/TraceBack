import pytest

from app.evaluation.experiments import ExperimentResult
from app.evaluation.regression import (
    ExperimentMetrics,
    RegressionPolicy,
    evaluate_regression,
    metrics_from_experiment,
)


def metrics(**overrides: float) -> ExperimentMetrics:
    values = {
        "pass_rate": 1.0,
        "root_cause_accuracy": 1.0,
        "evidence_recall": 1.0,
        "evidence_precision": 1.0,
        "average_confidence": 0.9,
        "average_duration_ms": 100.0,
    }
    values.update(overrides)
    return ExperimentMetrics(**values)


def test_default_regression_policy_passes_perfect_metrics() -> None:
    report = evaluate_regression(
        metrics(),
        RegressionPolicy(),
        passed_runs=10,
        total_runs=10,
    )
    assert report.passed
    assert report.failures == ()
    assert report.pass_rate_interval_lower < 1.0


@pytest.mark.parametrize(
    "field",
    ["pass_rate", "root_cause_accuracy", "evidence_recall", "evidence_precision"],
)
def test_quality_thresholds_are_enforced(field: str) -> None:
    values = {field: 0.8}
    report = evaluate_regression(
        metrics(**values),
        RegressionPolicy(
            minimum_pass_rate=0.9,
            minimum_root_cause_accuracy=0.9,
            minimum_evidence_recall=0.9,
            minimum_evidence_precision=0.9,
        ),
        passed_runs=8,
        total_runs=10,
    )
    assert not report.passed
    assert any(failure.metric == field for failure in report.failures)


def test_latency_ceiling_is_enforced() -> None:
    report = evaluate_regression(
        metrics(average_duration_ms=250),
        RegressionPolicy(maximum_average_duration_ms=200),
        passed_runs=10,
        total_runs=10,
    )
    assert not report.passed
    assert report.failures[0].metric == "average_duration_ms"
    assert report.failures[0].direction == "max"


def test_optional_confidence_threshold_is_enforced() -> None:
    report = evaluate_regression(
        metrics(average_confidence=0.5),
        RegressionPolicy(minimum_average_confidence=0.75),
        passed_runs=10,
        total_runs=10,
    )
    assert not report.passed
    assert any(failure.metric == "average_confidence" for failure in report.failures)


def test_scenario_thresholds_are_enforced() -> None:
    data = metrics()
    data = ExperimentMetrics(**{**data.__dict__, "scenario_pass_rates": {"redis": 0.5}})
    report = evaluate_regression(
        data,
        RegressionPolicy(minimum_scenario_pass_rate=0.9),
        passed_runs=9,
        total_runs=10,
    )
    assert not report.passed
    assert report.failures[0].metric == "scenario:redis"


@pytest.mark.parametrize(
    "field,value",
    [
        ("minimum_pass_rate", 1.1),
        ("minimum_root_cause_accuracy", -0.1),
        ("minimum_evidence_recall", 2),
        ("minimum_evidence_precision", -1),
        ("minimum_scenario_pass_rate", 1.2),
    ],
)
def test_invalid_quality_thresholds_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        RegressionPolicy(**{field: value})


def test_invalid_latency_and_confidence_thresholds_are_rejected() -> None:
    with pytest.raises(ValueError):
        RegressionPolicy(maximum_average_duration_ms=-1)
    with pytest.raises(ValueError):
        RegressionPolicy(minimum_average_confidence=1.1)


def test_metrics_adapter_preserves_experiment_values() -> None:
    result = ExperimentResult(
        "x",
        2,
        1,
        0.5,
        0.5,
        0.9,
        0.85,
        0.7,
        123,
        {"a": 0.5},
    )
    adapted = metrics_from_experiment(result)
    assert adapted.pass_rate == 0.5
    assert adapted.average_confidence == 0.7
    assert adapted.average_duration_ms == 123
    assert adapted.root_cause_accuracy == 0.5
    assert adapted.evidence_recall == 0.9
    assert adapted.evidence_precision == 0.85
    assert adapted.scenario_pass_rates == {"a": 0.5}


def test_regression_report_contains_latency_summary() -> None:
    report = evaluate_regression(
        metrics(average_duration_ms=12.5),
        RegressionPolicy(),
        passed_runs=1,
        total_runs=1,
    )
    assert report.latency is not None
    assert report.latency.mean == 12.5
