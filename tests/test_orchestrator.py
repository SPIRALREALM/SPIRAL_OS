import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import orchestrator
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
    assert result["model"]


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


def test_route_qnl_voice(monkeypatch):
    orch = MoGEOrchestrator()
    info = {"emotion": "neutral"}
    qnl = {"tone": "rubedo"}

    monkeypatch.setattr(
        "inanna_ai.voice_layer_albedo.modulate_voice",
        lambda text, tone: f"{tone}.wav",
    )
    monkeypatch.setattr(
        "SPIRAL_OS.symbolic_parser.parse_intent",
        lambda d: ["ok"],
    )

    result = orch.route(
        "hi",
        info,
        qnl_data=qnl,
        text_modality=False,
        voice_modality=True,
        music_modality=False,
    )

    assert result["voice_path"] == "rubedo.wav"
    assert result["qnl_intents"] == ["ok"]


def test_route_with_albedo_layer(monkeypatch):
    class DummyLayer:
        def __init__(self):
            self.calls = []

        def generate_response(self, text: str) -> str:
            self.calls.append(text)
            return f"albedo:{text}"

    layer = DummyLayer()
    orch = MoGEOrchestrator(albedo_layer=layer)
    info = {"emotion": "joy"}
    result = orch.route("hello", info, text_modality=True, voice_modality=False, music_modality=False)
    assert result["text"] == "albedo:hello"
    assert layer.calls == ["hello"]

def test_context_model_selection(monkeypatch):
    orch = MoGEOrchestrator()
    monkeypatch.setattr(
        "inanna_ai.corpus_memory.search_corpus",
        lambda *a, **k: [("p", "snippet")],
    )
    # First call with high emotion selects Mistral
    res1 = orch.route("I feel happy", {"emotion": "joy"})
    assert res1["model"] == "mistral"

    # Second neutral technical message still routes to Mistral due to context
    res2 = orch.route("import os", {"emotion": "neutral"})
    assert res2["model"] == "mistral"


def test_handle_input_parses_and_routes(monkeypatch):
    events = {}

    def fake_parse(text):
        events["parse"] = text
        return {"tone": "joy"}

    def fake_intent(data):
        events["intent"] = data
        return ["ok"]

    def fake_route(self, text, emotion_data, *, qnl_data=None, **kwargs):
        events["route"] = qnl_data
        return {"result": True}

    monkeypatch.setattr(orchestrator.qnl_engine, "parse_input", fake_parse)
    monkeypatch.setattr(orchestrator.symbolic_parser, "parse_intent", fake_intent)
    monkeypatch.setattr(MoGEOrchestrator, "route", fake_route)

    orch = MoGEOrchestrator()
    out = orch.handle_input("hello")

    assert events["parse"] == "hello"
    assert events["intent"] == {"tone": "joy"}
    assert events["route"] == {"tone": "joy"}
    assert out == {"result": True}


def test_schedule_action_executes(monkeypatch):
    called = []

    timer = orchestrator.schedule_action(lambda: called.append(True), 0.01)
    timer.join(0.1)

    assert called == [True]
