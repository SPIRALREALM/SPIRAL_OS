import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orchestrator import MoGEOrchestrator


def test_route_text_only(tmp_path, monkeypatch):
    orch = MoGEOrchestrator()
    info = {"emotion": "joy"}
    monkeypatch.setattr(
        "inanna_ai.corpus_memory.search_corpus",
        lambda *a, **k: [("p", "snippet")],
    )
    result = orch.route("hello", info, text_modality=True, voice_modality=False, music_modality=False)
    assert result["plane"] == "ascension"
    assert "text" in result and result["text"]


def test_route_voice(tmp_path):
    orch = MoGEOrchestrator()
    info = {"emotion": "calm"}
    result = orch.route("hi", info, text_modality=False, voice_modality=True, music_modality=False)
    assert result["plane"] == "ascension"
    assert Path(result["voice_path"]).exists()


def test_route_music(tmp_path):
    orch = MoGEOrchestrator()
    info = {"emotion": "joy"}
    result = orch.route("hi", info, text_modality=False, voice_modality=False, music_modality=True)
    assert Path(result["music_path"]).exists()
    assert result["qnl_phrases"]
