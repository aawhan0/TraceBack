from dataclasses import dataclass

from app.models.domain import Diagnosis, IncidentScenario


@dataclass(frozen=True)
class EvaluationResult:
    root_cause_match: bool
    evidence_recall: float
    evidence_precision: float
    confidence_valid: bool
    action_present: bool

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
    required = set(scenario.required_evidence_ids)
    selected = set(diagnosis.evidence_ids)
    valid_evidence = {item.id for item in scenario.evidence}

    if required:
        evidence_recall = len(required & selected) / len(required)
    else:
        evidence_recall = 1.0

    if selected:
        evidence_precision = len(selected & valid_evidence) / len(selected)
    else:
        evidence_precision = 1.0 if not required else 0.0

    normalized_root_cause = diagnosis.root_cause.casefold()
    root_cause_match = all(
        keyword.casefold() in normalized_root_cause
        for keyword in scenario.root_cause_keywords
    )

    confidence_valid = 0.0 <= diagnosis.confidence <= 1.0
    action_present = bool(diagnosis.recommended_action.strip())

    return EvaluationResult(
        root_cause_match=root_cause_match,
        evidence_recall=evidence_recall,
        evidence_precision=evidence_precision,
        confidence_valid=confidence_valid,
        action_present=action_present,
    )
