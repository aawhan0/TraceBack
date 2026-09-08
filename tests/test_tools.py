import pytest

from app.agent.contracts import ToolRequest
from app.scenarios.catalog import DATABASE_POOL_EXHAUSTION
from app.tools.scenario import ScenarioEvidenceTool


def test_scenario_tool_lists_all_evidence() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    response = tool.execute(ToolRequest(name=tool.name, arguments={"operation": "list"}))
    assert {item.id for item in response.evidence} == {"ev-db-001", "ev-db-002", "ev-db-003"}


def test_scenario_tool_searches_evidence_content() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    response = tool.execute(ToolRequest(name=tool.name, arguments={"operation": "search", "query": "timeout"}))
    assert [item.id for item in response.evidence] == ["ev-db-001"]


def test_scenario_tool_rejects_unknown_operation() -> None:
    tool = ScenarioEvidenceTool(DATABASE_POOL_EXHAUSTION)
    with pytest.raises(ValueError, match="Unsupported evidence operation"):
        tool.execute(ToolRequest(name=tool.name, arguments={"operation": "delete"}))
