import pytest

from app.agent.contracts import ToolRequest
from app.scenarios.catalog import DATABASE_POOL_EXHAUSTION
from app.tools.scenario import ScenarioEvidenceTool


def test_scenario_tool_lists_metadata_without_content() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    response = tool.execute(ToolRequest(name=tool.name, arguments={"operation": "list"}))
    assert {item.id for item in response.evidence} == {"ev-db-001", "ev-db-002", "ev-db-003"}
    assert all(item.content == "" for item in response.evidence)
    assert {(item.id, item.source, item.kind) for item in response.evidence} == {
        ("ev-db-001", "api", "logs"),
        ("ev-db-002", "database", "metrics"),
        ("ev-db-003", "api", "logs"),
    }


def test_scenario_tool_get_returns_full_content() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    response = tool.execute(
        ToolRequest(name=tool.name, arguments={"operation": "get", "evidence_id": "ev-db-001"})
    )
    assert len(response.evidence) == 1
    assert response.evidence[0].id == "ev-db-001"
    assert "timeout acquiring database connection" in response.evidence[0].content


def test_scenario_tool_get_unknown_id_returns_empty() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    response = tool.execute(
        ToolRequest(name=tool.name, arguments={"operation": "get", "evidence_id": "missing"})
    )
    assert response.evidence == ()


def test_scenario_tool_searches_evidence_content() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    response = tool.execute(
        ToolRequest(name=tool.name, arguments={"operation": "search", "query": "timeout"})
    )
    assert [item.id for item in response.evidence] == ["ev-db-001"]
    assert response.evidence[0].content


def test_scenario_tool_rejects_unknown_operation() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    with pytest.raises(ValueError, match="Unsupported evidence operation"):
        tool.execute(ToolRequest(name=tool.name, arguments={"operation": "delete"}))
