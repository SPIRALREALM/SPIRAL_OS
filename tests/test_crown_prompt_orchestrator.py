import sys
from pathlib import Path
import types

sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crown_prompt_orchestrator import crown_prompt_orchestrator
import servant_model_manager as smm


class DummyGLM:
    def __init__(self):
        self.seen = None

    def complete(self, prompt: str, quantum_context: str | None = None) -> str:
        self.seen = prompt
        return f"glm:{prompt}"


def test_basic_flow(monkeypatch):
    glm = DummyGLM()
    monkeypatch.setattr(
        "crown_prompt_orchestrator.load_interactions",
        lambda limit=3: [{"input": "hi"}],
    )
    result = crown_prompt_orchestrator("hello", glm)
    assert result["text"].startswith("glm:")
    assert result["model"] == "glm"
    assert "hi" in glm.seen


def test_servant_invocation(monkeypatch):
    glm = DummyGLM()
    smm.register_model("deepseek", lambda p: f"ds:{p}")
    result = crown_prompt_orchestrator("how do things work?", glm)
    assert result["text"] == "ds:how do things work?"
    assert result["model"] == "deepseek"

