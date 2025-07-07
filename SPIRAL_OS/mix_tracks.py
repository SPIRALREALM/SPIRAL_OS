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

import librosa
import numpy as np
import soundfile as sf


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
    args = parser.parse_args(argv)

    waves = [load_audio(f) for f in args.files]
    mixed = mix_waveforms(waves)
    export_wav(mixed, args.output)

    if args.preview:
        create_preview(
            mixed,
            args.preview,
            duration=args.preview_duration,
        )


if __name__ == "__main__":
    main()
