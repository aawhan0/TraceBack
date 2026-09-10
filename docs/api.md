# API Reference

TraceBack exposes a small FastAPI surface shared by the web dashboard and CLI workflows.

## Core endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| GET | `/health/ready` | Dependency readiness |
| GET | `/scenarios` | List built-in and persisted scenarios |
| POST | `/scenarios` | Create a custom scenario |
| GET | `/scenarios/{scenario_id}` | Inspect one scenario |
| POST | `/investigations` | Run an investigation in baseline or LLM mode |
| GET | `/runs` | List persisted investigation runs |
| GET | `/runs/{run_id}` | Inspect one persisted run |
| GET | `/runs/stats` | Aggregate run statistics |
| POST | `/experiments` | Execute a repeatable benchmark experiment |
| GET | `/experiments` | List persisted experiments |
| GET | `/experiments/{experiment_id}` | Inspect one experiment |
| GET | `/experiments/{baseline_id}/compare/{candidate_id}` | Compare compatible experiments |
| POST | `/experiments/matrix` | Execute a multi-configuration benchmark matrix |
| GET | `/knowledge` | Search the deterministic incident knowledge base |
| POST | `/jobs` | Create a persisted job |
| GET | `/jobs` | List jobs |
| GET | `/jobs/{job_id}` | Inspect one job |
| GET | `/ops/ready` | Operational readiness details |
| GET | `/ops/database` | Database/runtime information |

FastAPI generates the complete OpenAPI documentation at `/docs` when the service is running.

## Run an investigation

The investigation endpoint accepts a scenario ID and can select either the deterministic baseline or an LLM-backed investigator.

Baseline example:

```bash
curl -X POST http://127.0.0.1:8000/investigations \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"database-pool-exhaustion","mode":"baseline"}'
```

LLM example:

```bash
curl -X POST http://127.0.0.1:8000/investigations \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"database-pool-exhaustion","mode":"llm","model":"llama3.2"}'
```

The resulting diagnosis, evaluation outcome, runtime information, and trace data are persisted through the normal investigation path.

## Custom scenarios

Create a scenario through `POST /scenarios` with the same ground-truth concepts used by built-in scenarios: incident description, expected root cause, causal keywords, evidence, and optional required evidence IDs.

The new scenario enters the shared catalog and becomes available to investigation, benchmarking, and Knowledge Base workflows.

## Experiments

Create a repeatable benchmark:

```bash
curl -X POST http://127.0.0.1:8000/experiments \
  -H 'Content-Type: application/json' \
  -d '{"name":"baseline-smoke","scenario_ids":["database-pool-exhaustion","redis-connectivity-failure"],"repetitions":3,"mode":"baseline"}'
```

The experiment result includes aggregate evaluation metrics and persisted provenance. Compatible experiments can later be compared through the comparison endpoint.

## Knowledge Base

Search reusable incident patterns:

```text
GET /knowledge?q=database&limit=10
```

Results are deterministic and come from the same scenario catalog used by investigations, including persisted custom scenarios.

## Operational endpoints

Use `/health` for lightweight liveness checks and `/health/ready` when deployment tooling needs dependency readiness. `/ops/database` exposes database/runtime information intended for local and operational inspection.

## API documentation

When the backend is running locally, open:

```text
http://127.0.0.1:8000/docs
```

The generated OpenAPI document is the authoritative reference for request and response schemas.
