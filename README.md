# TraceBack

> **Local-first LLM incident investigation and evaluation system for production-style failures.**

TraceBack is an engineering-focused system for investigating software incidents with explicit evidence, structured diagnoses, MCP tools, and deterministic evaluation.

Given an incident, TraceBack gathers operational evidence, produces a structured diagnosis, records the evidence used, recommends a remediation action, and evaluates the result against scenario-defined ground truth.

The core idea is simple: **an LLM can generate a convincing answer without being correct, so diagnosis quality should be measurable.**

---

## Why TraceBack?

Incident investigation is a useful test case for agent reliability because the model must do more than produce prose. It needs to gather the right evidence, connect that evidence to a plausible cause, and produce an actionable result.

TraceBack separates four concerns:

| Concern | Responsibility |
| --- | --- |
| **Investigation** | Gather operational evidence through explicit tools |
| **Diagnosis** | Produce a structured root cause, evidence references, confidence, and action |
| **Grounding** | Make the evidence supporting the diagnosis explicit |
| **Evaluation** | Measure the diagnosis against deterministic scenario expectations |

This keeps the project focused on measurable agent behavior rather than chatbot-style demonstrations.

## Highlights

- Tool-based incident investigation through **MCP**
- Structured diagnosis validation with **Pydantic**
- Explicit evidence IDs for diagnosis grounding
- Deterministic root-cause evaluation
- Evidence recall and precision metrics
- Confidence validity and recommended-action checks
- Persisted investigation history in SQLite
- Repeatable benchmark experiments and regression gates
- Baseline vs. Ollama model investigations
- Experiment comparison and multi-configuration matrices
- Custom incident scenario authoring
- Operator-configured remote MCP evidence sources
- Model Playground for interactive runs
- Deterministic Incident Knowledge Base
- FastAPI backend + Next.js dashboard
- Docker Compose local deployment
- GitHub Actions CI, CodeQL, dependency review, container scanning, SBOMs, and release automation

---

## Architecture

```text
Incident
   │
   ▼
Investigation Service
   │
   ├── Deterministic baseline
   │
   └── LLM investigator ──► Provider / Ollama
                              │
                              ▼
                         MCP / tools
                              │
                              ▼
                      Operational evidence
                              │
                              ▼
                      Structured diagnosis
                              │
                              ▼
                  Deterministic evaluator
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
               Persisted run       Benchmarks
                    │                   │
                    └─────────┬─────────┘
                              ▼
                         Web dashboard
```

The important engineering boundary is between **generation and evaluation**: the investigator proposes the diagnosis; deterministic code measures whether it satisfies the scenario contract.

See [docs/architecture.md](docs/architecture.md) for the detailed design.

---

## Scenarios

TraceBack includes production-style failure scenarios such as:

- **Database pool exhaustion**
- **Redis connectivity failure**
- **Runaway worker CPU saturation**

The dashboard can also create custom scenarios containing an incident description, expected root cause, causal keywords, and evidence. Custom scenarios use the same investigation, evaluation, experiment, and knowledge-base paths as built-in scenarios.

---

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Language | Python 3.12+ |
| Backend | FastAPI |
| Frontend | Next.js 15, React 19, TypeScript |
| UI | Tailwind CSS, Recharts, shadcn-style primitives |
| Agent / tool protocol | MCP |
| LLM inference | Ollama |
| Validation | Pydantic |
| Persistence | SQLite |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Containers | Docker / Docker Compose |
| Package / CLI | PyPI: `trbk` |

---

## Quick Start

### Docker Compose

```powershell
git clone https://github.com/aawhan0/TraceBack.git
cd TraceBack
docker compose up --build -d
```

Open:

- Dashboard: http://127.0.0.1:3000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Stop the stack:

```powershell
docker compose down
```

### Python development

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m pytest
```

### Frontend development

```powershell
cd frontend
npm install
npm run typecheck
npm run build
npm run dev
```

---

## PyPI / CLI

TraceBack is distributed as the `trbk` Python package and exposes the `trbk` command-line interface.

```powershell
python -m pip install trbk
trbk --help
trbk scenarios
```

The product is branded **TraceBack**; `trbk` is the Python distribution and executable name.

### Investigate an incident

Deterministic baseline:

```powershell
trbk investigate database-pool-exhaustion
```

Ollama-backed investigation:

```powershell
trbk investigate database-pool-exhaustion --mode llm --model llama3.2
```

---

## Dashboard

The Next.js dashboard exposes the real application surface rather than mocked screens:

- **Investigate** — run baseline or LLM investigations and inspect diagnosis/evidence
- **Experiments** — create and inspect repeatable benchmark runs
- **Compare** — compare saved experiments
- **Evaluation** — inspect per-run evaluator dimensions
- **Reports** — export persisted runs as Markdown or JSON
- **Scenarios** — author custom incident cases
- **Playground** — interactively run scenarios against baseline or Ollama
- **History** — inspect persisted investigations
- **Knowledge Base** — search known incident patterns and latest run state
- **Documentation** — browse CLI and project guidance
- **Settings** — configure dashboard theme and inspect API health

---

## Evaluation

Each investigation is checked against deterministic scenario expectations.

| Metric | Measures |
| --- | --- |
| Root-cause match | Required causal keywords are present |
| Evidence recall | Required evidence selected by the diagnosis |
| Evidence precision | Selected evidence belongs to the scenario |
| Confidence validity | Confidence is within the valid range |
| Action present | A non-empty remediation action exists |
| Pass/fail | All required acceptance checks are satisfied |

Recall and precision are treated as fully satisfied at 100% for the overall pass decision.

The benchmark workflow adds repeated runs, pass rates, confidence and latency statistics, Wilson pass-rate intervals, regression gates, experiment provenance, experiment comparison, and configuration matrices.

Typical commands:

```powershell
trbk benchmark --mode baseline --repetitions 3 --name baseline-smoke
trbk benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
trbk compare <baseline-experiment-id> <candidate-experiment-id>
trbk matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --repetitions 3
```

The intended workflow is:

**run → persist provenance → compare → identify regressions or improvements**

---

## Custom MCP Evidence Sources

TraceBack supports operator-configured remote MCP evidence sources through `TRACEBACK_MCP_EVIDENCE_SOURCES`.

The integration uses a constrained structured evidence contract and preserves external-source attribution.

See [docs/mcp-evidence-sources.md](docs/mcp-evidence-sources.md) for configuration and the expected tool contract.

---

## Knowledge Base

The Knowledge Base provides deterministic search over the same incident scenario catalog used by investigations.

```text
GET /knowledge?q=<query>&limit=<1-50>
```

Results expose reusable incident patterns, expected root cause, evidence requirements, and latest persisted evaluation state.

---

## API

Core API endpoints include:

```text
GET  /health
GET  /scenarios
POST /scenarios
GET  /scenarios/{scenario_id}
POST /investigations
GET  /runs
GET  /runs/{run_id}
GET  /runs/stats
POST /experiments
GET  /experiments
GET  /experiments/{experiment_id}
GET  /experiments/{baseline_id}/compare/{candidate_id}
POST /experiments/matrix
GET  /knowledge?q=<query>&limit=<1-50>
POST /jobs
GET  /jobs
GET  /jobs/{job_id}
GET  /ops/ready
GET  /ops/database
```

FastAPI's generated documentation is available at `/docs`.

---

## MCP Development

Launch the local evidence server:

```powershell
python -m app.mcp.server
```

For MCP Inspector:

```powershell
mcp dev app/mcp/server.py
```

---

## Persistence and Operations

Completed investigations, experiments, and custom scenarios are persisted in SQLite.

TraceBack also exposes lightweight request correlation, runtime telemetry, readiness checks, and durable job state.

The current deployment boundary is intentionally **single-node and local-first**. Docker Compose keeps SQLite data outside the backend image by mounting persistent state at `/data`.

---

## Project Structure

```text
TraceBack/
├── .github/workflows/     # CI, security, dependency and release workflows
├── app/
│   ├── agent/             # investigators, runtime and provider boundary
│   ├── api/               # FastAPI routes
│   ├── evaluation/        # metrics, regression and benchmarking
│   ├── mcp/               # MCP server and external-source integration
│   ├── models/             # domain contracts
│   ├── observability/     # telemetry and runtime events
│   ├── providers/         # LLM providers
│   ├── repository/        # SQLite persistence
│   ├── scenarios/         # built-in scenario definitions
│   ├── services/          # application orchestration
│   └── tools/             # constrained investigation tools
├── frontend/              # Next.js dashboard
├── docs/                  # architecture and operational documentation
├── tests/                 # automated tests
├── Dockerfile             # backend production image
├── compose.yaml           # backend + frontend stack
├── pyproject.toml
└── README.md
```

---

## CI, Security, and Release Engineering

The repository includes automation for:

- Python verification and tests
- dependency review
- CodeQL analysis
- container vulnerability scanning with Trivy
- SPDX SBOM generation
- container release workflows
- build provenance / artifact attestation
- Dependabot updates

The production container runs as a non-root user and persists SQLite state separately from the image.

See [SECURITY.md](SECURITY.md) for the security policy.

---

## Engineering Principles

- **Measure before claiming.** Portfolio metrics should come from real evaluation runs.
- **Keep evaluation deterministic.** Do not use an LLM as the final judge of another LLM.
- **Ground diagnoses in evidence.** Root cause alone is not enough.
- **Keep tools real.** MCP integrations should represent actual investigation capabilities.
- **Keep inference replaceable.** Ollama is an implementation choice behind the provider boundary.
- **Test behavior, not test count.** Protect real contracts and edge cases.
- **Do not build fake UI.** Interactive screens should connect to actual backend behavior.
- **Stay portfolio-sized.** Demonstrate engineering depth without becoming a monitoring platform.

---

## Portfolio Positioning

TraceBack is intended to demonstrate a different engineering slice from the rest of the portfolio:

- **Dasaiko** — RAG and retrieval engineering
- **ModelDock** — ML infrastructure and model serving
- **TraceBack** — LLM agents, MCP, evaluation, and reliability

---

## Status

**Complete / portfolio-ready.**

The investigation engine, deterministic evaluation, persistence, benchmarking, Docker deployment, CI/security hardening, custom scenario authoring, Model Playground, custom MCP evidence sources, Incident Knowledge Base, dashboard, and PyPI/CLI distribution are implemented and locally validated.

---

## Author

### Aawhan Vyas

AI engineering, backend systems, full-stack development, and practical ML infrastructure.

- GitHub: [aawhan0](https://github.com/aawhan0)

## Security

See [SECURITY.md](SECURITY.md) for the security policy and responsible disclosure process.
