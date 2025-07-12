from __future__ import annotations

"""Log intent outcomes for reinforcement learning.

Entries are appended to ``data/feedback.json`` as dictionaries with the
following keys:
``timestamp`` ISO‑8601 time of the event,
``intent`` intent name,
``action`` handler action name,
``tone`` tonal label if provided,
``success`` boolean result indicator.
"""

from pathlib import Path
from datetime import datetime
import json

from inanna_ai import db_storage

FEEDBACK_FILE = Path("data/feedback.json")


def _load_entries() -> list[dict]:
    if FEEDBACK_FILE.exists():
        try:
            return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def log_result(intent: dict, success: bool, tone: str | None) -> None:
    """Append ``intent`` outcome to the feedback log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "intent": intent.get("intent"),
        "action": intent.get("action"),
        "tone": tone,
        "success": bool(success),
    }
    entries = _load_entries()
    entries.append(entry)
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    score = 1.0 if success else 0.0
    db_storage.log_feedback(tone or "neutral", score, score, score)
