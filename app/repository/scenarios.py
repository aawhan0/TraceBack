from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock

from app.models.domain import IncidentScenario


class SQLiteScenarioStore:
    """Durable repository for user-authored investigation scenarios."""

    def __init__(self, database_path: str = "data/traceback.db") -> None:
        self.database_path = database_path
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS custom_scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )

    def create(self, scenario: IncidentScenario) -> IncidentScenario:
        with self._lock, self._connect() as db:
            try:
                db.execute(
                    "INSERT INTO custom_scenarios (scenario_id, data) VALUES (?, ?)",
                    (scenario.id, scenario.model_dump_json()),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"Scenario already exists: {scenario.id}") from exc
        return scenario

    def get(self, scenario_id: str) -> IncidentScenario | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT data FROM custom_scenarios WHERE scenario_id = ?", (scenario_id,)
            ).fetchone()
        return IncidentScenario.model_validate_json(row["data"]) if row else None

    def list(self) -> list[IncidentScenario]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT data FROM custom_scenarios ORDER BY scenario_id ASC"
            ).fetchall()
        return [IncidentScenario.model_validate_json(row["data"]) for row in rows]
