from __future__ import annotations

"""Utilities for looking up QNL glyphs and recalling archetype notes."""

import re
from typing import Dict, List

import numpy as np
try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore

from MUSIC_FOUNDATION.qnl_utils import QNL_GLYPHS, QNL_TONES

_MODEL: "SentenceTransformer | None" = None


# Map moods to lists of informal tags
MOOD_TAGS: Dict[str, List[str]] = {
    "longing": ["yearning", "desire"],
    "joy": ["happy", "celebration"],
    "memory": ["past", "nostalgia"],
    "paradox": ["mystery", "conflict"],
    "awakening": ["rebirth", "insight"],
    "hope": ["faith", "aspiration"],
    "fusion": ["unity", "merging"],
}


_ARCHETYPE_SNIPPETS: Dict[str, str] = {
    "Jester": "Playful trickster bringing lightness and humour.",
    "Warrior": "Fierce champion of strength and discipline.",
    "Orphan": "Seeker of belonging and safety amongst others.",
    "Caregiver": "Nurturer who offers compassion and support.",
    "Hero": "Brave soul facing trials with courage.",
    "Sage": "Patient keeper of knowledge and truth.",
    "Everyman": "Relatable figure grounded in common life.",
}


def _get_model(name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Return a cached ``SentenceTransformer`` model."""
    if SentenceTransformer is None:  # pragma: no cover - optional dependency
        raise RuntimeError("sentence-transformers library not installed")
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(name)
    return _MODEL


def quantum_embed(text: str) -> np.ndarray:
    """Return an embedding vector for ``text``."""
    model = _get_model()
    emb = model.encode(text)
    return np.asarray(emb, dtype=np.float32)


# Reverse mapping from mood labels to QNL glyphs via note names
_MOOD_TO_GLYPH: Dict[str, str] = {
    mood: QNL_GLYPHS.get(note, "?")
    for note, mood in QNL_TONES.items()
}


def expand_glyphs(text: str) -> List[str]:
    """Return QNL glyphs referenced in ``text``.

    Note names (e.g. ``C#``) and mood words (``joy``, ``memory``) are expanded
    to their corresponding glyph symbols.
    """
    tokens = re.findall(r"[A-G]#?|[\w]+", text)
    glyphs: List[str] = []
    for token in tokens:
        key = token.upper()
        if key in QNL_GLYPHS:
            glyphs.append(QNL_GLYPHS[key])
            continue
        mood = token.lower()
        glyph = _MOOD_TO_GLYPH.get(mood)
        if glyph:
            glyphs.append(glyph)
    return glyphs


def recall_archetype(name: str) -> Dict[str, object]:
    """Return a short text blurb and embedding for ``name``."""
    title = name.capitalize()
    text = _ARCHETYPE_SNIPPETS.get(title, "")
    emb = quantum_embed(text or title)
    return {"name": title, "text": text, "embedding": emb}


__all__ = [
    "MOOD_TAGS",
    "expand_glyphs",
    "recall_archetype",
    "quantum_embed",
]
