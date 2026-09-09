from fastapi.testclient import TestClient

from app.main import create_app


def test_dashboard_is_available():
    response = TestClient(create_app()).get("/ui")
    assert response.status_code == 200
    assert "Traceback" in response.text
    assert "/investigations" in response.text
    assert "/jobs?limit=10" in response.text
    assert "/runs?limit=10" in response.text
