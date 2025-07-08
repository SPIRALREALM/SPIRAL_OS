"""Voice style parameters for Coqui TTS."""
from __future__ import annotations

from typing import Dict

VOICE_STYLES: Dict[str, Dict[str, float]] = {
    "neutral": {"speed": 1.0, "pitch": 0.0},
    "calm": {"speed": 0.9, "pitch": -1.0},
    "excited": {"speed": 1.1, "pitch": 1.0},
}


def get_voice_params(emotion: str) -> Dict[str, float]:
    """Return style parameters for ``emotion``.

    Parameters
    ----------
    emotion:
        Target emotion label such as ``"neutral"`` or ``"excited"``.

    Returns
    -------
    Dict[str, float]
        Mapping with ``speed`` and ``pitch`` entries.
    """
    return VOICE_STYLES.get(emotion.lower(), VOICE_STYLES["neutral"])

__all__ = ["get_voice_params", "VOICE_STYLES"]
