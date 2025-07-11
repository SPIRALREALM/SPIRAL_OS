#!/usr/bin/env python3
"""Mix audio files into a normalized track.

This script loads multiple audio files, sums them using NumPy, normalizes
the amplitude, and writes ``final_track.wav`` in 16-bit PCM format at
44.1 kHz. Optionally a short preview clip can be exported for quick
listening.
"""
from __future__ import annotations

import argparse
import os
from typing import Iterable, List

from scipy.signal import butter, lfilter

import librosa
import numpy as np
import soundfile as sf

from MUSIC_FOUNDATION.qnl_utils import quantum_embed


def load_audio(path: str, sample_rate: int = 44100) -> np.ndarray:
    """Return ``path`` as a mono waveform resampled to ``sample_rate``."""
    data, _ = librosa.load(path, sr=sample_rate, mono=True)
    return data.astype(np.float32)


def mix_waveforms(waves: Iterable[np.ndarray]) -> np.ndarray:
    """Sum and normalize a collection of waveforms."""
    waves = list(waves)
    if not waves:
        return np.zeros(1, dtype=np.float32)
    length = max(w.size for w in waves)
    mixed = np.zeros(length, dtype=np.float32)
    for w in waves:
        if w.size < length:
            w = np.pad(w, (0, length - w.size))
        mixed += w
    max_val = np.max(np.abs(mixed))
    if max_val > 0:
        mixed /= max_val
    return mixed


def export_wav(wave: np.ndarray, path: str, *, sample_rate: int = 44100) -> None:
    """Write ``wave`` to ``path`` as 16-bit PCM at ``sample_rate``."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sf.write(path, wave, sample_rate, subtype="PCM_16")


def create_preview(
    wave: np.ndarray,
    path: str,
    *,
    sample_rate: int = 44100,
    duration: float = 5.0,
) -> None:
    """Export the first ``duration`` seconds of ``wave`` to ``path``."""
    preview = wave[: int(sample_rate * duration)]
    export_wav(preview, path, sample_rate=sample_rate)


def embedding_to_params(embedding: np.ndarray) -> tuple[float, float, float]:
    """Return pitch, tempo and cutoff values mapped from ``embedding``."""
    if embedding.size == 0:
        return 0.0, 1.0, 1.0
    emb = embedding.astype(np.float32)
    max_abs = np.max(np.abs(emb)) or 1.0
    emb = emb / max_abs
    pitch = float(emb[0]) * 2.0  # +/-2 semitones
    tempo = 1.0 + float(emb[1]) * 0.1  # ~0.9 - 1.1
    cutoff = 0.5 + float(emb[2]) * 0.5  # 0.0 - 1.0 * Nyquist
    return pitch, tempo, cutoff


def apply_audio_params(
    wave: np.ndarray,
    sample_rate: int,
    pitch: float,
    tempo: float,
    cutoff: float,
) -> np.ndarray:
    """Apply pitch, tempo and low-pass filter adjustments."""
    out = wave
    if pitch:
        out = librosa.effects.pitch_shift(out, sr=sample_rate, n_steps=pitch)
    if tempo != 1.0:
        out = librosa.effects.time_stretch(out, rate=tempo)
    if cutoff < 1.0:
        nyq = 0.5 * sample_rate
        freq = max(min(cutoff * nyq, nyq - 1.0), 20.0) / nyq
        b, a = butter(4, freq, btype="low")
        out = lfilter(b, a, out)
    return out


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Mix audio files")
    parser.add_argument("files", nargs="+", help="Input audio files")
    parser.add_argument("--output", default="final_track.wav", help="Output WAV")
    parser.add_argument("--preview", help="Optional preview WAV path")
    parser.add_argument(
        "--preview-duration",
        type=float,
        default=5.0,
        help="Preview length in seconds",
    )
    parser.add_argument(
        "--qnl-text",
        help="Text to analyse with quantum embedding for live mixing",
    )
    args = parser.parse_args(argv)

    waves = [load_audio(f) for f in args.files]
    mixed = mix_waveforms(waves)

    if args.qnl_text:
        emb = quantum_embed(args.qnl_text)
        pitch, tempo, cutoff = embedding_to_params(emb)
        mixed = apply_audio_params(mixed, 44100, pitch, tempo, cutoff)

    export_wav(mixed, args.output)

    if args.preview:
        create_preview(
            mixed,
            args.preview,
            duration=args.preview_duration,
        )


if __name__ == "__main__":
    main()

