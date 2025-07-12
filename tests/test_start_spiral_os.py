import sys
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import builtins
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Stub heavy dependencies
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.modules["numpy"].random = types.SimpleNamespace(rand=lambda *a, **k: 0)
sys.modules["numpy"].int16 = "int16"
sys.modules["numpy"].float32 = float
sys.modules["numpy"].ndarray = object
scipy_mod = types.ModuleType("scipy")
scipy_io = types.ModuleType("scipy.io")
wavfile_mod = types.ModuleType("scipy.io.wavfile")
wavfile_mod.write = lambda *a, **k: None
scipy_io.wavfile = wavfile_mod
scipy_mod.io = scipy_io
signal_mod = types.ModuleType("scipy.signal")
signal_mod.butter = lambda *a, **k: (None, None)
signal_mod.lfilter = lambda *a, **k: []
scipy_mod.signal = signal_mod
sys.modules.setdefault("scipy.signal", signal_mod)
mod_sf = types.ModuleType("soundfile")
mod_sf.write = lambda *a, **k: None
sys.modules.setdefault("scipy", scipy_mod)
sys.modules.setdefault("scipy.io", scipy_io)
sys.modules.setdefault("scipy.io.wavfile", wavfile_mod)
stable_mod = types.ModuleType("stable_baselines3")
stable_mod.PPO = lambda *a, **k: object()
gym_mod = types.ModuleType("gymnasium")
gym_mod.Env = object
gym_mod.spaces = types.SimpleNamespace(Box=lambda **k: None)
sys.modules.setdefault("stable_baselines3", stable_mod)
sys.modules.setdefault("gymnasium", gym_mod)
sys.modules.setdefault("soundfile", mod_sf)

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
    monkeypatch.setattr(start_spiral_os.logging.config, "dictConfig", lambda c: None)

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

    _run_main(["--interface", "eth0", "--no-server", "--no-reflection"])

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
    monkeypatch.setattr(start_spiral_os.logging.config, "dictConfig", lambda c: None)
    monkeypatch.setattr(start_spiral_os.dnu, "monitor_traffic", lambda interface, packet_count=5: events.append("network"))

    class DummyOrch:
        def handle_input(self, text):
            events.append(text)

    monkeypatch.setattr(start_spiral_os, "MoGEOrchestrator", lambda *a, **k: DummyOrch())

    inputs = iter(["",])
    monkeypatch.setattr(builtins, "input", lambda _="": next(inputs))

    _run_main([
        "--skip-network",
        "--interface",
        "eth0",
        "--no-server",
        "--no-reflection",
    ])

    assert events == ["welcome", "summary", "analyze", "suggest", "reflect"]


def test_command_parsing(monkeypatch):
    events = []
    monkeypatch.setattr(start_spiral_os.inanna_ai, "display_welcome_message", lambda: None)
    monkeypatch.setattr(start_spiral_os.glm_init, "summarize_purpose", lambda: None)
    monkeypatch.setattr(start_spiral_os.glm_analyze, "analyze_code", lambda: None)
    monkeypatch.setattr(start_spiral_os.inanna_ai, "suggest_enhancement", lambda: None)
    monkeypatch.setattr(start_spiral_os.inanna_ai, "reflect_existence", lambda: None)
    monkeypatch.setattr(start_spiral_os.logging.config, "dictConfig", lambda c: None)

    class DummyOrch:
        def handle_input(self, text):
            events.append(text)

    monkeypatch.setattr(start_spiral_os, "MoGEOrchestrator", lambda *a, **k: DummyOrch())
    monkeypatch.setattr(builtins, "input", lambda _="": "")

    _run_main(["--command", "hello world", "--no-server", "--no-reflection"])

    assert events == ["hello world"]


def test_server_and_reflection_run(monkeypatch):
    calls = {"server": False, "reflect": 0}

    monkeypatch.setattr(start_spiral_os.inanna_ai, "display_welcome_message", lambda: None)
    monkeypatch.setattr(start_spiral_os.glm_init, "summarize_purpose", lambda: None)
    monkeypatch.setattr(start_spiral_os.glm_analyze, "analyze_code", lambda: None)
    monkeypatch.setattr(start_spiral_os.inanna_ai, "suggest_enhancement", lambda: None)
    monkeypatch.setattr(start_spiral_os.inanna_ai, "reflect_existence", lambda: None)
    monkeypatch.setattr(start_spiral_os.dnu, "monitor_traffic", lambda *a, **k: None)
    monkeypatch.setattr(start_spiral_os.logging.config, "dictConfig", lambda c: None)

    class DummyOrch:
        def handle_input(self, text):
            return {}

    monkeypatch.setattr(start_spiral_os, "MoGEOrchestrator", lambda *a, **k: DummyOrch())
    monkeypatch.setattr(builtins, "input", lambda _="": "")

    def fake_run_reflection_loop():
        calls["reflect"] += 1

    monkeypatch.setattr(start_spiral_os.reflection_loop, "run_reflection_loop", fake_run_reflection_loop)

    def fake_uvicorn_run(app, host="0.0.0.0", port=8000):
        calls["server"] = True

    monkeypatch.setattr(start_spiral_os.uvicorn, "run", fake_uvicorn_run)

    _run_main([])

    assert calls["server"]
    assert calls["reflect"] > 0

