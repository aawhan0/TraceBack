from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from threading import Lock
from uuid import uuid4


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


TERMINAL_STATUSES = {JobStatus.COMPLETED, JobStatus.FAILED}
ALLOWED_TRANSITIONS = {
    JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.FAILED},
    JobStatus.RUNNING: {JobStatus.QUEUED, JobStatus.COMPLETED, JobStatus.FAILED},
    JobStatus.COMPLETED: set(),
    JobStatus.FAILED: set(),
}


@dataclass(frozen=True)
class InvestigationJob:
    job_id: str
    scenario_id: str
    mode: str
    model: str | None
    status: JobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    run_id: str | None = None
    execution_id: str | None = None
    trace_id: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    attempts: int = 0
    max_attempts: int = 2
    idempotency_key: str | None = None


class JobStore:
    """Durable, bounded and thread-safe execution-state repository."""

    def __init__(self, max_jobs: int = 1000, database_path: str = "data/traceback.db") -> None:
        if max_jobs <= 0:
            raise ValueError("max_jobs must be positive")
        if max_jobs > 100_000:
            raise ValueError("max_jobs is unreasonably large")
        self.max_jobs = max_jobs
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
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS investigation_jobs (
                    job_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    model TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    run_id TEXT,
                    execution_id TEXT,
                    trace_id TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 2,
                    idempotency_key TEXT UNIQUE
                )
                """
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON investigation_jobs(created_at DESC)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON investigation_jobs(status)")

    @staticmethod
    def _parse(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    @classmethod
    def _from_row(cls, row: sqlite3.Row) -> InvestigationJob:
        return InvestigationJob(
            job_id=row["job_id"],
            scenario_id=row["scenario_id"],
            mode=row["mode"],
            model=row["model"],
            status=JobStatus(row["status"]),
            created_at=cls._parse(row["created_at"]),  # type: ignore[arg-type]
            started_at=cls._parse(row["started_at"]),
            completed_at=cls._parse(row["completed_at"]),
            run_id=row["run_id"],
            execution_id=row["execution_id"],
            trace_id=row["trace_id"],
            error_type=row["error_type"],
            error_message=row["error_message"],
            attempts=row["attempts"],
            max_attempts=row["max_attempts"],
            idempotency_key=row["idempotency_key"],
        )

    def create(self, scenario_id: str, mode: str, model: str | None = None, *,
               idempotency_key: str | None = None, max_attempts: int = 2) -> InvestigationJob:
        if max_attempts < 1 or max_attempts > 5:
            raise ValueError("max_attempts must be between 1 and 5")
        with self._lock, self._connect() as db:
            if idempotency_key:
                existing = db.execute(
                    "SELECT * FROM investigation_jobs WHERE idempotency_key = ?", (idempotency_key,)
                ).fetchone()
                if existing:
                    return self._from_row(existing)
            count = db.execute(
                "SELECT COUNT(*) FROM investigation_jobs WHERE status NOT IN ('completed', 'failed')"
            ).fetchone()[0]
            if count >= self.max_jobs:
                terminal_count = db.execute(
                    "SELECT COUNT(*) FROM investigation_jobs WHERE status IN ('completed', 'failed')"
                ).fetchone()[0]
                if terminal_count:
                    prune_count = max(1, terminal_count // 4)
                    rows = db.execute(
                        """SELECT job_id FROM investigation_jobs
                        WHERE status IN ('completed', 'failed')
                        ORDER BY created_at ASC LIMIT ?""",
                        (prune_count,),
                    ).fetchall()
                    for row in rows:
                        db.execute("DELETE FROM investigation_jobs WHERE job_id = ?", (row["job_id"],))
                    count = db.execute(
                        "SELECT COUNT(*) FROM investigation_jobs WHERE status NOT IN ('completed', 'failed')"
                    ).fetchone()[0]
            if count >= self.max_jobs:
                raise RuntimeError("job queue is full")
            now = datetime.now(timezone.utc)
            job = InvestigationJob(
                job_id=str(uuid4()), scenario_id=scenario_id, mode=mode, model=model,
                status=JobStatus.QUEUED, created_at=now, max_attempts=max_attempts,
                idempotency_key=idempotency_key,
            )
            db.execute(
                """INSERT INTO investigation_jobs
                (job_id, scenario_id, mode, model, status, created_at, attempts, max_attempts, idempotency_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (job.job_id, job.scenario_id, job.mode, job.model, job.status.value,
                 now.isoformat(), 0, max_attempts, idempotency_key),
            )
            return job

    def get(self, job_id: str) -> InvestigationJob | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM investigation_jobs WHERE job_id = ?", (job_id,)).fetchone()
        return self._from_row(row) if row else None

    def get_by_idempotency_key(self, key: str) -> InvestigationJob | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM investigation_jobs WHERE idempotency_key = ?", (key,)).fetchone()
        return self._from_row(row) if row else None

    def update(self, job_id: str, **changes: object) -> InvestigationJob:
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM investigation_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            current = self._from_row(row)
            target = changes.get("status", current.status)
            target = JobStatus(target) if isinstance(target, str) else target
            if target != current.status and target not in ALLOWED_TRANSITIONS[current.status]:
                raise ValueError(f"invalid job transition: {current.status.value} -> {target.value}")

            values = {
                "scenario_id": current.scenario_id, "mode": current.mode, "model": current.model,
                "status": target.value, "created_at": current.created_at.isoformat(),
                "started_at": current.started_at.isoformat() if current.started_at else None,
                "completed_at": current.completed_at.isoformat() if current.completed_at else None,
                "run_id": current.run_id, "execution_id": current.execution_id, "trace_id": current.trace_id,
                "error_type": current.error_type, "error_message": current.error_message,
                "attempts": current.attempts, "max_attempts": current.max_attempts,
                "idempotency_key": current.idempotency_key,
            }
            for key, value in changes.items():
                if key not in values:
                    raise ValueError(f"unknown job field: {key}")
                if isinstance(value, datetime):
                    value = value.isoformat()
                if isinstance(value, JobStatus):
                    value = value.value
                values[key] = value
            db.execute(
                """UPDATE investigation_jobs SET scenario_id=?, mode=?, model=?, status=?,
                created_at=?, started_at=?, completed_at=?, run_id=?, execution_id=?,
                trace_id=?, error_type=?, error_message=?, attempts=?, max_attempts=?,
                idempotency_key=? WHERE job_id=?""",
                (*values.values(), job_id),
            )
            updated = db.execute("SELECT * FROM investigation_jobs WHERE job_id = ?", (job_id,)).fetchone()
        return self._from_row(updated)

    def list(self, limit: int = 50) -> list[InvestigationJob]:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM investigation_jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def prune_terminal(self, keep: int | None = None) -> int:
        keep = self.max_jobs if keep is None else keep
        if keep < 0:
            raise ValueError("keep must be non-negative")
        with self._lock, self._connect() as db:
            rows = db.execute(
                """SELECT job_id FROM investigation_jobs
                WHERE status IN ('completed', 'failed')
                ORDER BY created_at DESC LIMIT -1 OFFSET ?""", (keep,)
            ).fetchall()
            for row in rows:
                db.execute("DELETE FROM investigation_jobs WHERE job_id = ?", (row["job_id"],))
            return len(rows)
