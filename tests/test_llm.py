import pytest

from app.agent.llm import LLMInvestigator
from app.providers.mock import MockLLMProvider
from app.scenarios.catalog import DATABASE_POOL_EXHAUSTION


def test_llm_investigator_uses_provider_and_returns_diagnosis() -> None:
    scenario = DATABASE_POOL_EXHAUSTION
    provider = MockLLMProvider(
        {
            "incident_id": scenario.incident.id,
            "root_cause": scenario.expected_root_cause,
            "evidence_ids": scenario.required_evidence_ids,
            "confidence": 0.91,
            "recommended_action": "Inspect pool sizing and connection leaks.",
        }
    )
    diagnosis = LLMInvestigator(scenario, provider).investigate(scenario.incident)
    assert diagnosis.root_cause == scenario.expected_root_cause
    assert diagnosis.evidence_ids == scenario.required_evidence_ids


def test_llm_investigator_rejects_wrong_incident() -> None:
    scenario = DATABASE_POOL_EXHAUSTION
    provider = MockLLMProvider({})
    other = scenario.incident.model_copy(update={"id": "other"})
    with pytest.raises(ValueError, match="does not belong"):
        LLMInvestigator(scenario, provider).investigate(other)
