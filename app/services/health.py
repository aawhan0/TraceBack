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


@dataclass(frozen=True)
class DependencyHealth:
    name: str
    healthy: bool
    detail: str


@dataclass(frozen=True)
class ReadinessReport:
    ready: bool
    dependencies: tuple[DependencyHealth, ...]


class ReadinessChecker:
    """Run named dependency checks and produce an operational readiness report."""

    def __init__(self, checks: dict[str, callable]) -> None:
        self._checks = dict(checks)

    def check(self) -> ReadinessReport:
        dependencies: list[DependencyHealth] = []
        for name in sorted(self._checks):
            try:
                detail = str(self._checks[name]())
            except Exception as exc:
                dependencies.append(
                    DependencyHealth(
                        name=name,
                        healthy=False,
                        detail=str(exc),
                    )
                )
            else:
                dependencies.append(
                    DependencyHealth(
                        name=name,
                        healthy=True,
                        detail=detail,
                    )
                )

        return ReadinessReport(
            ready=bool(dependencies) and all(item.healthy for item in dependencies),
            dependencies=tuple(dependencies),
        )


def sqlite_check(database_path: str) -> str:
    """Return a compact health result for the configured SQLite database."""
    from app.repository.maintenance import SQLiteMaintenance

    result = SQLiteMaintenance(database_path).integrity_check()
    if result != "ok":
        raise RuntimeError(f"sqlite integrity check failed: {result}")
    return "sqlite ok"


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
