from dataclasses import dataclass
from statistics import fmean

from app.evaluation.evaluator import EvaluationResult


@dataclass(frozen=True)
class AggregateEvaluation:
    total_runs: int
    passed_runs: int
    pass_rate: float
    root_cause_accuracy: float
    average_evidence_recall: float
    average_evidence_precision: float
    average_confidence: float


def aggregate_evaluations(
    results: list[EvaluationResult], confidences: list[float] | None = None
) -> AggregateEvaluation:
    if not results:
        raise ValueError("At least one evaluation result is required")
    if confidences is not None and len(confidences) != len(results):
        raise ValueError("Confidence values must match the number of evaluations")

    values = confidences or [0.0] * len(results)
    total = len(results)
    return AggregateEvaluation(
        total_runs=total,
        passed_runs=sum(result.passed for result in results),
        pass_rate=sum(result.passed for result in results) / total,
        root_cause_accuracy=sum(result.root_cause_match for result in results) / total,
        average_evidence_recall=fmean(result.evidence_recall for result in results),
        average_evidence_precision=fmean(result.evidence_precision for result in results),
        average_confidence=fmean(values),
    )
