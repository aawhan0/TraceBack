from __future__ import annotations

from app.evaluation.experiments import ExperimentResult
from app.evaluation.regression import RegressionReport


def _render_failure_diagnostics(
    result: ExperimentResult,
) -> list[str]:
    failed_runs = [
        run
        for run in result.runs
        if not run.evaluation.passed
    ]

    if not failed_runs:
        return []

    lines = [
        "",
        "## Failure diagnostics",
        "",
    ]

    for index, run in enumerate(failed_runs, start=1):
        evaluation = run.evaluation
        diagnosis = run.diagnosis

        missing_keywords = (
            ", ".join(sorted(evaluation.missing_root_cause_keywords))
            or "none"
        )
        missing_evidence = (
            ", ".join(sorted(evaluation.missing_evidence_ids))
            or "none"
        )
        invalid_evidence = (
            ", ".join(sorted(evaluation.invalid_evidence_ids))
            or "none"
        )
        selected_evidence = (
            ", ".join(sorted(diagnosis.evidence_ids))
            or "none"
        )

        lines.extend(
            [
                f"### Failure {index}: {run.scenario_id}",
                "",
                f"- Root-cause match: "
                f"`{'PASS' if evaluation.root_cause_match else 'FAIL'}`",
                f"- Evidence recall: "
                f"`{evaluation.evidence_recall:.2f}`",
                f"- Evidence precision: "
                f"`{evaluation.evidence_precision:.2f}`",
                f"- Missing root-cause keywords: "
                f"`{missing_keywords}`",
                f"- Missing evidence IDs: "
                f"`{missing_evidence}`",
                f"- Invalid evidence IDs: "
                f"`{invalid_evidence}`",
                f"- Selected evidence IDs: "
                f"`{selected_evidence}`",
                f"- Predicted root cause: "
                f"`{diagnosis.root_cause}`",
                f"- Confidence: "
                f"`{diagnosis.confidence:.3f}`",
                f"- Recommended action: "
                f"`{diagnosis.recommended_action}`",
                "",
            ]
        )

    return lines


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
        f"| Root-cause accuracy | {result.root_cause_accuracy:.2%} |",
        f"| Average evidence recall | "
        f"{result.average_evidence_recall:.2%} |",
        f"| Average evidence precision | "
        f"{result.average_evidence_precision:.2%} |",
        f"| Average confidence | {result.average_confidence:.3f} |",
        f"| Average duration | {result.average_duration_ms:.2f} ms |",
    ]

    if regression is not None:
        lines.extend(
            [
                f"| Pass-rate Wilson interval | "
                f"{regression.pass_rate_interval_lower:.2%} "
                f"– "
                f"{regression.pass_rate_interval_upper:.2%} |",
            ]
        )

    lines.extend(
        [
            "",
            "## Scenario results",
            "",
            "| Scenario | Pass rate |",
            "| --- | ---: |",
        ]
    )

    lines.extend(
        f"| {scenario_id} | {pass_rate:.2%} |"
        for scenario_id, pass_rate in sorted(
            result.scenario_pass_rates.items()
        )
    )

    lines.extend(_render_failure_diagnostics(result))

    if regression is not None:
        lines.extend(
            [
                "",
                "## Regression gate",
                "",
            ]
        )
        lines.append(
            f"**Status:** {'PASS' if regression.passed else 'FAIL'}"
        )
        lines.append("")

        if regression.failures:
            lines.extend(
                [
                    "| Metric | Actual | Expected |",
                    "| --- | ---: | ---: |",
                ]
            )
            lines.extend(
                f"| {failure.metric} | "
                f"{failure.actual:.4f} | "
                f"{failure.expected:.4f} |"
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
        f"| Pass rate | {baseline.pass_rate:.2%} | "
        f"{candidate.pass_rate:.2%} | "
        f"{candidate.pass_rate - baseline.pass_rate:+.2%} |",
        f"| Root-cause accuracy | "
        f"{baseline.root_cause_accuracy:.2%} | "
        f"{candidate.root_cause_accuracy:.2%} | "
        f"{candidate.root_cause_accuracy - baseline.root_cause_accuracy:+.2%} |",
        f"| Evidence recall | "
        f"{baseline.average_evidence_recall:.2%} | "
        f"{candidate.average_evidence_recall:.2%} | "
        f"{candidate.average_evidence_recall - baseline.average_evidence_recall:+.2%} |",
        f"| Evidence precision | "
        f"{baseline.average_evidence_precision:.2%} | "
        f"{candidate.average_evidence_precision:.2%} | "
        f"{candidate.average_evidence_precision - baseline.average_evidence_precision:+.2%} |",
        f"| Confidence | {baseline.average_confidence:.3f} | "
        f"{candidate.average_confidence:.3f} | "
        f"{candidate.average_confidence - baseline.average_confidence:+.3f} |",
        f"| Duration | {baseline.average_duration_ms:.2f} ms | "
        f"{candidate.average_duration_ms:.2f} ms | "
        f"{candidate.average_duration_ms - baseline.average_duration_ms:+.2f} ms |",
    ]

    return "\n".join(lines) + "\n"


def render_benchmark_comparison_markdown(comparison) -> str:
    """Render a persisted benchmark comparison for humans and CI artifacts."""

    lines = [
        "# Benchmark comparison",
        "",
        f"**Verdict:** {comparison.verdict.upper()}",
        "",
        f"- Baseline: {comparison.baseline_experiment_id}",
        f"- Candidate: {comparison.candidate_experiment_id}",
        f"- Dataset: {comparison.dataset_name}@{comparison.dataset_version}",
        f"- Fingerprint: `{comparison.dataset_fingerprint}`",
        "",
        "| Metric | Baseline | Candidate | Delta |",
        "| --- | ---: | ---: | ---: |",
        f"| Pass rate | {comparison.baseline_pass_rate:.2%} | "
        f"{comparison.candidate_pass_rate:.2%} | "
        f"{comparison.pass_rate_delta:+.2%} |",
        f"| Confidence | {comparison.baseline_confidence:.3f} | "
        f"{comparison.candidate_confidence:.3f} | "
        f"{comparison.confidence_delta:+.3f} |",
        f"| Duration | {comparison.baseline_duration_ms:.2f} ms | "
        f"{comparison.candidate_duration_ms:.2f} ms | "
        f"{comparison.duration_delta_ms:+.2f} ms |",
        "",
        "## Scenario deltas",
        "",
        "| Scenario | Baseline | Candidate | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]

    lines.extend(
        f"| {item.scenario_id} | "
        f"{item.baseline_pass_rate:.2%} | "
        f"{item.candidate_pass_rate:.2%} | "
        f"{item.pass_rate_delta:+.2%} |"
        for item in comparison.scenario_comparisons
    )

    return "\n".join(lines) + "\n"



