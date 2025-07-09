"""Validate network actions against the INANNA ethics corpus."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Tuple

from . import corpus_memory

logger = logging.getLogger(__name__)


class EthicalValidator:
    """Check actions against ethics and morality references in the corpus."""

    def __init__(self, memory_dirs: Iterable[Path] | None = None) -> None:
        self.memory_dirs = list(memory_dirs) if memory_dirs is not None else list(corpus_memory.MEMORY_DIRS)

    def validate_action(self, action: str, *, top_k: int = 5) -> Tuple[bool, str]:
        """Return ``(allowed, evidence)`` for ``action``."""
        results = corpus_memory.search_corpus(action, top_k=top_k, dirs=self.memory_dirs)
        if not results:
            logger.warning("No ethics corpus results for action: %s", action)
            return False, "no related corpus entry"

        for path, snippet in results:
            text = f"{path} {snippet}".lower()
            if "ethic" in text or "moral" in text:
                logger.info("Action validated via %s", path)
                return True, f"{path}: {snippet}"

        first = results[0]
        logger.info("Action unclear, first hit: %s", first[0])
        return False, f"unclear guidance: {first[0]}: {first[1]}"


__all__ = ["EthicalValidator"]
