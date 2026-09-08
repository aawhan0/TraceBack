import pytest

from app.agent.parser import DiagnosisParseError, parse_diagnosis


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
