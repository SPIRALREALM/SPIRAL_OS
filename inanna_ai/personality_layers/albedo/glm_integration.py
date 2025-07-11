"""Compatibility wrapper exposing :class:`~inanna_ai.glm_integration.GLMIntegration`.

``GLMIntegration.complete`` accepts an optional ``quantum_context`` string
forwarded to the HTTP payload.
"""

from ...glm_integration import GLMIntegration, DEFAULT_ENDPOINT, SAFE_ERROR_MESSAGE

__all__ = ["GLMIntegration", "DEFAULT_ENDPOINT", "SAFE_ERROR_MESSAGE"]
