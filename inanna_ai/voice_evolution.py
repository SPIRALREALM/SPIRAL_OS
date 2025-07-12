"""Helpers to evolve INANNA's vocal style."""
from __future__ import annotations

from typing import Any, Dict, Iterable
from pathlib import Path
import yaml

from . import db_storage

import numpy as np

DEFAULT_VOICE_STYLES: Dict[str, Dict[str, float]] = {
    "neutral": {"speed": 1.0, "pitch": 0.0},
    "calm": {"speed": 0.9, "pitch": -1.0},
    "excited": {"speed": 1.1, "pitch": 1.0},
}

CONFIG_PATH = Path(__file__).resolve().parents[1] / "voice_config.yaml"


def load_voice_config(path: Path = CONFIG_PATH) -> Dict[str, Dict[str, Any]]:
    """Return archetype settings loaded from ``path`` if it exists."""
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        out: Dict[str, Dict[str, Any]] = {}
        for key, info in data.items():
            if isinstance(info, dict):
                out[key.lower()] = info
        return out
    return {}


VOICE_CONFIG: Dict[str, Dict[str, Any]] = load_voice_config()

for info in VOICE_CONFIG.values():
    name = info.get("tone")
    if name:
        DEFAULT_VOICE_STYLES.setdefault(
            name.lower(),
            {
                "speed": float(info.get("speed", 1.0)),
                "pitch": float(info.get("pitch", 0.0)),
            },
        )


class VoiceEvolution:
    """Manage voice style parameters and allow future fine-tuning."""

    def __init__(self, styles: Dict[str, Dict[str, float]] | None = None) -> None:
        self.styles: Dict[str, Dict[str, float]] = (
            {k: v.copy() for k, v in (styles or DEFAULT_VOICE_STYLES).items()}
        )

    def get_params(self, emotion: str) -> Dict[str, float]:
        """Return style parameters for ``emotion`` label."""
        return self.styles.get(emotion.lower(), self.styles["neutral"])

    def update_from_history(self, history: Iterable[Dict[str, Any]]) -> None:
        """Adjust voice styles based on recent emotion analyses."""
        grouped: Dict[str, Dict[str, list[float]]] = {}
        for entry in history:
            emotion = entry.get("emotion")
            if emotion is None:
                continue
            if "arousal" not in entry or "valence" not in entry:
                continue
            data = grouped.setdefault(
                emotion, {"arousal": [], "valence": [], "sentiment": []}
            )
            data["arousal"].append(entry["arousal"])
            data["valence"].append(entry["valence"])
            if "sentiment" in entry and entry["sentiment"] is not None:
                data["sentiment"].append(entry["sentiment"])

        for emotion, values in grouped.items():
            arousal = float(np.mean(values["arousal"]))
            valence = float(np.mean(values["valence"]))
            sentiment = float(np.mean(values["sentiment"])) if values["sentiment"] else 0.0
            style = self.styles.setdefault(emotion, {"speed": 1.0, "pitch": 0.0})
            new_speed = round(1.0 + (arousal - 0.5) * 0.4, 3)
            new_pitch = round((valence - 0.5) * 2.0, 3)
            weight = 1.0 + sentiment
            style["speed"] = round((style["speed"] + new_speed * weight) / (1.0 + weight), 3)
            style["pitch"] = round((style["pitch"] + new_pitch * weight) / (1.0 + weight), 3)

    def reset(self) -> None:
        """Reset styles to the default values."""
        self.styles = {k: v.copy() for k, v in DEFAULT_VOICE_STYLES.items()}

    def load_profiles(self, db_path: Path = db_storage.DB_PATH) -> None:
        """Populate styles from stored voice profiles."""
        self.styles.update(db_storage.fetch_voice_profiles(db_path=db_path))

    def store_profiles(self, db_path: Path = db_storage.DB_PATH) -> None:
        """Persist current styles to ``db_path``."""
        db_storage.save_voice_profiles(self.styles, db_path=db_path)


_evolver = VoiceEvolution()


def get_voice_params(emotion: str) -> Dict[str, float]:
    """Return parameters from the default :class:`VoiceEvolution`."""
    return _evolver.get_params(emotion)


def update_voice_from_history(history: Iterable[Dict[str, Any]]) -> None:
    """Update the default :class:`VoiceEvolution` with ``history``."""
    _evolver.update_from_history(history)


def load_profiles(db_path: Path = db_storage.DB_PATH) -> None:
    """Load voice profiles into the default :class:`VoiceEvolution`."""
    _evolver.load_profiles(db_path)


def store_profiles(db_path: Path = db_storage.DB_PATH) -> None:
    """Persist profiles from the default :class:`VoiceEvolution`."""
    _evolver.store_profiles(db_path)


__all__ = [
    "VoiceEvolution",
    "get_voice_params",
    "update_voice_from_history",
    "load_profiles",
    "store_profiles",
    "DEFAULT_VOICE_STYLES",
    "VOICE_CONFIG",
    "load_voice_config",
]
