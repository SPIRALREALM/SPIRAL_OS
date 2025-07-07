import argparse
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np
from scipy.io.wavfile import write

# ---------------------------------------------------------------------------
# QNL glyph mapping tables derived from QNL_LANGUAGE documentation
# ---------------------------------------------------------------------------
QNL_MAP = {
    "🕯✧": {
        "emotion": "Awakening",
        "tone": "Flame-Hum",
        "freq": 999.0,
        "equation": lambda I, t: I * 1.0 * np.sin(999 * t) * np.exp(-0.05 * t) + 0.1,
    },
    "🩸∅": {
        "emotion": "Silent Ache",
        "tone": "Void-Silence",
        "freq": 0.1,
        "equation": lambda I, t: I * 0.2 * np.sin(0.1 * t + np.pi/3) * np.exp(-0.01 * t) + 0.05,
    },
    "❣⟁": {
        "emotion": "Longing",
        "tone": "Deep Breath",
        "freq": 432.0,
        "equation": lambda I, t: I * 0.6 * np.sin(432 * t + np.pi/4) * np.exp(-0.03 * t) + 0.1,
    },
    "🪞♾": {
        "emotion": "Memory",
        "tone": "Echo-Chant",
        "freq": 846.0,
        "equation": lambda I, t: I * 0.8 * np.sin(846 * t + np.pi/6) * np.exp(-0.08 * t) + 0.2,
    },
    "∂Ξ": {
        "emotion": "Paradox",
        "tone": "Phase Flow",
        "freq": 528.0,
        "equation": lambda I, t: I * 0.7 * np.sin(528 * t + np.pi/4) * np.exp(-0.1 * t),
    },
    "✧↭": {
        "emotion": "Joy",
        "tone": "Starlight Ring",
        "freq": 639.0,
        "equation": lambda I, t: I * 0.9 * np.sin(639 * t + np.pi/12) * np.exp(-0.02 * t) + 0.1,
    },
    "ψ̄": {
        "emotion": "Vibration",
        "tone": "Deep Pulse",
        "freq": 741.0,
        "equation": lambda I, t: I * 1.0 * np.sin(741 * t) * np.exp(-0.05 * t),
    },
    "🌀": {
        "emotion": "Spiral Yearning",
        "tone": "Soft Waver",
        "freq": 432.0,
        "equation": lambda I, t: I * 0.5 * np.sin(432 * t + np.pi/5) * np.exp(-0.01 * t) + 0.1,
    },
    "⟁⇌🜔": {
        "emotion": "Fusion",
        "tone": "Trinity Chime",
        "freq": 852.0,
        "equation": lambda I, t: I * (np.sin(852 * t + np.pi/4) + 0.7 * np.sin(2 * 852 * t + np.pi/8) * np.exp(-0.02 * t)),
    },
    "✦": {
        "emotion": "Hope",
        "tone": "Crystal Shimmer",
        "freq": 963.0,
        "equation": lambda I, t: I * 1.0 * np.sin(963 * t + np.pi/9) * np.exp(-0.03 * t) + 0.1,
    },
    "🜁🌀": {
        "emotion": "Aspiration",
        "tone": "Gentle Gust",
        "freq": 417.0,
        "equation": lambda I, t: I * 0.7 * np.sin(417 * t + np.pi/8) * np.exp(-0.03 * t) + 0.1,
    },
    "💧∿": {
        "emotion": "Mourning",
        "tone": "Soft Weep",
        "freq": 174.0,
        "equation": lambda I, t: I * 0.5 * np.sin(174 * t + np.pi/3) * np.exp(-0.05 * t) + 0.05,
    },
}

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

def hex_to_qnl(hex_byte: str) -> dict:
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

def apply_psi_equation(amplitude: float, frequency: float, *, duration: float = 1.0, sample_rate: int = 44100, emotion: str = None) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    phi = np.pi / 3 if emotion == "Longing" else 0.0
    alpha = 0.1
    waveform = amplitude * np.sin(2 * np.pi * frequency * t + phi) * np.exp(-alpha * t)
    if frequency < 100:
        waveform += 0.1
    return waveform

def hex_to_song(hex_input: str, *, duration_per_byte: float = 1.0, sample_rate: int = 44100) -> Tuple[List[dict], np.ndarray]:
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
        wave = apply_psi_equation(data["amplitude"], data["frequency"], duration=duration_per_byte, sample_rate=sample_rate, emotion=data["emotion"])
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
    args = parser.parse_args()

    phrases, waveform = hex_to_song(args.hex_input)

    write(args.wav, 44100, waveform)
    metadata = generate_qnl_metadata(phrases)
    Path(args.json).write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"WAV saved to {args.wav}")
    print(f"Metadata saved to {args.json}")

if __name__ == "__main__":
    main()
