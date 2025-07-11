from __future__ import annotations

"""Albedo personality layer combining state context with the GLM."""

from .alchemical_persona import AlchemicalPersona, State
from .glm_integration import GLMIntegration
from . import state_contexts


class AlbedoPersonality:
    """Generate text according to the current alchemical state."""

    def __init__(
        self,
        integration: GLMIntegration | None = None,
        persona: AlchemicalPersona | None = None,
    ) -> None:
        self._persona = persona or AlchemicalPersona()
        self._glm = integration or GLMIntegration()

    @property
    def state(self) -> str:
        """Return the name of the current state."""
        return self._persona.state.value

    def generate_response(self, text: str) -> str:
        """Generate a GLM response for ``text``."""
        entity = self._persona.recognize_entity(text)
        triggers = self._persona.detect_triggers(text)
        self._persona.update_metrics(triggers)
        template = state_contexts.CONTEXTS.get(self._persona.state.value, "{text}")
        ctx = {
            "text": text,
            "entity": entity,
            "triggers": ",".join(sorted(triggers)) if triggers else "",
        }
        prompt = template.format(**ctx)
        reply = self._glm.complete(prompt)
        self._persona.advance()
        return reply


__all__ = ["AlbedoPersonality", "AlchemicalPersona", "State"]
