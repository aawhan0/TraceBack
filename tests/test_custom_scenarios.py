from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def _payload(scenario_id: str) -> dict[str, object]:
    return {
        "id": scenario_id,
        "title": "Payment API timeout spike",
        "description": "Checkout requests time out while payment calls are retried.",
        "expected_root_cause": "Payment gateway timeout retry storm",
        "root_cause_keywords": ["payment", "gateway", "retry"],
        "evidence": [
            {
                "id": "ev-payment-001",
                "source": "api",
                "kind": "logs",
                "content": "payment-service: gateway timeout",
            },
            {
                "id": "ev-payment-002",
                "source": "gateway",
                "kind": "metrics",
                "content": "gateway timeout rate increased",
            },
        ],
        "required_evidence_ids": ["ev-payment-001"],
    }


def test_create_custom_scenario_persists_and_lists(monkeypatch, tmp_path):
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "traceback.db"))
    scenario_id = f"payment-timeout-{uuid4().hex[:8]}"
    client = TestClient(app)

    response = client.post("/scenarios", json=_payload(scenario_id))

    assert response.status_code == 201
    assert response.json()["id"] == scenario_id
    listed = client.get("/scenarios")
    assert listed.status_code == 200
    custom = next(item for item in listed.json() if item["id"] == scenario_id)
    assert custom["custom"] is True

    detail = client.get(f"/scenarios/{scenario_id}")
    assert detail.status_code == 200
    assert detail.json()["required_evidence_ids"] == ["ev-payment-001"]


def test_custom_scenario_can_be_investigated(monkeypatch, tmp_path):
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "traceback.db"))
    scenario_id = f"payment-timeout-{uuid4().hex[:8]}"
    client = TestClient(app)
    assert client.post("/scenarios", json=_payload(scenario_id)).status_code == 201

    response = client.post(
        "/investigations",
        json={"scenario_id": scenario_id, "mode": "baseline"},
    )

    assert response.status_code == 200
    assert response.json()["scenario_id"] == scenario_id


def test_custom_scenario_rejects_unknown_required_evidence(monkeypatch, tmp_path):
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "traceback.db"))
    payload = _payload(f"invalid-scenario-{uuid4().hex[:8]}")
    payload["required_evidence_ids"] = ["ev-missing"]

    response = TestClient(app).post("/scenarios", json=payload)

    assert response.status_code == 400
    assert "Required evidence IDs not found" in response.json()["detail"]
