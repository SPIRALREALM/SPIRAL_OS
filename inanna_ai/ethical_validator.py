"""Validate user prompts before hitting the language model.

This simple gate checks the requesting user and rejects prompts from
unauthorized sources before they reach the language models.
"""
from __future__ import annotations

from typing import Iterable


class EthicalValidator:
    """Rejects prompts from unauthorized users."""

    def __init__(self, allowed_users: Iterable[str] | None = None) -> None:
        self.allowed = set(allowed_users or [])

    def validate(self, user: str, prompt: str) -> bool:
        """Return ``True`` if ``user`` is authorized or raise ``PermissionError``."""
        if user not in self.allowed:
            raise PermissionError("unauthorized")
        return True


__all__ = ["EthicalValidator"]
