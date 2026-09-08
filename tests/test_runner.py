import pytest

from app.agent.baseline import BaselineInvestigator
from app.evaluation.runner import run_evaluation
from app.scenarios.catalog import SCENARIOS


def test_run_evaluation_aggregates_multiple_scenarios() -> None:
    result = run_evaluation(BaselineInvestigator, SCENARIOS)
    assert result.aggregate.total_runs == len(SCENARIOS)
    assert result.aggregate.pass_rate == 1.0
    assert len(result.reports) == len(SCENARIOS)


def test_run_evaluation_rejects_empty_scenarios() -> None:
    with pytest.raises(ValueError, match="At least one scenario"):
        run_evaluation(BaselineInvestigator, ())
