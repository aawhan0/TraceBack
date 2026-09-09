from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthCheck:
    name: str
    status: str
    detail: str
    latency_ms: float | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "degraded", "failed"}:
            raise ValueError("status must be ok, degraded, or failed")


@dataclass(frozen=True)
class ReadinessReport:
    ready: bool
    checks: tuple[HealthCheck, ...]

    @property
    def failed(self) -> tuple[HealthCheck, ...]:
        return tuple(check for check in self.checks if check.status == "failed")


class ReadinessRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}

    def set(self, check: HealthCheck) -> None:
        self._checks[check.name] = check

    def report(self) -> ReadinessReport:
        checks = tuple(self._checks[name] for name in sorted(self._checks))
        return ReadinessReport(
            ready=bool(checks) and not any(check.status == "failed" for check in checks),
            checks=checks,
        )
