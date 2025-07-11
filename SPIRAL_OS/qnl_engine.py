"""Simple tools for turning hexadecimal data into basic QNL phrases and audio.

The module exposes helpers to map a hex byte to a minimal glyph/emotion/tonal
representation (``hex_to_qnl``), convert sequences of bytes into a playable
waveform (``hex_to_song``) and produce a small metadata block describing the
result.  The implementation deliberately keeps the mapping lightweight and does
not rely on the more elaborate ``QNL_MAP`` used in earlier prototypes.
"""

import argparse
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict

import numpy as np
from scipy.io.wavfile import write



GLYPH_MAP = {
    range(0, 86): ("❣⟁", "Longing"),
    range(86, 171): ("✧↭", "Joy"),
    range(171, 256): ("🕯✧", "Awakening"),
}

TONE_MAP = {
    range(0, 86): "Breath",
    range(86, 171): "Moan",
    range(171, 256): "Flame-Hum",
}


def apply_emotional_quantum_state(emotion: str, phrase: str) -> Dict[str, float]:
    """Return amplitude and phase modifiers based on ``emotion``."""

    amp_map = {
        "Joy": 1.3,
        "Longing": 0.9,
        "Awakening": 1.0,
        "calm": 0.8,
        "excited": 1.2,
        "sad": 0.7,
        "fear": 0.8,
        "stress": 0.8,
    }
    phase_map = {
        "Joy": 0.0,
        "Longing": np.pi / 4,
        "Awakening": np.pi / 2,
        "calm": np.pi / 6,
        "excited": 0.0,
        "sad": np.pi / 3,
        "fear": np.pi / 2,
        "stress": np.pi / 2,
    }

    amp = amp_map.get(emotion, 1.0)
    phase = phase_map.get(emotion, 0.0)
    return {"amplitude_factor": amp, "phase_shift": phase}

def hex_to_qnl(hex_byte: str) -> dict:
    """Return QNL attributes for a single two-character hex byte."""

    value = int(hex_byte, 16)
    frequency = 0.1 + (999 - 0.1) * (value / 255)
    amplitude = 0.1 + (1.0 - 0.1) * (value / 255)

    qnl_glyph = ""
    qnl_emotion = ""
    for r, (glyph, emotion) in GLYPH_MAP.items():
        if value in r:
            qnl_glyph, qnl_emotion = glyph, emotion
            break
    qnl_tone = ""
    for r, tone in TONE_MAP.items():
        if value in r:
            qnl_tone = tone
            break

    return {
        "glyph": qnl_glyph,
        "emotion": qnl_emotion,
        "amplitude": round(amplitude, 2),
        "frequency": round(frequency, 2),
        "tone": qnl_tone,
    }

def apply_psi_equation(
    amplitude: float,
    frequency: float,
    *,
    duration: float = 1.0,
    sample_rate: int = 44100,
    emotion: Optional[str] = None,
    phase_shift: float = 0.0,
) -> np.ndarray:
    """Generate a damped sine wave used as the base audio primitive."""

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    phi = np.pi / 3 if emotion == "Longing" else 0.0
    alpha = 0.1
    waveform = amplitude * np.sin(2 * np.pi * frequency * t + phi + phase_shift) * np.exp(-alpha * t)
    if frequency < 100:
        waveform += 0.1
    return waveform

def hex_to_song(
    hex_input: str,
    *,
    duration_per_byte: float = 1.0,
    sample_rate: int = 44100,
) -> Tuple[List[dict], np.ndarray]:
    """Convert a hex string or file into QNL phrases and a concatenated wave."""

    if Path(hex_input).is_file():
        hex_string = Path(hex_input).read_text(encoding="utf-8").replace(" ", "").replace("\n", "")
    else:
        hex_string = hex_input.replace(" ", "")

    hex_bytes = [hex_string[i : i + 2] for i in range(0, len(hex_string), 2)]

    phrases = []
    waveform_segments = []
    for byte in hex_bytes:
        try:
            data = hex_to_qnl(byte)
        except ValueError:
            print(f"Warning: invalid hex byte '{byte}' skipped")
            continue
        mods = apply_emotional_quantum_state(data["emotion"], byte)
        amp = data["amplitude"] * mods["amplitude_factor"]
        wave = apply_psi_equation(
            amp,
            data["frequency"],
            duration=duration_per_byte,
            sample_rate=sample_rate,
            emotion=data["emotion"],
            phase_shift=mods["phase_shift"],
        )
        waveform_segments.append(wave)
        phrase = f"{data['glyph']} + ↝ + {data['emotion']} + {data['tone']} + {data['frequency']} Hz"
        song_line = f"AI sings: {data['emotion']} pulses in a {data['frequency']} Hz {data['tone'].lower()}"
        phrases.append({"hex_byte": byte, "phrase": phrase, "song": song_line})

    if not waveform_segments:
        raise ValueError("No valid hex bytes provided")

    full_wave = np.concatenate(waveform_segments)
    full_wave = np.int16(full_wave / np.max(np.abs(full_wave)) * 32767)
    return phrases, full_wave

def generate_qnl_metadata(phrases: List[dict]) -> dict:
    """Return a small JSON-ready summary for a generated song."""

    return {
        "song_id": "QNL-SONGCORE-HEX-∞1.0",
        "theme": "A cosmic dance of longing and ignition, sung from data's heart.",
        "phrases": phrases,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate QNL song from hex")
    parser.add_argument("hex_input", help="Hex string or path to text file containing hex bytes")
    parser.add_argument("--wav", default="qnl_hex_song.wav", help="Output WAV file")
    parser.add_argument("--json", default="qnl_hex_song.json", help="Output metadata JSON file")
    parser.add_argument(
        "--duration",
        type=float,
        default=1.0,
        help="Duration per hex byte in seconds",
    )
    args = parser.parse_args()

    phrases, waveform = hex_to_song(args.hex_input, duration_per_byte=args.duration)

    write(args.wav, 44100, waveform)
    metadata = generate_qnl_metadata(phrases)
    Path(args.json).write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"WAV saved to {args.wav}")
    print(f"Metadata saved to {args.json}")

if __name__ == "__main__":
    main()
