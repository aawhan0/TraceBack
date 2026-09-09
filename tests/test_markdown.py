from app.evaluation.experiments import ExperimentResult
from app.evaluation.markdown import render_comparison_markdown, render_experiment_markdown
from app.evaluation.regression import RegressionFailure, RegressionReport


def result(name: str, rate: float) -> ExperimentResult:
    return ExperimentResult(
        name=name,
        total_runs=10,
        passed_runs=int(rate * 10),
        pass_rate=rate,
        average_confidence=0.8,
        average_duration_ms=100.0,
        scenario_pass_rates={"db": rate},
    )


def test_experiment_markdown_contains_metrics() -> None:
    report = render_experiment_markdown(result("smoke", 1.0))
    assert "# Experiment: smoke" in report
    assert "| Pass rate | 100.00% |" in report
    assert "| db | 100.00% |" in report


def test_experiment_markdown_contains_regression_failures() -> None:
    regression = RegressionReport(
        passed=False,
        failures=(
            RegressionFailure("pass_rate", 0.5, 1.0, "min", "too low"),
        ),
        pass_rate_interval_lower=0.2,
        pass_rate_interval_upper=0.8,
    )
    report = render_experiment_markdown(result("smoke", 0.5), regression)
    assert "**Status:** FAIL" in report
    assert "| pass_rate | 0.5000 | 1.0000 |" in report


def test_experiment_markdown_reports_successful_gate() -> None:
    regression = RegressionReport(True, (), 0.7, 1.0)
    report = render_experiment_markdown(result("smoke", 1.0), regression)
    assert "**Status:** PASS" in report
    assert "All configured thresholds passed." in report


def test_comparison_markdown_shows_deltas() -> None:
    report = render_comparison_markdown(result("base", 0.8), result("candidate", 1.0))
    assert "# Experiment comparison" in report
    assert "+20.00%" in report
