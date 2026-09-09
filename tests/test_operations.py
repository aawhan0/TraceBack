from fastapi.testclient import TestClient

from app.main import create_app


def test_readiness_endpoint_reports_database() -> None:
    response = TestClient(create_app()).get("/ops/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_database_status_reports_integrity(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "ops.db"))
    response = TestClient(create_app()).get("/ops/database")
    assert response.status_code == 200
    assert response.json()["integrity"] == "ok"
    assert response.json()["foreign_keys"] is False


def test_readiness_checker_reports_failure() -> None:
    from app.services.health import ReadinessChecker

    def fail() -> str:
        raise RuntimeError("offline")

    report = ReadinessChecker({"database": fail}).check()
    assert report.ready is False
    assert report.dependencies[0].healthy is False
