# TraceBack Architecture

## Purpose

TraceBack investigates production-like software incidents using a deterministic baseline or an LLM investigator, gathers operational evidence through explicit tools, produces a structured diagnosis, and measures that diagnosis against deterministic scenario ground truth.

The architecture is intentionally small. The system demonstrates practical engineering around agents, MCP, structured outputs, evidence grounding, persistence, observability, and evaluation without becoming a full observability or incident-management platform.

## System flow

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

## Core boundaries

TraceBack keeps these responsibilities separate:

- **Investigation** gathers evidence and proposes a diagnosis.
- **Diagnosis** is a structured contract validated with Pydantic.
- **Evaluation** measures the diagnosis against scenario-defined expectations.
- **Persistence** stores completed runs, experiments, and custom scenarios.
- **Observability** records runtime events without changing the investigation result.
- **Benchmarking** coordinates repeated experiments and comparisons.
- **FastAPI** is the application-facing API; **MCP** is the tool protocol used by the investigation side.

The most important boundary is between **generation and evaluation**: the investigator proposes the diagnosis; deterministic code decides whether it satisfies the scenario contract.

## Main components

### Scenario catalog

A scenario defines a small, reproducible incident case. It contains the incident description, available evidence, expected root cause, causal keywords, and optional required evidence IDs.

Built-in scenarios are version-controlled. Custom scenarios are persisted in SQLite and enter the same catalog and investigation path.

### Investigation service

The service owns application orchestration. It selects the requested scenario and investigator mode, invokes the investigator, evaluates the resulting diagnosis, and persists the completed run.

### Investigators

TraceBack supports two investigation paths:

- **Deterministic baseline** for repeatable local validation and regression checks.
- **LLM investigator** for model-backed diagnosis through the provider abstraction.

The LLM path keeps provider-specific behavior behind a provider interface so Ollama does not become a core domain dependency.

### MCP and evidence tools

Evidence is retrieved through explicit tool contracts rather than silently injected context. TraceBack includes a real MCP evidence server and a constrained remote-source integration for operator-configured external MCP endpoints.

Evidence remains attributable through stable IDs, sources, kinds, and content.

### Structured diagnosis

The diagnosis contract contains:

- incident or scenario identity
- root cause
- evidence IDs
- confidence
- recommended action

Pydantic validation rejects malformed outputs before they enter the evaluation and reporting flow.

### Deterministic evaluator

The evaluator does not generate or improve the diagnosis. It measures:

- root-cause match
- evidence recall
- evidence precision
- confidence validity
- recommended-action presence
- overall pass/fail

Recall and precision are treated as fully satisfied at 100% for the overall pass decision.

### Persistence

Completed investigations are stored after evaluation. The application service owns orchestration while the repository layer owns storage.

```text
FastAPI / CLI
     │
     ▼
InvestigationService
     │
     ├── Investigator
     │     ├── Baseline
     │     └── LLM → Provider
     │
     ├── Evaluator
     │
     └── RunStore → SQLite
                         │
                         ▼
                   InvestigationRun
```

The same persistence boundary supports experiments and custom scenarios. Docker Compose keeps database state outside the backend image through persistent storage under `/data`.

### Observability

Investigation and benchmark execution emit runtime events through the observability layer.

```text
Investigation / Benchmark
          │
          ▼
      TraceContext
          │
          ▼
       EventSink
          │
          ▼
   Timeline / exporters
```

Observability records how the system behaved; evaluation decides whether the result met its contract.

### Benchmark platform

The benchmark path builds on the same scenario and investigation contracts:

```text
Scenario Catalog
      │
      ▼
Dataset / configuration
      │
      ▼
Benchmark Service
      │
      ▼
Repeated investigations
      │
      ▼
Persisted experiment
      │
      ├── statistics
      ├── calibration
      ├── regression policy
      └── comparison
```

This turns investigation quality into a repeatable measurement instead of a one-off demonstration.

## Evaluation boundary

```text
LLM / baseline output
          │
          ▼
Structured diagnosis
          │
          ▼
Deterministic evaluator
          │
          ├── root-cause match
          ├── evidence recall
          ├── evidence precision
          ├── confidence validity
          └── action presence
          │
          ▼
Persisted result / benchmark statistics
```

The evaluator should never silently modify the diagnosis. Its role is measurement.

## Design principles

### Local-first

Local inference keeps the development loop inexpensive and makes the default workflow easy to reproduce.

### Provider-agnostic

Ollama is the current local provider, not the application's core abstraction.

### Explicit evidence

Evidence has stable identifiers and attributable sources so diagnoses can be inspected and evaluated.

### Deterministic evaluation

Given the same diagnosis and scenario, evaluation should produce the same result.

### Reproducibility

Scenario definitions, benchmark configuration, and experiment provenance are persisted or version-controlled so runs can be repeated and compared.

### Small surface area

Infrastructure is introduced only when it solves a demonstrated product or evaluation requirement.

## Extension points

The architecture can be extended with additional MCP tools, LLM providers, scenarios, evaluation metrics, latency/token measurements, and model/configuration comparisons without changing the core generation/evaluation boundary.

## Non-goals

TraceBack is not intended to become:

- a full observability platform
- a replacement for production incident-management systems
- a generic chatbot
- a large distributed monitoring platform
- a collection of superficial integrations

The project stays focused on **LLM-assisted incident diagnosis and measurable reliability**.
