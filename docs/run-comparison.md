# Run Comparison

TraceBack can compare two saved benchmark experiments when they use the same dataset name, version, fingerprint, and scenario coverage.

The comparison view reports:

- pass-rate change
- average confidence change
- average duration change
- baseline and candidate provider/model
- per-scenario pass-rate deltas
- an overall `improved`, `regressed`, or `unchanged` verdict

Comparisons are read-only. They use persisted experiment results and the existing `/experiments/{baseline_id}/compare/{candidate_id}` API contract.
