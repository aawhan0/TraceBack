# API Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | /health | Service health |
| GET | /scenarios | List available scenarios |
| GET | /scenarios/{scenario_id} | Inspect one scenario |
| POST | /investigations | Run the deterministic investigation baseline |
| POST | /experiments | Run a repeatable benchmark and regression gate |
| GET | /experiments | List persisted benchmark experiments |
| GET | /experiments/{experiment_id} | Inspect one persisted experiment |
| GET | /datasets/core | Inspect the versioned core dataset |

FastAPI also exposes generated OpenAPI documentation when the service is running locally.

Example:

```bash
curl -X POST http://127.0.0.1:8000/investigations \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"database-pool-exhaustion"}'
```


## Benchmark request

Example:

    {
      "name": "baseline-smoke",
      "scenario_ids": [
        "database-pool-exhaustion",
        "redis-connectivity-failure"
      ],
      "repetitions": 3
    }

The response includes aggregate metrics, the dataset fingerprint, the Wilson pass-rate interval, and the regression gate outcome.
