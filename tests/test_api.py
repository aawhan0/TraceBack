from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_scenarios() -> None:
    response = client.get("/scenarios")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_investigation_endpoint_runs_baseline() -> None:
    response = client.post("/investigations", json={"scenario_id": "database-pool-exhaustion"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["passed"] is True
    assert payload["evidence_recall"] == 1.0


def test_unknown_scenario_returns_404() -> None:
    response = client.post("/investigations", json={"scenario_id": "missing"})
    assert response.status_code == 404
