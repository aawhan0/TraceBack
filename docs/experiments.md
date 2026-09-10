# Experiments and Regression Gates

TraceBack treats incident investigation as an experimentable system rather than a single request/response demo.

## Experiment model

An experiment defines:

- a stable name
- one or more scenario IDs
- a repetition count
- an investigation mode (`baseline` or `llm`)
- an optional model when using LLM mode

Every repetition uses the normal investigation service and deterministic evaluator. Results are persisted so they can be inspected later and compared with compatible experiments.

The aggregate result includes:

- total runs
- passed runs
- overall pass rate
- average confidence
- average duration
- per-scenario pass rates
- regression result

## Run an experiment from the CLI

Baseline benchmark:

```powershell
trbk benchmark --mode baseline --repetitions 3 --name baseline-smoke
```

LLM benchmark with Ollama:

```powershell
trbk benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
```

Selected scenarios can be repeated with `--scenario-id`:

```powershell
trbk benchmark --scenario-id database-pool-exhaustion --scenario-id redis-connectivity-failure --repetitions 3 --name database-redis-smoke
```

The CLI stores the resulting experiment and its provenance in the same persistence layer used by the dashboard.

## Regression gates

A regression policy expresses the minimum quality the experiment must meet. The benchmark path can enforce thresholds such as:

- minimum overall pass rate
- minimum root-cause accuracy
- minimum evidence recall
- minimum evidence precision
- minimum scenario pass rate
- optional minimum average confidence
- optional maximum average duration

For a simple pass-rate gate:

```powershell
trbk benchmark --repetitions 3 --min-pass-rate 0.9 --name baseline-gated
```

Make the command return a non-zero exit code when the gate fails:

```powershell
trbk benchmark --repetitions 3 --min-pass-rate 0.9 --fail-on-regression
```

Generate a Markdown-friendly report:

```powershell
trbk benchmark --repetitions 3 --name baseline-report --report
```

A failed gate is represented as structured regression data rather than an opaque boolean.

## Inspect saved experiments

List persisted experiments:

```powershell
trbk experiments --limit 20
```

Inspect one experiment:

```powershell
trbk experiment <experiment-id>
```

The dashboard's **Experiments** view provides the same persisted history and detail data.

## Compare experiments

Compatible experiments can be compared without rerunning them:

```powershell
trbk compare <baseline-experiment-id> <candidate-experiment-id>
```

Generate Markdown output:

```powershell
trbk compare <baseline-experiment-id> <candidate-experiment-id> --report
```

TraceBack checks dataset identity before comparing. Experiments built from incompatible datasets are rejected instead of producing a misleading improvement or regression.

The comparison reports pass-rate, confidence, and duration deltas together with per-scenario results and provider/model identity.

## Configuration matrices

A matrix evaluates multiple configurations against one scenario selection:

```powershell
trbk matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --repetitions 3
```

The matrix stores the dataset fingerprint, experiment IDs, configuration identities, and the best experiment according to the benchmark result.

## API

Create an experiment directly through FastAPI:

```bash
curl -X POST http://127.0.0.1:8000/experiments \
  -H 'Content-Type: application/json' \
  -d '{"name":"baseline-smoke","scenario_ids":["database-pool-exhaustion","redis-connectivity-failure"],"repetitions":3,"mode":"baseline"}'
```

The persisted experiment can then be inspected through the `/experiments` endpoints or the dashboard.

## Reproducibility

A useful experiment record should make it possible to answer:

1. What was evaluated?
2. Which scenarios or dataset were used?
3. How many repetitions were executed?
4. Which investigation mode/provider/model was used?
5. What metrics were produced?
6. Did the result satisfy the regression policy?

TraceBack keeps the evaluation decision deterministic and persists experiment provenance alongside the measured result.

## Core principle

Experiment orchestration never decides whether a diagnosis is correct. The deterministic evaluator owns that decision.

The workflow is intentionally simple:

```text
investigate
    ↓
persist runs
    ↓
benchmark repeatedly
    ↓
inspect experiment
    ↓
compare compatible experiments
    ↓
identify regressions or improvements
```
