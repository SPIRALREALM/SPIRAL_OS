from __future__ import annotations

"""Helpers for retrieving texts from Project Gutenberg."""

from pathlib import Path
from typing import List, Tuple
import re
import requests
from bs4 import BeautifulSoup

from .. import config

_SEARCH_URL = "https://www.gutenberg.org/ebooks/search/?query={query}"
_TEXT_PATTERNS = ["-0.txt", "-8.txt", ".txt"]


def search(query: str, max_results: int = 5) -> List[Tuple[str, str]]:
    """Return list of ``(book_id, title)`` for ``query``."""
    url = _SEARCH_URL.format(query=requests.utils.quote(query))
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for book in soup.select("li.booklink"):
        if len(results) >= max_results:
            break
        link = book.find("a", href=True)
        if not link:
            continue
        match = re.search(r"/(\d+)", link["href"])
        if not match:
            continue
        title = book.find("span", class_="title").get_text(strip=True)
        results.append((match.group(1), title))
    return results


def _download_file(url: str, dest: Path) -> Path:
    r = requests.get(url, timeout=20)
    if r.ok and r.text.strip():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return dest
    raise RuntimeError(f"Failed to download {url}")


def download(book_id: str, dest_dir: Path | None = None) -> Path:
    """Download ``book_id`` to ``dest_dir`` and return path."""
    if dest_dir is None:
        dest_dir = config.GUTENBERG_DIR
    for pattern in _TEXT_PATTERNS:
        url = f"https://www.gutenberg.org/files/{book_id}/{book_id}{pattern}"
        try:
            return _download_file(url, dest_dir / f"{book_id}.txt")
        except Exception:
            continue
    raise RuntimeError(f"Could not fetch book {book_id}")


def clean_text(path: Path) -> Path:
    """Remove Project Gutenberg headers and footers from ``path``."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    start = text.find("*** START")
    if start != -1:
        text = text[start:]
    end = text.find("*** END")
    if end != -1:
        text = text[:end]
    clean_path = config.GUTENBERG_DIR / path.name
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean_path.write_text(text.strip(), encoding="utf-8")
    return clean_path


def chunk(text: str, max_tokens: int = 200) -> List[str]:
    """Return chunks of ``text`` no longer than ``max_tokens`` words."""
    words = text.split()
    out = []
    for i in range(0, len(words), max_tokens):
        out.append(" ".join(words[i : i + max_tokens]))
    return out

