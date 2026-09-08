from dataclasses import dataclass

from app.agent.baseline import BaselineInvestigator
from app.evaluation.evaluator import EvaluationResult, evaluate_diagnosis
from app.models.domain import Diagnosis, IncidentScenario


@dataclass(frozen=True)
class InvestigationResult:
    scenario_id: str
    diagnosis: Diagnosis
    evaluation: EvaluationResult


class InvestigationService:
    """Application-level orchestration for investigation and evaluation."""

    def investigate(self, scenario: IncidentScenario) -> InvestigationResult:
        diagnosis = BaselineInvestigator(scenario).investigate(scenario.incident)
        evaluation = evaluate_diagnosis(scenario, diagnosis)
        return InvestigationResult(scenario.id, diagnosis, evaluation)
