from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel, Field

from app.scenarios.catalog import get_scenario
from app.services.job_runner import InvestigationJobRunner
from app.services.jobs import InvestigationJob, JobStatus, JobStore

router = APIRouter(prefix="/jobs", tags=["jobs"])
_store = JobStore()
_runner = InvestigationJobRunner(_store)


class JobRequest(BaseModel):
    scenario_id: str
    mode: str = Field(default="baseline", pattern="^(baseline|llm)$")
    model: str | None = None
    max_attempts: int = Field(default=2, ge=1, le=5)


class JobResponse(BaseModel):
    job_id: str
    scenario_id: str
    mode: str
    model: str | None
    status: JobStatus
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    run_id: str | None = None
    execution_id: str | None = None
    trace_id: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    attempts: int = 0
    max_attempts: int = 2


def _response(job: InvestigationJob) -> JobResponse:
    return JobResponse(
        job_id=job.job_id,
        scenario_id=job.scenario_id,
        mode=job.mode,
        model=job.model,
        status=job.status,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        run_id=job.run_id,
        execution_id=job.execution_id,
        trace_id=job.trace_id,
        error_type=job.error_type,
        error_message=job.error_message,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
    )


@router.post("", response_model=JobResponse, status_code=202)
def create_job(
    request: JobRequest,
    background_tasks: BackgroundTasks,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JobResponse:
    try:
        get_scenario(request.scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Scenario not found") from exc
    try:
        job = _store.create(
            request.scenario_id,
            request.mode,
            request.model,
            idempotency_key=idempotency_key,
            max_attempts=request.max_attempts,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if job.status == JobStatus.QUEUED and job.attempts == 0:
        background_tasks.add_task(_runner.run, job.job_id)
    return _response(job)


@router.get("", response_model=list[JobResponse])
def list_jobs(limit: int = 50) -> list[JobResponse]:
    try:
        return [_response(job) for job in _store.list(limit)]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    job = _store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _response(job)
