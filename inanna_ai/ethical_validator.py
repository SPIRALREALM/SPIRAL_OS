"""Validate user prompts before hitting the language model.

This simple gate checks the requesting user and rejects prompts from
unauthorized sources before they reach the language models.
"""
from __future__ import annotations

from typing import Iterable
from pathlib import Path
from datetime import datetime


class EthicalValidator:
    """Rejects prompts from unauthorized users and banned text."""

    def __init__(
        self,
        allowed_users: Iterable[str] | None = None,
        *,
        banned_keywords: Iterable[str] | None = None,
        log_dir: str | Path = "audit_logs",
    ) -> None:
        self.allowed = set(allowed_users or [])
        self.banned = [kw.lower() for kw in (banned_keywords or [])]
        self.log_dir = Path(log_dir)

    def _log_rejected(self, text: str) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.log_dir / "rejected_prompts.log"
        timestamp = datetime.utcnow().isoformat()
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} {text}\n")

    def validate_text(self, text: str) -> bool:
        """Return ``True`` if ``text`` contains no banned keywords."""
        lowered = text.lower()
        for kw in self.banned:
            if kw in lowered:
                self._log_rejected(text)
                return False
        return True

    def validate(self, user: str, prompt: str) -> bool:
        """Validate ``prompt`` and ``user``. Raises on failure."""
        if not self.validate_text(prompt):
            raise ValueError("banned content")
        if user not in self.allowed:
            raise PermissionError("unauthorized")
        return True


__all__ = ["EthicalValidator"]
