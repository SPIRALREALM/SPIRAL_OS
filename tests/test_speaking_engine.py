import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import speaking_engine


def test_synthesize_speech_creates_wav(tmp_path, monkeypatch):
    class DummyTTS:
        def __init__(self, text):
            self.text = text
        def save(self, path):
            Path(path).write_bytes(b"dummy")
    monkeypatch.setattr(speaking_engine, "gTTS", DummyTTS)
    monkeypatch.setattr(speaking_engine, "emotion_to_archetype", lambda e: "Sage")
    monkeypatch.setattr(speaking_engine, "get_voice_params", lambda e: {"speed": 1.0, "pitch": 0.0})
    monkeypatch.setattr(speaking_engine.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(speaking_engine.librosa, "load", lambda *a, **k: (np.zeros(22050), 22050))

    path = speaking_engine.synthesize_speech("hello", "calm")
    assert Path(path).exists()
