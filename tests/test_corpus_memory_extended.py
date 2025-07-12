import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import corpus_memory


def test_add_entry_logs_and_stores(monkeypatch, tmp_path):
    added = {}

    def dummy_embed(text):
        return np.array([len(text)], dtype=float)

    def dummy_add_vector(vec, dir_path, metadata=None):
        added['vector'] = vec
        added['dir'] = dir_path
        added['meta'] = metadata

    log_calls = {}

    monkeypatch.setattr(corpus_memory.qnl_utils, "quantum_embed", dummy_embed)
    monkeypatch.setattr(corpus_memory.vector_memory, "add_vector", dummy_add_vector)
    monkeypatch.setattr(corpus_memory, "CHROMA_DIR", tmp_path)
    monkeypatch.setattr(
        corpus_memory,
        "corpus_memory_logging",
        type(
            "L",
            (),
            {"log_interaction": lambda *a, **k: log_calls.setdefault("logged", True)},
        ),
    )

    meta = corpus_memory.add_entry("hello", "joy")
    assert added["vector"] == [5.0]
    assert added["dir"] == tmp_path
    assert added["meta"]["tone"] == "joy"
    assert meta["text"] == "hello"
    assert log_calls.get("logged")


def test_search_filters_and_orders(monkeypatch):
    def dummy_embed(text):
        return np.array([len(text)], dtype=float)

    records = [
        (np.array([3.0]), {"text": "foo", "tone": "joy"}),
        (np.array([5.0]), {"text": "bar", "tone": "calm"}),
        (np.array([2.0]), {"text": "baz", "tone": "joy"}),
    ]

    monkeypatch.setattr(corpus_memory.qnl_utils, "quantum_embed", dummy_embed)
    monkeypatch.setattr(corpus_memory.vector_memory, "load_vectors", lambda p: records)

    res = corpus_memory.search("hello!", emotion="joy", similarity_threshold=0.1)
    assert [r["text"] for r in res] == ["foo", "baz"]


def test_prioritize_by_tone():
    items = [
        {"text": "a", "tone": "calm"},
        {"text": "b", "tone": "joy"},
        {"text": "c", "tone": "joy"},
    ]
    out = corpus_memory.prioritize_by_tone(items, "joy")
    assert [i["text"] for i in out[:2]] == ["b", "c"]

