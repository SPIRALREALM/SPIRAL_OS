import sys
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import stt_whisper, emotion_analysis
from inanna_ai.listening_engine import _extract_features
from tests.data.test1_wav_base64 import TEST1_WAV_BASE64


def _write_audio(tmp_path: Path) -> Path:
    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(base64.b64decode(TEST1_WAV_BASE64))
    return audio_path


def test_transcribe_audio(tmp_path, monkeypatch):
    audio_path = _write_audio(tmp_path)

    class DummyModel:
        def __init__(self):
            self.path = None
        def transcribe(self, path: str):
            self.path = path
            return {"text": "hello"}

    dummy = DummyModel()
    monkeypatch.setattr(stt_whisper, "_get_model", lambda: dummy)

    text = stt_whisper.transcribe_audio(str(audio_path))
    assert text == "hello"
    assert dummy.path == str(audio_path)


def test_analyze_audio_emotion(tmp_path):
    audio_path = _write_audio(tmp_path)
    info = emotion_analysis.analyze_audio_emotion(str(audio_path))
    assert set(info) == {"emotion", "pitch", "tempo"}
    # helper functions should expose archetype and weight
    arch = emotion_analysis.get_current_archetype()
    weight = emotion_analysis.get_emotional_weight()
    assert isinstance(arch, str)
    assert isinstance(weight, float)


def test_extract_features(tmp_path):
    audio_path = _write_audio(tmp_path)
    import librosa

    wave, sr = librosa.load(audio_path, sr=None, mono=True)
    info = _extract_features(wave, sr)
    assert set(info) == {"emotion", "pitch", "tempo", "classification"}


def _save_sine(tmp_path: Path, freq: float, amp: float) -> Path:
    """Create a 1 second sine wave at ``freq`` Hz and ``amp`` amplitude."""
    import numpy as np
    from inanna_ai import utils

    sr = 22050
    t = np.linspace(0, 1.0, int(sr), False)
    wave = amp * np.sin(2 * np.pi * freq * t)
    path = tmp_path / f"{freq}_{amp}.wav"
    utils.save_wav(wave.astype(np.float32), str(path), sr=sr)
    return path


def test_emotion_archetype_mapping(tmp_path):
    joy_path = _save_sine(tmp_path, 440.0, 0.5)
    info = emotion_analysis.analyze_audio_emotion(str(joy_path))
    assert info["emotion"] == "joy"
    assert emotion_analysis.get_current_archetype() == "Jester"

    stress_path = _save_sine(tmp_path, 110.0, 0.9)
    info = emotion_analysis.analyze_audio_emotion(str(stress_path))
    assert info["emotion"] == "stress"
    assert emotion_analysis.get_current_archetype() == "Warrior"

    fear_path = _save_sine(tmp_path, 500.0, 0.02)
    info = emotion_analysis.analyze_audio_emotion(str(fear_path))
    assert info["emotion"] == "fear"
    assert emotion_analysis.get_current_archetype() == "Orphan"
