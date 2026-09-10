from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.domain import Diagnosis


class TimelineEntryResponse(BaseModel):
    name: str
    timestamp: datetime
    duration_ms: float | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class InvestigationTimelineResponse(BaseModel):
    trace_id: str
    event_count: int
    entries: list[TimelineEntryResponse]


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
    timeline: InvestigationTimelineResponse


class CustomScenarioEvidence(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=100)
    kind: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=2000)


class CustomScenarioRequest(BaseModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    expected_root_cause: str = Field(min_length=1, max_length=500)
    root_cause_keywords: list[str] = Field(min_length=1, max_length=20)
    evidence: list[CustomScenarioEvidence] = Field(min_length=1, max_length=50)
    required_evidence_ids: list[str] = Field(default_factory=list, max_length=50)


class MatrixConfigurationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    mode: Literal["baseline", "llm"] = "baseline"
    model: str | None = Field(default=None, min_length=1)


class MatrixRequest(BaseModel):
    matrix_id: str = Field(min_length=1, max_length=100)
    scenario_ids: list[str] = Field(min_length=1, max_length=20)
    configurations: list[MatrixConfigurationRequest] = Field(min_length=1, max_length=20)
    repetitions: int = Field(default=1, ge=1, le=100)
    min_pass_rate: float = Field(default=1.0, ge=0, le=1)


class MatrixResponse(BaseModel):
    matrix_id: str
    dataset_name: str
    dataset_version: str
    fingerprint: str
    case_count: int
    scenario_ids: list[str]


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
