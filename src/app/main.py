from fastapi import FastAPI

from app.api.v1 import auth, documents, experiment, health, stream
from app.config import get_settings
from app.log_config import configure_logging
from app.middleware import RequestIDMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="genai-svc")
    app.add_middleware(RequestIDMiddleware)
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(stream.router)
    if settings.app_env == "local":
        app.include_router(experiment.router)  # TEMPORARY; see api/v1/experiment.py
        app.include_router(auth.router)  # TEMPORARY dev-only; see api/v1/auth.py
    return app
