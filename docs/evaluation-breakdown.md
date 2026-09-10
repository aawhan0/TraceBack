# Evaluation Breakdown

The Evaluation view makes the persisted investigation evaluator results inspectable instead of exposing only a final pass/fail result.

## Dimensions

Each investigation run stores five evaluator dimensions:

- **Root-cause match** — every expected root-cause keyword must appear in the diagnosis.
- **Evidence recall** — the fraction of required evidence selected by the diagnosis.
- **Evidence precision** — the fraction of selected evidence that is valid for the scenario.
- **Confidence validity** — confidence must be within the `0.0`–`1.0` range.
- **Recommended action** — the diagnosis must contain a non-empty recommended action.

The persisted overall result passes only when all five conditions are satisfied. Evidence recall and precision must both equal `100%`.

## UI behavior

The page loads recent runs from `GET /runs` and the selected run from `GET /runs/{run_id}`. It does not re-run evaluation or mutate stored results.
