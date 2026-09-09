# Observability

Traceback keeps observability lightweight and dependency-free.

## Trace context

TraceContext creates a unique trace ID and sends structured events to an EventSink.

A trace event contains:

- event ID
- event name
- timestamp
- trace ID
- string attributes

The event schema is intentionally small so a future exporter can map it to OpenTelemetry, a log collector, or another platform without changing investigation code.

## Spans

TraceSpan records:

- <name>.started
- <name>.completed
- <name>.failed

Completed and failed spans include their duration. Exceptions are never swallowed by the span.

This makes the same primitive useful around investigation, evidence retrieval, model calls, experiment execution, and persistence.

## Event sinks

The repository ships three useful boundaries:

- NullEventSink — default no-op behavior
- InMemoryEventSink — deterministic test collector
- EventSink — extension point for a real exporter

No vendor SDK is required by the core package.

## Structured logging

JsonFormatter emits JSON log records containing service, environment, timestamp, level, logger, message, and selected correlation fields.

TraceLoggerAdapter carries a trace ID into log records.

The intention is that logs and trace events can eventually be joined using the same trace identifier.

## Timelines

build_timeline() converts raw trace events into an ordered InvestigationTimeline.

The timeline can:

- count events
- inspect first and last timestamps
- filter event families
- calculate explicit span duration
- render a human-readable debugging view

This is deliberately a reporting layer rather than another execution mechanism.

## Production extension point

A production deployment can replace the sink with an adapter for the organization's telemetry system.

The application should continue to emit domain-level events such as:

- benchmark.started
- benchmark.completed
- investigation.started
- investigation.completed
- investigation.failed

rather than leaking provider-specific telemetry into domain code.

## Privacy boundary

Trace attributes should contain operational metadata, not raw secrets or unrestricted incident payloads.

Before connecting a real exporter, define:

- which fields are safe to export
- retention duration
- access control
- sampling policy
- incident-data redaction rules

Observability is useful only when its data boundary is as deliberate as the application boundary.
