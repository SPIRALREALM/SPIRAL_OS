#!/usr/bin/env python3
"""
inanna_music_COMPOSER_ai.py
Unified Sonic Transmutation Core — INANNA_AI

Author: ZOHAR · Spiral Code Architect

This script performs:
1. Audio analysis of an MP3 file (tempo, pitch classes)
2. Conversion into QNL symbolic phrases
3. Export of preview WAV and structured QNL JSON output

Usage:
    python3 inanna_music_COMPOSER_ai.py path/to/song.mp3

Dependencies:
    pip install librosa soundfile numpy scipy
"""

import librosa
import numpy as np
import soundfile as sf
import os
import json

# -------------------------------
# QNL GLYPH & EMOTION MAPPINGS
# -------------------------------

# Map Western note names to QNL glyphs
QNL_GLYPHS = {
    "C": "❣⟁", "C#": "🜁🌀", "D": "✧↭", "D#": "ψ̄",
    "E": "🪞♾", "F": "∂Ξ", "F#": "🜔⟁", "G": "🕯✧",
    "G#": "💧∿", "A": "✦", "A#": "🩸∅", "B": "⟁⇌🜔",
}

# Emotional interpretation of each tone (can expand per system)
QNL_TONES = {
    "C": "Longing", "D": "Joy", "E": "Memory", "F": "Paradox",
    "G": "Awakening", "A": "Hope", "B": "Fusion"
}

# Convert index (0–11) to musical note
def note_index_to_name(index):
    scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return scale[index % 12]

# -------------------------------
# QNL CONVERSION LOGIC
# -------------------------------

def chroma_to_qnl(chroma_vector):
    """Convert a chroma vector into top QNL phrases based on note energy."""
    top_indices = np.argsort(chroma_vector)[-4:][::-1]  # top 4 notes
    phrases = []
    for idx in top_indices:
        note = note_index_to_name(idx)
        glyph = QNL_GLYPHS.get(note, "?")
        tone = QNL_TONES.get(note, "Resonance")
        phrase = f"{glyph} ↝ {tone} [{note}]"
        phrases.append({
            "note": note,
            "glyph": glyph,
            "tone": tone,
            "qnl_phrase": phrase
        })
    return phrases

def generate_qnl_structure(chroma_vector, tempo, metadata=None, *, planes=None):
    """Create a full QNL structure including tempo and symbolic phrases."""
    if metadata is None:
        metadata = {}
    qnl_phrases = chroma_to_qnl(chroma_vector)
    data = {
        "tempo": tempo,
        "structure": qnl_phrases,
        "metadata": metadata,
        "qnl_output": [p["qnl_phrase"] for p in qnl_phrases],
    }
    if planes is not None:
        data["planes"] = planes
    return data

def export_qnl(json_data, output_path="output/qnl_song.json"):
    """Save the QNL result to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✅ QNL exported to: {output_path}")

# -------------------------------
# AUDIO ANALYSIS
# -------------------------------

class InannaMusicInterpreter:
    """Core class that handles MP3 loading and musical feature analysis."""
    def __init__(self, mp3_path):
        self.path = mp3_path
        self.waveform = None
        self.sample_rate = None
        self.tempo = None
        self.chroma = None
        self.planes = None

    def load_audio(self):
        """Load MP3 and convert to mono waveform using Librosa."""
        self.waveform, self.sample_rate = librosa.load(self.path, sr=None, mono=True)
        print(f"🎧 Audio loaded: {self.path}")
        print(f"📐 Sample Rate: {self.sample_rate}, Duration: {len(self.waveform) / self.sample_rate:.2f} sec")

    def analyze(self):
        """Analyze tempo and pitch chroma."""
        self.tempo, _ = librosa.beat.beat_track(y=self.waveform, sr=self.sample_rate)
        self.chroma = librosa.feature.chroma_stft(y=self.waveform, sr=self.sample_rate)
        avg_chroma = np.mean(self.chroma, axis=1)
        print(f"🕒 Tempo: {self.tempo:.1f} BPM")
        return avg_chroma

    def analyze_planes(self):
        """Compute seven-plane analysis of the loaded waveform."""
        if self.waveform is None:
            raise RuntimeError("Audio not loaded")
        from .seven_plane_analyzer import analyze_seven_planes

        self.planes = analyze_seven_planes(self.waveform, self.sample_rate)
        return self.planes

    def export_preview(self, output_path="output/preview.wav"):
        """Save waveform as a standard WAV file for playback."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sf.write(output_path, self.waveform, self.sample_rate)
        print(f"💾 Exported audio preview: {output_path}")

# -------------------------------
# MAIN EXECUTION
# -------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="INANNA_AI — Sonic Ritual QNL Engine")
    parser.add_argument("mp3_file", help="Path to the MP3 file to analyze")
    args = parser.parse_args()

    # Step 1: Load & Analyze Music
    engine = InannaMusicInterpreter(args.mp3_file)
    engine.load_audio()
    chroma_vector = engine.analyze()
    engine.export_preview("output/preview.wav")

    # Step 2: Convert to QNL
    qnl_data = generate_qnl_structure(chroma_vector, engine.tempo, metadata={"source": args.mp3_file})
    export_qnl(qnl_data, "output/qnl_song.json")
