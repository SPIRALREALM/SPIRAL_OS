from __future__ import annotations

"""Mirror reflection loop utilities."""

from pathlib import Path
import json
import logging
from typing import Dict

try:  # pragma: no cover - optional dependency
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore

import numpy as np

from core import video_engine, self_correction_engine
import emotional_state

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[1] / "mirror_thresholds.json"


def load_thresholds() -> Dict[str, float]:
    """Return mirror thresholds from :data:`CONFIG_PATH`."""
    if not CONFIG_PATH.exists():
        logger.warning("mirror_thresholds missing: %s", CONFIG_PATH)
        return {"default": 0.0}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Failed reading mirror_thresholds")
        return {"default": 0.0}
    return {str(k): float(v) for k, v in data.items()}


def detect_expression(frame: np.ndarray) -> str:
    """Return a basic expression label for ``frame``."""
    mean = float(frame.mean())
    if mean > 170:
        return "joy"
    if mean < 85:
        return "sadness"
    return "neutral"


def run_reflection_loop(iterations: int = 10) -> None:
    """Compare intended emotion with avatar output and self-correct."""
    thresholds = load_thresholds()
    stream = video_engine.start_stream()
    for _ in range(iterations):
        try:
            frame = next(stream)
        except StopIteration:
            break
        if cv2 is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        detected = detect_expression(frame)
        intended = emotional_state.get_last_emotion() or "neutral"
        if detected != intended:
            tol = thresholds.get(intended, thresholds.get("default", 0.0))
            self_correction_engine.adjust(detected, intended, tol)


__all__ = ["run_reflection_loop", "detect_expression", "load_thresholds"]
