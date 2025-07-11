from __future__ import annotations

"""Fetch README files from GitHub repositories."""

from pathlib import Path
from typing import List
import base64
import os
import requests

from .. import config

_LIST_FILE = Path(__file__).resolve().parents[2] / "learning_sources" / "github_repos.txt"
_API_BASE = "https://api.github.com/repos/"


def load_repo_list(path: Path | None = None) -> List[str]:
    """Return repositories listed in ``path``."""
    if path is None:
        path = _LIST_FILE
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def _headers() -> dict:
    token = config.GITHUB_TOKEN
    if not token:
        token = os.getenv("GITHUB_TOKEN", "")
    if token:
        return {"Authorization": f"token {token}"}
    return {}


def fetch_repo(repo: str, dest_dir: Path | None = None) -> List[Path]:
    """Download README for ``repo`` and return saved paths."""
    if dest_dir is None:
        dest_dir = config.GITHUB_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    owner_repo = repo.strip()
    readme_url = f"{_API_BASE}{owner_repo}/readme"
    r = requests.get(readme_url, headers=_headers(), timeout=10)
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data.get("content", "")).decode("utf-8", "ignore")
    path = dest_dir / f"{owner_repo.replace('/', '_')}_README.md"
    path.write_text(content, encoding="utf-8")
    return [path]


def fetch_all(path: Path | None = None) -> List[Path]:
    """Fetch all repositories listed in ``path``."""
    files: List[Path] = []
    for repo in load_repo_list(path):
        try:
            files.extend(fetch_repo(repo))
        except Exception:
            continue
    return files

