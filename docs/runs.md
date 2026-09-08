# Investigation Run History

Traceback persists every completed investigation to a local SQLite database.

## Why persistence exists

An investigation system becomes much more useful when results can be inspected after the request finishes. Persisted runs provide:

- a stable run ID
- the scenario and investigation mode
- provider identity
- the structured diagnosis
- deterministic evaluation metrics
- confidence
- execution duration
- creation time

This creates the foundation for model experiments and regression analysis without introducing an external database.

## API

Run an investigation:

POST /investigations

Inspect recent runs:

GET /runs?scenario_id=database-pool-exhaustion&limit=20

Inspect one complete run:

GET /runs/{run_id}

Inspect historical statistics:

GET /runs/stats?scenario_id=database-pool-exhaustion

## CLI

The package exposes a `traceback` command:

```bash
traceback scenarios
traceback investigate database-pool-exhaustion
traceback runs --scenario-id database-pool-exhaustion
traceback show <run-id>
traceback stats --scenario-id database-pool-exhaustion
```

The same commands work with `python -m app.cli` during development.

## Storage

The default database is `data/traceback.db`.

Set `TRACEBACK_DATABASE_PATH` to use another location, or `:memory:` for an ephemeral store.

The database is intentionally local and SQLite-backed at this stage. A repository protocol keeps persistence replaceable when Traceback needs a shared production datastore.
