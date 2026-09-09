# Persistence

TraceBack stores investigation and benchmark history in SQLite through repository abstractions.

## Stored records

### Investigation runs

Each run retains:

- run identity and scenario
- execution mode and provider
- full diagnosis
- evaluation metrics
- pass/fail result
- execution duration
- creation timestamp

### Experiments

Benchmark records retain:

- experiment identity
- dataset identity and fingerprint
- aggregate result
- regression report
- creation timestamp

### Audit events

Operational actions can be stored independently through SQLiteAuditStore. Audit payloads are JSON encoded and indexed by resource and event type.

## Durability model

Writes use SQLite transactions through Python's standard-library sqlite3 module. Schema creation is idempotent, and commonly queried fields have indexes.

The stores intentionally expose protocols (RunStore, ExperimentStore, AuditStore) so the investigation engine does not need to know which database technology is used.

## Retention

Retention is explicit and opt-in through SQLiteMaintenance. This keeps historical investigation data available by default and prevents accidental data loss during normal application operation.

## Future migration

A shared PostgreSQL-backed implementation can replace the SQLite adapters without changing the service-level contracts. This is the intended path when TraceBack moves from a single-node deployment to multiple API workers.
