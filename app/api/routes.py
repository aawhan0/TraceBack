from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    BenchmarkResponse,
    DatasetResponse,
    ExperimentRequest,
    ExperimentResponse,
    ExperimentSummaryResponse,
    InvestigationRequest,
    InvestigationResponse,
)
from app.config import Settings
from app.evaluation.dataset import build_manifest
from app.evaluation.experiments import ExperimentRunner, ExperimentSpec
from app.services.benchmark import BenchmarkRequest, BenchmarkService, default_dataset
from app.models.domain import HealthResponse, InvestigationRun, RunStats, RunSummary
from app.providers.ollama import OllamaProvider
from app.repository.runs import SQLiteRunStore
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
        run_id=result.run_id,
        duration_ms=result.duration_ms,
        created_at=result.created_at,
    )



def _run_store() -> SQLiteRunStore:
    return SQLiteRunStore(Settings.from_environment().database_path)


@router.get("/runs", response_model=list[RunSummary], tags=["runs"])
def list_runs(scenario_id: str | None = None, limit: int = 50) -> list[RunSummary]:
    try:
        return list(_run_store().list(scenario_id=scenario_id, limit=limit))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/runs/stats", response_model=RunStats, tags=["runs"])
def run_stats(scenario_id: str | None = None):
    return _run_store().stats(scenario_id=scenario_id)


@router.get("/runs/{run_id}", response_model=InvestigationRun, tags=["runs"])
def get_run(run_id: str) -> InvestigationRun:
    run = _run_store().get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Investigation run not found")
    return run


@router.post("/experiments", response_model=BenchmarkResponse, tags=["experiments"])
def run_experiment(request: ExperimentRequest) -> BenchmarkResponse:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    try:
        dataset = build_manifest(
            request.name,
            "request",
            [catalog[scenario_id] for scenario_id in request.scenario_ids],
        )
        benchmark = BenchmarkService()
        result = benchmark.run(
            BenchmarkRequest(request.name, dataset, request.repetitions),
            catalog,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BenchmarkResponse(
        experiment_id=result.experiment_id,
        name=result.result.name,
        dataset_name=result.dataset_name,
        dataset_version=result.dataset_version,
        dataset_fingerprint=result.dataset_fingerprint,
        total_runs=result.result.total_runs,
        passed_runs=result.result.passed_runs,
        pass_rate=result.result.pass_rate,
        average_confidence=result.result.average_confidence,
        average_duration_ms=result.result.average_duration_ms,
        scenario_pass_rates=result.result.scenario_pass_rates,
        regression_passed=result.regression.passed,
        regression_failures=[
            {
                "metric": failure.metric,
                "actual": failure.actual,
                "expected": failure.expected,
                "direction": failure.direction,
                "message": failure.message,
            }
            for failure in result.regression.failures
        ],
        pass_rate_interval_lower=result.regression.pass_rate_interval_lower,
        pass_rate_interval_upper=result.regression.pass_rate_interval_upper,
    )


@router.get("/experiments", response_model=list[ExperimentSummaryResponse], tags=["experiments"])
def list_experiments(limit: int = 50) -> list[ExperimentSummaryResponse]:
    try:
        records = BenchmarkService().list(limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [
        ExperimentSummaryResponse(
            experiment_id=record.experiment_id,
            name=record.name,
            dataset_name=record.dataset_name,
            dataset_version=record.dataset_version,
            dataset_fingerprint=record.dataset_fingerprint,
            created_at=record.created_at,
            total_runs=record.result.total_runs,
            passed_runs=record.result.passed_runs,
            pass_rate=record.result.pass_rate,
            regression_passed=record.regression.passed if record.regression else None,
        )
        for record in records
    ]


@router.get("/experiments/{experiment_id}", response_model=BenchmarkResponse, tags=["experiments"])
def get_experiment(experiment_id: str) -> BenchmarkResponse:
    record = BenchmarkService().get(experiment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    regression = record.regression
    failures = regression.failures if regression else ()
    return BenchmarkResponse(
        experiment_id=record.experiment_id,
        name=record.result.name,
        dataset_name=record.dataset_name,
        dataset_version=record.dataset_version,
        dataset_fingerprint=record.dataset_fingerprint,
        total_runs=record.result.total_runs,
        passed_runs=record.result.passed_runs,
        pass_rate=record.result.pass_rate,
        average_confidence=record.result.average_confidence,
        average_duration_ms=record.result.average_duration_ms,
        scenario_pass_rates=record.result.scenario_pass_rates,
        regression_passed=regression.passed if regression else True,
        regression_failures=[
            {
                "metric": failure.metric,
                "actual": failure.actual,
                "expected": failure.expected,
                "direction": failure.direction,
                "message": failure.message,
            }
            for failure in failures
        ],
        pass_rate_interval_lower=regression.pass_rate_interval_lower if regression else 0.0,
        pass_rate_interval_upper=regression.pass_rate_interval_upper if regression else 0.0,
    )


@router.get("/datasets/core", response_model=DatasetResponse, tags=["datasets"])
def core_dataset() -> DatasetResponse:
    dataset = default_dataset({scenario.id: scenario for scenario in SCENARIOS})
    return DatasetResponse(
        name=dataset.name,
        version=dataset.version,
        description=dataset.description,
        fingerprint=dataset.fingerprint,
        case_count=dataset.case_count,
        scenario_ids=[case.scenario_id for case in dataset.cases],
    )
