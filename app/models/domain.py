from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Incident(BaseModel):
    id: str
    title: str
    description: str
    status: Literal["open", "investigating", "resolved"] = "open"
    created_at: datetime | None = None


class Evidence(BaseModel):
    id: str
    source: str
    kind: str
    content: str
    timestamp: datetime | None = None
    relevance: float | None = Field(default=None, ge=0, le=1)


class Diagnosis(BaseModel):
    incident_id: str
    root_cause: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    recommended_action: str = Field(min_length=1)


class IncidentScenario(BaseModel):
    id: str
    incident: Incident
    evidence: list[Evidence]
    expected_root_cause: str
    root_cause_keywords: list[str] = Field(min_length=1)
    required_evidence_ids: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class InvestigationRun(BaseModel):
    run_id: str
    scenario_id: str
    mode: Literal["baseline", "llm"]
    provider: str
    diagnosis: Diagnosis
    root_cause_match: bool
    evidence_recall: float = Field(ge=0, le=1)
    evidence_precision: float = Field(ge=0, le=1)
    confidence_valid: bool
    action_present: bool
    passed: bool
    duration_ms: float = Field(ge=0)
    created_at: datetime


class RunSummary(BaseModel):
    run_id: str
    scenario_id: str
    mode: Literal["baseline", "llm"]
    provider: str
    passed: bool
    confidence: float = Field(ge=0, le=1)
    duration_ms: float = Field(ge=0)
    created_at: datetime
