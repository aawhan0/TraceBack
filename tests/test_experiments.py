import pytest

from app.evaluation.experiments import (
    ExperimentResult,
    ExperimentSpec,
    RegressionGate,
    compare_experiments,
    summarize_experiment,
)
from app.scenarios.catalog import SCENARIOS
from app.services.investigation import InvestigationService


def test_experiment_spec_rejects_invalid_repetitions() -> None:
    with pytest.raises(ValueError, match="repetitions"):
        ExperimentSpec("smoke", (SCENARIOS[0].id,), repetitions=0)


def test_summarize_experiment_groups_scenario_pass_rates() -> None:
    service = InvestigationService()
    results = [
        service.investigate(SCENARIOS[0]),
        service.investigate(SCENARIOS[1]),
        service.investigate(SCENARIOS[0]),
    ]

    summary = summarize_experiment("baseline-smoke", results)

    assert summary.total_runs == 3
    assert summary.passed_runs == 3
    assert summary.pass_rate == 1.0
    assert summary.root_cause_accuracy == 1.0
    assert summary.average_evidence_recall == 1.0
    assert summary.average_evidence_precision == 1.0
    assert summary.scenario_pass_rates[SCENARIOS[0].id] == 1.0


def test_regression_gate_and_comparison() -> None:
    baseline = ExperimentResult("baseline", 4, 4, 1.0, 1.0, 1.0, 1.0, 0.8, 100.0, {})
    candidate = ExperimentResult("candidate", 4, 3, 0.75, 0.75, 0.8, 0.9, 0.9, 120.0, {})

    assert RegressionGate(0.75).check(candidate)
    assert not RegressionGate(0.76).check(candidate)

    delta = compare_experiments(baseline, candidate)
    assert delta["pass_rate_delta"] == pytest.approx(-0.25)
    assert delta["root_cause_accuracy_delta"] == pytest.approx(-0.25)
    assert delta["evidence_recall_delta"] == pytest.approx(-0.2)
    assert delta["evidence_precision_delta"] == pytest.approx(-0.1)
    assert delta["average_confidence_delta"] == pytest.approx(0.1)
    assert delta["average_duration_ms_delta"] == pytest.approx(20.0)
