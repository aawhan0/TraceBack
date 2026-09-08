# Evaluation Contract

Traceback keeps evaluation separate from generation.

## Per-run metrics

Each diagnosis produces root-cause match, evidence recall, evidence precision, confidence validity, action presence, and an overall pass/fail result.

## Aggregate metrics

Repeated evaluations can be summarized with total runs, passed runs, pass rate, root-cause accuracy, average evidence recall, average evidence precision, and average confidence.

The aggregate function rejects empty result sets and mismatched confidence lists so incomplete experiment data cannot silently become a report.

## Acceptance rule

A diagnosis passes only when all required conditions are satisfied. The evaluator does not modify or repair a model response.

Generation can be probabilistic; measurement should remain deterministic.
