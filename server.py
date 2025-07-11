"""Simple FastAPI application for health checks."""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "alive"}


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    """Return service readiness status."""
    return {"status": "ready"}
