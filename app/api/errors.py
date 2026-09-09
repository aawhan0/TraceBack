from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None


@dataclass(frozen=True)
class ApiError:
    code: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] | None = None
    occurred_at: datetime | None = None

    def as_dict(self) -> dict[str, Any]:
        occurred_at = self.occurred_at or datetime.now(timezone.utc)
        return {
            "code": self.code,
            "message": self.message,
            "request_id": self.request_id,
            "details": self.details or {},
            "occurred_at": occurred_at.isoformat(),
        }


class TracebackApiError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
