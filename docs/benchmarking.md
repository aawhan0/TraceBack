# Benchmarking and Regression

Traceback's benchmark layer is built on top of the normal investigation path. It does not create a second implementation of investigation; it repeatedly executes the same service and evaluates every diagnosis through the same deterministic evaluator.

## Benchmark lifecycle

Dataset Manifest
      |
      v
Benchmark Request
      |
      v
Experiment Runner
      |
      +----> Investigation Service
      |             |
      |             +----> Investigator
      |             +----> Evidence tools
      |             +----> Deterministic evaluator
      |             +----> Run persistence
      |
      v
Experiment Result
      |
      +----> Descriptive statistics
      +----> Confidence calibration
      +----> Regression policy
      |
      v
Experiment Record

## Datasets

A DatasetManifest identifies a versioned collection of scenario IDs. The manifest has a SHA-256 fingerprint so a benchmark record can tell you exactly which selection produced the result.

Datasets support:

- stable names and versions
- tags
- weighted cases
- deterministic selection
- catalog validation
- JSON export
- content fingerprints

A dataset version should be bumped when its case selection or meaning changes.

## Experiment execution

An ExperimentSpec controls the scenario set and repetition count. The runner executes each selected scenario the requested number of times.

Every individual run still flows through InvestigationService, which means run history and per-run evaluation remain available.

The aggregate result currently includes:

- total runs
- passed runs
- pass rate
- average confidence
- average duration
- per-scenario pass rates

## Statistical reporting

The statistics module provides percentile summaries and Wilson score intervals. Wilson intervals are useful for small benchmark sets because a raw 100% pass rate from three examples should not be interpreted as equally strong evidence as 100% from 3,000 examples.

Confidence calibration is measured separately with:

- Brier score
- expected calibration error
- maximum calibration error
- confidence buckets
- confidence standard error

These measurements describe the quality of a model's confidence signal. They do not override the deterministic evaluator.

## Regression gates

A RegressionPolicy expresses release requirements explicitly.

Available thresholds include:

- minimum overall pass rate
- minimum root-cause accuracy
- minimum evidence recall
- minimum evidence precision
- minimum scenario pass rate
- optional minimum average confidence
- optional maximum average duration

A failed gate produces structured RegressionFailure records instead of a generic boolean.

## Reproducibility

A useful benchmark record should answer four questions:

1. What was evaluated?
2. Which dataset was used?
3. What result did the system produce?
4. Did it satisfy the release policy?

Traceback now persists the dataset name, version, fingerprint, aggregate result, regression report, and creation time.

The next natural extension is to persist model/provider configuration and git revision alongside the record.

## CI usage

A CI job can run a benchmark with a strict threshold and fail the job when the gate fails.

Example:

    traceback benchmark --name ci-baseline --repetitions 3 --min-pass-rate 1.0 --report

The CLI report is Markdown-friendly so it can be attached to CI summaries or pull-request comments.

## API surface

| Endpoint | Purpose |
| --- | --- |
| POST /experiments | Execute a selected experiment |
| GET /experiments | List persisted experiments |
| GET /experiments/{experiment_id} | Inspect one experiment |
| GET /datasets/core | Inspect the built-in dataset |

## Design constraints

The benchmark layer deliberately avoids:

- hidden scoring heuristics
- model-specific evaluation code
- network calls inside statistics
- a mandatory telemetry vendor
- a separate database service
- random sampling by default

The goal is a transparent evaluation foundation that can grow into a production benchmarking system without making the core investigation path harder to reason about.


## Reproducible execution provenance

Every benchmark now records the execution identity alongside its metrics. A persisted experiment can therefore be traced back to:

- application version
- Git revision (TRACEBACK_GIT_SHA, then GITHUB_SHA, or unknown)
- Python runtime version
- Traceback environment
- investigator provider
- model name when an LLM benchmark is used

The benchmark control path supports both deterministic baseline runs and Ollama-backed LLM runs. The same dataset, repetitions, evaluator, regression policy, and persistence path are used for both modes.

### CLI

Baseline benchmark:

    traceback benchmark --mode baseline --repetitions 3 --name baseline-smoke

LLM benchmark:

    traceback benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke

### API

POST /experiments accepts mode (baseline or llm) and an optional model. LLM mode requires a model and uses the configured Ollama endpoint. The response and persisted experiment record include a provenance object so benchmark results remain interpretable after the run has completed.
