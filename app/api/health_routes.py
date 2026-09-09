from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.api.middleware import METRICS
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


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    snapshot = METRICS.snapshot()
    lines = []
    for name, value in sorted(snapshot.counters.items()):
        lines.append(f"{name.replace('.', '_')} {value}")
    for name, (count, minimum, maximum) in sorted(snapshot.timings.items()):
        metric = name.replace(".", "_")
        lines.append(f"{metric}_count {count}")
        lines.append(f"{metric}_min {minimum}")
        lines.append(f"{metric}_max {maximum}")
    return "\n".join(lines) + ("\n" if lines else "")
