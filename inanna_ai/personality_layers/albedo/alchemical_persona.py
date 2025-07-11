from __future__ import annotations

"""State machine tracking alchemical progress and emotional metrics."""

from dataclasses import dataclass, field
from enum import Enum
import random
import re
from typing import Callable, Dict, Iterable, Set, Tuple


class State(Enum):
    """Possible alchemical phases."""

    NIGREDO = "nigredo"
    ALBEDO = "albedo"
    RUBEDO = "rubedo"


TriggerSet = Set[str]


@dataclass
class AlchemicalPersona:
    """Track alchemical state, entanglement and shadow balance."""

    weights: Dict[State, float] = field(
        default_factory=lambda: {s: 1.0 for s in State}
    )
    shadow_balance: float = 0.0
    entanglement: float = 0.0
    state: State = State.NIGREDO
    rng: Callable[[], float] = random.random

    def detect_state_trigger(self, text: str) -> Tuple[str, TriggerSet]:
        """Return entity type and emotion triggers found in ``text``."""
        if re.search(r"\b(angel|demon|spirit|god)\b", text, re.I):
            entity = "deity"
        elif re.search(r"\b[A-Z][a-z]+\b", text):
            entity = "person"
        else:
            entity = "object"

        mapping = {
            "love": "affection",
            "joy": "joy",
            "fear": "fear",
            "anger": "anger",
            "hate": "anger",
        }
        lower = text.lower()
        triggers = {label for word, label in mapping.items() if word in lower}
        return entity, triggers

    def update_metrics(self, triggers: Iterable[str] | None) -> None:
        """Adjust entanglement and shadow balance using ``triggers``."""
        if not triggers:
            return
        self.entanglement += 0.1
        if any(t in {"anger", "fear"} for t in triggers):
            self.shadow_balance = min(1.0, self.shadow_balance + 0.1)
        else:
            self.shadow_balance = max(0.0, self.shadow_balance - 0.1)

    def advance(self) -> None:
        """Move to the next state using transition ``weights``."""
        w = self.weights.get(self.state, 1.0)
        if self.rng() > w:
            return
        if self.state is State.NIGREDO:
            self.state = State.ALBEDO
        elif self.state is State.ALBEDO:
            self.state = State.RUBEDO
        else:
            self.state = State.NIGREDO


__all__ = ["AlchemicalPersona", "State", "TriggerSet"]
