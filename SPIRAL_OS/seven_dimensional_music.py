#!/usr/bin/env python3
"""Layered music generator for the Spiral OS.

This script loads a melody from a MIDI or WAV file, optionally
transmutes a data payload via the QNL engine, and mixes three
basic layers (human, crystal, synthetic). The final track and
any intermediate layers are written to disk.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
from typing import List, Tuple, Optional
import json
import yaml

import numpy as np
import soundfile as sf
import librosa

try:
    import mido
except Exception:  # pragma: no cover - optional
    mido = None

from SPIRAL_OS import qnl_engine
from SPIRAL_OS.mix_tracks import apply_audio_params, embedding_to_params
from MUSIC_FOUNDATION.synthetic_stego import embed_data, extract_data
from MUSIC_FOUNDATION.seven_plane_analyzer import analyze_seven_planes
from MUSIC_FOUNDATION.qnl_utils import quantum_embed
from inanna_ai import emotion_analysis


QNL_LAYER_MAP_PATH = Path(__file__).resolve().parents[1] / "qnl_to_music_layer_map.yaml"


def load_qnl_layer_map(path: Path = QNL_LAYER_MAP_PATH) -> dict:
    """Return mapping of QNL emotions to layer parameters."""
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return {k.lower(): v for k, v in data.items() if isinstance(v, dict)}
    return {}


def midi_to_wave(midi_path: str, sample_rate: int = 44100) -> Tuple[np.ndarray, int]:
    """Convert a simple MIDI file to a waveform using sine oscillators."""
    if mido is None:
        raise RuntimeError("mido is required for MIDI input")

    mid = mido.MidiFile(midi_path)
    tempo = 500000  # default microseconds per beat
    ticks_per_beat = mid.ticks_per_beat
    note_on_times = {}
    events: List[Tuple[float, float, int]] = []
    current = 0.0
    for msg in mid:
        current += mido.tick2second(msg.time, ticks_per_beat, tempo)
        if msg.type == "set_tempo":
            tempo = msg.tempo
        elif msg.type == "note_on" and msg.velocity > 0:
            note_on_times[msg.note] = current
        elif msg.type in {"note_off", "note_on"} and msg.velocity == 0:
            start = note_on_times.pop(msg.note, None)
            if start is not None:
                events.append((start, current, msg.note))

    if not events:
        return np.zeros(1, dtype=np.float32), sample_rate
    duration = max(e[1] for e in events)
    wave = np.zeros(int(duration * sample_rate) + 1, dtype=np.float32)
    for start, end, note in events:
        start_i = int(start * sample_rate)
        end_i = int(end * sample_rate)
        t = np.arange(end_i - start_i) / sample_rate
        freq = librosa.midi_to_hz(note)
        wave[start_i:end_i] += 0.5 * np.sin(2 * np.pi * freq * t)
    if np.max(np.abs(wave)):
        wave /= np.max(np.abs(wave))
    return wave, sample_rate


def load_melody(path: str) -> Tuple[np.ndarray, int]:
    """Load a melody from a MIDI/WAV/MP3 file."""
    ext = Path(path).suffix.lower()
    if ext in {".mid", ".midi"}:
        return midi_to_wave(path)
    if ext in {".wav", ".mp3", ".flac", ".ogg"}:
        data, sr = librosa.load(path, sr=44100, mono=True)
        return data.astype(np.float32), sr
    raise ValueError(f"Unsupported file type: {path}")


def build_human_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
) -> np.ndarray:
    """Return the base waveform adjusted by audio parameters."""
    out = apply_audio_params(wave, sr, pitch, tempo, cutoff)
    return out.astype(np.float32)


def build_crystal_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
) -> np.ndarray:
    """Return a pre-emphasized shimmer with audio parameter adjustments."""
    out = apply_audio_params(wave, sr, pitch, tempo, cutoff)
    return librosa.effects.preemphasis(out)


def build_synthetic_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
    *,
    weight: float = 1.0,
) -> np.ndarray:
    """Return an amplitude-modulated texture influenced by ``weight``."""
    out = apply_audio_params(wave, sr, pitch, tempo, cutoff)
    t = np.arange(out.size) / sr
    mod_freq = 2 + weight * 4
    mod = np.sin(2 * np.pi * mod_freq * t)
    return out * mod


def build_melody_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
) -> np.ndarray:
    """Return melody layer with standard adjustments."""
    return apply_audio_params(wave, sr, pitch, tempo, cutoff)


def build_rhythm_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
) -> np.ndarray:
    """Return rhythmic pulses modulated by ``tempo``."""
    out = apply_audio_params(wave, sr, pitch, tempo, cutoff)
    t = np.arange(out.size) / sr
    mod = 0.5 * (1.0 + np.sign(np.sin(2 * np.pi * tempo * t)))
    return out * mod


def build_harmonics_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
) -> np.ndarray:
    """Return harmonic component of ``wave``."""
    harm = librosa.effects.harmonic(wave)
    return apply_audio_params(harm, sr, pitch, tempo, cutoff)


def build_ambient_layer(
    wave: np.ndarray,
    sr: int,
    pitch: float = 0.0,
    tempo: float = 1.0,
    cutoff: float = 1.0,
) -> np.ndarray:
    """Return a soft, lowpass ambient layer."""
    out = apply_audio_params(wave, sr, pitch, tempo, cutoff)
    return librosa.effects.preemphasis(out, coef=-0.97)


def build_payload_layer(payload: str, sr: int) -> Tuple[np.ndarray, list[dict]]:
    """Transform a hex payload via ``qnl_engine`` into audio and return phrases."""
    phrases, data = qnl_engine.hex_to_song(payload)
    wave = data.astype(np.float32) / 32767.0
    if sr != 44100:
        wave = librosa.resample(wave, orig_sr=44100, target_sr=sr)
    sf.write("payload_layer.wav", wave, sr)
    return wave, phrases


def mix_layers(layers: List[np.ndarray]) -> np.ndarray:
    """Sum and normalize a list of waveforms."""
    if not layers:
        return np.zeros(1, dtype=np.float32)
    length = max(layer.size for layer in layers)
    mixed = np.zeros(length, dtype=np.float32)
    for layer in layers:
        if layer.size < length:
            layer = np.pad(layer, (0, length - layer.size))
        mixed += layer
    if np.max(np.abs(mixed)):
        mixed /= np.max(np.abs(mixed))
    return mixed


def generate_quantum_music(
    context: str,
    emotion: str,
    *,
    output_dir: str | Path = ".",
) -> Path:
    """Create a short track from ``context`` and ``emotion`` using QNL."""

    emb = quantum_embed(f"{context} {emotion}")
    pitch, tempo, cutoff = embedding_to_params(emb)
    weight = emotion_analysis.emotion_weight(emotion)

    hex_input = context.encode("utf-8").hex()
    _, raw = qnl_engine.hex_to_song(hex_input, duration_per_byte=0.05)
    wave = raw.astype(np.float32) / 32767.0
    sr = 44100

    layer_map = load_qnl_layer_map()
    cfg = layer_map.get(emotion.lower(), layer_map.get("neutral", {}))

    def params(layer: str) -> tuple[float, float, float]:
        info = cfg.get(layer, {})
        p = pitch + float(info.get("pitch", 0.0))
        t = tempo * float(info.get("tempo", 1.0))
        c = cutoff * float(info.get("cutoff", 1.0))
        return p, t, c

    melody = build_melody_layer(wave, sr, *params("melody"))
    rhythm = build_rhythm_layer(wave, sr, *params("rhythm"))
    harmonics = build_harmonics_layer(wave, sr, *params("harmonics"))
    ambient = build_ambient_layer(wave, sr, *params("ambient"))

    synthetic = build_synthetic_layer(
        wave,
        sr,
        pitch,
        tempo,
        cutoff,
        weight=weight,
    )

    crystal = build_crystal_layer(wave, sr, pitch, tempo, cutoff)
    human = build_human_layer(wave, sr, pitch, tempo, cutoff)

    final = mix_layers([melody, rhythm, harmonics, ambient, human, crystal, synthetic])

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"quantum_{abs(hash(context+emotion))}.wav"
    sf.write(out_path, final, sr)

    planes = analyze_seven_planes(final, sr)
    json_path = out_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"planes": planes}, fh, indent=2, ensure_ascii=False)

    return out_path


def play_sequence(name: str, mood: str) -> str:
    """Generate a short clip using ``name`` and ``mood``."""
    out = generate_quantum_music(name, mood, output_dir=tempfile.gettempdir())
    return str(out)


def reactive_music_loop(
    context: str,
    audio_paths: List[str],
    *,
    output_dir: str | Path = ".",
) -> list[Path]:
    """Generate music whenever the detected emotion changes."""

    outputs: list[Path] = []
    last_emotion: str | None = None
    for path in audio_paths:
        info = emotion_analysis.analyze_audio_emotion(str(path))
        emo = info.get("emotion", "neutral")
        if last_emotion is None or emo != last_emotion:
            out = generate_quantum_music(context, emo, output_dir=output_dir)
            outputs.append(out)
        last_emotion = emo
    return outputs


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Create seven dimensional music")
    parser.add_argument("melody", help="Input melody (MIDI/WAV)")
    parser.add_argument("--payload", help="Optional hex data for a payload")
    parser.add_argument("--output", default="final_track.wav", help="Output WAV")
    parser.add_argument(
        "--secret",
        "--message",
        dest="secret",
        help="Message to hide inside human_layer.wav and verify extraction",
    )
    args = parser.parse_args(argv)

    wave, sr = load_melody(args.melody)
    human = build_human_layer(wave, sr)
    crystal = build_crystal_layer(wave, sr)
    synthetic = build_synthetic_layer(wave, sr)

    sf.write("human_layer.wav", human, sr)
    if args.secret:
        embed_data("human_layer.wav", "human_layer.wav", args.secret)
        recovered = extract_data("human_layer.wav")
        print(f"Hidden message extracted: {recovered}")
        human, _ = sf.read("human_layer.wav", always_2d=False)

    sf.write("crystal_layer.wav", crystal, sr)
    sf.write("synthetic_layer.wav", synthetic, sr)

    layers = [human, crystal, synthetic]
    qnl_meta = None
    if args.payload:
        payload_wave, phrases = build_payload_layer(args.payload, sr)
        qnl_meta = qnl_engine.generate_qnl_metadata(phrases)
        layers.append(payload_wave)

    final = mix_layers(layers)
    sf.write(args.output, final, sr)
    print(f"Final track saved to {args.output}")

    planes = analyze_seven_planes(final, sr)
    element_map = {
        "physical": "bass",
        "emotional": "melody",
        "mental": "harmony",
        "astral": "texture",
        "etheric": "crystal",
        "celestial": "percussion",
        "divine": "qnl",
    }
    for plane, elem in element_map.items():
        if plane in planes:
            planes[plane]["element"] = elem

    json_path = Path(args.output).with_suffix(".json")
    out_data = {"planes": planes}
    if qnl_meta is not None:
        out_data["qnl"] = qnl_meta
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out_data, fh, indent=2, ensure_ascii=False)
    print(f"Analysis saved to {json_path}")


if __name__ == "__main__":
    main()
