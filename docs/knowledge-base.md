# Incident Knowledge Base

TraceBack includes a lightweight incident knowledge base built directly from the scenario catalog rather than a second source of truth.

## What it stores

Each knowledge entry exposes:

- incident title and description
- deterministic expected root cause
- evidence-item count
- required evidence IDs
- latest persisted investigation run, when available
- latest run pass/fail state and confidence

Custom scenarios created in the dashboard appear automatically because the knowledge endpoint reads the same scenario catalog used by investigations and experiments.

## Search

The backend exposes:

```text
GET /knowledge?q=<query>&limit=<1-50>
```

Search is deterministic and bounded. It checks scenario IDs, incident text, root-cause expectations, causal keywords, evidence sources, evidence kinds, and evidence content. Results report which query terms matched.

This is intentionally not an LLM-generated knowledge layer. The purpose is to make previously defined incident knowledge discoverable without creating another evaluation or retrieval system.

## Dashboard

Open **Knowledge Base** in the dashboard to search known failure patterns and inspect the latest evaluation state associated with each scenario.
