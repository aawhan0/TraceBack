# Investigation Flow

Traceback now has a deterministic end-to-end control path that does not require an LLM.

```text
Client
  |
  v
FastAPI
  |
  v
Investigation Service
  |
  +-- Scenario evidence tool
  |      +-- list
  |      +-- get
  |      +-- search
  |
  v
Baseline Investigator
  |
  v
Structured Diagnosis
  |
  v
Deterministic Evaluator
  |
  v
API response
```

## Tool boundary

ScenarioEvidenceTool exposes scenario evidence through a constrained request/response interface. It supports list, get, and search operations.

The conceptual interface can later be backed by real MCP servers without forcing the evaluator or API to know how evidence was retrieved.

## Baseline investigator

BaselineInvestigator is a deterministic reference implementation. It validates the incident, retrieves evidence through the tool boundary, checks root-cause keywords against evidence, and creates a structured diagnosis.

It is not the final LLM agent. It is a control implementation for testing the rest of the system before model inference is introduced.

## API

- GET /scenarios — list scenario IDs and incident titles.
- GET /scenarios/{scenario_id} — inspect a scenario and its evidence.
- POST /investigations — run the deterministic investigation baseline.

Example request:

```json
{"scenario_id": "database-pool-exhaustion"}
```

## Why the baseline first?

A model should not become the hidden dependency for every test. The deterministic baseline gives future investigators a known control path and keeps infrastructure failures separate from model failures.
