import json
import sqlite3
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from app.models.domain import Diagnosis, InvestigationRun, RunSummary


class RunStore(Protocol):
    def save(self, run: InvestigationRun) -> None:
        """Persist an investigation run."""

    def get(self, run_id: str) -> InvestigationRun | None:
        """Return one run, if it exists."""

    def list(self, scenario_id: str | None = None, limit: int = 50) -> Sequence[RunSummary]:
        """Return recent run summaries."""


class SQLiteRunStore:
    """Small durable run store using SQLite from the Python standard library."""

    def __init__(self, database_path: str = "data/traceback.db") -> None:
        self.database_path = database_path
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS investigation_runs (
                    run_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    diagnosis_json TEXT NOT NULL,
                    root_cause_match INTEGER NOT NULL,
                    evidence_recall REAL NOT NULL,
                    evidence_precision REAL NOT NULL,
                    confidence_valid INTEGER NOT NULL,
                    action_present INTEGER NOT NULL,
                    passed INTEGER NOT NULL,
                    duration_ms REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_investigation_runs_scenario_created
                ON investigation_runs (scenario_id, created_at DESC)
                """
            )

    def save(self, run: InvestigationRun) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO investigation_runs (
                    run_id, scenario_id, mode, provider, diagnosis_json,
                    root_cause_match, evidence_recall, evidence_precision,
                    confidence_valid, action_present, passed, duration_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.scenario_id,
                    run.mode,
                    run.provider,
                    run.diagnosis.model_dump_json(),
                    run.root_cause_match,
                    run.evidence_recall,
                    run.evidence_precision,
                    run.confidence_valid,
                    run.action_present,
                    run.passed,
                    run.duration_ms,
                    run.created_at.isoformat(),
                ),
            )

    def get(self, run_id: str) -> InvestigationRun | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM investigation_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return self._row_to_run(row) if row else None

    def list(self, scenario_id: str | None = None, limit: int = 50) -> Sequence[RunSummary]:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")

        query = "SELECT * FROM investigation_runs"
        parameters: tuple[object, ...] = ()
        if scenario_id:
            query += " WHERE scenario_id = ?"
            parameters = (scenario_id,)
        query += " ORDER BY created_at DESC LIMIT ?"
        parameters += (limit,)

        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()

        return [
            RunSummary(
                run_id=row["run_id"],
                scenario_id=row["scenario_id"],
                mode=row["mode"],
                provider=row["provider"],
                passed=bool(row["passed"]),
                confidence=Diagnosis.model_validate_json(row["diagnosis_json"]).confidence,
                duration_ms=row["duration_ms"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    @staticmethod
    def _row_to_run(row: sqlite3.Row) -> InvestigationRun:
        return InvestigationRun(
            run_id=row["run_id"],
            scenario_id=row["scenario_id"],
            mode=row["mode"],
            provider=row["provider"],
            diagnosis=Diagnosis.model_validate_json(row["diagnosis_json"]),
            root_cause_match=bool(row["root_cause_match"]),
            evidence_recall=row["evidence_recall"],
            evidence_precision=row["evidence_precision"],
            confidence_valid=bool(row["confidence_valid"]),
            action_present=bool(row["action_present"]),
            passed=bool(row["passed"]),
            duration_ms=row["duration_ms"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
