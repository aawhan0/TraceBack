from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass(frozen=True)
class OperationResult:
    status: Status
    operation: str
    started_at: datetime
    finished_at: datetime
    data: dict[str, Any]

    @property
    def duration_ms(self) -> float:
        return max(
            0.0,
            (self.finished_at - self.started_at).total_seconds() * 1000,
        )

    @classmethod
    def success(
        cls,
        operation: str,
        data: dict[str, Any] | None = None,
    ) -> OperationResult:
        now = datetime.now(timezone.utc)
        return cls(Status.SUCCESS, operation, now, now, dict(data or {}))

    @classmethod
    def failure(cls, operation: str, message: str) -> OperationResult:
        now = datetime.now(timezone.utc)
        return cls(Status.FAILURE, operation, now, now, {"error": message})
