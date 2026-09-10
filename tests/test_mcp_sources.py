import pytest

from app.mcp.sources import load_sources


def test_load_sources_from_json() -> None:
    sources = load_sources(
        '[{"id":"payments","url":"https://example.com/mcp","tool":"get_incident_evidence"}]'
    )

    assert sources[0].id == "payments"
    assert sources[0].url == "https://example.com/mcp"
    assert sources[0].tool == "get_incident_evidence"


def test_load_sources_rejects_duplicate_ids() -> None:
    raw = (
        '[{"id":"payments","url":"https://one.example/mcp"},'
        '{"id":"payments","url":"https://two.example/mcp"}]'
    )

    with pytest.raises(ValueError, match="unique"):
        load_sources(raw)


def test_load_sources_rejects_non_http_url() -> None:
    with pytest.raises(ValueError, match="Unsupported MCP source URL"):
        load_sources('[{"id":"local","url":"file:///tmp/evidence"}]')


def test_load_sources_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="valid JSON"):
        load_sources("not-json")
