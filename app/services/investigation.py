from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.agent.baseline import BaselineInvestigator
from app.agent.contracts import Investigator, LLMProvider
from app.agent.llm import LLMInvestigator
from app.agent.runtime import InvestigationRuntime
from app.config import Settings
from app.evaluation.evaluator import EvaluationResult, evaluate_diagnosis
from app.models.domain import Diagnosis, IncidentScenario, InvestigationRun
from app.observability.events import TraceContext
from app.repository.runs import RunStore, SQLiteRunStore, utc_now


@dataclass(frozen=True)
class InvestigationResult:
    run_id: str
    scenario_id: str
    diagnosis: Diagnosis
    evaluation: EvaluationResult
    investigator: str
    duration_ms: float
    created_at: datetime
    execution_id: str
    trace_id: str


class InvestigationService:
    """Application-level orchestration for investigation, evaluation and persistence."""

    def investigate(
        self,
        scenario: IncidentScenario,
        investigator: Investigator | None = None,
        provider: LLMProvider | None = None,
        run_store: RunStore | None = None,
        trace: TraceContext | None = None,
        max_duration_ms: float = 60_000,
    ) -> InvestigationResult:
        if investigator is None:
            investigator = (
                LLMInvestigator(scenario, provider)
                if provider is not None
                else BaselineInvestigator(scenario)
            )

        execution = InvestigationRuntime(
            investigator,
            trace=trace,
            max_duration_ms=max_duration_ms,
        ).execute(scenario.incident)
        if execution.phase != "completed" or execution.diagnosis is None:
            raise RuntimeError(
                f"investigation execution failed: {execution.error_type}: "
                f"{execution.error_message}"
            )

        diagnosis = execution.diagnosis
        evaluation = evaluate_diagnosis(scenario, diagnosis)
        run_id = str(uuid4())
        created_at = utc_now()
        result = InvestigationResult(
            run_id=run_id,
            scenario_id=scenario.id,
            diagnosis=diagnosis,
            evaluation=evaluation,
            investigator=type(investigator).__name__,
            duration_ms=execution.duration_ms,
            created_at=created_at,
            execution_id=execution.execution_id,
            trace_id=execution.trace_id,
        )
        store = run_store or SQLiteRunStore(Settings.from_environment().database_path)
        store.save(
            InvestigationRun(
                run_id=run_id,
                scenario_id=result.scenario_id,
                mode="llm" if provider is not None else "baseline",
                provider=getattr(provider, "name", "baseline") if provider is not None else "baseline",
                diagnosis=result.diagnosis,
                root_cause_match=result.evaluation.root_cause_match,
                evidence_recall=result.evaluation.evidence_recall,
                evidence_precision=result.evaluation.evidence_precision,
                confidence_valid=result.evaluation.confidence_valid,
                action_present=result.evaluation.action_present,
                passed=result.evaluation.passed,
                duration_ms=execution.duration_ms,
                created_at=created_at,
            )
        )
        return result
