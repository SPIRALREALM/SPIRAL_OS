import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import auto_retrain


def test_build_dataset():
    feedback = [
        {"intent": "open", "action": "door", "success": True},
        {"intent": "close", "action": "door", "success": True},
        {"intent": "fail", "action": "door", "success": False},
    ]
    ds = auto_retrain.build_dataset(feedback)
    assert ds == [
        {"prompt": "open", "completion": "door"},
        {"prompt": "close", "completion": "door"},
    ]


def test_main_invokes_api(tmp_path, monkeypatch):
    insight = {}
    feedback = [
        {
            "intent": "open",
            "action": "door",
            "success": True,
            "response_quality": 1.0,
            "memory_overlap": 0.0,
        }
    ]
    ins = tmp_path / "insight.json"
    ins.write_text(json.dumps(insight), encoding="utf-8")
    fb = tmp_path / "feed.json"
    fb.write_text(json.dumps(feedback), encoding="utf-8")
    monkeypatch.setattr(auto_retrain, "INSIGHT_FILE", ins)
    monkeypatch.setattr(auto_retrain, "FEEDBACK_FILE", fb)
    monkeypatch.setattr(auto_retrain, "NOVELTY_THRESHOLD", 0.0)
    monkeypatch.setattr(auto_retrain, "COHERENCE_THRESHOLD", 0.0)
    monkeypatch.setattr(auto_retrain, "system_idle", lambda: True)

    calls = {}

    def fake_ft(data):
        calls["data"] = data

    dummy_api = SimpleNamespace(fine_tune=fake_ft)
    monkeypatch.setitem(sys.modules, "llm_api", dummy_api)

    auto_retrain.main(["--run"])

    assert calls.get("data") == [{"prompt": "open", "completion": "door"}]
