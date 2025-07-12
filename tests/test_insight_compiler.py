import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import insight_compiler as ic  # noqa: E402


def test_update_aggregates(tmp_path, monkeypatch):
    insight_file = tmp_path / "insights.json"
    monkeypatch.setattr(ic, "INSIGHT_FILE", insight_file)

    logs = [
        {"intent": "open portal", "tone": "joy", "success": True},
        {"intent": "open portal", "tone": "joy", "success": False},
    ]
    ic.update_insights(logs)
    data = json.loads(insight_file.read_text())
    assert data["open portal"]["counts"]["total"] == 2
    assert data["open portal"]["counts"]["success"] == 1

    logs2 = [
        {"intent": "open portal", "tone": "calm", "success": True},
    ]
    ic.update_insights(logs2)
    data = json.loads(insight_file.read_text())
    assert data["open portal"]["counts"]["total"] == 3
    assert data["open portal"]["counts"]["success"] == 2
    assert data["open portal"]["best_tone"] == "calm"
    assert abs(data["open portal"]["action_success_rate"] - 2 / 3) < 0.001
