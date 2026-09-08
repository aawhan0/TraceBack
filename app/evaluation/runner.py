from dataclasses import dataclass
from typing import Callable

from app.agent.contracts import Investigator
from app.evaluation.aggregate import AggregateEvaluation, aggregate_evaluations
from app.evaluation.evaluator import EvaluationResult, evaluate_diagnosis
from app.evaluation.report import EvaluationReport
from app.models.domain import IncidentScenario


@dataclass(frozen=True)
class EvaluationRun:
    aggregate: AggregateEvaluation
    reports: tuple[EvaluationReport, ...]


def run_evaluation(
    investigator_factory: Callable[[IncidentScenario], Investigator],
    scenarios: tuple[IncidentScenario, ...],
) -> EvaluationRun:
    if not scenarios:
        raise ValueError("At least one scenario is required")

    reports: list[EvaluationReport] = []
    results: list[EvaluationResult] = []
    confidences: list[float] = []

    for scenario in scenarios:
        investigator = investigator_factory(scenario)
        diagnosis = investigator.investigate(scenario.incident)
        evaluation = evaluate_diagnosis(scenario, diagnosis)
        results.append(evaluation)
        confidences.append(diagnosis.confidence)
        reports.append(EvaluationReport(diagnosis=diagnosis, evaluation=evaluation))

    return EvaluationRun(
        aggregate=aggregate_evaluations(results, confidences),
        reports=tuple(reports),
    )
