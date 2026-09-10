# Custom scenarios

TraceBack supports user-authored incident scenarios in addition to the built-in catalog.

## What a scenario contains

A custom scenario defines:

- a stable slug-style scenario ID
- an incident title and description
- an expected root cause
- causal keywords for deterministic root-cause matching
- one or more evidence records
- optional required evidence IDs for recall evaluation

Evidence records keep the same structure used by built-in scenarios: ID, source, kind, and content.

## Persistence

Custom scenarios are stored in the configured SQLite database in the `custom_scenarios` table. The built-in catalog remains version-controlled in Python, while custom records are loaded dynamically from SQLite.

This means a scenario created through the dashboard survives backend restarts and is available through the same investigation path as built-in cases.

## API

Create a scenario with `POST /scenarios`:

```json
{
  "id": "payment-timeout",
  "title": "Payment API timeout spike",
  "description": "Checkout requests time out while payment calls are retried.",
  "expected_root_cause": "Payment gateway timeout retry storm",
  "root_cause_keywords": ["payment", "gateway", "retry"],
  "evidence": [
    {
      "id": "ev-payment-001",
      "source": "api",
      "kind": "logs",
      "content": "payment-service: gateway timeout"
    }
  ],
  "required_evidence_ids": ["ev-payment-001"]
}
```

Scenario IDs must use lowercase letters, numbers, and hyphens. Evidence IDs must be unique within a scenario, and every required evidence ID must refer to an evidence item in that scenario.

`GET /scenarios` returns built-in and custom scenarios together. `GET /scenarios/{scenario_id}` returns the complete definition. Once created, the same ID can be supplied to `POST /investigations` and to experiment or matrix requests.

## Design boundary

Custom scenarios do not introduce a second investigation implementation. They feed the existing `IncidentScenario` contract, MCP evidence tool, deterministic evaluator, and benchmarking services. This keeps scenario authoring separate from the investigation engine while preserving identical evaluation semantics.
