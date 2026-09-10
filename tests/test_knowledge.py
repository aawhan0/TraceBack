from fastapi.testclient import TestClient

from app.main import app


def test_knowledge_lists_builtin_scenarios() -> None:
    response = TestClient(app).get("/knowledge")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["root_cause"]


def test_knowledge_search_matches_evidence_content() -> None:
    response = TestClient(app).get("/knowledge", params={"q": "connection pool"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["scenario_id"] == "database-pool-exhaustion"
    assert "connection" in payload[0]["matched_terms"]
    assert "pool" in payload[0]["matched_terms"]


def test_knowledge_search_returns_empty_for_unknown_query() -> None:
    response = TestClient(app).get("/knowledge", params={"q": "unknown failure pattern"})

    assert response.status_code == 200
    assert response.json() == []
