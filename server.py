"""Simple FastAPI application for health checks."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from glm_shell import send_command

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "alive"}


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    """Return service readiness status."""
    return {"status": "ready"}


class ShellCommand(BaseModel):
    """Payload for ``/glm-command``."""

    command: str


@app.post("/glm-command")
def glm_command(cmd: ShellCommand) -> dict[str, str]:
    """Execute ``cmd.command`` via the GLM shell and return the result."""
    result = send_command(cmd.command)
    return {"result": result}
