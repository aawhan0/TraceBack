from fastapi.testclient import TestClient
from app.main import create_app

def test_create_job_returns_accepted_job():
    client = TestClient(create_app())
    response = client.post("/jobs", json={"scenario_id": "database-pool-exhaustion"})
    assert response.status_code == 202
    body = response.json()
    assert body["job_id"]
    assert body["status"] in {"queued", "completed"}

def test_create_job_rejects_unknown_scenario():
    client = TestClient(create_app())
    assert client.post("/jobs", json={"scenario_id": "missing"}).status_code == 404

def test_get_missing_job():
    client = TestClient(create_app())
    assert client.get("/jobs/missing").status_code == 404
