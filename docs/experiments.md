# Experiments and Regression Gates

TraceBack treats incident investigation as an experimentable system rather than a one-off request/response demo. Every experiment uses the normal investigation service, deterministic evaluator, and persistence path.

## Experiment model

An experiment defines:

- a stable name
- one or more scenario IDs
- a repetition count
- an investigation mode (`baseline` or `llm`)
- an optional model for LLM mode

Every repetition follows the same investigation and deterministic evaluation path. Results are persisted so they can be inspected later and compared with compatible experiments.

## Run an experiment

### CLI

Deterministic baseline:

```powershell
trbk benchmark --mode baseline --repetitions 3 --name baseline-smoke
```

Ollama-backed LLM benchmark:

```powershell
trbk benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
```

Selected scenarios:

```powershell
trbk benchmark --scenario-id database-pool-exhaustion --scenario-id redis-connectivity-failure --repetitions 3 --name database-redis-smoke
```

The benchmark stores the resulting experiment and provenance in the same persistence layer used by the dashboard.

### Regression gates

Set a minimum acceptable pass rate:

```powershell
trbk benchmark --repetitions 3 --min-pass-rate 0.9 --name baseline-gated
```

Fail the command when the gate is not satisfied:

```powershell
trbk benchmark --repetitions 3 --min-pass-rate 0.9 --fail-on-regression
```

Generate a Markdown report:

```powershell
trbk benchmark --repetitions 3 --name baseline-report --report
```

The regression policy can also enforce thresholds for root-cause accuracy, evidence recall, evidence precision, scenario pass rate, average confidence, and average duration.

## Inspect saved experiments

List persisted experiments:

```powershell
trbk experiments --limit 20
```

Inspect one experiment:

```powershell
trbk experiment <experiment-id>
```

The dashboard's **Experiments** view exposes the same persisted history and detail data.

## Compare experiments

Compatible experiments can be compared without rerunning them:

```powershell
trbk compare <baseline-experiment-id> <candidate-experiment-id>
trbk compare <baseline-experiment-id> <candidate-experiment-id> --report
```

TraceBack checks dataset identity and scenario compatibility before comparing. A mismatch is rejected instead of producing a misleading improvement or regression.

The comparison includes pass-rate, confidence, and duration deltas together with per-scenario results and provider/model identity.

## Configuration matrices

Evaluate multiple configurations against the same scenario selection:

```powershell
trbk matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --repetitions 3
```

A matrix persists configuration identities, experiment IDs, the dataset fingerprint, and the selected best experiment.

## API

Create an experiment through FastAPI:

```bash
curl -X POST http://127.0.0.1:8000/experiments \
  -H 'Content-Type: application/json' \
  -d '{"name":"baseline-smoke","scenario_ids":["database-pool-exhaustion","redis-connectivity-failure"],"repetitions":3,"mode":"baseline"}'
```

Inspect persisted experiments with:

```text
GET /experiments
GET /experiments/{experiment_id}
```

## Reproducibility

A useful experiment record should make it possible to answer:

1. What was evaluated?
2. Which scenarios or dataset were used?
3. How many repetitions were executed?
4. Which investigation mode/provider/model was used?
5. What metrics were produced?
6. Did the result satisfy the regression policy?

TraceBack persists experiment identity and provenance alongside the measured result so benchmark runs remain interpretable after completion.

## Core principle

Experiment orchestration never decides whether a diagnosis is correct. The deterministic evaluator owns that decision.

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

See [benchmarking.md](benchmarking.md) for the statistical and benchmark model, and [cli.md](cli.md) for the complete command reference.