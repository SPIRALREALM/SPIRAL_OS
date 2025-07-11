from __future__ import annotations

"""Lightweight emotion analysis tools using Librosa."""

from typing import Dict, Any, Tuple

# Mapping from emotional labels to Jungian archetypes
EMOTION_ARCHETYPES = {
    "joy": "Jester",
    "stress": "Warrior",
    "fear": "Orphan",
    "sad": "Caregiver",
    "excited": "Hero",
    "calm": "Sage",
    "neutral": "Everyman",
}

# Coarse weight for each emotion; can be used by higher level modules
EMOTION_WEIGHT = {
    "joy": 1.0,
    "stress": 0.8,
    "fear": 0.8,
    "sad": 0.7,
    "excited": 0.6,
    "calm": 0.4,
    "neutral": 0.2,
}

# Simple mapping from emotion to a descriptive "quantum tone"
EMOTION_QUANTUM_TONE = {
    "joy": "Radiant",
    "stress": "Tension",
    "fear": "Flicker",
    "sad": "Echo",
    "excited": "Burst",
    "calm": "Drift",
    "neutral": "Still",
}

_CURRENT_STATE = {
    "emotion": "neutral",
    "archetype": EMOTION_ARCHETYPES["neutral"],
    "weight": EMOTION_WEIGHT["neutral"],
}

import librosa
import numpy as np



def analyze_audio_emotion(audio_path: str) -> Dict[str, Any]:
    """Return a simple emotion estimate with pitch and tempo of ``audio_path``.

    The function loads the audio file, computes its average pitch using
    :func:`librosa.yin` and estimates tempo via
    :func:`librosa.beat.beat_track`. A basic rule-based classifier then
    assigns one of ``"excited"``, ``"calm"`` or ``"neutral"`` emotions based on
    these values.
    """
    wave, sr = librosa.load(audio_path, sr=None, mono=True)

    f0 = librosa.yin(
        wave,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
    )
    pitch = float(np.nanmean(f0))

    tempo, _ = librosa.beat.beat_track(y=wave, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])

    # Average absolute amplitude is used as a rough energy metric
    energy = float(np.mean(np.abs(wave)))

    emotion = "neutral"
    if energy > 0.4:
        emotion = "stress"
    elif pitch > 400 and energy < 0.1:
        emotion = "fear"
    elif pitch > 300 and energy > 0.2:
        emotion = "joy"
    elif pitch < 160 and energy < 0.1:
        emotion = "sad"
    elif pitch > 180 and tempo > 120:
        emotion = "excited"
    elif pitch < 120 and tempo < 90:
        emotion = "calm"

    _CURRENT_STATE["emotion"] = emotion
    _CURRENT_STATE["archetype"] = EMOTION_ARCHETYPES.get(emotion, "Everyman")
    _CURRENT_STATE["weight"] = EMOTION_WEIGHT.get(emotion, 0.0)

    return {"emotion": emotion, "pitch": round(pitch, 2), "tempo": round(tempo, 2)}

def get_current_archetype() -> str:
    """Return the Jungian archetype for the last analyzed emotion."""
    return _CURRENT_STATE["archetype"]


def get_emotional_weight() -> float:
    """Return a coarse numeric weight for the last analyzed emotion."""
    return _CURRENT_STATE["weight"]


def emotion_to_archetype(emotion: str) -> str:
    """Map an emotion label to its corresponding Jungian archetype."""
    return EMOTION_ARCHETYPES.get(emotion, "Everyman")


def emotion_weight(emotion: str) -> float:
    """Return the weight associated with ``emotion``."""
    return EMOTION_WEIGHT.get(emotion, 0.0)


def get_emotion_and_tone(emotion: str | None = None) -> Tuple[str, str]:
    """Return ``emotion`` and its associated quantum tone."""

    if emotion is None:
        emotion = _CURRENT_STATE["emotion"]
    tone = EMOTION_QUANTUM_TONE.get(emotion, "Still")
    return emotion, tone


__all__ = [
    "analyze_audio_emotion",
    "get_current_archetype",
    "get_emotional_weight",
    "emotion_to_archetype",
    "emotion_weight",
    "get_emotion_and_tone",
]
