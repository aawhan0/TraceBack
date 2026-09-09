# Deployment

TraceBack is now packaged as a small production-oriented container.

## Build

From the repository root:

```bash
docker build -t traceback:local .
```

## Run

The container listens on port 8000:

```bash
docker run --rm \
  -p 8000:8000 \
  -v traceback-data:/data \
  traceback:local
```

The SQLite volume is intentional. Investigation runs, experiments, jobs, and audit state must survive container replacement.

The application runs as a non-root user and stores its default database at `/data/traceback.db`.

## Configuration

Production configuration continues to use the existing environment variables:

- `TRACEBACK_ENVIRONMENT=production`
- `TRACEBACK_DATABASE_PATH=/data/traceback.db`
- `TRACEBACK_CORS_ORIGINS`
- `TRACEBACK_RATE_LIMIT_REQUESTS`
- `TRACEBACK_RATE_LIMIT_WINDOW_SECONDS`
- `TRACEBACK_LOG_LEVEL`
- `TRACEBACK_MODEL`
- `OLLAMA_BASE_URL`
- `TRACEBACK_OLLAMA_TIMEOUT`

For a remote Ollama service, set `OLLAMA_BASE_URL` to the reachable provider endpoint. The container does not bundle Ollama, keeping model serving separate from the application lifecycle.

## Health

Use:

```text
GET /health
GET /health/ready
```

`/health` is suitable for a lightweight container liveness check. `/health/ready` reports application dependency readiness.

## Persistence boundary

The current deployment remains intentionally single-node:

```text
HTTP
  |
  v
TraceBack container
  |
  +--> SQLite volume
  |
  +--> Ollama / external provider
```

The repository and service boundaries keep persistence and model providers replaceable, but this container should not be presented as a horizontally scaled deployment. A shared database and queue are the next infrastructure step if multi-instance operation becomes necessary.

## CI

The repository CI builds the container on pull requests and pushes. This catches Dockerfile/package regressions without requiring a registry or publishing credentials.
