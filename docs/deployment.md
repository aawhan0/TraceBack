# Deployment

TraceBack is packaged as a small production-oriented container.

## Docker

Build the image:

```bash
docker build -t traceback:local .
```

Run it with durable SQLite state:

```bash
docker run --rm \
  -p 8000:8000 \
  -v traceback-data:/data \
  traceback:local
```

The application runs as a non-root user and stores its default database at `/data/traceback.db`.

## Docker Compose

For the simplest repeatable deployment:

```bash
docker compose up --build -d
docker compose ps
```

The Compose service builds the same production Dockerfile, exposes port 8000, persists SQLite through the named `traceback-data` volume, restarts after unexpected exits, and uses the image healthcheck for liveness.

Stop it with:

```bash
docker compose down
```

The named volume is retained by default. To intentionally remove persisted application state:

```bash
docker compose down -v
```

### External Ollama

Ollama is intentionally not bundled into the Compose file. The application can point at an existing Ollama service through `OLLAMA_BASE_URL` without tying model serving to the application container lifecycle.

For example:

```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434 docker compose up --build -d
```

The exact network address depends on the deployment platform; do not assume `host.docker.internal` is available everywhere.

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

Repository CI builds the container on pull requests and pushes, and validates the Compose configuration. This catches Dockerfile, packaging, and deployment-definition regressions without requiring registry credentials.
