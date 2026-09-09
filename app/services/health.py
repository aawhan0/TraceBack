from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from app.repository.runs import RunStore


@dataclass(frozen=True)
class ComponentHealth:
    name: str
    status: str
    latency_ms: float
    detail: str


class HealthService:
    def __init__(self, run_store: RunStore):
        self.run_store = run_store

    def check(self) -> tuple[ComponentHealth, ...]:
        started = perf_counter()
        try:
            self.run_store.stats()
            return (
                ComponentHealth(
                    name="database",
                    status="ok",
                    latency_ms=(perf_counter() - started) * 1000,
                    detail="sqlite store reachable",
                ),
            )
        except Exception as exc:
            return (
                ComponentHealth(
                    name="database",
                    status="failed",
                    latency_ms=(perf_counter() - started) * 1000,
                    detail=str(exc),
                ),
            )
