from app.services.jobs import JobStatus, JobStore


def test_jobs_survive_store_reconstruction(tmp_path):
    path = str(tmp_path / "jobs.db")
    first = JobStore(database_path=path)
    job = first.create("database-pool-exhaustion", "baseline")
    first.update(job.job_id, status=JobStatus.RUNNING, attempts=1)

    second = JobStore(database_path=path)
    restored = second.get(job.job_id)

    assert restored is not None
    assert restored.status == JobStatus.RUNNING
    assert restored.attempts == 1


def test_idempotency_returns_same_job(tmp_path):
    store = JobStore(database_path=str(tmp_path / "jobs.db"))
    first = store.create("database-pool-exhaustion", "baseline", idempotency_key="abc")
    second = store.create("database-pool-exhaustion", "baseline", idempotency_key="abc")
    assert first.job_id == second.job_id


def test_invalid_transition_is_rejected(tmp_path):
    import pytest

    store = JobStore(database_path=str(tmp_path / "jobs.db"))
    job = store.create("database-pool-exhaustion", "baseline")

    with pytest.raises(ValueError, match="invalid job transition"):
        store.update(job.job_id, status=JobStatus.COMPLETED)


def test_retry_transition_is_supported(tmp_path):
    store = JobStore(database_path=str(tmp_path / "jobs.db"))
    job = store.create("database-pool-exhaustion", "baseline", max_attempts=3)
    running = store.update(job.job_id, status=JobStatus.RUNNING, attempts=1)
    queued = store.update(running.job_id, status=JobStatus.QUEUED)
    assert queued.status == JobStatus.QUEUED
    assert queued.attempts == 1
