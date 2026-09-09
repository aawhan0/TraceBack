# Platform Contracts

Traceback keeps its core investigation path deliberately small while giving surrounding infrastructure explicit contracts.

## Provider boundary

`app.providers.contracts` defines ProviderRequest, ProviderResponse, CompletionProvider, ProviderRegistry, and ProviderError. The investigation system can depend on a provider interface without coupling its domain logic to Ollama.

## Audit events

`app.observability.audit` provides an append-only in-process audit abstraction with event type, actor, resource identity, UTC timestamp, and structured payload.

## Latency

`app.evaluation.latency` provides count, mean, min/max, p50, p95, and p99 latency summaries. Tail latency matters because average latency can hide bad outliers.

## Readiness

`app.services.readiness` separates service readiness from liveness and supports ok, degraded, and failed checks.

## API errors

`app.api.errors` defines a stable error vocabulary for future API handlers.

## Pagination

`app.api.pagination` provides a generic page/cursor contract so history endpoints can evolve beyond a hard-coded limit.

## Result envelopes

`app.services.results` provides explicit success, failure, and partial operation statuses.

## Design rule

These contracts are intentionally boring. Each abstraction should earn its place by making a boundary, measurable behavior, or future integration point clearer. They should not exist merely to increase framework surface area.
