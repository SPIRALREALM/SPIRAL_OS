from __future__ import annotations

"""Lightweight text vector memory built on ChromaDB."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
import math

import numpy as np

try:  # pragma: no cover - optional dependency
    import chromadb
    from chromadb.api import Collection
except Exception:  # pragma: no cover - optional dependency
    chromadb = None  # type: ignore
    Collection = object  # type: ignore

from SPIRAL_OS import qnl_utils


_DIR = Path(__file__).resolve().parent / "data" / "vector_memory"
_COLLECTION_NAME = "memory"
_DECAY_SECONDS = 86_400.0  # one day

_COLLECTION: Collection | None = None


def _get_collection() -> Collection:
    """Return a persistent Chroma collection."""
    if chromadb is None:  # pragma: no cover - optional dependency
        raise RuntimeError("chromadb library not installed")
    global _COLLECTION
    if _COLLECTION is None:
        _DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(_DIR))
        _COLLECTION = client.get_or_create_collection(_COLLECTION_NAME)
    return _COLLECTION


def add_vector(text: str, metadata: Dict[str, Any]) -> None:
    """Embed ``text`` and store it with ``metadata``."""
    emb = qnl_utils.quantum_embed(text)
    meta = dict(metadata)
    meta.setdefault("text", text)
    meta.setdefault("timestamp", datetime.utcnow().isoformat())
    col = _get_collection()
    col.add(
        ids=[uuid.uuid4().hex],
        embeddings=[emb.tolist()],
        metadatas=[meta],
    )


def _decay(ts: str) -> float:
    try:
        t = datetime.fromisoformat(ts)
    except Exception:  # pragma: no cover - invalid timestamp
        return 1.0
    age = (datetime.utcnow() - t).total_seconds()
    return math.exp(-age / _DECAY_SECONDS)


def search(query: str, filter: Optional[Dict[str, Any]] = None, *, k: int = 5) -> List[Dict[str, Any]]:
    """Return ``k`` fuzzy matches for ``query`` ordered by decayed similarity."""

    qvec = qnl_utils.quantum_embed(query)
    col = _get_collection()
    res = col.query(query_embeddings=[qvec.tolist()], n_results=max(k * 5, k))
    metas = res.get("metadatas", [[]])[0]
    embs = [np.asarray(e, dtype=float) for e in res.get("embeddings", [[]])[0]]

    results: List[Dict[str, Any]] = []
    for emb, meta in zip(embs, metas):
        if filter is not None:
            skip = False
            for key, val in filter.items():
                if meta.get(key) != val:
                    skip = True
                    break
            if skip:
                continue
        if not emb.size:
            continue
        sim = float(emb @ qvec / ((np.linalg.norm(emb) * np.linalg.norm(qvec)) + 1e-8))
        weight = _decay(meta.get("timestamp", ""))
        score = sim * weight
        out = dict(meta)
        out["score"] = score
        results.append(out)

    results.sort(key=lambda m: m.get("score", 0.0), reverse=True)
    return results[:k]


__all__ = ["add_vector", "search"]

