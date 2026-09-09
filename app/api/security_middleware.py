from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.security import RateLimiter


class SecurityMiddleware(BaseHTTPMiddleware):
    """Apply lightweight abuse protection and browser security headers."""

    def __init__(self, app, limiter: RateLimiter | None = None) -> None:
        super().__init__(app)
        self.limiter = limiter or RateLimiter()

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        if not self.limiter.allow(client):
            response = JSONResponse(
                status_code=429,
                content={
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests",
                    "request_id": getattr(request.state, "request_id", None),
                    "details": {},
                },
            )
        else:
            response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
