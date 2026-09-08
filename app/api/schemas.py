from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.domain import Diagnosis


class InvestigationRequest(BaseModel):
    scenario_id: str = Field(min_length=1)
    mode: Literal["baseline", "llm"] = "baseline"
    model: str | None = Field(default=None, min_length=1)


class InvestigationResponse(BaseModel):
    scenario_id: str
    mode: Literal["baseline", "llm"]
    provider: str
    diagnosis: Diagnosis
    root_cause_match: bool
    evidence_recall: float
    evidence_precision: float
    confidence_valid: bool
    action_present: bool
    passed: bool
    run_id: str
    duration_ms: float
    created_at: datetime
