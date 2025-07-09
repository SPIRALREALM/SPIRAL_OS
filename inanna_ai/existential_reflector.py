"""Generate a short self-description using a placeholder GLM endpoint."""
from __future__ import annotations

import logging
from pathlib import Path
import os

try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - fallback when requests missing
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
INANNA_DIR = ROOT / "INANNA_AI"
QNL_DIR = ROOT / "QNL_LANGUAGE"
AUDIT_DIR = ROOT / "audit_logs"
INSIGHTS_FILE = AUDIT_DIR / "existential_insights.txt"
ENDPOINT = os.getenv("GLM_API_URL", "https://api.example.com/glm")


class ExistentialReflector:
    """Helper to query the GLM about the system identity."""

    @staticmethod
    def reflect_on_identity() -> str:
        """Return a concise self-description derived from project texts."""
        if requests is None:
            raise RuntimeError("requests library is required")

        texts = []
        for directory in (INANNA_DIR, QNL_DIR):
            if directory.exists():
                for path in directory.glob("*.md"):
                    try:
                        texts.append(path.read_text(encoding="utf-8"))
                    except Exception:  # pragma: no cover - unreadable file
                        logger.warning("Failed to read %s", path)

        data = {"text": "\n".join(texts)}
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        resp = requests.post(ENDPOINT, json=data, timeout=10)
        try:
            desc = resp.json().get("description", "")
        except Exception:  # pragma: no cover - non-json response
            desc = resp.text

        INSIGHTS_FILE.write_text(desc, encoding="utf-8")
        logger.info("Wrote existential insights to %s", INSIGHTS_FILE)
        return desc


if __name__ == "__main__":  # pragma: no cover - manual execution
    print(ExistentialReflector.reflect_on_identity())
