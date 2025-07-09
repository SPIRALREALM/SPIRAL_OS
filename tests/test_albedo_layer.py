import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai.personality_layers.albedo import (
    AlbedoPersonalityLayer,
    glm_integration,
    state_contexts,
)


class DummyResponse:
    def __init__(self, text: str):
        self._text = text
        self.text = text

    def json(self):
        return {"text": self._text}


def _patch_requests(monkeypatch, prompts):
    dummy = types.ModuleType("requests")

    def post(url, json, timeout=10):
        prompts.append(json.get("prompt"))
        return DummyResponse("reply")

    dummy.post = post
    monkeypatch.setattr(glm_integration, "requests", dummy)


def test_state_transitions(monkeypatch):
    prompts = []
    _patch_requests(monkeypatch, prompts)
    layer = AlbedoPersonalityLayer()

    assert layer.state == "nigredo"
    layer.generate_response("hi")
    assert layer.state == "albedo"
    layer.generate_response("hi")
    assert layer.state == "rubedo"
    layer.generate_response("hi")
    assert layer.state == "rubedo"


def test_prompt_construction(monkeypatch):
    prompts = []
    _patch_requests(monkeypatch, prompts)
    monkeypatch.setattr(state_contexts, "CONTEXTS", {"nigredo": "A {text}"})
    layer = AlbedoPersonalityLayer()
    layer.generate_response("hello")
    assert prompts == ["A hello"]
