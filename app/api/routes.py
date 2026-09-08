from fastapi import APIRouter, HTTPException

from app.api.schemas import InvestigationRequest, InvestigationResponse
from app.config import Settings
from app.models.domain import HealthResponse
from app.providers.ollama import OllamaProvider
from app.scenarios.catalog import SCENARIOS, get_scenario
from app.services.investigation import InvestigationService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="traceback")


@router.get("/scenarios", tags=["scenarios"])
def list_scenarios() -> list[dict[str, str]]:
    return [{"id": scenario.id, "title": scenario.incident.title} for scenario in SCENARIOS]


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

    service = InvestigationService()
    provider_name = "baseline"
    if request.mode == "llm":
        settings = Settings.from_environment()
        provider = OllamaProvider(
            model=request.model or settings.model,
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout,
        )
        provider_name = provider.name
        try:
            result = service.investigate(scenario, provider=provider)
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
    else:
        result = service.investigate(scenario)

    return InvestigationResponse(
        scenario_id=result.scenario_id,
        mode=request.mode,
        provider=provider_name,
        diagnosis=result.diagnosis,
        root_cause_match=result.evaluation.root_cause_match,
        evidence_recall=result.evaluation.evidence_recall,
        evidence_precision=result.evaluation.evidence_precision,
        confidence_valid=result.evaluation.confidence_valid,
        action_present=result.evaluation.action_present,
        passed=result.evaluation.passed,
    )
