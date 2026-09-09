import time

from app.agent.runtime import InvestigationPhase, InvestigationRuntime
from app.models.domain import Diagnosis, Incident
from app.observability.events import InMemoryEventSink, TraceContext


class FakeInvestigator:
    def investigate(self, incident):
        return Diagnosis(
            incident_id=incident.id,
            root_cause="database pool exhaustion",
            evidence_ids=["db-1"],
            confidence=0.9,
            recommended_action="Increase pool capacity.",
        )


class FailingInvestigator:
    def investigate(self, incident):
        raise ValueError("model output was invalid")


class SlowInvestigator:
    def investigate(self, incident):
        time.sleep(0.01)
        return FakeInvestigator().investigate(incident)


def incident():
    return Incident(id="inc-1", title="Database errors", description="Requests are failing.")


def test_runtime_completes_and_records_lifecycle():
    sink = InMemoryEventSink()
    trace = TraceContext.create(sink)
    execution = InvestigationRuntime(FakeInvestigator(), trace=trace).execute(incident())

    assert execution.phase == InvestigationPhase.COMPLETED
    assert execution.diagnosis is not None
    assert execution.execution_id
    assert execution.trace_id == trace.trace_id
    assert [step.name for step in execution.steps] == [
        "investigation.started", "investigator", "investigation.completed"
    ]
    assert [event.name for event in sink.events()] == [
        "investigation.created", "investigation.started", "investigator.started",
        "investigator.completed", "investigation.completed"
    ]


def test_runtime_converts_investigator_failure_to_failed_execution():
    sink = InMemoryEventSink()
    execution = InvestigationRuntime(FailingInvestigator(), trace=TraceContext.create(sink)).execute(incident())

    assert execution.phase == InvestigationPhase.FAILED
    assert execution.diagnosis is None
    assert execution.error_type == "ValueError"
    assert execution.error_message == "model output was invalid"
    assert sink.events()[-1].name == "investigation.failed"


def test_runtime_or_raise_preserves_failure_boundary():
    try:
        InvestigationRuntime(FailingInvestigator()).execute_or_raise(incident())
    except RuntimeError as exc:
        assert "ValueError" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_runtime_rejects_non_positive_deadline():
    try:
        InvestigationRuntime(FakeInvestigator(), max_duration_ms=0)
    except ValueError as exc:
        assert "max_duration_ms" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_runtime_enforces_deadline_after_investigator_returns():
    execution = InvestigationRuntime(SlowInvestigator(), max_duration_ms=1).execute(incident())
    assert execution.phase == InvestigationPhase.FAILED
    assert execution.error_type == "TimeoutError"
