from __future__ import annotations

"""Compose short ritual music based on emotion and play it."""

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from MUSIC_FOUNDATION import layer_generators
from MUSIC_FOUNDATION.synthetic_stego_engine import encode_phrase
from MUSIC_FOUNDATION.inanna_music_COMPOSER_ai import (
    load_emotion_music_map,
    select_music_params,
)
from inanna_ai.speaking_engine import play_wav

EMOTION_MAP = Path(__file__).resolve().parent / "emotion_music_map.yaml"
RITUAL_PROFILE = Path(__file__).resolve().parent / "ritual_profile.json"


def load_ritual_profile(path: Path = RITUAL_PROFILE) -> dict:
    """Return ritual mappings loaded from ``path`` if available."""
    if path.exists():
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return {k: v for k, v in data.items() if isinstance(v, dict)}
    return {}


def compose_ritual_music(
    emotion: str,
    ritual: str,
    *,
    hide: bool = False,
    out_path: Path = Path("ritual.wav"),
) -> Path:
    """Generate a simple melody and optionally hide ritual steps."""
    mapping = load_emotion_music_map(EMOTION_MAP)
    tempo, _scale, melody, _rhythm = select_music_params(emotion, mapping, 100.0)
    wave = layer_generators.compose_human_layer(tempo, melody, wav_path=str(out_path))

    if hide:
        profile = load_ritual_profile()
        phrase = " ".join(profile.get(ritual, {}).get(emotion, []))
        if phrase:
            stego_wave = encode_phrase(phrase)
            if stego_wave.size < wave.size:
                stego_wave = np.pad(stego_wave, (0, wave.size - stego_wave.size))
            mixed = wave[: stego_wave.size] + stego_wave[: wave.size]
            max_val = np.max(np.abs(mixed))
            if max_val > 0:
                mixed /= max_val
            sf.write(out_path, mixed, 44100)
    return out_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Play ritual music")
    parser.add_argument("--emotion", default="neutral", help="Emotion driving the tone")
    parser.add_argument("--ritual", default="\u2609", help="Ritual symbol")
    parser.add_argument(
        "--stego",
        action="store_true",
        help="Hide ritual phrase inside the WAV",
    )
    parser.add_argument("--output", default="ritual.wav", help="Output WAV path")
    args = parser.parse_args(argv)

    out = compose_ritual_music(
        args.emotion, args.ritual, hide=args.stego, out_path=Path(args.output)
    )
    play_wav(str(out))


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
