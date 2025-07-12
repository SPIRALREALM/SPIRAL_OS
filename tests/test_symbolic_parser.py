import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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

