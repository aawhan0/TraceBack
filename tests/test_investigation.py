import pytest

from app.agent.baseline import BaselineInvestigator
from app.evaluation.aggregate import aggregate_evaluations
from app.evaluation.evaluator import evaluate_diagnosis
from app.scenarios.catalog import SCENARIOS
from app.services.investigation import InvestigationService


def test_baseline_investigator_returns_structured_diagnosis() -> None:
    scenario = SCENARIOS[0]
    diagnosis = BaselineInvestigator(scenario).investigate(scenario.incident)
    assert diagnosis.incident_id == scenario.incident.id
    assert diagnosis.root_cause == scenario.expected_root_cause
    assert diagnosis.evidence_ids
    assert 0 <= diagnosis.confidence <= 1
    assert diagnosis.recommended_action


def test_investigation_service_is_end_to_end() -> None:
    result = InvestigationService().investigate(SCENARIOS[1])
    assert result.scenario_id == SCENARIOS[1].id
    assert result.evaluation.passed


def test_aggregate_evaluation_summarizes_repeated_runs() -> None:
    scenario = SCENARIOS[0]
    diagnosis = BaselineInvestigator(scenario).investigate(scenario.incident)
    evaluation = evaluate_diagnosis(scenario, diagnosis)
    aggregate = aggregate_evaluations([evaluation, evaluation], [0.8, 0.9])
    assert aggregate.total_runs == 2
    assert aggregate.passed_runs == 2
    assert aggregate.pass_rate == 1.0
    assert aggregate.average_confidence == pytest.approx(0.85)
