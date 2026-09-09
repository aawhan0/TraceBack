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
    mode: Literal["baseline", "llm"] = "baseline"
    model: str | None = Field(default=None, min_length=1)


class ExperimentResponse(BaseModel):
    name: str
    total_runs: int
    passed_runs: int
    pass_rate: float
    average_confidence: float
    average_duration_ms: float
    scenario_pass_rates: dict[str, float]


class RegressionFailureResponse(BaseModel):
    metric: str
    actual: float
    expected: float
    direction: str
    message: str


class BenchmarkProvenanceResponse(BaseModel):
    application_version: str
    git_revision: str
    python_version: str
    environment: str
    provider: str
    model: str | None


class BenchmarkResponse(BaseModel):
    experiment_id: str
    name: str
    dataset_name: str
    dataset_version: str
    dataset_fingerprint: str
    total_runs: int
    passed_runs: int
    pass_rate: float
    average_confidence: float
    average_duration_ms: float
    scenario_pass_rates: dict[str, float]
    regression_passed: bool
    regression_failures: list[RegressionFailureResponse]
    pass_rate_interval_lower: float
    pass_rate_interval_upper: float
    provenance: BenchmarkProvenanceResponse | None = None


class ExperimentSummaryResponse(BaseModel):
    experiment_id: str
    name: str
    dataset_name: str
    dataset_version: str
    dataset_fingerprint: str
    created_at: datetime
    total_runs: int
    passed_runs: int
    pass_rate: float
    regression_passed: bool | None
    provenance: BenchmarkProvenanceResponse | None = None


class DatasetResponse(BaseModel):
    name: str
    version: str
    description: str
    fingerprint: str
    case_count: int
    scenario_ids: list[str]


class HealthComponentResponse(BaseModel):
    name: str
    status: Literal["ok", "degraded", "failed"]
    latency_ms: float = Field(ge=0)
    detail: str


class HealthDetailResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    environment: str
    checks: list[HealthComponentResponse]
