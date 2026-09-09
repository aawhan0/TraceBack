from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from app.evaluation.experiments import ExperimentResult
from app.evaluation.provenance import BenchmarkProvenance
from app.evaluation.regression import RegressionReport


@dataclass(frozen=True)
class ExperimentRecord:
    experiment_id: str
    name: str
    dataset_name: str
    dataset_version: str
    dataset_fingerprint: str
    result: ExperimentResult
    regression: RegressionReport | None
    created_at: datetime
    provenance: BenchmarkProvenance | None = None


class ExperimentStore(Protocol):
    def save(self, record: ExperimentRecord) -> None:
        """Persist an experiment record."""

    def get(self, experiment_id: str) -> ExperimentRecord | None:
        """Load one experiment record."""

    def list(self, limit: int = 50) -> list[ExperimentRecord]:
        """Return recent experiment records."""


class SQLiteExperimentStore:
    """Durable storage for benchmark metadata, outcomes, and provenance."""

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
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    dataset_version TEXT NOT NULL,
                    dataset_fingerprint TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    regression_json TEXT,
                    provenance_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(experiments)").fetchall()
            }
            if "provenance_json" not in columns:
                connection.execute("ALTER TABLE experiments ADD COLUMN provenance_json TEXT")
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_experiments_created
                ON experiments (created_at DESC)
                """
            )

    def save(self, record: ExperimentRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO experiments (
                    experiment_id, name, dataset_name, dataset_version,
                    dataset_fingerprint, result_json, regression_json,
                    provenance_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.experiment_id,
                    record.name,
                    record.dataset_name,
                    record.dataset_version,
                    record.dataset_fingerprint,
                    json.dumps(_result_to_dict(record.result), sort_keys=True),
                    json.dumps(_regression_to_dict(record.regression), sort_keys=True)
                    if record.regression is not None
                    else None,
                    json.dumps(record.provenance.as_dict(), sort_keys=True)
                    if record.provenance is not None
                    else None,
                    record.created_at.isoformat(),
                ),
            )

    def get(self, experiment_id: str) -> ExperimentRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM experiments WHERE experiment_id = ?",
                (experiment_id,),
            ).fetchone()
        return _row_to_record(row) if row else None

    def list(self, limit: int = 50) -> list[ExperimentRecord]:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM experiments ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_record(row) for row in rows]


def _result_to_dict(result: ExperimentResult) -> dict[str, object]:
    return {
        "name": result.name,
        "total_runs": result.total_runs,
        "passed_runs": result.passed_runs,
        "pass_rate": result.pass_rate,
        "average_confidence": result.average_confidence,
        "average_duration_ms": result.average_duration_ms,
        "scenario_pass_rates": result.scenario_pass_rates,
    }


def _regression_to_dict(report: RegressionReport | None) -> dict[str, object] | None:
    if report is None:
        return None
    return {
        "passed": report.passed,
        "failures": [
            {
                "metric": item.metric,
                "actual": item.actual,
                "expected": item.expected,
                "direction": item.direction,
                "message": item.message,
            }
            for item in report.failures
        ],
        "pass_rate_interval_lower": report.pass_rate_interval_lower,
        "pass_rate_interval_upper": report.pass_rate_interval_upper,
    }


def _provenance_from_row(row: sqlite3.Row) -> BenchmarkProvenance | None:
    value = row["provenance_json"]
    if not value:
        return None
    data = json.loads(value)
    return BenchmarkProvenance(**data)


def _row_to_record(row: sqlite3.Row) -> ExperimentRecord:
    result_data = json.loads(row["result_json"])
    result = ExperimentResult(
        name=result_data["name"],
        total_runs=result_data["total_runs"],
        passed_runs=result_data["passed_runs"],
        pass_rate=result_data["pass_rate"],
        average_confidence=result_data["average_confidence"],
        average_duration_ms=result_data["average_duration_ms"],
        scenario_pass_rates=result_data["scenario_pass_rates"],
    )
    regression_data = json.loads(row["regression_json"]) if row["regression_json"] else None
    regression = None
    if regression_data:
        from app.evaluation.regression import RegressionFailure, RegressionReport

        regression = RegressionReport(
            passed=regression_data["passed"],
            failures=tuple(
                RegressionFailure(**failure) for failure in regression_data["failures"]
            ),
            pass_rate_interval_lower=regression_data["pass_rate_interval_lower"],
            pass_rate_interval_upper=regression_data["pass_rate_interval_upper"],
        )
    return ExperimentRecord(
        experiment_id=row["experiment_id"],
        name=row["name"],
        dataset_name=row["dataset_name"],
        dataset_version=row["dataset_version"],
        dataset_fingerprint=row["dataset_fingerprint"],
        result=result,
        regression=regression,
        created_at=datetime.fromisoformat(row["created_at"]),
        provenance=_provenance_from_row(row),
    )
