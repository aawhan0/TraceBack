from fastapi import APIRouter, HTTPException

from app.api.schemas import InvestigationRequest, InvestigationResponse
from app.models.domain import HealthResponse
from app.scenarios.catalog import SCENARIOS, get_scenario
from app.services.investigation import InvestigationService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="traceback")


@router.get("/scenarios", tags=["scenarios"])
def list_scenarios() -> list[dict[str, str]]:
    return [{"id": s.id, "title": s.incident.title} for s in SCENARIOS]


@router.get("/scenarios/{scenario_id}", tags=["scenarios"])
def scenario_detail(scenario_id: str):
    try:
        return get_scenario(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Scenario not found") from exc


@router.post("/investigations", response_model=InvestigationResponse, tags=["investigations"])
def investigate(request: InvestigationRequest) -> InvestigationResponse:
    try:
        scenario = get_scenario(request.scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Scenario not found") from exc

    result = InvestigationService().investigate(scenario)
    return InvestigationResponse(
        scenario_id=result.scenario_id,
        diagnosis=result.diagnosis,
        root_cause_match=result.evaluation.root_cause_match,
        evidence_recall=result.evaluation.evidence_recall,
        evidence_precision=result.evaluation.evidence_precision,
        confidence_valid=result.evaluation.confidence_valid,
        action_present=result.evaluation.action_present,
        passed=result.evaluation.passed,
    )
