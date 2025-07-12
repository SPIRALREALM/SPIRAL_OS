import sys
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import init_crown_agent
import console_interface
import inanna_ai.glm_integration as gi


class DummyResponse:
    def __init__(self, text: str) -> None:
        self._text = text
        self.text = text

    def json(self):
        return {"text": self._text}

    def raise_for_status(self):
        return None


class DummySession:
    def __init__(self, prompts: list[str]):
        self._prompts = prompts

    def prompt(self, prompt_str: str):
        if not self._prompts:
            raise EOFError
        return self._prompts.pop(0)


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_initialize_crown(monkeypatch, tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("glm_api_url: http://file\n", encoding="utf-8")

    monkeypatch.setattr(init_crown_agent, "CONFIG_FILE", cfg)
    monkeypatch.setattr(init_crown_agent, "_init_memory", lambda c: None)
    monkeypatch.setattr(init_crown_agent, "_init_servants", lambda c: None)
    monkeypatch.setattr(init_crown_agent, "_check_glm", lambda i: None)

    dummy = ModuleType("requests")
    dummy.post = lambda *a, **k: DummyResponse("pong")
    dummy.RequestException = Exception
    monkeypatch.setattr(gi, "requests", dummy)

    monkeypatch.setenv("GLM_API_URL", "http://env")
    monkeypatch.setenv("GLM_API_KEY", "secret")

    client = init_crown_agent.initialize_crown()
    assert isinstance(client, gi.GLMIntegration)
    assert client.endpoint == "http://env"
    assert client.headers == {"Authorization": "Bearer secret"}
    assert client.complete("hi") == "pong"


def test_console_flow(monkeypatch, capsys):
    calls = {}

    def dummy_orchestrator(msg, glm):
        calls["msg"] = msg
        calls["glm"] = glm
        return "reply"

    glm = object()

    monkeypatch.setattr(console_interface, "initialize_crown", lambda: glm)
    monkeypatch.setattr(console_interface, "crown_prompt_orchestrator", dummy_orchestrator)
    monkeypatch.setattr(console_interface, "PromptSession", lambda history=None: DummySession(["hello", "/exit"]))
    monkeypatch.setattr(console_interface, "patch_stdout", lambda: DummyContext())

    console_interface.run_repl()
    out = capsys.readouterr().out
    assert "reply" in out
    assert calls == {"msg": "hello", "glm": glm}
