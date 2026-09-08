# API Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | /health | Service health |
| GET | /scenarios | List available scenarios |
| GET | /scenarios/{scenario_id} | Inspect one scenario |
| POST | /investigations | Run the deterministic investigation baseline |

FastAPI also exposes generated OpenAPI documentation when the service is running locally.

Example:

```bash
curl -X POST http://127.0.0.1:8000/investigations \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"database-pool-exhaustion"}'
```
