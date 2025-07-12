import sys
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import builtins

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

start_path = ROOT / "start_spiral_os.py"
loader = SourceFileLoader("start_spiral_os", str(start_path))
spec = importlib.util.spec_from_loader("start_spiral_os", loader)
start_spiral_os = importlib.util.module_from_spec(spec)
loader.exec_module(start_spiral_os)


def _run_main(args):
    argv_backup = sys.argv.copy()
    sys.argv = ["start_spiral_os.py"] + args
    try:
        start_spiral_os.main()
    finally:
        sys.argv = argv_backup


def test_sequence_with_network(monkeypatch):
    events = []
    monkeypatch.setattr(start_spiral_os.inanna_ai, "display_welcome_message", lambda: events.append("welcome"))
    monkeypatch.setattr(start_spiral_os.glm_init, "summarize_purpose", lambda: events.append("summary") or "sum")
    monkeypatch.setattr(start_spiral_os.glm_analyze, "analyze_code", lambda: events.append("analyze") or "ana")
    monkeypatch.setattr(start_spiral_os.inanna_ai, "suggest_enhancement", lambda: events.append("suggest") or [])
    monkeypatch.setattr(start_spiral_os.inanna_ai, "reflect_existence", lambda: events.append("reflect") or "id")

    calls = {}
    def fake_monitor(interface, packet_count=5):
        events.append("network")
        calls["iface"] = interface
    monkeypatch.setattr(start_spiral_os.dnu, "monitor_traffic", fake_monitor)

    class DummyOrch:
        def handle_input(self, text):
            events.append(text)

    monkeypatch.setattr(start_spiral_os, "MoGEOrchestrator", lambda *a, **k: DummyOrch())

    inputs = iter(["hi", ""])
    monkeypatch.setattr(builtins, "input", lambda _="": next(inputs))

    _run_main(["--interface", "eth0"])

    assert events == [
        "welcome",
        "summary",
        "analyze",
        "suggest",
        "reflect",
        "hi",
        "network",
    ]
    assert calls["iface"] == "eth0"


def test_sequence_skip_network(monkeypatch):
    events = []
    monkeypatch.setattr(start_spiral_os.inanna_ai, "display_welcome_message", lambda: events.append("welcome"))
    monkeypatch.setattr(start_spiral_os.glm_init, "summarize_purpose", lambda: events.append("summary") or "sum")
    monkeypatch.setattr(start_spiral_os.glm_analyze, "analyze_code", lambda: events.append("analyze") or "ana")
    monkeypatch.setattr(start_spiral_os.inanna_ai, "suggest_enhancement", lambda: events.append("suggest") or [])
    monkeypatch.setattr(start_spiral_os.inanna_ai, "reflect_existence", lambda: events.append("reflect") or "id")
    monkeypatch.setattr(start_spiral_os.dnu, "monitor_traffic", lambda interface, packet_count=5: events.append("network"))

    class DummyOrch:
        def handle_input(self, text):
            events.append(text)

    monkeypatch.setattr(start_spiral_os, "MoGEOrchestrator", lambda *a, **k: DummyOrch())

    inputs = iter(["",])
    monkeypatch.setattr(builtins, "input", lambda _="": next(inputs))

    _run_main(["--skip-network", "--interface", "eth0"])

    assert events == ["welcome", "summary", "analyze", "suggest", "reflect"]


def test_command_parsing(monkeypatch):
    events = []
    monkeypatch.setattr(start_spiral_os.inanna_ai, "display_welcome_message", lambda: None)
    monkeypatch.setattr(start_spiral_os.glm_init, "summarize_purpose", lambda: None)
    monkeypatch.setattr(start_spiral_os.glm_analyze, "analyze_code", lambda: None)
    monkeypatch.setattr(start_spiral_os.inanna_ai, "suggest_enhancement", lambda: None)
    monkeypatch.setattr(start_spiral_os.inanna_ai, "reflect_existence", lambda: None)

    class DummyOrch:
        def handle_input(self, text):
            events.append(text)

    monkeypatch.setattr(start_spiral_os, "MoGEOrchestrator", lambda *a, **k: DummyOrch())
    monkeypatch.setattr(builtins, "input", lambda _="": "")

    _run_main(["--command", "hello world"])

    assert events == ["hello world"]

