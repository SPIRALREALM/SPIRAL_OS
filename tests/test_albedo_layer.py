import sys
import types
from pathlib import Path
import importlib

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

    def post(url, json, timeout=10, headers=None):
        prompts.append((json.get("prompt"), headers))
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
    assert layer.state == "nigredo"


def test_prompt_construction(monkeypatch):
    prompts = []
    _patch_requests(monkeypatch, prompts)
    monkeypatch.setattr(state_contexts, "CONTEXTS", {"nigredo": "A {text}"})
    layer = AlbedoPersonalityLayer()
    layer.generate_response("hello")
    assert prompts == [("A hello", None)]


def test_env_overrides_endpoint(monkeypatch):
    monkeypatch.setenv("GLM_API_URL", "http://foo")
    gi = importlib.reload(glm_integration)
    assert gi.ENDPOINT == "http://foo"


def test_glm_header(monkeypatch):
    prompts = []
    monkeypatch.setenv("GLM_API_KEY", "tok")
    gi = importlib.reload(glm_integration)
    _patch_requests(monkeypatch, prompts)
    gi.generate_completion("hello")
    assert prompts == [("hello", {"Authorization": "Bearer tok"})]
