"""Backend application entry point (Phase 1: Software Core)."""

from backend.app.core.config import settings


def get_app_info() -> dict[str, str]:
    """Return baseline application metadata before FastAPI router wiring."""
    return {
        "name": settings.app_name,
        "env": settings.app_env,
        "timezone": settings.app_timezone,
        "currency": settings.app_currency,
    }


try:
    from fastapi import FastAPI

    app = FastAPI(title=settings.app_name, version="0.1.0")

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        """Health check endpoint (NFR-11)."""
        return {"status": "ok", **get_app_info()}
except ImportError:  # Allows running smoke tests before pip install -r requirements.txt
    app = None
