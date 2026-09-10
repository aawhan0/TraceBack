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
    assert payload["root_cause_accuracy"] == 1.0
    assert payload["average_evidence_recall"] == 1.0
    assert payload["average_evidence_precision"] == 1.0
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
    assert payload["root_cause_accuracy"] == 1.0
    assert payload["average_evidence_recall"] == 1.0
    assert payload["average_evidence_precision"] == 1.0

    history = client.get("/experiments")
    assert history.status_code == 200
    assert history.json()[0]["experiment_id"] == payload["experiment_id"]

    detail = client.get(f"/experiments/{payload['experiment_id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["dataset_fingerprint"] == payload["dataset_fingerprint"]
    assert body["root_cause_accuracy"] == 1.0
    assert body["average_evidence_recall"] == 1.0
    assert body["average_evidence_precision"] == 1.0
    assert body["provenance"]["git_revision"]


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


def test_experiment_comparison_endpoint_returns_deltas(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "compare.db"))
    payload = {
        "name": "comparison-smoke",
        "scenario_ids": ["database-pool-exhaustion"],
        "repetitions": 1,
    }
    first = client.post("/experiments", json=payload)
    second = client.post("/experiments", json={**payload, "name": "comparison-candidate"})
    assert first.status_code == 200
    assert second.status_code == 200

    comparison = client.get(
        f"/experiments/{first.json()['experiment_id']}/compare/{second.json()['experiment_id']}"
    )
    assert comparison.status_code == 200
    body = comparison.json()
    assert body["dataset"]["fingerprint"] == first.json()["dataset_fingerprint"]
    assert body["metrics"]["pass_rate"]["delta"] == 0.0
    assert body["metrics"]["root_cause_accuracy"]["delta"] == 0.0
    assert body["metrics"]["evidence_recall"]["delta"] == 0.0
    assert body["metrics"]["evidence_precision"]["delta"] == 0.0
    assert body["verdict"] == "unchanged"


def test_experiment_comparison_endpoint_rejects_missing_experiment() -> None:
    response = client.get("/experiments/missing/compare/also-missing")
    assert response.status_code == 404


def test_experiment_matrix_endpoint_runs_shared_dataset(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "matrix.db"))
    response = client.post(
        "/experiments/matrix",
        json={
            "matrix_id": "api-matrix",
            "scenario_ids": ["database-pool-exhaustion"],
            "configurations": [
                {"name": "baseline", "mode": "baseline"},
                {"name": "candidate", "mode": "baseline"},
            ],
            "repetitions": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["matrix_id"] == "api-matrix"
    assert len(payload["experiment_ids"]) == 2
    assert payload["best_experiment_id"] in payload["experiment_ids"]
    assert len(payload["comparisons"]) == 1
    assert payload["dataset_name"] == "core-scenarios"


def test_experiment_matrix_rejects_duplicate_configuration_names() -> None:
    response = client.post(
        "/experiments/matrix",
        json={
            "matrix_id": "invalid",
            "scenario_ids": ["database-pool-exhaustion"],
            "configurations": [
                {"name": "same"},
                {"name": "same"},
            ],
        },
    )
    assert response.status_code == 400
