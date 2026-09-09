# Job persistence

TraceBack stores investigation job state in SQLite behind the JobStore interface.

## Lifecycle

The durable state machine is:

queued -> running -> completed
queued -> running -> failed
running -> queued (bounded retry)

Terminal states cannot be reopened accidentally.

## Durability

TRACEBACK_DATABASE_PATH controls the database location and defaults to
data/traceback.db. SQLite WAL mode, a busy timeout, and per-operation
connections support concurrent API reads and background worker writes.

Reconstructing JobStore against the same database restores existing jobs, so a
process restart no longer erases execution history.

## Idempotency

Clients can supply an idempotency key when creating a job. Repeating the same
key returns the existing job instead of creating a duplicate execution.

## Retry policy

Each job carries a bounded attempt count. The store accepts one to five
attempts. The worker owns retry scheduling while the repository owns durable
attempt state.

## Worker boundary

JobRepository is the application facade. A future PostgreSQL-backed repository
or queue consumer can replace the SQLite implementation without changing the
HTTP job contract.
