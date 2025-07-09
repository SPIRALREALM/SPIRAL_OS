import sys
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai.existential_reflector import ExistentialReflector


class DummyResponse:
    def __init__(self, data: dict[str, str]):
        self._data = data
        self.text = data.get("description", "")

    def json(self):
        return self._data


def test_reflect_on_identity(tmp_path, monkeypatch):
    ina = tmp_path / "INANNA_AI"
    qnl = tmp_path / "QNL_LANGUAGE"
    ina.mkdir()
    qnl.mkdir()
    (ina / "a.md").write_text("hello", encoding="utf-8")
    (qnl / "b.md").write_text("world", encoding="utf-8")

    audit = tmp_path / "audit_logs"

    import inanna_ai.existential_reflector as er
    monkeypatch.setattr(er, "INANNA_DIR", ina)
    monkeypatch.setattr(er, "QNL_DIR", qnl)
    monkeypatch.setattr(er, "AUDIT_DIR", audit)
    monkeypatch.setattr(er, "INSIGHTS_FILE", audit / "existential_insights.txt")

    dummy = ModuleType("requests")
    dummy.post = lambda *a, **k: DummyResponse({"description": "I am"})
    monkeypatch.setattr(er, "requests", dummy)

    desc = ExistentialReflector.reflect_on_identity()
    assert desc == "I am"
    assert (audit / "existential_insights.txt").read_text() == "I am"


def test_reflect_existence_function(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ExistentialReflector, "reflect_on_identity", lambda: "desc")
    from INANNA_AI_AGENT import inanna_ai
    monkeypatch.setattr(inanna_ai, "ExistentialReflector", ExistentialReflector)
    out = inanna_ai.reflect_existence()
    captured = capsys.readouterr().out
    assert out == "desc"
    assert "desc" in captured
