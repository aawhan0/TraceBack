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
- **Custom scenario authoring** with persisted ground truth and evidence
- **Model Playground** for interactive baseline vs. Ollama investigation runs
- **Local-first inference** using Ollama
- **Provider-agnostic LLM boundary** so inference can be replaced without redesigning the system
- **FastAPI backend** for exposing the system as a real service
- **Next.js dashboard** for interactive investigation, experiments, and run history
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

See [docs/architecture.md](docs/architecture.md) for the architecture notes.

## Current Scenarios

Traceback ships with a small set of practical production-style failures:

- **Database pool exhaustion**
- **Redis connectivity failure**
- **Runaway worker CPU saturation**

The dashboard can also create **custom scenarios** with a persisted incident description, expected root cause, causal keywords, and evidence set. Custom scenarios immediately become available to investigation and benchmarking through the same scenario catalog.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Language | Python 3.12+ |
| API | FastAPI |
| Frontend | Next.js 15, React 19, TypeScript |
| Charts / UI | Recharts, Tailwind CSS, shadcn-style primitives |
| Agent/tool protocol | MCP |
| LLM inference | Ollama |
| Data validation | Pydantic |
| Persistence | SQLite |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Containers | Docker / Docker Compose |

## Run Locally

Traceback uses Python 3.12+ for the backend and Node.js 22 for the Next.js frontend container.

### 1. Create the Python environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. Run the backend test suite

```powershell
python -m pytest
```

The verification suite covers the API, investigation flow, evaluation, persistence, jobs, security hardening, Docker definitions, and related behavior.

### 3. Run the full stack with Docker Compose

```powershell
docker compose up --build -d
```

Open the dashboard at:

- Dashboard: `http://127.0.0.1:3000`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

The Next.js frontend proxies `/api/*` requests to the FastAPI service, keeping browser requests same-origin while the application remains split into frontend and backend containers.

Stop Compose:

```powershell
docker compose down
```

### 4. Run the frontend outside Docker

```powershell
cd frontend
npm install
npm run typecheck
npm run build
npm run dev
```

Then open `http://127.0.0.1:3000`.

### 5. Run a baseline investigation

```powershell
traceback investigate database-pool-exhaustion
```

Baseline investigation does not require an LLM runtime.

The dashboard's investigation, experiments, playground, and history views call the real backend contracts. Charts intentionally remain empty until corresponding real runs or experiments exist.

### 6. Try the Model Playground

Open **Playground** in the dashboard to select a built-in or custom scenario, choose an Ollama model, and compare a deterministic baseline run with an LLM-backed run. The result panel exposes the same diagnosis, evidence, evaluation outcome, latency, and run ID used elsewhere in Traceback.

## Custom scenarios

Use the **Scenarios** view in the dashboard to author a reusable incident case. Each custom scenario stores:

- a stable scenario ID and incident title
- a production-style incident description
- the expected root cause
- causal keywords used by deterministic evaluation
- one or more evidence items with source, kind, ID, and content
- optional required evidence IDs for recall evaluation

Custom scenarios are persisted in the same SQLite database as the rest of Traceback. They are returned by `GET /scenarios`, can be investigated through `POST /investigations`, and can participate in experiments and matrices without changing the investigation engine.

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
- `POST /scenarios`
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

Completed investigations, experiments, and custom scenarios are persisted locally in SQLite. Traceback also exposes lightweight operational telemetry, readiness checks, request correlation, and durable job state.

The current deployment boundary is intentionally single-node and local-first. SQLite state can be mounted into `/data` when using the production container.

## Docker

Build the backend production image:

```powershell
docker build -t traceback:local .
```

Or use the complete stack:

```powershell
docker compose up --build -d
```

Compose exposes the backend on `8000` and the frontend on `3000`, persists SQLite state through the `traceback-data` named volume, and uses application health endpoints for container healthchecks.

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
│   ├── api/               # FastAPI routes and web/API integration
│   ├── evaluation/        # metrics, regression, comparison, benchmarking
│   ├── mcp/               # MCP evidence server
│   ├── models/            # domain contracts
│   ├── observability/     # telemetry and metrics
│   ├── providers/         # LLM providers
│   ├── repository/        # SQLite persistence
│   ├── scenarios/         # built-in and persisted incident scenarios
│   ├── services/          # application orchestration
│   └── tools/             # constrained investigation tools
├── frontend/              # Next.js investigation dashboard
├── docs/                  # architecture and operational contracts
├── tests/                 # automated behavior tests
├── Dockerfile             # backend image
├── compose.yaml           # backend + frontend stack
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

The backend, evaluation system, persistence, runtime/job layer, Docker setup, CI/security hardening, custom scenario authoring, and functional Next.js web UI are implemented. The project is now in final local validation and portfolio-polish mode.

## Author

### Aawhan Vyas

AI engineering, backend systems, full-stack development, and practical ML infrastructure.

- GitHub: [aawhan0](https://github.com/aawhan0)

## Security

See [SECURITY.md](SECURITY.md) for the security policy and responsible disclosure process.
