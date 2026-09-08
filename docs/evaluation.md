# Evaluation Contract

Traceback keeps evaluation separate from generation.

## Per-run metrics

Each diagnosis produces root-cause match, evidence recall, evidence precision, confidence validity, action presence, and an overall pass/fail result.

The evaluator rejects a diagnosis belonging to a different incident. This prevents cross-scenario results from being accidentally scored as valid.

## Aggregate metrics

Repeated evaluations can be summarized with total runs, passed runs, pass rate, root-cause accuracy, average evidence recall, average evidence precision, and average confidence.

run_evaluation executes an investigator factory over a scenario set and returns both aggregate metrics and typed per-scenario reports.

## Comparing experiments

compare_evaluations produces explicit deltas between two aggregate results. This creates a foundation for comparing models, prompts, providers, or tool strategies without mixing experiment logic into the evaluator.

## Acceptance rule

A diagnosis passes only when all required conditions are satisfied. The evaluator does not modify or repair a model response.

Generation can be probabilistic; measurement should remain deterministic.
