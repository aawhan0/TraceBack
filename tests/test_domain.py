import pytest
from pydantic import ValidationError

from app.models.domain import Diagnosis, Evidence, Incident


def test_diagnosis_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        Diagnosis(
            incident_id="inc-1",
            root_cause="unknown",
            confidence=1.1,
            recommended_action="investigate",
        )


def test_evidence_rejects_invalid_relevance() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            id="ev-1",
            source="api",
            kind="logs",
            content="error",
            relevance=-0.1,
        )


def test_incident_has_safe_default_status() -> None:
    incident = Incident(id="inc-1", title="Test", description="Test")

    assert incident.status == "open"
