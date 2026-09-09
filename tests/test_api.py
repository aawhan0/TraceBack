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


def test_investigation_result_is_persisted_and_retrievable(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "api.db"))
    response = client.post("/investigations", json={"scenario_id": "database-pool-exhaustion"})
    assert response.status_code == 200

    payload = response.json()
    run_id = payload["run_id"]

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["run_id"] == run_id
    assert detail.json()["diagnosis"]["incident_id"] == "inc-001"

    history = client.get("/runs", params={"scenario_id": "database-pool-exhaustion"})
    assert history.status_code == 200
    assert history.json()[0]["run_id"] == run_id

    stats = client.get("/runs/stats", params={"scenario_id": "database-pool-exhaustion"})
    assert stats.status_code == 200
    assert stats.json()["total_runs"] == 1
    assert stats.json()["passed_runs"] == 1


def test_missing_run_returns_404() -> None:
    response = client.get("/runs/does-not-exist")
    assert response.status_code == 404


def test_unknown_scenario_returns_404() -> None:
    response = client.post("/investigations", json={"scenario_id": "missing"})
    assert response.status_code == 404


def test_experiment_endpoint_runs_repeatable_baseline(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "experiment.db"))
    response = client.post(
        "/experiments",
        json={
            "name": "api-smoke",
            "scenario_ids": ["database-pool-exhaustion", "redis-connectivity-failure"],
            "repetitions": 2,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_runs"] == 4
    assert payload["passed_runs"] == 4
    assert payload["pass_rate"] == 1.0
    assert len(payload["scenario_pass_rates"]) == 2
    assert payload["provenance"]["provider"] == "baseline"
    assert payload["provenance"]["model"] is None


def test_experiment_endpoint_rejects_unknown_scenario() -> None:
    response = client.post(
        "/experiments",
        json={"name": "invalid", "scenario_ids": ["missing"], "repetitions": 1},
    )
    assert response.status_code == 404


def test_experiment_history_and_detail_are_persisted(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "benchmark.db"))
    response = client.post(
        "/experiments",
        json={
            "name": "history-smoke",
            "scenario_ids": ["database-pool-exhaustion"],
            "repetitions": 2,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["experiment_id"]
    assert payload["regression_passed"] is True
    assert payload["pass_rate_interval_lower"] < 1.0

    history = client.get("/experiments")
    assert history.status_code == 200
    assert history.json()[0]["experiment_id"] == payload["experiment_id"]

    detail = client.get(f"/experiments/{payload['experiment_id']}")
    assert detail.status_code == 200
    assert detail.json()["dataset_fingerprint"] == payload["dataset_fingerprint"]
    assert detail.json()["provenance"]["git_revision"]


def test_missing_experiment_returns_404(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "missing.db"))
    response = client.get("/experiments/missing")
    assert response.status_code == 404


def test_core_dataset_endpoint_is_versioned() -> None:
    response = client.get("/datasets/core")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "core-scenarios"
    assert payload["version"] == "1"
    assert payload["case_count"] == 3
    assert len(payload["fingerprint"]) == 64
