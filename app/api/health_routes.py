from fastapi import APIRouter

from app.api.dependencies import get_settings
from app.api.schemas import HealthDetailResponse, HealthComponentResponse
from app.repository.runs import SQLiteRunStore
from app.services.health import HealthService

router = APIRouter(prefix="/health", tags=["system"])


@router.get("/ready", response_model=HealthDetailResponse)
def readiness() -> HealthDetailResponse:
    settings = get_settings()
    checks = HealthService(SQLiteRunStore(settings.database_path)).check()
    return HealthDetailResponse(
        status="ok" if all(check.status == "ok" for check in checks) else "degraded",
        service="traceback",
        environment=settings.environment,
        checks=[
            HealthComponentResponse(
                name=check.name,
                status=check.status,
                latency_ms=check.latency_ms,
                detail=check.detail,
            )
            for check in checks
        ],
    )
