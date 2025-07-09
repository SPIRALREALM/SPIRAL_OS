"""Summarize project purpose using a placeholder GLM endpoint."""
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
README_FILE = ROOT / "README.md"
QNL_DIR = ROOT / "QNL_LANGUAGE"
AUDIT_DIR = ROOT / "audit_logs"
PURPOSE_FILE = AUDIT_DIR / "purpose.txt"
ENDPOINT = os.getenv("GLM_API_URL", "https://api.example.com/glm")


def summarize_purpose() -> str:
    """Read project texts and store a summary produced by the GLM endpoint."""
    if requests is None:
        raise RuntimeError("requests library is required")

    texts = []
    if README_FILE.exists():
        texts.append(README_FILE.read_text(encoding="utf-8"))
    if QNL_DIR.exists():
        for path in QNL_DIR.glob("*.md"):
            try:
                texts.append(path.read_text(encoding="utf-8"))
            except Exception:  # pragma: no cover - unreadable file
                logger.warning("Failed to read %s", path)

    data = {"text": "\n".join(texts)}
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.post(ENDPOINT, json=data, timeout=10)
    try:
        summary = resp.json().get("summary", "")
    except Exception:  # pragma: no cover - non-json response
        summary = resp.text

    PURPOSE_FILE.write_text(summary, encoding="utf-8")
    logger.info("Wrote summary to %s", PURPOSE_FILE)
    return summary


if __name__ == "__main__":  # pragma: no cover - manual execution
    print(summarize_purpose())
