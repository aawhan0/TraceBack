# Asynchronous investigation jobs

TraceBack exposes a small asynchronous execution boundary for investigations that may outlive an HTTP request.

## Lifecycle

POST /jobs -> queued -> running -> completed | failed

Completed jobs expose the existing persisted run ID, execution ID, and trace ID. Diagnosis data remains owned by the existing run and experiment persistence boundaries.

## API

Create a job:

curl -X POST http://127.0.0.1:8000/jobs -H 'Content-Type: application/json' -d '{"scenario_id":"database-pool-exhaustion"}'

Poll a job:

curl http://127.0.0.1:8000/jobs/<job-id>

List jobs:

curl 'http://127.0.0.1:8000/jobs?limit=20'

## Design boundary

The current implementation uses FastAPI background tasks and a bounded, thread-safe in-process registry. It is intentionally single-process. A future worker queue can replace this execution mechanism behind the same HTTP lifecycle contract without changing investigation or evaluation code.
