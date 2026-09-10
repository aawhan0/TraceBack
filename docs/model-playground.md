# Model Playground

The dashboard Playground provides a focused way to exercise the investigation engine without creating a benchmark first.

Choose any built-in or custom scenario, optionally enter an Ollama model, and run either the deterministic baseline or the LLM investigator. The page calls the real `POST /investigations` API and displays the resulting pass/fail status, confidence, latency, root cause, recommended action, selected evidence IDs, and persisted run ID.

The playground intentionally does not introduce a separate inference path. It is a thin UI over the same investigation and evaluation services used by the rest of the application, which keeps playground results comparable with history, evaluation, and reports.
