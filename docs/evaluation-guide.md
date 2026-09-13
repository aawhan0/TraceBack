# Evaluation Guide

TraceBack evaluates an investigation run across five independent dimensions:

| Dimension | Passing condition |
| --- | --- |
| Root-cause match | Every expected root-cause keyword is present in the diagnosis |
| Evidence recall | All required evidence items are selected |
| Evidence precision | Every selected evidence item belongs to the scenario |
| Confidence validity | Confidence is within the inclusive `0..1` range |
| Recommended action | The diagnosis contains a non-empty remediation action |

## Overall pass rule

A run passes only when all five dimensions pass. Evidence recall and precision must both equal `1.0` (100%). This intentionally favors evidence-complete diagnoses over plausible but weakly supported answers.

## Reading the evaluation page

The Evaluation page lists recent persisted runs and loads the complete evaluator result for the selected run. The overall result shows how many of the five dimensions passed, while each card exposes the individual signal and its definition.

Use **Re-run investigation** to create a fresh run for the same scenario and mode. Compare the new run with the original rather than treating a single score as definitive.

## Interpreting results

- A root-cause match without evidence precision is not sufficient: the diagnosis may be correct for the wrong reasons.
- High confidence is meaningful only when confidence validity and evidence checks pass.
- A failed run is a review signal, not proof that the system is unusable.
- Baseline and LLM runs should be compared on the same scenario set and under the same evaluation rules.

## Limitations

The current evaluator is scenario-based and deterministic. It measures whether the diagnosis satisfies the scenario's expected conditions; it does not establish production incident resolution, causal certainty, or business impact.
