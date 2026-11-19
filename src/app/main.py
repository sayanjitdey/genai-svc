from fastapi import FastAPI

from app.api.v1 import documents, health


def create_app() -> FastAPI:
    app = FastAPI(title="genai-svc")
    app.include_router(health.router)
    app.include_router(documents.router)
    return app
