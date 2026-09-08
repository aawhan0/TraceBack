from app.evaluation.aggregate import AggregateEvaluation
from app.evaluation.compare import compare_evaluations


def make_aggregate(pass_rate: float, accuracy: float) -> AggregateEvaluation:
    passed = 2 if pass_rate == 1.0 else 1
    return AggregateEvaluation(2, passed, pass_rate, accuracy, 1.0, 1.0, 0.8)


def test_compare_evaluations_reports_deltas() -> None:
    comparison = compare_evaluations(
        make_aggregate(0.5, 0.5),
        make_aggregate(1.0, 1.0),
    )
    assert comparison.pass_rate_delta == 0.5
    assert comparison.root_cause_accuracy_delta == 0.5
