from app.services.jobs import JobStatus, JobStore

def test_job_store_lifecycle_fields_are_preserved():
    store = JobStore(max_jobs=4)
    job = store.create("database-pool-exhaustion", "baseline")
    updated = store.update(job.job_id, status=JobStatus.RUNNING, execution_id="exec-1")
    assert updated.status == JobStatus.RUNNING
    assert updated.execution_id == "exec-1"
    assert store.get(job.job_id) == updated

def test_job_store_rejects_invalid_limits():
    store = JobStore()
    try:
        store.list(0)
    except ValueError as exc:
        assert "between 1 and 200" in str(exc)
    else:
        raise AssertionError("expected ValueError")

def test_job_store_prunes_terminal_jobs_when_full():
    store = JobStore(max_jobs=2)
    first = store.create("database-pool-exhaustion", "baseline")
    store.update(first.job_id, status=JobStatus.COMPLETED)
    store.create("redis-connectivity-failure", "baseline")
    third = store.create("runaway-worker-cpu", "baseline")
    assert store.get(third.job_id) is not None
