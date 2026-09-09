# Investigation Runtime

The runtime is the execution boundary around TraceBack's investigator implementations.

## Responsibilities

The runtime owns operational lifecycle state without becoming part of the diagnostic decision:

1. create an execution and trace ID
2. mark the investigation as running
3. invoke the configured investigator
4. enforce a cooperative wall-clock execution budget
5. record completion or failure
6. return structured execution metadata

The runtime does not evaluate or modify a diagnosis.

## Execution model

API or CLI
  -> InvestigationRuntime
  -> Investigator
  -> InvestigationExecution

An execution contains an execution ID, trace ID, lifecycle phase, diagnosis when
successful, step timings, total duration, and failure metadata when unsuccessful.

## Failure semantics

Investigator exceptions become a failed execution. This preserves the execution
identity and trace while allowing callers to choose their preferred boundary.

execute() returns structured failure state.

execute_or_raise() converts that state into a RuntimeError for callers that
prefer exception-based control flow.

The timeout is intentionally cooperative. The runtime checks the deadline
before and after investigator execution; it does not terminate threads or processes.

## Why this boundary matters

The runtime gives TraceBack a stable place to add retries, cancellation, tool
budgets, token accounting, streaming progress, persistent execution state, and
API status endpoints without pushing operational concerns into the evaluator or
domain models.