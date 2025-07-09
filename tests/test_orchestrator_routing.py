import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orchestrator import MoGEOrchestrator


def test_route_all_modalities(monkeypatch, tmp_path):
    orch = MoGEOrchestrator()
    info = {"emotion": "joy"}

    monkeypatch.setattr(
        "inanna_ai.corpus_memory.search_corpus",
        lambda *a, **k: [("p", "snippet")],
    )

    voice_path = tmp_path / "voice.wav"
    monkeypatch.setattr(
        "inanna_ai.tts_coqui.synthesize_speech",
        lambda text, emotion: str(voice_path),
    )

    dummy_wave = np.zeros(10, dtype=np.int16)
    monkeypatch.setattr(
        "SPIRAL_OS.qnl_engine.hex_to_song",
        lambda x, duration_per_byte=1.0: ([{"phrase": "p"}], dummy_wave),
    )

    written = {}

    def fake_write(path, wave, sr):
        written["path"] = path
        written["wave"] = wave
        written["sr"] = sr
    monkeypatch.setattr("orchestrator.sf.write", fake_write)

    result = orch.route(
        "hello",
        info,
        text_modality=True,
        voice_modality=True,
        music_modality=True,
    )

    assert result["plane"] in {"ascension", "underworld"}
    assert result["text"]
    assert result["voice_path"] == str(voice_path)
    assert result["music_path"] == str(written["path"])
    assert result["qnl_phrases"] == [{"phrase": "p"}]
    assert isinstance(written["wave"], np.ndarray)
    assert written["sr"] == 44100
