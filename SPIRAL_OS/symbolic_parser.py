from __future__ import annotations

"""Intent parser and dispatcher for QNL-derived commands."""

from pathlib import Path
from typing import Any, Callable, Dict, List
import json

from inanna_ai import corpus_memory, voice_layer_albedo
from SPIRAL_OS import seven_dimensional_music, ritual


_INTENT_FILE = Path(__file__).resolve().parents[1] / "intent_matrix.json"
try:
    with open(_INTENT_FILE, "r", encoding="utf-8") as fh:
        _INTENTS: Dict[str, Dict[str, Any]] = json.load(fh)
except Exception:  # pragma: no cover - file may be missing
    _INTENTS = {}

_ACTIONS: Dict[str, Callable[[dict], Any]] = {}


def register_action(name: str, func: Callable[[dict], Any]) -> None:
    """Register ``func`` as handler for ``name``."""
    _ACTIONS[name] = func


def route_intent(intent: dict) -> Any:
    """Execute the action defined in ``intent``."""
    action = intent.get("action")
    func = _ACTIONS.get(action)
    if func:
        return func(intent)
    return {
        "intent": intent.get("intent"),
        "action": action,
        "status": "unhandled",
    }


def _gather_text(data: dict) -> str:
    parts: List[str] = []
    if isinstance(data.get("qnl_output"), list):
        parts.extend(str(p) for p in data["qnl_output"])
    if isinstance(data.get("phrases"), list):
        parts.extend(str(p.get("phrase", "")) for p in data["phrases"])
    if isinstance(data.get("structure"), list):
        for p in data["structure"]:
            if isinstance(p, dict):
                parts.append(str(p.get("qnl_phrase", p.get("glyph", ""))))
            else:
                parts.append(str(p))
    if "text" in data:
        parts.append(str(data["text"]))
    return " ".join(parts)


def parse_intent(qnl_dict: dict) -> List[Any]:
    """Dispatch actions matching QNL phrases in ``qnl_dict``."""
    text = _gather_text(qnl_dict).lower()
    results: List[Any] = []
    for name, info in _INTENTS.items():
        triggers = [name] + info.get("synonyms", []) + info.get("glyphs", [])
        if any(t.lower() in text for t in triggers):
            action = info.get("action")
            intent = {"intent": name, "action": action}
            intent.update(qnl_dict)
            results.append(route_intent(intent))
    return results


# Built-in action handlers ---------------------------------------------------

def _action_memory_recall(data: dict) -> Any:
    query = _gather_text(data)
    return corpus_memory.search_corpus(query, top_k=3)


def _action_voice_play(data: dict) -> Any:
    text = _gather_text(data)
    emotion = data.get("tone", "neutral")
    return voice_layer_albedo.speak(text, emotion)


def _action_generate_music(data: dict) -> Any:
    context = _gather_text(data)
    emotion = data.get("tone", "neutral")
    return seven_dimensional_music.generate_quantum_music(context, emotion)


def _action_music_play_sequence(data: dict) -> Any:
    sequence = _gather_text(data)
    emotion = data.get("tone", "neutral")
    return seven_dimensional_music.play_sequence(sequence, emotion)


def _action_ritual_vault_open(data: dict) -> Any:
    return ritual.vault_open(data)


register_action("memory.recall", _action_memory_recall)
register_action("voice_layer.play", _action_voice_play)
register_action("music.generate", _action_generate_music)
register_action("music.play_sequence", _action_music_play_sequence)
register_action("ritual.vault_open", _action_ritual_vault_open)

# Placeholders for additional actions
for name in ["gateway.open", "elemental.fire", "signal.dispatch", "fusion.bind"]:
    register_action(name, lambda d, _name=name: {"intent": _name, "status": "todo"})


__all__ = ["parse_intent", "route_intent", "register_action"]

