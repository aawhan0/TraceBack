import pytest

from app.agent.baseline import BaselineInvestigator
from app.evaluation.aggregate import aggregate_evaluations
from app.evaluation.evaluator import evaluate_diagnosis
from app.observability.events import InMemoryEventSink, TraceContext
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
    scenario = SCENARIOS[1]
    sink = InMemoryEventSink()
    result = InvestigationService().investigate(
        scenario,
        trace=TraceContext.create(sink),
    )
    assert result.scenario_id == scenario.id
    assert result.evaluation.passed
    assert result.execution_id
    assert result.trace_id
    assert result.duration_ms >= 0
    assert sink.events()


def test_investigation_service_exposes_runtime_timeline() -> None:
    result = InvestigationService().investigate(SCENARIOS[0])
    names = result.timeline.names()
    assert result.timeline.trace_id == result.trace_id
    assert result.timeline.event_count >= 5
    assert names[0] == "investigation.created"
    assert "investigation.started" in names
    assert "investigator.started" in names
    assert "investigator.completed" in names
    assert names[-1] == "investigation.completed"


def test_investigation_service_persists_runtime_identity() -> None:
    scenario = SCENARIOS[0]
    result = InvestigationService().investigate(scenario)
    assert result.run_id
    assert result.execution_id
    assert result.trace_id


def test_aggregate_evaluation_summarizes_repeated_runs() -> None:
    scenario = SCENARIOS[0]
    diagnosis = BaselineInvestigator(scenario).investigate(scenario.incident)
    evaluation = evaluate_diagnosis(scenario, diagnosis)
    aggregate = aggregate_evaluations([evaluation, evaluation], [0.8, 0.9])
    assert aggregate.total_runs == 2
    assert aggregate.passed_runs == 2
    assert aggregate.pass_rate == 1.0
    assert aggregate.average_confidence == pytest.approx(0.85)
