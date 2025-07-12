from __future__ import annotations

"""Avatar video generation utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Iterator, Optional
import logging
import numpy as np
import tomllib

from .facial_expression_controller import apply_expression
import emotional_state
from . import context_tracker

try:  # pragma: no cover - optional dependency
    import mediapipe as mp
except Exception:  # pragma: no cover - optional dependency
    mp = None  # type: ignore

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "guides" / "avatar_config.toml"


@dataclass
class AvatarTraits:
    """Simple avatar trait configuration."""

    eye_color: tuple[int, int, int] = (0, 255, 0)
    sigil: str = ""


def _load_traits() -> AvatarTraits:
    if not _CONFIG_PATH.exists():
        logger.warning("Avatar config missing: %s", _CONFIG_PATH)
        return AvatarTraits()
    data = tomllib.loads(_CONFIG_PATH.read_text())
    eye_color = data.get("eye_color", [0, 255, 0])
    if isinstance(eye_color, list) and len(eye_color) == 3:
        eye = tuple(int(v) for v in eye_color)
    else:
        eye = (0, 255, 0)
    sigil = str(data.get("sigil", ""))
    return AvatarTraits(eye, sigil)


def _get_face_mesh() -> Optional[object]:  # pragma: no cover - optional
    if mp is None:
        return None
    return mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, refine_landmarks=True
    )


def generate_avatar_stream() -> Iterator[np.ndarray]:
    """Yield RGB frames representing the configured avatar."""
    traits = _load_traits()
    color = np.array(traits.eye_color, dtype=np.uint8)
    mesh = _get_face_mesh()
    try:
        while True:
            frame = np.zeros((64, 64, 3), dtype=np.uint8)
            frame[:] = color
            if context_tracker.state.avatar_loaded:
                emotion = emotional_state.get_last_emotion()
                frame = apply_expression(frame, emotion)
                if mesh is not None:
                    # Feed dummy frame to mediapipe to update landmarks
                    _ = mesh.process(frame)
            yield frame
    finally:
        if mesh is not None:
            mesh.close()


def start_stream() -> Iterator[np.ndarray]:
    """Return an iterator producing avatar frames."""
    return generate_avatar_stream()


__all__ = ["start_stream", "generate_avatar_stream", "AvatarTraits"]
