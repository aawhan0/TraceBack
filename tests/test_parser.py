import pytest

from app.agent.parser import (
    AgentActionParseError,
    DiagnosisAction,
    DiagnosisParseError,
    ToolCallAction,
    parse_agent_action,
    parse_diagnosis,
)


def test_parse_diagnosis_accepts_json() -> None:
    diagnosis = parse_diagnosis(
        '{"incident_id":"inc-001","root_cause":"database connection pool exhaustion",'
        '"evidence_ids":["ev-db-001"],"confidence":0.8,'
        '"recommended_action":"Inspect pool usage."}'
    )
    assert diagnosis.incident_id == "inc-001"
    assert diagnosis.confidence == 0.8


def test_parse_diagnosis_accepts_markdown_json_fence() -> None:
    fence = chr(96) * 3
    raw = fence + 'json\n{"incident_id":"inc-001","root_cause":"database",'
    raw += '"evidence_ids":[],"confidence":0.5,"recommended_action":"Investigate."}\n'
    raw += fence
    diagnosis = parse_diagnosis(raw)
    assert diagnosis.root_cause == "database"


@pytest.mark.parametrize("raw", ["", "not json", '{"incident_id":"inc-001"}'])
def test_parse_diagnosis_rejects_invalid_output(raw: str) -> None:
    with pytest.raises(DiagnosisParseError):
        parse_diagnosis(raw)


def test_parse_agent_action_tool_call() -> None:
    action = parse_agent_action(
        '{"type":"tool_call","tool":"scenario_evidence",'
        '"arguments":{"operation":"list"}}'
    )
    assert isinstance(action, ToolCallAction)
    assert action.tool == "scenario_evidence"
    assert action.arguments == {"operation": "list"}


def test_parse_agent_action_diagnosis() -> None:
    action = parse_agent_action(
        '{"type":"diagnosis","incident_id":"inc-001",'
        '"root_cause":"database connection pool exhaustion",'
        '"evidence_ids":["ev-db-001"],"confidence":0.8,'
        '"recommended_action":"Inspect pool usage."}'
    )
    assert isinstance(action, DiagnosisAction)
    assert action.diagnosis.incident_id == "inc-001"
    assert action.diagnosis.evidence_ids == ["ev-db-001"]


def test_parse_agent_action_accepts_markdown_fence() -> None:
    fence = chr(96) * 3
    raw = (
        fence
        + 'json\n{"type":"tool_call","tool":"scenario_evidence",'
        + '"arguments":{"operation":"get","evidence_id":"ev-db-001"}}\n'
        + fence
    )
    action = parse_agent_action(raw)
    assert isinstance(action, ToolCallAction)
    assert action.arguments["evidence_id"] == "ev-db-001"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "not json",
        "[]",
        '{"type":"unknown"}',
        '{"type":"tool_call","tool":"","arguments":{}}',
        '{"type":"tool_call","tool":"scenario_evidence","arguments":{"operation":1}}',
        '{"type":"diagnosis","incident_id":"inc-001"}',
    ],
)
def test_parse_agent_action_rejects_invalid_output(raw: str) -> None:
    with pytest.raises(AgentActionParseError):
        parse_agent_action(raw)
