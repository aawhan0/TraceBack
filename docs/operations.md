# Operations

TraceBack keeps operational concerns separate from investigation logic so the backend can be run locally today and deployed behind a proper platform later.

## Readiness

GET /ops/ready checks dependencies required for the service to accept work. A healthy response contains a ready status and dependency details. A dependency failure returns HTTP 503 with structured dependency details.

## Database diagnostics

GET /ops/database exposes non-sensitive local database diagnostics:

- SQLite integrity-check result
- foreign-key enforcement state

It intentionally does not expose the database path or connection details.

## Retention

SQLiteMaintenance.prune() provides explicit retention rather than silently deleting operational history.

    from app.repository.maintenance import SQLiteMaintenance

    maintenance = SQLiteMaintenance("data/traceback.db")
    result = maintenance.prune(older_than_days=30, vacuum=True)

Retention is an operator decision. TraceBack does not automatically discard investigation evidence.

## Audit persistence

SQLiteAuditStore persists structured audit events using the same SQLite database as investigation history. Events are append-only and can be filtered by resource or event type.

## Metrics

MetricsRegistry is a dependency-free local metrics abstraction. It supports counters, duration observations, snapshots, and context-managed timers. It is deliberately small so it can later be adapted to Prometheus/OpenTelemetry without coupling the domain layer to a vendor.

## Deployment boundary

The current operational layer is intentionally process-local:

- rate limiting is in-memory
- metrics are in-memory
- SQLite is local

For a multi-instance deployment, these should be replaced or backed by shared infrastructure. The repository interfaces are the seam for that migration.
