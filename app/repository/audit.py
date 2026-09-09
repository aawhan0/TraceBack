from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Protocol

from app.observability.audit import AuditEvent


class AuditStore(Protocol):
    def append(self, event: AuditEvent) -> None: ...
    def list(
        self,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]: ...


class SQLiteAuditStore:
    """Durable append-only audit store sharing TraceBack's SQLite database."""

    def __init__(self, database_path: str = "data/traceback.db") -> None:
        self.database_path = database_path
        self._memory_connection: sqlite3.Connection | None = None
        if database_path == ":memory:":
            self._memory_connection = sqlite3.connect(":memory:")
        else:
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = self._memory_connection or sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_resource_time
                ON audit_events (resource_type, resource_id, occurred_at DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_type_time
                ON audit_events (event_type, occurred_at DESC)
                """
            )

    def append(self, event: AuditEvent) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    event_id, event_type, occurred_at, actor,
                    resource_type, resource_id, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.occurred_at.isoformat(),
                    event.actor,
                    event.resource_type,
                    event.resource_id,
                    json.dumps(event.payload, sort_keys=True),
                ),
            )

    def list(
        self,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        clauses: list[str] = []
        values: list[str | int] = []
        if resource_type is not None:
            clauses.append("resource_type = ?")
            values.append(resource_type)
        if resource_id is not None:
            clauses.append("resource_id = ?")
            values.append(resource_id)
        if event_type is not None:
            clauses.append("event_type = ?")
            values.append(event_type)
        query = "SELECT * FROM audit_events"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY occurred_at DESC LIMIT ?"
        values.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return [self._row_to_event(row) for row in rows]

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> AuditEvent:
        return AuditEvent(
            event_id=row["event_id"],
            event_type=row["event_type"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            actor=row["actor"],
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            payload=json.loads(row["payload_json"]),
        )
