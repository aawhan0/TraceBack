from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class MaintenanceResult:
    deleted_runs: int
    deleted_experiments: int
    deleted_audit_events: int
    vacuumed: bool


class SQLiteMaintenance:
    """Controlled database maintenance operations for local deployments."""

    def __init__(self, database_path: str = "data/traceback.db") -> None:
        self.database_path = database_path
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def prune(self, *, older_than_days: int = 30, vacuum: bool = False) -> MaintenanceResult:
        if older_than_days < 1:
            raise ValueError("older_than_days must be positive")
        if self.database_path == ":memory:":
            return MaintenanceResult(0, 0, 0, False)

        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=older_than_days)
        ).isoformat()
        with self._connect() as connection:
            runs = connection.execute(
                "DELETE FROM investigation_runs WHERE created_at < ?", (cutoff,)
            ).rowcount
            experiments = connection.execute(
                "DELETE FROM experiments WHERE created_at < ?", (cutoff,)
            ).rowcount
            audit = connection.execute(
                "DELETE FROM audit_events WHERE occurred_at < ?", (cutoff,)
            ).rowcount
            if vacuum:
                connection.commit()
                connection.execute("VACUUM")
        return MaintenanceResult(
            deleted_runs=runs,
            deleted_experiments=experiments,
            deleted_audit_events=audit,
            vacuumed=vacuum,
        )

    def integrity_check(self) -> str:
        with self._connect() as connection:
            row = connection.execute("PRAGMA integrity_check").fetchone()
        return str(row[0])

    def foreign_keys_enabled(self) -> bool:
        with self._connect() as connection:
            row = connection.execute("PRAGMA foreign_keys").fetchone()
        return bool(row[0])

    def optimize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA optimize")
