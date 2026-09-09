# Experiment matrices

TraceBack can run several benchmark configurations against one immutable dataset. This is useful when comparing a baseline with multiple model configurations without accidentally changing the evaluated scenario set.

The matrix boundary is deliberately small:

```text
immutable dataset
       |
       +--> baseline
       +--> model A
       +--> model B
       |
       v
persisted experiments
       |
       v
baseline-relative comparisons
```

Every configuration produces a normal persisted experiment. The matrix does not introduce a second benchmark implementation.

## Configuration rules

- Configuration names must be unique.
- A baseline cannot specify a model.
- An LLM configuration must specify a model.
- A matrix is limited to 20 configurations.
- Every configuration receives the exact same dataset manifest.
- The first configuration is the comparison baseline.
- The best configuration is selected by pass rate, then confidence, then lower latency.

The frontend can consume these same persisted experiment and comparison contracts later; no UI-specific state is introduced here.
