from __future__ import annotations

from app.evaluation.experiments import ExperimentResult
from app.evaluation.regression import RegressionReport


def render_experiment_markdown(
    result: ExperimentResult,
    regression: RegressionReport | None = None,
) -> str:
    lines = [
        f"# Experiment: {result.name}",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total runs | {result.total_runs} |",
        f"| Passed runs | {result.passed_runs} |",
        f"| Pass rate | {result.pass_rate:.2%} |",
        f"| Average confidence | {result.average_confidence:.3f} |",
        f"| Average duration | {result.average_duration_ms:.2f} ms |",
        "",
        "## Scenario results",
        "",
        "| Scenario | Pass rate |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {scenario_id} | {pass_rate:.2%} |"
        for scenario_id, pass_rate in sorted(result.scenario_pass_rates.items())
    )
    if regression is not None:
        lines.extend(["", "## Regression gate", ""])
        lines.append(f"**Status:** {'PASS' if regression.passed else 'FAIL'}")
        lines.append("")
        if regression.failures:
            lines.extend(
                [
                    "| Metric | Actual | Expected |",
                    "| --- | ---: | ---: |",
                ]
            )
            lines.extend(
                f"| {failure.metric} | {failure.actual:.4f} | {failure.expected:.4f} |"
                for failure in regression.failures
            )
        else:
            lines.append("All configured thresholds passed.")
    return "\n".join(lines) + "\n"


def render_comparison_markdown(
    baseline: ExperimentResult,
    candidate: ExperimentResult,
) -> str:
    lines = [
        "# Experiment comparison",
        "",
        "| Metric | Baseline | Candidate | Delta |",
        "| --- | ---: | ---: | ---: |",
        f"| Pass rate | {baseline.pass_rate:.2%} | {candidate.pass_rate:.2%} | "
        f"{candidate.pass_rate - baseline.pass_rate:+.2%} |",
        f"| Confidence | {baseline.average_confidence:.3f} | "
        f"{candidate.average_confidence:.3f} | "
        f"{candidate.average_confidence - baseline.average_confidence:+.3f} |",
        f"| Duration | {baseline.average_duration_ms:.2f} ms | "
        f"{candidate.average_duration_ms:.2f} ms | "
        f"{candidate.average_duration_ms - baseline.average_duration_ms:+.2f} ms |",
    ]
    return "\n".join(lines) + "\n"
