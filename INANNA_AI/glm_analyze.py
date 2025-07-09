"""Analyze Python modules using a placeholder GLM endpoint."""
from __future__ import annotations

import logging
from pathlib import Path

try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - fallback when requests missing
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "inanna_ai"
AUDIT_DIR = ROOT / "audit_logs"
ANALYSIS_FILE = AUDIT_DIR / "code_analysis.txt"
ENDPOINT = "https://api.example.com/glm"


def analyze_code() -> str:
    """Send code base to the GLM endpoint and store the suggestions."""
    if requests is None:
        raise RuntimeError("requests library is required")

    snippets = []
    if CODE_DIR.exists():
        for path in CODE_DIR.rglob("*.py"):
            try:
                snippets.append(f"# {path}\n{path.read_text(encoding='utf-8')}")
            except Exception:  # pragma: no cover - unreadable file
                logger.warning("Failed to read %s", path)

    data = {"text": "\n".join(snippets)}
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.post(ENDPOINT, json=data, timeout=10)
    try:
        analysis = resp.json().get("analysis", "")
    except Exception:  # pragma: no cover - non-json response
        analysis = resp.text

    ANALYSIS_FILE.write_text(analysis, encoding="utf-8")
    logger.info("Wrote code analysis to %s", ANALYSIS_FILE)
    return analysis


if __name__ == "__main__":  # pragma: no cover - manual execution
    print(analyze_code())
