from __future__ import annotations

"""Simple embedding-based search across the corpus memory directories."""

import argparse
from datetime import datetime
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from . import config

import numpy as np
try:
    import chromadb
    from chromadb.api import Collection
except Exception:  # pragma: no cover - optional dependency
    chromadb = None  # type: ignore
    Collection = object  # type: ignore
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
    config.GITHUB_DIR,
]

# Directory for the persistent Chroma collection
CHROMA_DIR = _REPO_ROOT / "data" / "chroma"


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


def create_collection(name: str = "corpus", dir_path: Path = CHROMA_DIR) -> Collection:
    """Return a Chroma collection stored under ``dir_path``."""
    if chromadb is None:  # pragma: no cover - optional dependency
        raise RuntimeError("chromadb library not installed")
    dir_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(dir_path))
    return client.get_or_create_collection(name)


def add_embeddings(
    collection: Collection,
    texts: Dict[str, str],
    model: SentenceTransformer,
) -> None:
    """Add ``texts`` to ``collection`` with metadata."""
    paths = list(texts.keys())
    emb = _build_embeddings(list(texts.values()), model)
    metadatas = [
        {"path": p, "timestamp": datetime.fromtimestamp(os.path.getmtime(p)).isoformat()}
        for p in paths
    ]
    collection.add(
        ids=paths,
        embeddings=[e.tolist() for e in emb],
        metadatas=metadatas,
    )


def reindex_corpus(
    dirs: Iterable[Path] | None = None,
    *,
    model_name: str = "all-MiniLM-L6-v2",
    name: str = "corpus",
    dir_path: Path = CHROMA_DIR,
) -> None:
    """Rebuild the Chroma collection from Markdown sources."""
    if dirs is None:
        dirs = MEMORY_DIRS
    texts = scan_memory(dirs)
    if not texts:
        return
    if SentenceTransformer is None:  # pragma: no cover - optional dependency
        raise RuntimeError("sentence-transformers library not installed")
    if chromadb is None:  # pragma: no cover - optional dependency
        raise RuntimeError("chromadb library not installed")
    model = SentenceTransformer(model_name)
    client = chromadb.PersistentClient(path=str(dir_path))
    try:
        client.delete_collection(name)
    except Exception:
        pass
    collection = client.create_collection(name)
    add_embeddings(collection, texts, model)


def search_corpus(
    query: str,
    *,
    top_k: int = 3,
    dirs: Iterable[Path] | None = None,  # unused
    model_name: str = "all-MiniLM-L6-v2",
) -> List[Tuple[str, str]]:
    """Return ``top_k`` matching files and snippets for ``query``."""
    if SentenceTransformer is None:  # pragma: no cover - optional dependency
        raise RuntimeError("sentence-transformers library not installed")
    if chromadb is None:  # pragma: no cover - optional dependency
        raise RuntimeError("chromadb library not installed")

    collection = create_collection()
    model = SentenceTransformer(model_name)
    query_emb = _build_embeddings([query], model)[0]

    res = collection.query(query_embeddings=[query_emb.tolist()], n_results=top_k)
    ids = res.get("ids", [[]])[0]
    results: List[Tuple[str, str]] = []
    for p in ids:
        try:
            text = Path(p).read_text(encoding="utf-8")
            snippet = text.splitlines()[0][:200]
        except Exception:
            snippet = ""
        results.append((p, snippet))
    return results


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Search corpus memory")
    parser.add_argument("--search", help="Query string")
    parser.add_argument("--top", type=int, default=3, help="Number of matches")
    parser.add_argument("--reindex", action="store_true", help="Rebuild index")
    args = parser.parse_args(argv)

    if args.reindex:
        reindex_corpus()
        if not args.search:
            return

    if not args.search:
        parser.error("--search is required unless --reindex is used")

    results = search_corpus(args.search, top_k=args.top)
    for path, snippet in results:
        print(f"{path}: {snippet}")


if __name__ == "__main__":
    main()

__all__ = [
    "scan_memory",
    "create_collection",
    "add_embeddings",
    "reindex_corpus",
    "search_corpus",
    "main",
    "MEMORY_DIRS",
    "CHROMA_DIR",
]
