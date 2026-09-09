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


class ExperimentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scenario_ids: list[str] = Field(min_length=1, max_length=20)
    repetitions: int = Field(default=1, ge=1, le=100)


class ExperimentResponse(BaseModel):
    name: str
    total_runs: int
    passed_runs: int
    pass_rate: float
    average_confidence: float
    average_duration_ms: float
    scenario_pass_rates: dict[str, float]
