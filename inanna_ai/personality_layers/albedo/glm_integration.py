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
SAFE_ERROR_MESSAGE = "GLM unavailable"


class GLMIntegration:
    """Small wrapper around a GLM endpoint."""

    def __init__(self, endpoint: str | None = None, api_key: str | None = None, temperature: float = 0.8) -> None:
        self.endpoint = endpoint or ENDPOINT
        self.api_key = api_key or API_KEY
        self.temperature = temperature

    @property
    def headers(self) -> dict[str, str] | None:
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return None

    def complete(self, prompt: str) -> str:
        """Return the GLM completion for ``prompt``."""
        if requests is None:
            logger.warning("requests missing; returning safe message")
            return SAFE_ERROR_MESSAGE

        payload = {"prompt": prompt, "temperature": self.temperature}
        try:
            resp = requests.post(self.endpoint, json=payload, timeout=10, headers=self.headers)
            resp.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            logger.error("Failed to query %s: %s", self.endpoint, exc)
            return SAFE_ERROR_MESSAGE

        try:
            text = resp.json().get("text", "")
        except Exception:  # pragma: no cover - non-json response
            text = resp.text
        return text or SAFE_ERROR_MESSAGE


__all__ = ["GLMIntegration", "ENDPOINT", "SAFE_ERROR_MESSAGE"]
