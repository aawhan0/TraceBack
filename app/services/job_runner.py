from __future__ import annotations

from datetime import datetime, timezone

from app.config import Settings
from app.providers.ollama import OllamaProvider
from app.scenarios.catalog import get_scenario
from app.services.investigation import InvestigationService
from app.observability.events import TraceContext, TraceSpan\nfrom app.services.jobs import JobStatus, JobStore


class InvestigationJobRunner:
    """Executes jobs with durable lifecycle state and bounded retries."""

    def __init__(self, store: JobStore) -> None:
        self.store = store

    def run(self, job_id: str) -> None:
        job = self.store.get(job_id)
        if job is None:
            raise KeyError(job_id)

        while job.attempts < job.max_attempts:
            job = self.store.update(
                job_id,
                status=JobStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
                attempts=job.attempts + 1,
            )
            try:
                scenario = get_scenario(job.scenario_id)
                service = InvestigationService()
                if job.mode == "llm":
                    settings = Settings.from_environment()
                    provider = OllamaProvider(
                        job.model or settings.model,
                        settings.ollama_base_url,
                        settings.ollama_timeout,
                    )
                    result = service.investigate(scenario, provider=provider)
                else:
                    result = service.investigate(scenario)
                self.store.update(
                    job_id,
                    status=JobStatus.COMPLETED,
                    completed_at=datetime.now(timezone.utc),
                    run_id=result.run_id,
                    execution_id=result.execution_id,
                    trace_id=result.trace_id,
                    error_type=None,
                    error_message=None,
                )
                return
            except Exception as exc:
                if job.attempts < job.max_attempts:
                    job = self.store.update(
                        job_id,
                        status=JobStatus.QUEUED,
                        error_type=type(exc).__name__,
                        error_message=str(exc),
                    )
                    continue
                self.store.update(
                    job_id,
                    status=JobStatus.FAILED,
                    completed_at=datetime.now(timezone.utc),
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                return
