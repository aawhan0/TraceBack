# Experiments and Regression Gates

Traceback treats investigation as an experimentable system rather than a single request/response demo.

## Experiment specification

An ExperimentSpec defines a name, one or more scenario IDs, and a repetition count. Every run continues through the same deterministic evaluator and is persisted by the normal investigation service.

The runner reports:

- total runs
- passed runs
- overall pass rate
- average confidence
- average duration
- per-scenario pass rates

## API

Run a repeatable baseline experiment:

    curl -X POST http://127.0.0.1:8000/experiments \
      -H 'Content-Type: application/json' \
      -d '{"name":"baseline-smoke","scenario_ids":["database-pool-exhaustion","redis-connectivity-failure"],"repetitions":3}'

The endpoint is intended for local evaluation and future model/configuration experiments.

## CLI

Run all scenarios twice:

    traceback benchmark --repetitions 2 --name baseline-smoke

Run selected scenarios:

    traceback benchmark --scenario-id database-pool-exhaustion --scenario-id redis-connectivity-failure

## Regression gates

RegressionGate defines a minimum acceptable pass rate. This keeps model or tool changes measurable:

    gate = RegressionGate(minimum_pass_rate=0.95)

    if not gate.check(result):
        raise RuntimeError("Experiment failed regression gate")

The gate currently focuses on pass rate. More thresholds should be added only when the corresponding measurements are reliable.

## Comparing configurations

compare_experiments() reports candidate-minus-baseline deltas for pass rate, confidence, and latency.

This gives Traceback a clean path toward:

- model benchmark matrices
- persisted experiment metadata
- CI regression thresholds
- benchmark datasets
- latency and cost tracking
- statistical confidence intervals

The important boundary remains unchanged: experiment orchestration never decides whether a diagnosis is correct. The deterministic evaluator owns that decision.
