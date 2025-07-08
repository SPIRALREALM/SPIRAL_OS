from __future__ import annotations

"""Lightweight emotion analysis tools using Librosa."""

from typing import Dict, Any

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

    emotion = "neutral"
    if pitch > 180 and tempo > 120:
        emotion = "excited"
    elif pitch < 120 and tempo < 90:
        emotion = "calm"

    return {"emotion": emotion, "pitch": round(pitch, 2), "tempo": round(tempo, 2)}


__all__ = ["analyze_audio_emotion"]
