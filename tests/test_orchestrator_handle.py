import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub heavy optional dependencies before importing the module
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))

import orchestrator
from orchestrator import MoGEOrchestrator


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
