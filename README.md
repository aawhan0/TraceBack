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
- **Backend-driven web dashboard** at `/ui`

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

See [docs/architecture.md](docs/architecture.md) for the architecture notes.

## Current Scenarios

Traceback currently focuses on a small set of practical production-style failures:

- **Database pool exhaustion**
- **Redis connectivity failure**
- **Runaway worker CPU saturation**

The scenarios are intentionally limited. More scenarios should be added only when they demonstrate meaningful generality or expose a real weakness in the system.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Language | Python 3.12+ |
| API | FastAPI |
| Agent/tool protocol | MCP |
| LLM inference | Ollama |
| Data validation | Pydantic |
| Persistence | SQLite |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Containers | Docker / Docker Compose |

## Run Locally

Traceback uses Python 3.12+.

### 1. Create the environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. Run the test suite

```powershell
python -m pytest
```

The local verification suite currently covers the API, dashboard, investigation flow, evaluation, persistence, jobs, security hardening, Docker definitions, and related behavior.

### 3. Start the API

```powershell
uvicorn app.main:app --reload
```

Then open:

- Dashboard: `http://127.0.0.1:8000/ui`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

### 4. Run a baseline investigation

```powershell
traceback investigate database-pool-exhaustion
```

Baseline investigation does not require an LLM runtime.

### 5. Use the web dashboard

The `/ui` dashboard is backed by the real API and supports:

- single incident investigations
- repeatable benchmarks
- multi-configuration experiment matrices
- persisted experiment history
- experiment comparison
- recent job and investigation-run views

No UI action is mocked; it calls the existing backend contracts.

## LLM development

LLM mode uses Ollama by default and reads:

- `TRACEBACK_MODEL`
- `OLLAMA_BASE_URL`
- `TRACEBACK_OLLAMA_TIMEOUT`

Example:

```powershell
traceback investigate database-pool-exhaustion --mode llm --model llama3.2
```

The LLM path and deterministic baseline share the same diagnosis contract and evaluator.

## MCP development

The evidence server can be launched locally with:

```powershell
python -m app.mcp.server
```

For MCP Inspector development:

```powershell
mcp dev app/mcp/server.py
```

The MCP server exposes scenario evidence through a constrained tool boundary.

## Evaluation and benchmarking

For each investigation, Traceback evaluates:

| Metric | What it measures |
| --- | --- |
| Root-cause match | Whether the diagnosis contains the required causal keywords |
| Evidence recall | How much required evidence was selected |
| Evidence precision | How much selected evidence is valid for the scenario |
| Confidence | Whether the reported confidence is valid and observable |
| Action present | Whether a recommended action was produced |
| Pass/fail | Whether the diagnosis satisfies the scenario's acceptance criteria |

A run passes when the current scenario rules are satisfied.

Benchmarking adds:

- repeated runs
- pass rates
- confidence statistics
- latency statistics
- Wilson pass-rate intervals
- regression gates
- persisted experiment provenance
- experiment comparison
- multi-configuration matrices

Typical commands:

```powershell
traceback benchmark --mode baseline --repetitions 3 --name baseline-smoke
traceback benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
traceback compare <baseline-experiment-id> <candidate-experiment-id>
traceback matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --repetitions 3
```

This makes the workflow a measurable loop:

**run → persist provenance → compare → identify regressions/improvements**

## API

Core endpoints include:

- `GET /health`
- `GET /scenarios`
- `GET /scenarios/{scenario_id}`
- `POST /investigations`
- `GET /runs`
- `GET /runs/{run_id}`
- `GET /runs/stats`
- `POST /experiments`
- `GET /experiments`
- `GET /experiments/{experiment_id}`
- `GET /experiments/{baseline_id}/compare/{candidate_id}`
- `POST /experiments/matrix`
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `GET /ops/ready`
- `GET /ops/database`

FastAPI's generated documentation is available at `/docs`.

## CLI

After installation, the `traceback` command provides:

```text
traceback scenarios
traceback investigate <scenario-id>
traceback runs --scenario-id <scenario-id>
traceback show <run-id>
traceback stats --scenario-id <scenario-id>
traceback benchmark --repetitions 3 --name baseline-smoke
traceback experiments --limit 20
traceback experiment <experiment-id>
traceback compare <baseline-id> <candidate-id>
traceback matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2
```

## Persistence and operations

Completed investigations and experiments are persisted locally in SQLite. Traceback also exposes lightweight operational telemetry, readiness checks, request correlation, and durable job state.

The current deployment boundary is intentionally single-node and local-first. SQLite state can be mounted into `/data` when using the production container.

## Docker

Build the production image:

```powershell
docker build -t traceback:local .
```

Run it:

```powershell
docker run --rm -p 8000:8000 -v traceback-data:/data traceback:local
```

Or use Compose:

```powershell
docker compose up --build -d
```

Compose exposes port `8000`, persists SQLite state through the `traceback-data` named volume, and uses the application's health endpoint for the container healthcheck.

Stop Compose:

```powershell
docker compose down
```

See [docs/deployment.md](docs/deployment.md) for the deployment contract and configuration details.

## CI, security, and release engineering

Traceback includes GitHub Actions workflows for:

- Python/static verification and tests
- dependency review
- CodeQL analysis
- container vulnerability scanning with Trivy
- SPDX SBOM generation
- container releases
- build provenance / artifact attestation
- dependency maintenance via Dependabot

The repository also uses a non-root production container and keeps database state separate from the image.

See [SECURITY.md](SECURITY.md) and the documents under `docs/` for the detailed boundaries.

## Project structure

```text
Traceback/
├── .github/workflows/     # CI, security, dependency and release workflows
├── app/
│   ├── agent/             # investigators, LLM/provider boundary, runtime
│   ├── api/               # FastAPI routes and web dashboard
│   ├── evaluation/        # metrics, regression, comparison, benchmarking
│   ├── mcp/               # MCP evidence server
│   ├── models/            # domain contracts
│   ├── observability/     # telemetry and metrics
│   ├── providers/         # LLM providers
│   ├── repository/        # SQLite persistence
│   ├── scenarios/         # version-controlled incident scenarios
│   ├── services/          # application orchestration
│   └── tools/             # constrained investigation tools
├── docs/                  # architecture and operational contracts
├── tests/                 # automated behavior tests
├── Dockerfile
├── compose.yaml
├── pyproject.toml
└── README.md
```

## Engineering principles

- **Measure before claiming.** Resume metrics should come from actual evaluation runs.
- **Keep the evaluator deterministic.** Do not use an LLM to judge whether an LLM was correct.
- **Ground diagnoses in evidence.** A root cause without supporting evidence is not enough.
- **Keep tools real.** MCP integrations should represent actual investigation capabilities.
- **Prefer small abstractions.** Introduce infrastructure only when it solves a real problem.
- **Keep inference replaceable.** Ollama is an implementation choice, not the application's core abstraction.
- **Test behavior, not test count.** Tests should protect meaningful behavior and edge cases.
- **Do not build fake UI.** Every interactive capability should connect to real backend functionality.
- **Stay portfolio-sized.** Traceback should demonstrate engineering depth without becoming an observability platform.

## Project positioning

Traceback complements rather than duplicates the rest of the portfolio:

- **Dasaiko** — RAG and retrieval engineering
- **ModelDock** — ML infrastructure and model serving
- **Traceback** — LLM agents, MCP, evaluation, and reliability

## Status

The backend, evaluation system, persistence, runtime/job layer, Docker setup, CI/security hardening, and functional web UI are implemented. The current phase is local end-to-end validation and final portfolio polish.

## Author

### Aawhan Vyas

AI engineering, backend systems, full-stack development, and practical ML infrastructure.

- GitHub: [aawhan0](https://github.com/aawhan0)

## Security

See [SECURITY.md](SECURITY.md) for the security policy and responsible disclosure process.
