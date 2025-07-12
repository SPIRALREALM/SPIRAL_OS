import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import corpus_memory_logging as cml


def test_log_and_load(tmp_path, monkeypatch):
    log_path = tmp_path / "interactions.jsonl"
    monkeypatch.setattr(cml, "INTERACTIONS_FILE", log_path)

    cml.log_interaction("hello", {"intent": "greet", "emotion": "joy"}, {}, "ok")
    cml.log_interaction("bye", {"intent": "exit"}, {"emotion": "calm"}, "done")

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["input"] == "hello" and first["emotion"] == "joy"

    all_entries = cml.load_interactions()
    assert len(all_entries) == 2
    assert all_entries[-1]["outcome"] == "done"

    limited = cml.load_interactions(limit=1)
    assert limited == all_entries[-1:]
