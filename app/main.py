from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Traceback",
    description="LLM-assisted incident investigation and deterministic evaluation.",
    version="0.1.0",
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
