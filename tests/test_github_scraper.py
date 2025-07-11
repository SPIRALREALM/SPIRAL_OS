import sys
from pathlib import Path
import base64
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai.learning import github_scraper as gs


def test_fetch_repo_saves_readme(monkeypatch, tmp_path):
    content = "hello"
    encoded = base64.b64encode(content.encode()).decode()

    class DummyResp:
        def raise_for_status(self):
            return None
        def json(self):
            return {"content": encoded}

    monkeypatch.setattr(gs, "_headers", lambda: {})
    dummy_req = types.ModuleType("requests")
    dummy_req.get = lambda *a, **k: DummyResp()
    monkeypatch.setattr(gs, "requests", dummy_req)

    paths = gs.fetch_repo("psf/requests", dest_dir=tmp_path)
    expected = tmp_path / "psf_requests_README.md"
    assert paths == [expected]
    assert expected.read_text() == content


def test_fetch_all_uses_repo_list(monkeypatch, tmp_path):
    repos = ["a/b", "c/d"]
    monkeypatch.setattr(gs, "load_repo_list", lambda p=None: repos)

    saved = []
    def dummy_fetch_repo(repo, dest_dir=None):
        path = tmp_path / f"{repo.replace('/', '_')}.md"
        path.write_text(repo, encoding="utf-8")
        saved.append(repo)
        return [path]

    monkeypatch.setattr(gs, "fetch_repo", dummy_fetch_repo)

    files = gs.fetch_all(Path("dummy"))
    assert saved == repos
    assert len(files) == 2
