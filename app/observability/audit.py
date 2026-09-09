from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: str
    occurred_at: datetime
    actor: str
    resource_type: str
    resource_id: str
    payload: dict[str, Any]

    @classmethod
    def create(
        cls,
        event_type: str,
        *,
        actor: str,
        resource_type: str,
        resource_id: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditEvent:
        if not event_type.strip():
            raise ValueError("event_type is required")
        if not resource_id.strip():
            raise ValueError("resource_id is required")
        return cls(
            event_id=str(uuid4()),
            event_type=event_type,
            occurred_at=datetime.now(timezone.utc),
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=dict(payload or {}),
        )


class AuditLog:
    """Small append-only audit abstraction for local and future remote sinks."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> AuditEvent:
        self._events.append(event)
        return event

    def list(
        self,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        events = [
            event
            for event in self._events
            if (resource_type is None or event.resource_type == resource_type)
            and (resource_id is None or event.resource_id == resource_id)
        ]
        return list(reversed(events[-limit:]))
