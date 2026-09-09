from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.observability.audit import AuditEvent, AuditLog
from app.observability.metrics import MetricsRegistry
from app.services.request_validation import validate_request_id


METRICS = MetricsRegistry()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a stable request ID and timing headers to every response."""

    def __init__(self, app, audit_log: AuditLog | None = None):
        super().__init__(app)
        self.audit_log = audit_log or AuditLog()

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        try:
            request_id = validate_request_id(request_id)
        except ValueError:
            request_id = str(uuid4())
        started = perf_counter()
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:
            elapsed = (perf_counter() - started) * 1000
            self.audit_log.append(
                AuditEvent.create(
                    "request.failed",
                    actor="system",
                    resource_type="http_request",
                    resource_id=request_id,
                    payload={
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": round(elapsed, 3),
                    },
                )
            )
            METRICS.increment("http.requests.total")
            METRICS.observe("http.request.duration_seconds", elapsed / 1000)
            raise

        elapsed = (perf_counter() - started) * 1000
        METRICS.increment("http.requests.total")
        METRICS.observe("http.request.duration_seconds", elapsed / 1000)
        METRICS.increment(f"http.responses.{response.status_code}")
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{elapsed:.3f}"
        return response
