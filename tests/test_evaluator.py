from app.evaluation.evaluator import evaluate_diagnosis
from app.models.domain import Diagnosis
from app.scenarios.catalog import (
    DATABASE_POOL_EXHAUSTION,
    REDIS_CONNECTIVITY_FAILURE,
)


def test_correct_database_diagnosis_passes() -> None:
    diagnosis = Diagnosis(
        incident_id=DATABASE_POOL_EXHAUSTION.incident.id,
        root_cause="Database connection pool exhaustion",
        evidence_ids=["ev-db-001", "ev-db-002"],
        confidence=0.92,
        recommended_action="Inspect pool sizing and release leaked connections.",
    )

    result = evaluate_diagnosis(DATABASE_POOL_EXHAUSTION, diagnosis)

    assert result.passed
    assert result.root_cause_match
    assert result.evidence_recall == 1.0
    assert result.evidence_precision == 1.0


def test_missing_required_evidence_fails() -> None:
    diagnosis = Diagnosis(
        incident_id=DATABASE_POOL_EXHAUSTION.incident.id,
        root_cause="Database connection pool exhaustion",
        evidence_ids=["ev-db-001"],
        confidence=0.8,
        recommended_action="Inspect database connection usage.",
    )

    result = evaluate_diagnosis(DATABASE_POOL_EXHAUSTION, diagnosis)

    assert not result.passed
    assert result.evidence_recall == 0.5


def test_irrelevant_evidence_reduces_precision() -> None:
    diagnosis = Diagnosis(
        incident_id=REDIS_CONNECTIVITY_FAILURE.incident.id,
        root_cause="Redis connectivity failure caused by network policy",
        evidence_ids=["ev-redis-001", "not-real"],
        confidence=0.8,
        recommended_action="Inspect the network policy.",
    )

    result = evaluate_diagnosis(REDIS_CONNECTIVITY_FAILURE, diagnosis)

    assert not result.passed
    assert result.evidence_precision == 0.5


def test_root_cause_mismatch_fails() -> None:
    diagnosis = Diagnosis(
        incident_id=REDIS_CONNECTIVITY_FAILURE.incident.id,
        root_cause="Database connection pool exhaustion",
        evidence_ids=["ev-redis-001", "ev-redis-003"],
        confidence=0.8,
        recommended_action="Inspect the service.",
    )

    result = evaluate_diagnosis(REDIS_CONNECTIVITY_FAILURE, diagnosis)

    assert not result.passed
    assert not result.root_cause_match
