from fastapi import FastAPI

from app.api.v1 import health


def create_app() -> FastAPI:
    app = FastAPI(title="genai-svc")
    app.include_router(health.router)
    return app
