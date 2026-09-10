# Re-run Investigation

The Evaluation view can re-run the currently selected investigation with the same scenario and execution mode.

## Behavior

1. Select a persisted run from **Recent runs**.
2. Click **Re-run investigation**.
3. TraceBack sends a new `POST /investigations` request using the selected run's `scenario_id` and `mode`.
4. The new run is persisted independently and becomes the selected run.

The original run is never overwritten, keeping every attempt available for comparison.
