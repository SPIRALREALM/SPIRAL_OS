"""Helpers to evolve INANNA's vocal style."""
from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np

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
        """Adjust voice styles based on recent emotion analyses."""
        grouped: Dict[str, Dict[str, list[float]]] = {}
        for entry in history:
            emotion = entry.get("emotion")
            if emotion is None:
                continue
            if "arousal" not in entry or "valence" not in entry:
                continue
            data = grouped.setdefault(emotion, {"arousal": [], "valence": []})
            data["arousal"].append(entry["arousal"])
            data["valence"].append(entry["valence"])

        for emotion, values in grouped.items():
            arousal = float(np.mean(values["arousal"]))
            valence = float(np.mean(values["valence"]))
            style = self.styles.setdefault(emotion, {"speed": 1.0, "pitch": 0.0})
            style["speed"] = round(1.0 + (arousal - 0.5) * 0.4, 3)
            style["pitch"] = round((valence - 0.5) * 2.0, 3)

    def reset(self) -> None:
        """Reset styles to the default values."""
        self.styles = {k: v.copy() for k, v in DEFAULT_VOICE_STYLES.items()}


_evolver = VoiceEvolution()


def get_voice_params(emotion: str) -> Dict[str, float]:
    """Return parameters from the default :class:`VoiceEvolution`."""
    return _evolver.get_params(emotion)


def update_voice_from_history(history: Iterable[Dict[str, Any]]) -> None:
    """Update the default :class:`VoiceEvolution` with ``history``."""
    _evolver.update_from_history(history)


__all__ = [
    "VoiceEvolution",
    "get_voice_params",
    "update_voice_from_history",
    "DEFAULT_VOICE_STYLES",
]
