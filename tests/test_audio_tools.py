import sys
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import stt_whisper, emotion_analysis
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
