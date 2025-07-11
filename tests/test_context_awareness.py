import importlib
import sys
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_module(monkeypatch):
    dummy = ModuleType('sentence_transformers')

    class DummyModel:
        def __init__(self, name: str) -> None:
            self.calls = []

        def encode(self, text, convert_to_numpy=True):
            self.calls.append(text)
            return [len(text)]

    dummy.SentenceTransformer = lambda name: DummyModel(name)
    monkeypatch.setitem(sys.modules, 'sentence_transformers', dummy)
    return importlib.reload(
        __import__('inanna_ai.context_awareness', fromlist=['record_interaction'])
    )


def test_record_and_retrieve(monkeypatch):
    ca = _load_module(monkeypatch)

    ca.record_interaction('hello')
    ca.record_interaction('world')

    assert ca.retrieve_context(1) == ['world']
    assert ca.retrieve_context(2) == ['hello', 'world']
    hist = list(ca._HISTORY)
    assert len(hist) == 2
    assert hist[0][1][0] == 5


def test_validator_uses_context(monkeypatch):
    ca = _load_module(monkeypatch)
    from inanna_ai.ethical_validator import EthicalValidator

    val = EthicalValidator(allowed_users={'alice'})

    def fake_semantic(text, recent_context=None):
        if recent_context and 'bad' in ' '.join(recent_context):
            return ['harm']
        return []

    val.semantic_check = fake_semantic

    ca.record_interaction('very bad')

    assert val.validate_text('ok', recent_context=ca.retrieve_context(1)) is False
    assert val.validate_text('ok', recent_context=[]) is True

