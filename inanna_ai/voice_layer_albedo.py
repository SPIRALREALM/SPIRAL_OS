from __future__ import annotations

"""Voice modulation layer with alchemical tone presets."""

from typing import Dict

from . import speaking_engine, voice_evolution

# Tone presets mapping to speed and pitch adjustments
TONE_PRESETS: Dict[str, Dict[str, float]] = {
    "albedo": {"speed": 1.05, "pitch": 0.2},
    "nigredo": {"speed": 0.9, "pitch": -0.3},
    "rubedo": {"speed": 1.1, "pitch": 0.5},
    "lunar": {"speed": 0.95, "pitch": -0.4},
}


def _ensure_preset(tone: str) -> None:
    """Inject preset ``tone`` into the voice evolution styles."""
    preset = TONE_PRESETS.get(tone)
    if not preset:
        return
    voice_evolution.DEFAULT_VOICE_STYLES.setdefault(tone, preset)
    voice_evolution._evolver.styles.setdefault(tone, preset)


def modulate_voice(text: str, tone: str) -> str:
    """Synthesize ``text`` using the style defined by ``tone``."""
    tone = tone.lower()
    _ensure_preset(tone)
    return speaking_engine.synthesize_speech(text, tone)


__all__ = ["modulate_voice", "TONE_PRESETS"]
