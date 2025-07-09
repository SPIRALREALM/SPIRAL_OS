from __future__ import annotations

"""Simple state machine cycling through Nigredo -> Albedo -> Rubedo -> Nigredo."""

from enum import Enum


class State(Enum):
    NIGREDO = "nigredo"
    ALBEDO = "albedo"
    RUBEDO = "rubedo"


class AlbedoCore:
    """Track the current alchemical state."""

    def __init__(self) -> None:
        self.state = State.NIGREDO

    def advance(self) -> None:
        """Advance to the next state, wrapping around after ``RUBEDO``."""
        if self.state is State.NIGREDO:
            self.state = State.ALBEDO
        elif self.state is State.ALBEDO:
            self.state = State.RUBEDO
        elif self.state is State.RUBEDO:
            self.state = State.NIGREDO


__all__ = ["AlbedoCore", "State"]
