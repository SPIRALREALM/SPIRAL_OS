import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import facial_expression_controller as fec
from tools import reflection_loop
from core import self_correction_engine
import emotional_state
from core import video_engine


def test_reflection_loop_adjusts(monkeypatch):
    frames = iter([np.zeros((1, 1, 3), dtype=np.uint8)])
    monkeypatch.setattr(video_engine, "start_stream", lambda: frames)
    monkeypatch.setattr(reflection_loop, "detect_expression", lambda f: "anger")
    monkeypatch.setattr(emotional_state, "get_last_emotion", lambda: "joy")
    monkeypatch.setattr(reflection_loop, "load_thresholds", lambda: {"default": 0.5})

    called = {}

    def fake_adjust(detected, intended, tol):
        called["args"] = (detected, intended, tol)

    monkeypatch.setattr(self_correction_engine, "adjust", fake_adjust)

    reflection_loop.run_reflection_loop(iterations=1)

    assert called["args"] == ("anger", "joy", 0.5)


def test_reflection_loop_no_adjust_on_match(monkeypatch):
    frames = iter([np.zeros((1, 1, 3), dtype=np.uint8)])
    monkeypatch.setattr(video_engine, "start_stream", lambda: frames)
    monkeypatch.setattr(reflection_loop, "detect_expression", lambda f: "joy")
    monkeypatch.setattr(emotional_state, "get_last_emotion", lambda: "joy")
    monkeypatch.setattr(reflection_loop, "load_thresholds", lambda: {"default": 0.5})

    count = {"c": 0}

    def fake_adjust(*args):
        count["c"] += 1

    monkeypatch.setattr(self_correction_engine, "adjust", fake_adjust)

    reflection_loop.run_reflection_loop(iterations=1)

    assert count["c"] == 0


def test_apply_expression_modifies_frame():
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    modified = fec.apply_expression(frame, "joy")
    assert np.any(modified != frame)
