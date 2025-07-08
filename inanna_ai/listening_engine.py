from __future__ import annotations

"""Real-time microphone listening with basic feature extraction."""

import logging
import tempfile
from pathlib import Path
from queue import Queue, Empty
from typing import Dict, Generator, Optional, Tuple

import numpy as np
import librosa

from . import utils

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - optional dependency
    sd = None


logger = logging.getLogger(__name__)


def _extract_features(wave: np.ndarray, sr: int) -> Dict[str, float]:
    """Return pitch, tempo, emotion and classification for ``wave``."""
    if len(wave) == 0:
        return {"emotion": "neutral", "pitch": 0.0, "tempo": 0.0, "classification": "silence"}

    f0 = librosa.yin(wave, librosa.note_to_hz("C2"), librosa.note_to_hz("C7"), sr=sr)
    pitch = float(np.nanmean(f0))
    tempo, _ = librosa.beat.beat_track(y=wave, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])

    energy = float(np.mean(wave ** 2))
    classification = "silence"
    if energy > 1e-4:
        classification = "speech" if 80 <= pitch <= 300 else "noise"

    emotion = "neutral"
    if pitch > 180 and tempo > 120:
        emotion = "excited"
    elif pitch < 120 and tempo < 90:
        emotion = "calm"

    return {
        "emotion": emotion,
        "pitch": round(pitch, 2),
        "tempo": round(tempo, 2),
        "classification": classification,
    }


class ListeningEngine:
    """Stream audio from the microphone and yield analysis for each chunk."""

    def __init__(self, sr: int = 44100, chunk_duration: float = 0.5) -> None:
        if sd is None:
            raise RuntimeError("sounddevice library not installed")
        self.sr = sr
        self.chunk_size = int(sr * chunk_duration)
        self._queue: "Queue[np.ndarray]" = Queue()
        self._stream: Optional[sd.InputStream] = None

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:  # pragma: no cover - external callback
        if status:
            logger.warning("InputStream status: %s", status)
        self._queue.put(indata[:, 0].copy())

    def __enter__(self) -> "ListeningEngine":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

    def start(self) -> None:
        """Start streaming from the microphone."""
        if self._stream is not None:
            return
        self._stream = sd.InputStream(
            samplerate=self.sr,
            channels=1,
            blocksize=self.chunk_size,
            callback=self._callback,
        )
        self._stream.start()
        logger.info("Listening engine started")

    def stop(self) -> None:
        """Stop the microphone stream."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            logger.info("Listening engine stopped")

    def stream_chunks(self, duration: Optional[float] = None) -> Generator[Tuple[np.ndarray, Dict[str, float]], None, None]:
        """Yield (waveform, features) tuples for each audio chunk."""
        if self._stream is None:
            self.start()
        total_frames = int(duration * self.sr) if duration else None
        frames_read = 0
        while total_frames is None or frames_read < total_frames:
            try:
                chunk = self._queue.get(timeout=duration)
            except Empty:
                continue
            frames_read += len(chunk)
            features = _extract_features(chunk, self.sr)
            yield chunk, features
            if total_frames is not None and frames_read >= total_frames:
                break

    def record(self, duration: float) -> Tuple[str, Dict[str, float]]:
        """Capture ``duration`` seconds of audio and return file path and last state."""
        chunks = []
        last_state: Dict[str, float] = {}
        for chunk, state in self.stream_chunks(duration):
            chunks.append(chunk)
            last_state = state
        wave = np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)
        path = Path(tempfile.gettempdir()) / "inanna_stream.wav"
        utils.save_wav(wave.astype(np.float32), str(path), sr=self.sr)
        return str(path), last_state


__all__ = ["ListeningEngine"]

