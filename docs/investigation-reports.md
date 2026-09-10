# Investigation Report Export

The Reports view exports a persisted TraceBack investigation without re-running the investigation.

## Formats

- **Markdown** — human-readable incident report containing run metadata, diagnosis, recommended action, evidence IDs, and the five evaluation dimensions.
- **JSON** — the persisted run payload for downstream tooling or archival.

Reports are generated in the browser from data returned by `GET /runs` and `GET /runs/{run_id}`. The export does not change stored run data.
