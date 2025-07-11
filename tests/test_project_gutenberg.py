import sys
from pathlib import Path
import types
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai.learning import project_gutenberg as pg


def test_search_parses_results(monkeypatch):
    html = """
    <li class='booklink'>
      <a href='/ebooks/123'></a>
      <span class='title'>Title A</span>
    </li>
    <li class='booklink'>
      <a href='/ebooks/456'></a>
      <span class='title'>Title B</span>
    </li>
    """
    class DummyResp:
        text = html
        def raise_for_status(self):
            return None

    dummy_req = types.ModuleType("requests")
    dummy_req.get = lambda *a, **k: DummyResp()
    dummy_req.utils = types.SimpleNamespace(quote=lambda q: q)
    monkeypatch.setattr(pg, "requests", dummy_req)

    class DummySoup:
        def __init__(self, text):
            self.text = text

        def select(self, selector):
            matches = re.findall(r"<a href='/ebooks/(\d+)'></a>\s*<span class='title'>([^<]+)", self.text)
            books = []
            for book_id, title in matches:
                class Book:
                    def __init__(self, bid, t):
                        self.bid = bid
                        self.title = t

                    def find(self, tag, href=False, class_=None):
                        if tag == "a" and href:
                            return {"href": f"/{self.bid}"}
                        if tag == "span" and class_ == "title":
                            return types.SimpleNamespace(get_text=lambda strip=True: self.title)
                        return None

                books.append(Book(book_id, title))
            return books

    monkeypatch.setattr(pg, "BeautifulSoup", lambda text, parser: DummySoup(text))
    results = pg.search("foo", max_results=2)
    assert results == [("123", "Title A"), ("456", "Title B")]


def test_download_tries_patterns(monkeypatch, tmp_path):
    calls = []
    def dummy_download(url, dest):
        calls.append(url)
        if url.endswith("-0.txt"):
            raise RuntimeError("fail")
        dest.write_text("content", encoding="utf-8")
        return dest
    monkeypatch.setattr(pg, "_download_file", dummy_download)
    path = pg.download("789", dest_dir=tmp_path)
    assert path.read_text() == "content"
    assert calls[0].endswith("789-0.txt")
    assert any(url.endswith(".txt") for url in calls)


def test_chunk_respects_token_limit():
    text = " ".join(str(i) for i in range(10))
    chunks = pg.chunk(text, max_tokens=3)
    assert all(len(c.split()) <= 3 for c in chunks)
    assert " ".join(chunks) == text
