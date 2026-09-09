from __future__ import annotations

from app.services.jobs import InvestigationJob, JobStore


class JobRepository:
    """Application-facing facade around durable job storage."""

    def __init__(self, store: JobStore | None = None) -> None:
        self.store = store or JobStore()

    def create(self, *args, **kwargs) -> InvestigationJob:
        return self.store.create(*args, **kwargs)

    def get(self, job_id: str) -> InvestigationJob | None:
        return self.store.get(job_id)

    def list(self, limit: int = 50) -> list[InvestigationJob]:
        return self.store.list(limit)

    def update(self, job_id: str, **changes) -> InvestigationJob:
        return self.store.update(job_id, **changes)

    def prune(self, keep: int | None = None) -> int:
        return self.store.prune_terminal(keep)
