from pydantic import BaseModel, Field

from app.models.domain import Diagnosis


class InvestigationRequest(BaseModel):
    scenario_id: str = Field(min_length=1)


class InvestigationResponse(BaseModel):
    scenario_id: str
    diagnosis: Diagnosis
    root_cause_match: bool
    evidence_recall: float
    evidence_precision: float
    confidence_valid: bool
    action_present: bool
    passed: bool
