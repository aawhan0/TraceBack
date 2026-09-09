# Traceback Architecture

## Purpose

Traceback investigates production-like software incidents using an LLM agent and operational tools, then evaluates the resulting diagnosis against deterministic scenario ground truth.

The architecture is intentionally small. The project is designed to demonstrate engineering principles around agents, MCP, structured outputs, grounding, and evaluation without becoming a full observability platform.

## System Flow

```text
┌──────────────┐
│   Incident   │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Investigation Agent │
└─────────┬───────────┘
          │
          │ MCP tool calls
          ▼
┌─────────────────────┐
│ Operational Tools   │
│ logs / metrics / ...│
└─────────┬───────────┘
          │
          │ Evidence
          ▼
┌─────────────────────┐
│ Structured Diagnosis│
│ Pydantic validation │
└─────────┬───────────┘
          │
          │ diagnosis + evidence
          ▼
┌─────────────────────┐
│ Deterministic       │
│ Evaluator           │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Evaluation Report   │
└─────────────────────┘
```

## Current implementation boundary

The repository now has a working deterministic control path around the future LLM/MCP integrations:

- the API selects a version-controlled scenario
- the service invokes an investigator
- the investigator retrieves evidence through a tool contract
- the diagnosis is validated by Pydantic
- deterministic evaluation measures the result
- aggregate evaluation summarizes repeated runs

The baseline investigator is deliberately replaceable. It exists to prove the contracts and orchestration before model behavior is introduced.

## Current implementation boundary

Traceback now has both sides of the agent boundary:

- a deterministic baseline investigator
- an LLM investigator with a provider protocol
- an Ollama HTTP provider
- strict Diagnosis parsing and validation
- a constrained scenario evidence tool
- a real MCP server exposing incident evidence
- deterministic per-run and aggregate evaluation
- comparison utilities for experiments

FastAPI remains the application-facing API while MCP is the model-facing tool protocol.

## Main Components

### Incident

The incident is the starting point for an investigation.

It contains enough context for the agent to understand the reported problem without encoding the answer directly into the prompt.

### Evidence

Evidence represents operational observations gathered during the investigation.

Each evidence item has an identifier so the final diagnosis can explicitly reference the information used to reach its conclusion.

This is important for grounding: the system can evaluate not only **what** the model concluded, but also **which evidence** it used.

### MCP Tool Layer

The agent interacts with operational evidence through tools exposed through MCP.

The exact tool set can evolve, but the architectural requirement is that evidence comes through an explicit tool boundary rather than being silently injected as hidden context.

Tools should return attributable, structured evidence where practical.

### LLM Provider

The LLM is responsible for reasoning over the incident and gathered evidence.

Ollama is the current local inference implementation.

The application should depend on a provider-level interface rather than Ollama-specific behavior wherever practical. This allows future model/provider comparisons without rewriting the investigation system.

### Structured Diagnosis

The agent returns a structured diagnosis rather than an arbitrary block of text.

The diagnosis contains:

- incident ID
- root cause
- evidence IDs
- confidence
- recommended action

Pydantic validation should reject malformed outputs before they enter the evaluation/reporting pipeline.

### Scenario Registry

An incident scenario defines deterministic ground truth for a testable failure mode.

A scenario contains:

- incident
- available evidence
- expected root cause
- root-cause keywords
- required evidence IDs

Scenarios are deliberately small and human-readable.

### Deterministic Evaluator

The evaluator is intentionally separate from the LLM.

It checks measurable properties of the diagnosis, including:

- root-cause match
- required evidence recall
- evidence precision
- confidence validity
- action presence

This prevents a second probabilistic model from becoming the authority on whether the first model was correct.

### Aggregate Evaluation

A scenario can be executed repeatedly.

The aggregate layer summarizes repeated runs so different models, prompts, configurations, or tool strategies can eventually be compared using the same scenario definitions.

## Evaluation Boundary

The most important architectural boundary is:

```text
LLM output
    │
    ▼
Structured diagnosis
    │
    ▼
Deterministic evaluator
    │
    ├── correct / incorrect
    ├── evidence recall
    ├── evidence precision
    └── aggregate reliability
```

The evaluator should not change the diagnosis or improve it. Its job is to measure it.

## Design Principles

### Local-first

Local inference keeps the initial development loop inexpensive and makes incident data easier to keep local.

### Provider-agnostic

The application should not make Ollama a hard dependency of core domain logic.

### Explicit evidence

Evidence should have stable IDs and identifiable sources.

### Deterministic evaluation

Given the same diagnosis and scenario, evaluation should produce the same result.

### Small surface area

New infrastructure should be justified by an actual engineering requirement.

### Reproducibility

Scenario definitions and evaluation configuration should be version-controlled so model results can be reproduced and compared.

## Future Extension Points

The architecture leaves room for:

- additional MCP investigation tools
- additional LLM providers
- more incident scenarios
- richer evaluation metrics
- latency/token measurements
- model/configuration comparison
- a minimal web UI

These are extension points, not requirements for the initial system.

## Non-Goals

Traceback is not intended to become:

- a full observability platform
- a production incident-management replacement
- a generic chatbot
- a large-scale distributed monitoring system
- a collection of dozens of superficial integrations

The system should stay focused on **LLM-assisted incident diagnosis and measurable reliability**.


## Persistence boundary

Completed investigations are persisted after deterministic evaluation. The application service owns orchestration; the repository owns storage.

```text
FastAPI / CLI
     |
     v
InvestigationService
     |
     +--> Investigator
     |      +--> Baseline
     |      +--> LLM -> Provider
     |
     +--> Evaluator
     |
     +--> RunStore -> SQLite
     |
     v
InvestigationRun
```

The `RunStore` protocol keeps SQLite-specific details out of the investigation domain. This makes historical runs available now while leaving room for a shared datastore later.


## Evaluation platform

The investigation path now feeds a higher-level benchmark platform.

Scenario Catalog
      |
      v
Dataset Manifest -----> fingerprint
      |
      v
Benchmark Service
      |
      v
Experiment Runner
      |
      +----> Investigation Service ----> Run Store
      |
      v
Experiment Result
      |
      +----> Statistics
      +----> Calibration
      +----> Regression Policy
      |
      v
Experiment Store

Observability is orthogonal:

Investigation / Benchmark
      |
      v
TraceContext -> EventSink -> Timeline / Exporter

This separation matters. Evaluation decides whether an investigation meets its contract; observability records how the system behaved; persistence stores what happened; the benchmark service coordinates repeatable runs.

No layer is responsible for silently changing another layer's result.
