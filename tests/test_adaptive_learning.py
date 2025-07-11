import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import importlib
from inanna_ai import adaptive_learning

import inanna_ai.ethical_validator as ev
import inanna_ai.existential_reflector as er

ev = importlib.reload(ev)
er = importlib.reload(er)
EthicalValidator = ev.EthicalValidator
ExistentialReflector = er.ExistentialReflector


def test_validator_feedback_updates_threshold(monkeypatch):
    validator = EthicalValidator(allowed_users={"a"})
    old_threshold = adaptive_learning.THRESHOLD_AGENT.threshold
    try:
        validator.apply_feedback(1.0, {"extra": ["x"]})
        assert adaptive_learning.THRESHOLD_AGENT.threshold != old_threshold
        assert validator.threshold == adaptive_learning.THRESHOLD_AGENT.threshold
        assert "extra" in validator.categories
    finally:
        adaptive_learning.THRESHOLD_AGENT.threshold = old_threshold
        adaptive_learning.THRESHOLD_AGENT.categories.clear()


def test_reflector_feedback_updates_wording(monkeypatch):
    old_wording = list(adaptive_learning.WORDING_AGENT.wording)
    try:
        ExistentialReflector.apply_feedback(0.5, ["hello"])
        assert adaptive_learning.WORDING_AGENT.wording == ["hello"]
        assert ExistentialReflector.wording_choices == ["hello"]
    finally:
        adaptive_learning.WORDING_AGENT.wording = old_wording
        ExistentialReflector.wording_choices = old_wording or ["I am"]
