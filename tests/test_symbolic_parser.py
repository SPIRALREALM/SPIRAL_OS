import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub heavy optional dependencies before importing the module
sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))
sys.modules.setdefault("EmotiVoice", types.ModuleType("EmotiVoice"))
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("soundfile", types.ModuleType("soundfile"))
sys.modules.setdefault("openvoice", types.ModuleType("openvoice"))
sys.modules.setdefault("gtts", types.ModuleType("gtts"))

from SPIRAL_OS import symbolic_parser


def test_parse_intent_memory(monkeypatch):
    called = {}

    def dummy_search(query, top_k=3, dirs=None, model_name="all-MiniLM-L6-v2"):
        called['query'] = query
        return [("p", "s")]

    monkeypatch.setattr(symbolic_parser.corpus_memory, "search_corpus", dummy_search)

    result = symbolic_parser.parse_intent({"text": "summon memory"})

    assert called['query']
    assert result == [[("p", "s")]]



def test_parse_intent_voice(monkeypatch):
    calls = {}

    def fake_speak(text: str, emotion: str):
        calls['args'] = (text, emotion)
        return 'v.wav'

    monkeypatch.setattr(symbolic_parser.speaking_engine, 'synthesize_speech', fake_speak)
    result = symbolic_parser.parse_intent({'text': 'weave sound', 'tone': 'joy'})
    assert result == ['v.wav']
    assert calls['args'] == ('weave sound', 'joy')


def test_parse_intent_placeholder(monkeypatch):
    called = {}

    def fake_open(data):
        called['data'] = data
        return 'ok'

    monkeypatch.setitem(symbolic_parser._ACTIONS, 'gateway.open', fake_open)
    result = symbolic_parser.parse_intent({'text': 'open portal'})
    assert result == ['ok']
    assert called['data']['text'] == 'open portal'
