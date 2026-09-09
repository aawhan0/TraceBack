from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import Settings
from app.repository.maintenance import SQLiteMaintenance
from app.services.health import ReadinessChecker, sqlite_check

router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/ready")
def readiness() -> dict[str, object]:
    settings = Settings.from_environment()
    report = ReadinessChecker({"database": sqlite_check(settings.database_path)}).check()
    if not report.ready:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "dependencies": [
                    {"name": item.name, "healthy": item.healthy, "detail": item.detail}
                    for item in report.dependencies
                ],
            },
        )
    return {
        "status": "ready",
        "dependencies": [
            {"name": item.name, "healthy": item.healthy, "detail": item.detail}
            for item in report.dependencies
        ],
    }


@router.get("/database")
def database_status() -> dict[str, object]:
    settings = Settings.from_environment()
    maintenance = SQLiteMaintenance(settings.database_path)
    return {
        "integrity": maintenance.integrity_check(),
        "foreign_keys": maintenance.foreign_keys_enabled(),
    }
