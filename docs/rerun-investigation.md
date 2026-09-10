# Re-run Investigation

The Evaluation view can re-run the currently selected investigation with the same scenario and execution mode.

## Behavior

1. Select a persisted run from **Recent runs**.
2. Review its evaluation details.
3. Click **Re-run investigation**.
4. TraceBack sends a new `POST /investigations` request using the selected run's `scenario_id` and `mode`.
5. The new run is persisted independently and becomes the selected run.

Re-running does not overwrite the original run, so results remain comparable across attempts.

For LLM runs, the re-run uses the application's configured model/provider settings, matching the normal investigation endpoint behavior.
