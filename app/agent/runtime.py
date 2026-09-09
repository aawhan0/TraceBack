from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable
from uuid import uuid4

from app.agent.contracts import Investigator
from app.models.domain import Diagnosis, Incident
from app.observability.events import TraceContext


class InvestigationPhase(str):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class InvestigationStep:
    sequence: int
    phase: str
    name: str
    duration_ms: float
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InvestigationExecution:
    execution_id: str
    trace_id: str
    incident_id: str
    phase: str
    diagnosis: Diagnosis | None
    steps: tuple[InvestigationStep, ...]
    duration_ms: float
    error_type: str | None = None
    error_message: str | None = None


class InvestigationRuntime:
    """Owns the lifecycle around one bounded investigation execution."""

    def __init__(self, investigator: Investigator, *, trace: TraceContext | None = None, max_duration_ms: float = 60_000) -> None:
        if max_duration_ms <= 0:
            raise ValueError("max_duration_ms must be positive")
        self._investigator = investigator
        self._trace = trace or TraceContext.create()
        self._max_duration_ms = max_duration_ms

    @property
    def trace_id(self) -> str:
        return self._trace.trace_id

    def execute(self, incident: Incident) -> InvestigationExecution:
        execution_id = str(uuid4())
        started = perf_counter()
        steps: list[InvestigationStep] = []
        self._trace.record('investigation.created', execution_id=execution_id, incident_id=incident.id)
        self._trace.record('investigation.started', execution_id=execution_id, incident_id=incident.id)
        self._record_step(steps, started, InvestigationPhase.RUNNING, 'investigation.started')
        try:
            self._check_deadline(started)
            diagnosis = self._run_investigator(incident, steps)
            self._check_deadline(started)
        except Exception as exc:
            duration_ms = (perf_counter() - started) * 1000
            self._trace.record('investigation.failed', execution_id=execution_id, incident_id=incident.id, error_type=type(exc).__name__)
            self._record_step(steps, started, InvestigationPhase.FAILED, 'investigation.failed', error_type=type(exc).__name__)
            return InvestigationExecution(execution_id, self.trace_id, incident.id, InvestigationPhase.FAILED, None, tuple(steps), duration_ms, type(exc).__name__, str(exc))
        duration_ms = (perf_counter() - started) * 1000
        self._trace.record('investigation.completed', execution_id=execution_id, incident_id=incident.id, duration_ms=f'{duration_ms:.3f}')
        self._record_step(steps, started, InvestigationPhase.COMPLETED, 'investigation.completed')
        return InvestigationExecution(execution_id, self.trace_id, incident.id, InvestigationPhase.COMPLETED, diagnosis, tuple(steps), duration_ms)

    def execute_or_raise(self, incident: Incident) -> Diagnosis:
        execution = self.execute(incident)
        if execution.phase == InvestigationPhase.FAILED:
            raise RuntimeError(f'investigation failed: {execution.error_type}: {execution.error_message}')
        assert execution.diagnosis is not None
        return execution.diagnosis

    def _run_investigator(self, incident: Incident, steps: list[InvestigationStep]) -> Diagnosis:
        started = perf_counter()
        self._trace.record('investigator.started', incident_id=incident.id)
        try:
            diagnosis = self._investigator.investigate(incident)
        except Exception as exc:
            self._trace.record('investigator.failed', incident_id=incident.id, error_type=type(exc).__name__)
            raise
        finally:
            steps.append(InvestigationStep(len(steps) + 1, InvestigationPhase.RUNNING, 'investigator', (perf_counter() - started) * 1000))
        self._trace.record('investigator.completed', incident_id=incident.id, evidence_count=len(diagnosis.evidence_ids))
        return diagnosis

    def _check_deadline(self, started: float) -> None:
        if (perf_counter() - started) * 1000 > self._max_duration_ms:
            raise TimeoutError('investigation exceeded max_duration_ms')

    def _record_step(self, steps: list[InvestigationStep], started: float, phase: str, name: str, **metadata: object) -> None:
        steps.append(InvestigationStep(len(steps) + 1, phase, name, (perf_counter() - started) * 1000, {k: str(v) for k, v in metadata.items()}))


def run_investigation(investigator: Investigator, incident: Incident, *, trace: TraceContext | None = None, max_duration_ms: float = 60_000, on_complete: Callable[[InvestigationExecution], None] | None = None) -> InvestigationExecution:
    execution = InvestigationRuntime(investigator, trace=trace, max_duration_ms=max_duration_ms).execute(incident)
    if on_complete is not None:
        on_complete(execution)
    return execution
