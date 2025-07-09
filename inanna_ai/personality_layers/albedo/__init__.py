from __future__ import annotations

"""Albedo personality layer combining state context with the GLM."""

from .albedo_core import AlbedoCore, State
from .glm_integration import generate_completion
from . import state_contexts


class AlbedoPersonalityLayer:
    """Generate text according to the current alchemical state."""

    def __init__(self, client=generate_completion) -> None:
        self._core = AlbedoCore()
        self._client = client

    @property
    def state(self) -> str:
        """Return the name of the current state."""
        return self._core.state.value

    def generate_response(self, text: str) -> str:
        """Generate a GLM response for ``text``."""
        template = state_contexts.CONTEXTS.get(self._core.state.value, "{text}")
        prompt = template.format(text=text)
        reply = self._client(prompt)
        self._core.advance()
        return reply


__all__ = ["AlbedoPersonalityLayer", "AlbedoCore", "State"]
