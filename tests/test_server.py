import sys
from pathlib import Path
import asyncio

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server


def test_health_and_ready_return_200():
    """Endpoints should respond with HTTP 200 when app is running."""

    async def run_requests() -> tuple[int, int]:
        with TestClient(server.app) as test_client:
            transport = httpx.ASGITransport(app=test_client.app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                health = await client.get("/health")
                ready = await client.get("/ready")
        return health.status_code, ready.status_code

    status_health, status_ready = asyncio.run(run_requests())
    assert status_health == 200
    assert status_ready == 200


def test_glm_command_endpoint(monkeypatch):
    """POST /glm-command should return GLM output."""

    async def run_request() -> tuple[int, dict[str, str]]:
        with TestClient(server.app) as test_client:
            transport = httpx.ASGITransport(app=test_client.app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                resp = await client.post("/glm-command", json={"command": "ls"})
        return resp.status_code, resp.json()

    monkeypatch.setattr(server, "send_command", lambda cmd: f"ran {cmd}")
    status, data = asyncio.run(run_request())
    assert status == 200
    assert data == {"result": "ran ls"}
