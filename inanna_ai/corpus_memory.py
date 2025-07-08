from __future__ import annotations

"""Simple embedding-based search across the corpus memory directories."""

import argparse
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore

# Location of the repository root
_REPO_ROOT = Path(__file__).resolve().parents[1]

# Default memory folders relative to the repo root
MEMORY_DIRS: List[Path] = [
    _REPO_ROOT / "INANNA_AI",
    _REPO_ROOT / "GENESIS",
    _REPO_ROOT / "IGNITION",
    _REPO_ROOT / "QNL_LANGUAGE",
]


def scan_memory(dirs: Iterable[Path] = MEMORY_DIRS) -> Dict[str, str]:
    """Return mapping of file path to text for Markdown files in ``dirs``."""
    texts: Dict[str, str] = {}
    for directory in dirs:
        if not directory.exists():
            continue
        for fp in sorted(directory.glob("*.md")):
            try:
                texts[str(fp)] = fp.read_text(encoding="utf-8")
            except Exception:
                continue
    return texts


def _build_embeddings(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    """Return embeddings for ``texts`` using ``model``."""
    return np.asarray(model.encode(texts, convert_to_numpy=True))


def search_corpus(
    query: str,
    *,
    top_k: int = 3,
    dirs: Iterable[Path] | None = None,
    model_name: str = "all-MiniLM-L6-v2",
) -> List[Tuple[str, str]]:
    """Return ``top_k`` matching files and snippets for ``query``."""
    if dirs is None:
        dirs = MEMORY_DIRS

    texts = scan_memory(dirs)
    if not texts:
        return []

    if SentenceTransformer is None:  # pragma: no cover - optional dependency
        raise RuntimeError("sentence-transformers library not installed")
    model = SentenceTransformer(model_name)
    file_paths = list(texts.keys())
    corpus_emb = _build_embeddings(list(texts.values()), model)
    query_emb = _build_embeddings([query], model)[0]

    norms = np.linalg.norm(corpus_emb, axis=1) * np.linalg.norm(query_emb)
    sims = (corpus_emb @ query_emb) / (norms + 1e-8)
    top_idx = sims.argsort()[::-1][:top_k]

    results: List[Tuple[str, str]] = []
    for idx in top_idx:
        path = file_paths[idx]
        snippet = texts[path].splitlines()[0][:200]
        results.append((path, snippet))
    return results


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Search corpus memory")
    parser.add_argument("--search", required=True, help="Query string")
    parser.add_argument("--top", type=int, default=3, help="Number of matches")
    args = parser.parse_args(argv)

    results = search_corpus(args.search, top_k=args.top)
    for path, snippet in results:
        print(f"{path}: {snippet}")


if __name__ == "__main__":
    main()

__all__ = ["scan_memory", "search_corpus", "main", "MEMORY_DIRS"]
