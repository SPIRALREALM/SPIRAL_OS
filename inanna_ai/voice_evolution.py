"""Helpers to evolve INANNA's vocal style."""
from __future__ import annotations

from typing import Any, Dict, Iterable

DEFAULT_VOICE_STYLES: Dict[str, Dict[str, float]] = {
    "neutral": {"speed": 1.0, "pitch": 0.0},
    "calm": {"speed": 0.9, "pitch": -1.0},
    "excited": {"speed": 1.1, "pitch": 1.0},
}


class VoiceEvolution:
    """Manage voice style parameters and allow future fine-tuning."""

    def __init__(self, styles: Dict[str, Dict[str, float]] | None = None) -> None:
        self.styles: Dict[str, Dict[str, float]] = (
            {k: v.copy() for k, v in (styles or DEFAULT_VOICE_STYLES).items()}
        )

    def get_params(self, emotion: str) -> Dict[str, float]:
        """Return style parameters for ``emotion`` label."""
        return self.styles.get(emotion.lower(), self.styles["neutral"])

    def update_from_history(self, history: Iterable[Dict[str, Any]]) -> None:
        """Placeholder for future style adaptation logic."""
        _ = history

    def reset(self) -> None:
        """Reset styles to the default values."""
        self.styles = {k: v.copy() for k, v in DEFAULT_VOICE_STYLES.items()}


_evolver = VoiceEvolution()


def get_voice_params(emotion: str) -> Dict[str, float]:
    """Return parameters from the default :class:`VoiceEvolution`."""
    return _evolver.get_params(emotion)


__all__ = ["VoiceEvolution", "get_voice_params", "DEFAULT_VOICE_STYLES"]
