from __future__ import annotations

"""Maintain short-term conversation context with embeddings."""

from collections import deque
from typing import Deque, List, Tuple
import logging

import numpy as np
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore


MAX_HISTORY = 20
MODEL_NAME = "all-MiniLM-L6-v2"

_HISTORY: Deque[Tuple[str, np.ndarray | None]] = deque(maxlen=MAX_HISTORY)
_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer | None:
    """Return global embedding model, loading on demand."""
    global _MODEL
    if _MODEL is None and SentenceTransformer is not None:
        try:
            _MODEL = SentenceTransformer(MODEL_NAME)
        except Exception as exc:  # pragma: no cover - failures
            logging.warning("Failed to load SentenceTransformer: %s", exc)
            _MODEL = None
    return _MODEL


def record_interaction(text: str) -> None:
    """Store ``text`` and its embedding in the history deque."""
    model = _get_model()
    emb = None
    if model is not None:
        emb = np.asarray(model.encode(text, convert_to_numpy=True))
    _HISTORY.append((text, emb))


def retrieve_context(n: int) -> List[str]:
    """Return the last ``n`` interaction texts."""
    return [t for t, _ in list(_HISTORY)[-n:]]


__all__ = ["record_interaction", "retrieve_context", "MAX_HISTORY"]
