from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from app.agent.baseline import BaselineInvestigator
from app.agent.contracts import Investigator, LLMProvider
from app.agent.llm import LLMInvestigator
from app.evaluation.evaluator import EvaluationResult, evaluate_diagnosis
from app.models.domain import Diagnosis, IncidentScenario, InvestigationRun
from app.repository.runs import RunStore, SQLiteRunStore, utc_now


@dataclass(frozen=True)
class InvestigationResult:
    scenario_id: str
    diagnosis: Diagnosis
    evaluation: EvaluationResult
    investigator: str


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
        result = InvestigationResult(
            scenario_id=scenario.id,
            diagnosis=diagnosis,
            evaluation=evaluation,
            investigator=type(investigator).__name__,
        )
        store = run_store or SQLiteRunStore()
        store.save(
            InvestigationRun(
                run_id=str(uuid4()),
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
                created_at=utc_now(),
            )
        )
        return result
