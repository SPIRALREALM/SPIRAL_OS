from __future__ import annotations

"""Wrapper around a placeholder GLM-4.1V-9B endpoint."""

import logging
import os

try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - fallback when requests missing
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

ENDPOINT = os.getenv("GLM_API_URL", "https://api.example.com/glm41v_9b")
API_KEY = os.getenv("GLM_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else None


def generate_completion(prompt: str) -> str:
    """Return the GLM completion for ``prompt``."""
    if requests is None:
        raise RuntimeError("requests library is required")

    resp = requests.post(ENDPOINT, json={"prompt": prompt}, timeout=10, headers=HEADERS)
    try:
        text = resp.json().get("text", "")
    except Exception:  # pragma: no cover - non-json response
        text = resp.text
    return text


__all__ = ["generate_completion", "ENDPOINT"]
