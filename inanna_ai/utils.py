"""Utility helpers for audio processing and logging."""
from __future__ import annotations

import logging
import os
from typing import Tuple
import re

import librosa
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


def setup_logger(level: int = logging.INFO) -> None:
    """Configure basic logging."""
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")


def load_audio(path: str, sr: int = 44100, mono: bool = True) -> Tuple[np.ndarray, int]:
    """Load ``path`` into a waveform and return it with the sample rate."""
    wave, sample_rate = librosa.load(path, sr=sr, mono=mono)
    logger.info("Loaded audio %s (sr=%d)", path, sample_rate)
    return wave, sample_rate


def save_wav(wave: np.ndarray, path: str, sr: int = 44100) -> None:
    """Write ``wave`` to ``path`` as 16-bit PCM WAV."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sf.write(path, wave, sr, subtype="PCM_16")
    logger.info("Saved WAV to %s", path)


SENTIMENT_LEXICON = {
    "good": 1.0,
    "love": 1.0,
    "great": 1.0,
    "happy": 0.5,
    "nice": 0.5,
    "bad": -1.0,
    "hate": -1.0,
    "awful": -1.0,
    "sad": -0.5,
    "terrible": -1.0,
}


def sentiment_score(text: str) -> float:
    """Return a crude sentiment score between -1 and 1 for ``text``."""
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return 0.0
    score = sum(SENTIMENT_LEXICON.get(tok, 0.0) for tok in tokens)
    return float(np.clip(score / len(tokens), -1.0, 1.0))
