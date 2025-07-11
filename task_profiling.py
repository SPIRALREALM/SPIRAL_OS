from __future__ import annotations

"""Simple heuristics for classifying input text."""

INSTRUCTION_KEYWORDS = {
    "how to",
    "step",
    "instructions",
    "tutorial",
    "guide",
}

EMOTIONAL_KEYWORDS = {
    "feel",
    "emotion",
    "sad",
    "happy",
    "love",
    "hate",
}

PHILOSOPHY_KEYWORDS = {
    "meaning of life",
    "existence",
    "philosophy",
    "why are we",
    "purpose",
}

TECHNICAL_KEYWORDS = {
    "error",
    "exception",
    "traceback",
    "install",
    "import",
    "code",
}


def classify_task(text: str) -> str:
    """Return a coarse category for ``text``."""
    lowered = text.lower()
    if any(k in lowered for k in INSTRUCTION_KEYWORDS):
        return "instructional"
    if any(k in lowered for k in EMOTIONAL_KEYWORDS):
        return "emotional"
    if any(k in lowered for k in PHILOSOPHY_KEYWORDS):
        return "philosophical"
    return "technical"


__all__ = ["classify_task"]
