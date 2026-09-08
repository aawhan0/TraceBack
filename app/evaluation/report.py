from dataclasses import dataclass

from app.evaluation.evaluator import EvaluationResult
from app.models.domain import Diagnosis


@dataclass(frozen=True)
class EvaluationReport:
    diagnosis: Diagnosis
    evaluation: EvaluationResult

    @property
    def summary(self) -> str:
        status = "PASS" if self.evaluation.passed else "FAIL"
        return (
            f"{status}: root_cause={self.evaluation.root_cause_match}, "
            f"recall={self.evaluation.evidence_recall:.2f}, "
            f"precision={self.evaluation.evidence_precision:.2f}"
        )
