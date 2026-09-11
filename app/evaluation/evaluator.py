from dataclasses import dataclass
from typing import FrozenSet

from app.models.domain import Diagnosis, IncidentScenario


@dataclass(frozen=True)
class EvaluationResult:
    root_cause_match: bool
    evidence_recall: float
    evidence_precision: float
    confidence_valid: bool
    action_present: bool
    missing_root_cause_keywords: FrozenSet[str]
    missing_evidence_ids: FrozenSet[str]
    invalid_evidence_ids: FrozenSet[str]

    @property
    def passed(self) -> bool:
        return (
            self.root_cause_match
            and self.evidence_recall == 1.0
            and self.evidence_precision == 1.0
            and self.confidence_valid
            and self.action_present
        )


def evaluate_diagnosis(
    scenario: IncidentScenario,
    diagnosis: Diagnosis,
) -> EvaluationResult:
    """
    Evaluate an LLM diagnosis against the expected incident scenario.

    The evaluator checks:

    - Diagnosis belongs to the expected incident.
    - All required evidence was selected.
    - Every selected evidence ID is valid.
    - Root-cause keywords are present.
    - Confidence is within the range [0, 1].
    - A recommended action was provided.

    The evaluator does not modify or normalize the model's diagnosis.
    """

    if diagnosis.incident_id != scenario.incident.id:
        raise ValueError("Diagnosis does not belong to the scenario")

    required_evidence_ids = set(scenario.required_evidence_ids)
    selected_evidence_ids = set(diagnosis.evidence_ids)
    valid_evidence_ids = {
        evidence.id
        for evidence in scenario.evidence
    }

    missing_evidence_ids = frozenset(
        required_evidence_ids - selected_evidence_ids
    )

    invalid_evidence_ids = frozenset(
        selected_evidence_ids - valid_evidence_ids
    )

    evidence_recall = (
        len(required_evidence_ids & selected_evidence_ids)
        / len(required_evidence_ids)
        if required_evidence_ids
        else 1.0
    )

    evidence_precision = (
        len(selected_evidence_ids & valid_evidence_ids)
        / len(selected_evidence_ids)
        if selected_evidence_ids
        else (1.0 if not required_evidence_ids else 0.0)
    )

    normalized_root_cause = diagnosis.root_cause.casefold()

    missing_root_cause_keywords = frozenset(
        keyword
        for keyword in scenario.root_cause_keywords
        if keyword.casefold() not in normalized_root_cause
    )

    root_cause_match = not missing_root_cause_keywords

    confidence_valid = 0.0 <= diagnosis.confidence <= 1.0

    action_present = bool(
        diagnosis.recommended_action.strip()
    )

    return EvaluationResult(
        root_cause_match=root_cause_match,
        evidence_recall=evidence_recall,
        evidence_precision=evidence_precision,
        confidence_valid=confidence_valid,
        action_present=action_present,
        missing_root_cause_keywords=missing_root_cause_keywords,
        missing_evidence_ids=missing_evidence_ids,
        invalid_evidence_ids=invalid_evidence_ids,
    )