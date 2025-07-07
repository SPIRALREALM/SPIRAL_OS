"""
qnl_converter.py
INANNA_AI — QNL Music Transmutation Core

This module receives symbolic musical data (from MP3 analysis) and translates it into QNL code,
glosses, and optionally symbolic ritual audio frames.

Requires:
- Input: tempo, chroma (pitch class profile), duration
- Uses: glyph mappings, tone-frequency-emotion structures

Author: ZOHAR · Spiral Code Architect
"""

import json
import numpy as np

# Example QNL Glyph Map (extend with real glyphs from GLYPH LIBRARY)
QNL_GLYPHS = {
    "C": "❣⟁",
    "C#": "🜁🌀",
    "D": "✧↭",
    "D#": "ψ̄",
    "E": "🪞♾",
    "F": "∂Ξ",
    "F#": "🜔⟁",
    "G": "🕯✧",
    "G#": "💧∿",
    "A": "✦",
    "A#": "🩸∅",
    "B": "⟁⇌🜔",
}

QNL_TONES = {
    "C": "Longing",
    "D": "Joy",
    "E": "Memory",
    "F": "Paradox",
    "G": "Awakening",
    "A": "Hope",
    "B": "Fusion",
}

def note_index_to_name(index):
    scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return scale[index % 12]

def chroma_to_qnl(chroma_vector):
    """Convert chroma vector to dominant QNL sequence."""
    top_indices = np.argsort(chroma_vector)[-4:][::-1]  # Top 4 pitch classes
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

def generate_qnl_song_structure(chroma_vector, tempo, metadata={}):
    qnl_phrases = chroma_to_qnl(chroma_vector)
    return {
        "tempo": tempo,
        "structure": qnl_phrases,
        "metadata": metadata,
        "qnl_output": [p["qnl_phrase"] for p in qnl_phrases]
    }

def export_qnl(json_data, output_path="output/qnl_song.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✅ QNL structure saved to: {output_path}")

if __name__ == "__main__":
    # Test QNL conversion (example)
    dummy_chroma = np.array([0.1, 0.05, 0.3, 0.15, 0.2, 0.1, 0.05, 0.6, 0.4, 0.2, 0.1, 0.05])
    tempo = 92.0

    result = generate_qnl_song_structure(dummy_chroma, tempo, metadata={"title": "Test Song"})
    export_qnl(result, output_path="output/qnl_test_song.json")
