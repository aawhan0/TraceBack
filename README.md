# Traceback

> **Local-first LLM incident diagnosis and evaluation system for investigating production-like failures with MCP tools, structured evidence, and deterministic evaluation.**

Traceback is an engineering-focused portfolio project for exploring how LLMs can investigate software incidents without treating generated answers as automatically correct.

Given a production-like incident, Traceback gathers operational evidence through tools, produces a structured diagnosis, identifies the likely root cause, cites the evidence used, recommends an action, and evaluates the result against deterministic ground truth.

The goal is not to build another chatbot or a Datadog/PagerDuty competitor. The goal is to build a small, testable system that makes **LLM incident diagnosis measurable**.

## Why Traceback?

LLM-based incident investigation is easy to demonstrate and hard to evaluate.

A model can produce a convincing explanation while selecting irrelevant evidence or identifying the wrong cause. Traceback therefore separates:

- **Investigation** — what evidence the agent can gather.
- **Diagnosis** — what the model believes happened.
- **Grounding** — which evidence supports that diagnosis.
- **Evaluation** — whether the diagnosis matches deterministic expectations.

This makes model behavior measurable rather than purely subjective.

## Highlights

- **Tool-based incident investigation** through MCP
- **Structured diagnosis outputs** validated with Pydantic
- **Evidence grounding** through explicit evidence IDs
- **Deterministic evaluation** against scenario ground truth
- **Root-cause matching** using scenario-defined causal keywords
- **Evidence recall and precision** metrics
- **Repeated evaluation runs** for measuring model reliability
- **Aggregate reports** for comparing model/configuration behavior
- **Repeatable experiments** across scenarios and repetitions
- **Regression gates** for protecting measured investigation quality
- **Local-first inference** using Ollama
- **Provider-agnostic LLM boundary** so inference can be replaced without redesigning the system
- **FastAPI backend** for exposing the system as a real service
- **Pytest coverage** for agent, tool, model, evaluation, and reporting behavior
- **GitHub Actions CI** for automated verification

## Architecture

At a high level, Traceback follows this flow:

```text
Incident
   │
   ▼
Investigation Agent
   │
   ├── MCP tools ──► Operational Evidence
   │                       │
   └───────────────────────┘
               │
               ▼
       Structured Diagnosis
               │
               ├── Root cause
               ├── Evidence IDs
               ├── Confidence
               └── Recommended action
               │
               ▼
       Deterministic Evaluator
               │
               ├── Root-cause match
               ├── Evidence recall
               ├── Evidence precision
               ├── Confidence validity
               └── Action presence
               │
               ▼
         Evaluation Report
```

The important boundary is between **generation** and **evaluation**: the LLM proposes a diagnosis, while deterministic code decides whether that diagnosis satisfies the scenario's measurable criteria.

See [docs/architecture.md](docs/architecture.md) for the initial architecture notes.

## Core Domain

### Incident

Represents the software problem being investigated.

Typical fields include:

- `id`
- `title`
- `description`
- `status`
- `created_at`

### Evidence

Represents operational information available during investigation.

Typical fields include:

- `id`
- `source`
- `kind`
- `content`
- `timestamp`
- `relevance`

### Diagnosis

Represents the structured output produced by the agent:

- `incident_id`
- `root_cause`
- `evidence_ids`
- `confidence`
- `recommended_action`

### IncidentScenario

Defines deterministic ground truth used for evaluation:

- incident
- available evidence
- expected root cause
- root-cause keywords
- required evidence IDs

## Evaluation

Evaluation is a first-class part of Traceback.

For a scenario, the evaluator checks:

| Metric | What it measures |
| --- | --- |
| Root-cause match | Whether the diagnosis contains the required causal keywords |
| Evidence recall | How much required evidence was selected |
| Evidence precision | How much selected evidence is valid for the scenario |
| Confidence | Whether the reported confidence is valid and observable |
| Action present | Whether a recommended action was produced |
| Pass/fail | Whether the diagnosis satisfies the scenario's acceptance criteria |

A run passes when the current scenario rules are satisfied:

- root cause matches
- required evidence recall is 100%
- evidence precision is 100%
- a recommended action exists
- confidence is between 0 and 1

Aggregate evaluation can then summarize repeated runs using:

- total runs
- passed runs
- pass rate
- root-cause accuracy
- evidence recall
- evidence precision
- average confidence

This is intentionally deterministic. The evaluator should not ask another LLM whether the first LLM was correct.

## Current Scenarios

Traceback currently focuses on a small set of practical production-style failures:

- **Database pool exhaustion**
- **Redis connectivity failure**
- **Runaway worker CPU saturation**

The scenarios are intentionally limited. More scenarios should be added only when they demonstrate meaningful generality or expose a real weakness in the system.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Language | Python |
| API | FastAPI |
| Agent/tool protocol | MCP |
| LLM inference | Ollama |
| Data validation | Pydantic |
| Testing | Pytest |
| CI | GitHub Actions |

Ollama is the current local inference implementation, but the application should keep the LLM provider boundary replaceable.

## Run Locally

The project is currently being built incrementally. The exact application setup will be documented here as the runtime structure stabilizes.

For development, the intended stack is:

```text
Python + FastAPI
MCP tools
Ollama
Pytest
```

Once the application entrypoint and dependency files are finalized, this section will become the canonical copy-paste setup guide.

## Verification

The repository includes GitHub Actions CI.

The current CI checks include:

- repository hygiene
- GitHub Actions workflow validation
- Python dependency consistency
- Ruff static analysis
- Python compilation
- pytest
- coverage and test-result artifacts

The CI is deliberately being tightened as real project capabilities are added. Checks should represent actual project behavior rather than exist simply to increase the apparent complexity of the pipeline.

## Project Structure

The target structure is intentionally small and will evolve with the implementation:

```text
Traceback/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── architecture.md
├── app/
│   ├── api/
│   ├── agent/
│   ├── evaluation/
│   ├── models/
│   ├── tools/
│   └── ...
├── tests/
└── README.md
```

The structure above is a design direction, not a claim that every directory already exists.

## Engineering Principles

Traceback follows a few practical rules:

- **Measure before claiming.** Resume metrics should come from actual evaluation runs.
- **Keep the evaluator deterministic.** Do not use an LLM to judge whether an LLM was correct.
- **Ground diagnoses in evidence.** A root cause without supporting evidence is not enough.
- **Keep tools real.** MCP integrations should represent actual investigation capabilities.
- **Prefer small abstractions.** Introduce infrastructure only when it solves a real problem.
- **Keep inference replaceable.** Ollama is an implementation choice, not the application's core abstraction.
- **Test behavior, not test count.** Tests should protect meaningful behavior and edge cases.
- **Do not build fake UI.** Every interactive capability should connect to real backend functionality.
- **Stay portfolio-sized.** Traceback should demonstrate engineering depth without becoming an observability platform.

## Relationship to Other Projects

Traceback is designed to complement, rather than duplicate, two other portfolio projects:

- **Dasaiko** — RAG and retrieval engineering
- **ModelDock** — ML infrastructure and model serving
- **Traceback** — LLM agents, MCP, evaluation, and reliability

## Roadmap

The current implementation priorities are:

1. Make the incident investigation flow reliable.
2. Make MCP/tool interactions real.
3. Harden structured diagnosis validation.
4. Make deterministic evaluation trustworthy.
5. Make evaluation reports useful.
6. Add only enough scenarios to demonstrate generality.
7. Build a minimal functional UI.
8. Expand meaningful test coverage.
9. Run real model/configuration evaluations.
10. Record actual quantitative results.
11. Polish documentation and portfolio presentation.

## What is actually implemented?

Traceback now has a working deterministic control path before any LLM dependency is introduced:

1. Select a version-controlled incident scenario.
2. Retrieve attributable evidence through a constrained investigation tool.
3. Produce a validated Diagnosis.
4. Evaluate root cause, evidence grounding, confidence, and action presence deterministically.
5. Expose the flow through FastAPI.
6. Aggregate repeated evaluations for future model experiments.

This is intentional. The first LLM investigator will be measured against a working baseline rather than being allowed to define what "working" means.

## API quick start

Start the service:

```bash
uvicorn app.main:app --reload
```

Useful endpoints:

- `GET /health`
- `GET /scenarios`
- `GET /scenarios/{scenario_id}`
- `POST /investigations`

Run a baseline investigation:

```bash
curl -X POST http://127.0.0.1:8000/investigations \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"database-pool-exhaustion"}'
```

The generated API documentation is available at `/docs`.

## Development boundary

The current baseline is deliberately not presented as an LLM agent. The important interfaces are already separated:

- **Investigator** — produces a structured diagnosis.
- **InvestigationTool** — provides attributable operational evidence.
- **Evaluator** — measures the diagnosis without changing it.
- **InvestigationService** — orchestrates the application flow.

The next implementation can replace the baseline investigator with an LLM-backed implementation and replace ScenarioEvidenceTool with real MCP-backed tools while preserving the evaluation contract.

## What is implemented now?

Traceback has moved beyond the deterministic foundation. The repository now contains:

- a deterministic baseline investigator
- an LLM investigator with a provider protocol
- a local Ollama provider
- strict JSON-to-Diagnosis parsing
- a real MCP evidence server using the official MCP Python SDK
- a constrained evidence tool with list/get/search operations
- per-run evaluation reports
- aggregate evaluation across scenarios
- experiment comparison deltas
- an API switch between baseline and LLM investigation modes

The model path and the baseline path share the same Diagnosis contract and deterministic evaluator. This makes future model comparisons meaningful rather than anecdotal.

#
## Investigation history

Every completed investigation now receives a stable run ID and is persisted locally in SQLite. This makes results inspectable after the original request and provides a foundation for regression tracking and model experiments.

### API

- `POST /investigations` — run and persist an investigation
- `POST /experiments` — run a repeatable multi-scenario experiment
- `GET /runs` — list recent runs, optionally filtered by scenario
- `GET /runs/{run_id}` — inspect a complete persisted run
- `GET /runs/stats` — aggregate historical pass rate, confidence, and latency

### CLI

After installing the project:

```bash
traceback scenarios
traceback investigate database-pool-exhaustion
traceback runs --scenario-id database-pool-exhaustion
traceback show <run-id>
traceback stats --scenario-id database-pool-exhaustion
traceback benchmark --repetitions 3 --name baseline-smoke
```

See [docs/runs.md](docs/runs.md) for the persistence contract and [docs/experiments.md](docs/experiments.md) for repeatable benchmarks and regression gates.

## MCP development

The evidence server can be launched locally with:

python -m app.mcp.server

For MCP Inspector development, use:

mcp dev app/mcp/server.py

The MCP server exposes get_incident_evidence and intentionally has access only to version-controlled scenario evidence.

### LLM development

Baseline investigation requires no model runtime.

LLM mode uses Ollama by default and reads:

- TRACEBACK_MODEL
- OLLAMA_BASE_URL
- TRACEBACK_OLLAMA_TIMEOUT

See docs/llm.md and docs/mcp.md for the detailed boundaries.

## Production operations

Traceback exposes lightweight operational telemetry without adding a vendor monitoring dependency. `GET /health/ready` reports dependency readiness, while `GET /health/metrics` exposes process-local counters and timing summaries in a Prometheus-compatible text shape. HTTP responses carry request correlation and response-time headers, and durable investigation jobs preserve a trace ID across their lifecycle. This keeps the core portable while leaving the telemetry sink replaceable for a production deployment.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and pull request guidance.

## Security

See [SECURITY.md](SECURITY.md) for the project's security policy.

## Author

### Aawhan Vyas

AI engineering, backend systems, full-stack development, and practical ML infrastructure.

- GitHub: [aawhan0](https://github.com/aawhan0)


## Benchmark platform

Traceback now includes a reproducible benchmark layer on top of investigations.

- Versioned dataset manifests with deterministic fingerprints
- Repeatable scenario execution
- Wilson pass-rate intervals and descriptive latency statistics
- Confidence calibration metrics
- Explicit regression policies
- Persisted experiment records
- Structured trace events and JSON logging
- Markdown benchmark reports
- CLI and HTTP interfaces for experiment execution and history

Typical workflow:

    traceback benchmark --repetitions 3 --min-pass-rate 1.0 --report

See [docs/benchmarking.md](docs/benchmarking.md) for the benchmark contract and [docs/observability.md](docs/observability.md) for tracing and structured logging.


## Reproducible model benchmarking

Benchmark runs are now explicitly attributable to the execution environment and investigator configuration. Each experiment can record its application version, Git revision, Python version, environment, provider, and model alongside the measured result.

The benchmark path supports both the deterministic baseline and the Ollama-backed investigator:

```bash
traceback benchmark --mode baseline --repetitions 3 --name baseline-smoke
traceback benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
```

This keeps model comparisons on the same scenario dataset, evaluator, regression policy, and persistence path instead of creating a separate evaluation implementation for LLM runs.


### Benchmark comparison

Persisted benchmark experiments can now be compared directly. Traceback validates dataset compatibility before calculating deltas, then reports overall and per-scenario quality changes together with provider/model identity.

```bash
traceback compare <baseline-experiment-id> <candidate-experiment-id>
traceback compare <baseline-experiment-id> <candidate-experiment-id> --report
```

This makes model evaluation a closed loop: **run → persist provenance → compare → identify regressions/improvements**.


### Multi-configuration experiment matrices

TraceBack can run several configurations against the same immutable dataset and persist each result as a normal experiment:

    traceback matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --config qwen=llm:qwen2.5 --repetitions 3

The first configuration is the comparison baseline. Each configuration receives the same dataset fingerprint, and the matrix returns the persisted experiment IDs plus the best-performing configuration. This keeps model evaluation reproducible while avoiding a separate benchmark implementation for every provider/model combination.

API clients can use POST /experiments/matrix; the frontend remains deferred until the backend contracts are complete.


## Container deployment

TraceBack includes a production-oriented Docker image for running the API as a non-root user with SQLite state mounted at `/data`. The container exposes port 8000 and includes a lightweight `/health` healthcheck.

```bash
docker build -t traceback:local .
docker run --rm -p 8000:8000 -v traceback-data:/data traceback:local
```

See [docs/deployment.md](docs/deployment.md) for configuration, persistence, health checks, and the current single-node deployment boundary.


For a repeatable local deployment, use Docker Compose:

```bash
docker compose up --build -d
```

The Compose deployment uses the production image and persists SQLite state in a named volume. See [docs/deployment.md](docs/deployment.md).
