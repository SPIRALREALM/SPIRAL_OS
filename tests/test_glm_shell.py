import sys
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import importlib


class DummyGLM:
    def __init__(self):
        self.prompts = []

    def complete(self, prompt: str, quantum_context: str | None = None) -> str:
        self.prompts.append((prompt, quantum_context))
        return "response"


def test_send_command(monkeypatch):
    dummy = DummyGLM()
    mod = ModuleType("init_crown_agent")
    mod.initialize_crown = lambda: dummy
    monkeypatch.setitem(sys.modules, "init_crown_agent", mod)
    glm_shell = importlib.import_module("glm_shell")
    out = glm_shell.send_command("ls -la")
    assert out == "response"
    assert dummy.prompts == [("[shell]ls -la", None)]

