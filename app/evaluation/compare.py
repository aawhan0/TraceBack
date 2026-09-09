from dataclasses import dataclass

from app.evaluation.aggregate import AggregateEvaluation


@dataclass(frozen=True)
class EvaluationComparison:
    baseline_pass_rate: float
    candidate_pass_rate: float
    pass_rate_delta: float
    baseline_root_cause_accuracy: float
    candidate_root_cause_accuracy: float
    root_cause_accuracy_delta: float


def compare_evaluations(
    baseline: AggregateEvaluation,
    candidate: AggregateEvaluation,
) -> EvaluationComparison:
    return EvaluationComparison(
        baseline_pass_rate=baseline.pass_rate,
        candidate_pass_rate=candidate.pass_rate,
        pass_rate_delta=candidate.pass_rate - baseline.pass_rate,
        baseline_root_cause_accuracy=baseline.root_cause_accuracy,
        candidate_root_cause_accuracy=candidate.root_cause_accuracy,
        root_cause_accuracy_delta=(
            candidate.root_cause_accuracy - baseline.root_cause_accuracy
        ),
    )


# Backwards-compatible exports for callers using the comparison module directly.
from app.evaluation.comparison import IncompatibleBenchmarkError
