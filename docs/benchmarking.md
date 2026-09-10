# Benchmarking and Regression

TraceBack's benchmark layer repeatedly exercises the normal investigation path and evaluates every result with the same deterministic evaluator used by individual runs.

## Benchmark lifecycle

```text
Scenario catalog
      │
      ▼
Dataset selection
      │
      ▼
Benchmark request
      │
      ▼
Experiment runner
      │
      ├── Investigation Service
      │       ├── Investigator
      │       ├── Evidence tools
      │       ├── Deterministic evaluator
      │       └── Run persistence
      │
      ▼
Experiment result
      │
      ├── Statistics
      ├── Confidence calibration
      ├── Regression policy
      └── Provenance
      │
      ▼
Persisted experiment
```

## Dataset identity

A benchmark operates on a defined scenario selection. Dataset identity and fingerprints keep results comparable and prevent accidental comparisons against different case sets.

The benchmark path is intentionally deterministic in its scenario selection. The same scenario definitions and evaluator are reused across baseline and LLM modes.

## Run an experiment

### CLI

Baseline:

```powershell
trbk benchmark --mode baseline --repetitions 3 --name baseline-smoke
```

LLM with Ollama:

```powershell
trbk benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
```

Selected scenarios:

```powershell
trbk benchmark --scenario-id database-pool-exhaustion --scenario-id redis-connectivity-failure --repetitions 3 --name database-redis-smoke
```

The benchmark persists the experiment, its measured result, and execution provenance.

### API

The same flow is available through `POST /experiments`.

```bash
curl -X POST http://127.0.0.1:8000/experiments \
  -H 'Content-Type: application/json' \
  -d '{"name":"baseline-smoke","scenario_ids":["database-pool-exhaustion","redis-connectivity-failure"],"repetitions":3,"mode":"baseline"}'
```

## Metrics

The aggregate result currently includes:

- total runs
- passed runs
- pass rate
- average confidence
- average duration
- per-scenario pass rates

The statistics layer also provides percentile summaries and Wilson score intervals. These help interpret small benchmark samples without treating a raw pass rate as stronger evidence than the sample size supports.

Confidence calibration is tracked separately with:

- Brier score
- expected calibration error
- maximum calibration error
- confidence buckets
- confidence standard error

Calibration describes the confidence signal; it does not replace the deterministic evaluator.

## Regression policy

A regression policy expresses explicit release thresholds. Supported measurements include:

- minimum overall pass rate
- minimum root-cause accuracy
- minimum evidence recall
- minimum evidence precision
- minimum scenario pass rate
- optional minimum average confidence
- optional maximum average duration

Example:

```powershell
trbk benchmark --repetitions 3 --min-pass-rate 0.9 --name baseline-gated
```

Fail the command when the regression gate is not satisfied:

```powershell
trbk benchmark --repetitions 3 --min-pass-rate 0.9 --fail-on-regression
```

Generate a Markdown-friendly report:

```powershell
trbk benchmark --repetitions 3 --name baseline-report --report
```

A failed gate produces structured regression information rather than silently treating the benchmark as successful.

## Reproducibility and provenance

A persisted experiment records the information needed to understand what was measured, including dataset identity and execution context. Current provenance covers application version, Git revision when available, Python runtime, environment, investigator provider, and LLM model when applicable.

The key questions are:

1. What was evaluated?
2. Which dataset or scenario selection was used?
3. How was it executed?
4. What result did it produce?
5. Did it satisfy the release policy?

## Comparing experiments

Compatible experiments can be compared without rerunning them:

```powershell
trbk compare <baseline-experiment-id> <candidate-experiment-id>
trbk compare <baseline-experiment-id> <candidate-experiment-id> --report
```

Comparison is intentionally strict. Experiments must share compatible dataset identity and scenario selection. The result includes:

- overall pass-rate delta
- average confidence delta
- average duration delta
- per-scenario pass-rate deltas
- baseline/candidate provider identity
- baseline/candidate model identity
- improved, regressed, or unchanged verdict

An incompatible dataset produces an HTTP 409 instead of a misleading comparison.

## Configuration matrices

Use a matrix to evaluate multiple configurations against the same scenario selection:

```powershell
trbk matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --repetitions 3
```

The matrix persists configuration identities, experiment IDs, dataset fingerprint, and the selected best experiment.

## CI usage

A CI pipeline can run the same benchmark commands with a strict regression threshold and fail the job when quality falls below policy. This makes evaluation quality a release signal rather than a one-off manual check.

## Design constraints

The benchmark layer deliberately avoids hidden scoring heuristics, model-specific evaluator logic, mandatory telemetry vendors, and a separate database service. Investigation, evaluation, persistence, and benchmarking remain distinct responsibilities.
