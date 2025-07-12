from __future__ import annotations

"""Minimal on-disk vector storage used by corpus memory."""

from pathlib import Path
from typing import Iterable, List, Tuple
import json

import numpy as np


_FILE_NAME = "vectors.jsonl"


def add_vector(vector: Iterable[float], dir_path: Path, metadata: dict | None = None) -> None:
    """Append ``vector`` with ``metadata`` to a JSONL file under ``dir_path``."""
    dir_path.mkdir(parents=True, exist_ok=True)
    record = {"vector": list(vector), "metadata": metadata or {}}
    path = dir_path / _FILE_NAME
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False))
        fh.write("\n")


def load_vectors(dir_path: Path) -> List[Tuple[np.ndarray, dict]]:
    """Return stored vectors and metadata from ``dir_path``."""
    path = dir_path / _FILE_NAME
    if not path.exists():
        return []
    entries: List[Tuple[np.ndarray, dict]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            vec = np.asarray(obj.get("vector", []), dtype=float)
            meta = obj.get("metadata", {})
            entries.append((vec, meta))
    return entries


__all__ = ["add_vector", "load_vectors"]
