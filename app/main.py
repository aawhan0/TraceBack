from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.errors import ErrorResponse, TracebackApiError
from app.api.middleware import RequestContextMiddleware
from app.api.routes import router
from app.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    application = FastAPI(
        title="Traceback",
        description="LLM-assisted incident investigation and deterministic evaluation.",
        version="0.1.0",
    )

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

    application.add_middleware(RequestContextMiddleware)

    @application.exception_handler(TracebackApiError)
    async def traceback_error_handler(request: Request, exc: TracebackApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.code,
                message=exc.message,
                request_id=getattr(request.state, "request_id", None),
                details=exc.details,
            ).model_dump(mode="json"),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code="validation_error",
                message="Request validation failed",
                request_id=getattr(request.state, "request_id", None),
                details={"errors": exc.errors()},
            ).model_dump(mode="json"),
        )

    application.include_router(router)
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
