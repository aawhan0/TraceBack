from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from uuid import uuid4

from app.agent.baseline import BaselineInvestigator
from app.agent.contracts import Investigator, LLMProvider
from app.agent.llm import LLMInvestigator
from app.evaluation.evaluator import EvaluationResult, evaluate_diagnosis
from app.config import Settings
from app.models.domain import Diagnosis, IncidentScenario, InvestigationRun
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


class InvestigationService:
    """Application-level orchestration for baseline and LLM investigation."""

    def investigate(
        self,
        scenario: IncidentScenario,
        investigator: Investigator | None = None,
        provider: LLMProvider | None = None,
        run_store: RunStore | None = None,
    ) -> InvestigationResult:
        if investigator is None:
            investigator = (
                LLMInvestigator(scenario, provider)
                if provider is not None
                else BaselineInvestigator(scenario)
            )

        started = perf_counter()
        diagnosis = investigator.investigate(scenario.incident)
        evaluation = evaluate_diagnosis(scenario, diagnosis)
        duration_ms = (perf_counter() - started) * 1000
        run_id = str(uuid4())
        created_at = utc_now()
        result = InvestigationResult(
            run_id=run_id,
            scenario_id=scenario.id,
            diagnosis=diagnosis,
            evaluation=evaluation,
            investigator=type(investigator).__name__,
            duration_ms=duration_ms,
            created_at=created_at,
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
                duration_ms=duration_ms,
                created_at=created_at,
            )
        )
        return result
