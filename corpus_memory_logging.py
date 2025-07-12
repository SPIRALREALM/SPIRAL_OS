from __future__ import annotations

"""Append and read JSONL interaction records for corpus memory usage."""

from pathlib import Path
from datetime import datetime
import json
from typing import Any, List

INTERACTIONS_FILE = Path("data/interactions.jsonl")


def log_interaction(input_text: str, intent: dict, result: dict, outcome: str) -> None:
    """Append ``input_text`` and ``result`` details to :data:`INTERACTIONS_FILE`."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input": input_text,
        "intent": intent,
        "result": result,
        "outcome": outcome,
    }
    emotion = result.get("emotion") or intent.get("emotion")
    if emotion is not None:
        entry["emotion"] = emotion
    INTERACTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with INTERACTIONS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False))
        fh.write("\n")


def load_interactions(limit: int | None = None) -> List[dict[str, Any]]:
    """Return recorded interactions ordered from oldest to newest."""
    if not INTERACTIONS_FILE.exists():
        return []
    entries: List[dict[str, Any]] = []
    with INTERACTIONS_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    if limit is not None:
        entries = entries[-limit:]
    return entries


__all__ = ["log_interaction", "load_interactions", "INTERACTIONS_FILE"]
