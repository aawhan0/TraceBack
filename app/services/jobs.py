from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from threading import Lock
from uuid import uuid4

class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

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

class JobStore:
    """Bounded, thread-safe execution-state registry."""
    def __init__(self, max_jobs: int = 1000) -> None:
        if max_jobs <= 0:
            raise ValueError("max_jobs must be positive")
        self.max_jobs = max_jobs
        self._jobs: dict[str, InvestigationJob] = {}
        self._lock = Lock()

    def create(self, scenario_id: str, mode: str, model: str | None = None) -> InvestigationJob:
        job = InvestigationJob(str(uuid4()), scenario_id, mode, model, JobStatus.QUEUED,
                               datetime.now(timezone.utc))
        with self._lock:
            self._prune_completed()
            if len(self._jobs) >= self.max_jobs:
                raise RuntimeError("job queue is full")
            self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> InvestigationJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **changes: object) -> InvestigationJob:
        with self._lock:
            current = self._jobs.get(job_id)
            if current is None:
                raise KeyError(job_id)
            updated = InvestigationJob(**{**current.__dict__, **changes})
            self._jobs[job_id] = updated
            return updated

    def list(self, limit: int = 50) -> list[InvestigationJob]:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        with self._lock:
            return sorted(self._jobs.values(), key=lambda item: item.created_at, reverse=True)[:limit]

    def _prune_completed(self) -> None:
        if len(self._jobs) < self.max_jobs:
            return
        terminal = sorted(
            (j for j in self._jobs.values() if j.status in {JobStatus.COMPLETED, JobStatus.FAILED}),
            key=lambda item: item.created_at,
        )
        for job in terminal[: max(1, len(terminal) // 4)]:
            self._jobs.pop(job.job_id, None)
