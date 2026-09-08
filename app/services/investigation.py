from dataclasses import dataclass

from app.agent.baseline import BaselineInvestigator
from app.agent.contracts import Investigator, LLMProvider
from app.agent.llm import LLMInvestigator
from app.evaluation.evaluator import EvaluationResult, evaluate_diagnosis
from app.models.domain import Diagnosis, IncidentScenario


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
    ) -> InvestigationResult:
        if investigator is None:
            investigator = (
                LLMInvestigator(scenario, provider)
                if provider is not None
                else BaselineInvestigator(scenario)
            )

        diagnosis = investigator.investigate(scenario.incident)
        evaluation = evaluate_diagnosis(scenario, diagnosis)
        return InvestigationResult(
            scenario_id=scenario.id,
            diagnosis=diagnosis,
            evaluation=evaluation,
            investigator=type(investigator).__name__,
        )
