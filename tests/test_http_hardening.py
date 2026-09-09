from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_request_id() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_health_preserves_client_request_id() -> None:
    response = client.get("/health", headers={"X-Request-ID": "test-request-123"})
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_ready_reports_database_health(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "ready.db"))
    from app.api.dependencies import reset_settings_cache

    reset_settings_cache()
    response = client.get("/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "traceback"
    assert payload["status"] == "ok"
    assert payload["checks"][0]["name"] == "database"


def test_invalid_json_shape_returns_structured_error() -> None:
    response = client.post(
        "/investigations",
        json={"scenario_id": "", "mode": "unknown"},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"
    assert payload["request_id"]
    assert payload["details"]["errors"]

def test_security_headers_are_present() -> None:
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"


def test_invalid_request_id_is_replaced() -> None:
    response = client.get("/health", headers={"X-Request-ID": "\x00bad"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Request-ID"] != "\x00bad"
