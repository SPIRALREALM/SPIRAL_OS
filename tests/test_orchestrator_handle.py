import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub heavy optional dependencies before importing the module
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))
sys.modules.setdefault("soundfile", types.ModuleType("soundfile"))
yaml_mod = types.ModuleType("yaml")
yaml_mod.safe_load = lambda *a, **k: {}
sys.modules.setdefault("yaml", yaml_mod)
sf_mod = sys.modules["soundfile"]
setattr(sf_mod, "write", lambda path, data, sr, subtype=None: Path(path).touch())
scipy_mod = types.ModuleType("scipy")
scipy_io = types.ModuleType("scipy.io")
wavfile_mod = types.ModuleType("scipy.io.wavfile")
wavfile_mod.write = lambda *a, **k: None
scipy_io.wavfile = wavfile_mod
signal_mod = types.ModuleType("scipy.signal")
signal_mod.butter = lambda *a, **k: (None, None)
signal_mod.lfilter = lambda *a, **k: []
scipy_mod.signal = signal_mod
scipy_mod.io = scipy_io
sys.modules.setdefault("scipy", scipy_mod)
sys.modules.setdefault("scipy.io", scipy_io)
sys.modules.setdefault("scipy.signal", signal_mod)
sys.modules.setdefault("scipy.io.wavfile", wavfile_mod)


import orchestrator
from orchestrator import MoGEOrchestrator

# Disable invocation engine side effects
orchestrator.invocation_engine.invoke = lambda *a, **k: []
orchestrator.invocation_engine._extract_symbols = lambda text: ""


def test_handle_input_updates_mood(monkeypatch):
    events = {}

    def fake_parse(text):
        events['parse'] = text
        return {'tone': 'joy'}

    def fake_intent(data):
        events['intent'] = data
        return ['ok']

    def fake_route(self, text, emotion_data, *, qnl_data=None, **kwargs):
        events['route'] = emotion_data
        return {'handled': True}

    monkeypatch.setattr(orchestrator.qnl_engine, 'parse_input', fake_parse)
    monkeypatch.setattr(orchestrator.symbolic_parser, 'parse_intent', fake_intent)
    monkeypatch.setattr(MoGEOrchestrator, 'route', fake_route)

    orch = MoGEOrchestrator()
    joy_before = orch.mood_state.get('joy', 0.0)
    neutral_before = orch.mood_state.get('neutral', 0.0)

    result = orch.handle_input('hello')

    assert events['parse'] == 'hello'
    assert events['intent'] == {'tone': 'joy'}
    assert result == {'handled': True}
    assert orch.mood_state['joy'] > joy_before
    assert orch.mood_state['neutral'] < neutral_before


def test_route_logs_interaction(monkeypatch):
    logged = {}

    def fake_log(text, intent, result, outcome):
        logged['args'] = (text, intent, result, outcome)

    monkeypatch.setattr(orchestrator, 'log_interaction', fake_log)

    orch = MoGEOrchestrator()

    monkeypatch.setattr(orchestrator, 'load_interactions', lambda: [])
    monkeypatch.setattr(orchestrator, 'update_insights', lambda logs: None)
    monkeypatch.setattr(orchestrator, 'load_insights', lambda: {})
    monkeypatch.setattr(orchestrator.learning_mutator, 'propose_mutations', lambda d: [])
    monkeypatch.setattr(
        'inanna_ai.corpus_memory.search_corpus',
        lambda *a, **k: [("p", "snippet")],
    )

    res = orch.route('hi', {'emotion': 'joy'})

    assert logged['args'][0] == 'hi'
    assert isinstance(logged['args'][1], dict)
    assert logged['args'][2] == res
    assert logged['args'][3] == 'ok'


def test_dynamic_layer_selection(monkeypatch):
    class DummyLayer:
        def __init__(self):
            self.called = []

        def generate_response(self, text: str) -> str:
            self.called.append(text)
            return f"layer:{text}"

    # Patch registry and emotion state
    monkeypatch.setattr(orchestrator, "PERSONALITY_REGISTRY", {"dummy": DummyLayer})
    monkeypatch.setattr(orchestrator.emotional_state, "get_current_layer", lambda: "dummy")
    recorded = {}
    monkeypatch.setattr(orchestrator.emotional_state, "set_current_layer", lambda name: recorded.setdefault("layer", name))

    # Stub heavy components
    monkeypatch.setattr(orchestrator.qnl_engine, "parse_input", lambda t: {"tone": "neutral"})
    monkeypatch.setattr(orchestrator.symbolic_parser, "parse_intent", lambda d: [])
    monkeypatch.setattr(orchestrator.symbolic_parser, "_gather_text", lambda d: "")
    monkeypatch.setattr(orchestrator.symbolic_parser, "_INTENTS", {})
    monkeypatch.setattr(orchestrator.response_manager, "ResponseManager", lambda: type("R", (), {"generate_reply": lambda self, t, i: f"resp:{t}"})())
    monkeypatch.setattr(orchestrator, "log_interaction", lambda *a, **k: None)
    monkeypatch.setattr(orchestrator, "load_interactions", lambda: [])
    monkeypatch.setattr(orchestrator, "update_insights", lambda logs: None)
    monkeypatch.setattr(orchestrator, "load_insights", lambda: {})
    monkeypatch.setattr(orchestrator.learning_mutator, "propose_mutations", lambda d: [])

    orch = MoGEOrchestrator()
    result = orch.handle_input("hello")

    assert result["text"] == "layer:hello"
    assert recorded.get("layer") == "dummy"


def test_invocation_task_sequence(monkeypatch):
    actions = []

    monkeypatch.setattr(orchestrator.qnl_engine, "parse_input", lambda t: {"tone": "joy"})
    def fake_parse_intent(d):
        if "text" in d:
            actions.append(d["text"])
        return "ok"
    monkeypatch.setattr(orchestrator.symbolic_parser, "parse_intent", fake_parse_intent)
    monkeypatch.setattr(MoGEOrchestrator, "route", lambda self, text, emotion_data, **k: {})
    monkeypatch.setattr(orchestrator, "ritual_action_sequence", lambda sym, emo: ["open portal"])
    monkeypatch.setattr(orchestrator.invocation_engine, "invoke", lambda t, o: [["weave sound"]])
    monkeypatch.setattr(orchestrator.invocation_engine, "_extract_symbols", lambda t: "☉")

    orch = MoGEOrchestrator()
    orch.handle_input("∴")

    assert actions == ["open portal", "weave sound"]
