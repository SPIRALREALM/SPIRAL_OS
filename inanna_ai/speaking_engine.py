"""Generate speech using gTTS with emotion-based style adjustments."""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import librosa

from .utils import save_wav, load_audio
from .voice_evolution import get_voice_params
from .emotion_analysis import emotion_to_archetype

try:
    from gtts import gTTS
except Exception:  # pragma: no cover - optional dependency
    gTTS = None  # type: ignore

try:  # optional playback dependency
    import sounddevice as sd
except Exception:  # pragma: no cover - optional dependency
    sd = None

logger = logging.getLogger(__name__)


def _sine_placeholder(text: str) -> Tuple[np.ndarray, int]:
    """Return a simple sine wave when gTTS is unavailable."""
    duration = max(1.0, len(text) / 20)
    sr = 22050
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    wave = 0.1 * np.sin(2 * np.pi * 220 * t)
    return wave.astype(np.float32), sr


def _apply_style(wave: np.ndarray, sr: int, style: Dict[str, float]) -> np.ndarray:
    """Apply pitch shift and speed change according to ``style``."""
    pitch = style.get("pitch", 0.0)
    speed = style.get("speed", 1.0)
    if pitch:
        wave = librosa.effects.pitch_shift(wave, sr=sr, n_steps=pitch)
    if speed and speed != 1.0:
        wave = librosa.effects.time_stretch(wave, rate=speed)
    return wave


def synthesize_speech(text: str, emotion: str) -> str:
    """Synthesize ``text`` to a WAV file styled by ``emotion``."""
    style = get_voice_params(emotion)
    archetype = emotion_to_archetype(emotion)
    out_path = Path(tempfile.gettempdir()) / f"gtts_{abs(hash(text))}.wav"

    if gTTS is None:
        wave, sr = _sine_placeholder(f"{archetype} {text}")
    else:
        try:
            mp3_a = out_path.with_suffix(".arch.mp3")
            mp3_b = out_path.with_suffix(".text.mp3")
            gTTS(text=archetype).save(str(mp3_a))
            gTTS(text=text).save(str(mp3_b))
            wave_a, sr = librosa.load(str(mp3_a), sr=None, mono=True)
            wave_b, sr_b = librosa.load(str(mp3_b), sr=None, mono=True)
            mp3_a.unlink(missing_ok=True)
            mp3_b.unlink(missing_ok=True)
            if sr_b != sr:
                wave_b = librosa.resample(wave_b, sr_b, sr)
            pause = np.zeros(int(sr * 0.2), dtype=np.float32)
            wave = np.concatenate([wave_a, pause, wave_b])
        except Exception as exc:  # pragma: no cover - external call may fail
            logger.warning("gTTS synthesis failed: %s", exc)
            wave, sr = _sine_placeholder(f"{archetype} {text}")

    wave = _apply_style(wave, sr, style)
    save_wav(wave, str(out_path), sr=sr)
    return str(out_path)


def play_wav(path: str) -> None:
    """Play a WAV file if a playback backend is available."""
    if sd is None:
        logger.warning("sounddevice library not installed; cannot play audio")
        return
    wave, sr = load_audio(path, sr=None, mono=True)
    sd.play(wave, sr)
    sd.wait()


class SpeakingEngine:
    """Wrapper that synthesizes and plays speech."""

    def synthesize(self, text: str, emotion: str) -> str:
        """Return a path to synthesized speech for ``text``."""
        return synthesize_speech(text, emotion)

    def play(self, path: str) -> None:
        """Play an existing WAV file."""
        play_wav(path)

    def speak(self, text: str, emotion: str) -> str:
        """Synthesize speech and play it immediately."""
        path = self.synthesize(text, emotion)
        self.play(path)
        return path


__all__ = ["synthesize_speech", "play_wav", "SpeakingEngine"]
