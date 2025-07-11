import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import corpus_memory


def test_cli_search(tmp_path, monkeypatch, capsys):
    dirs = []
    for name in ["INANNA_AI", "GENESIS", "IGNITION", "QNL_LANGUAGE", "github"]:
        d = tmp_path / name
        d.mkdir()
        dirs.append(d)
    (dirs[1] / "found.md").write_text("A magical unicorn appears.", encoding="utf-8")
    (dirs[0] / "other.md").write_text("Nothing to see here.", encoding="utf-8")

    monkeypatch.setattr(corpus_memory, "MEMORY_DIRS", dirs)

    class DummyModel:
        def __init__(self, name: str) -> None:
            pass

        def encode(self, texts, convert_to_numpy=True):
            def vec(t):
                return np.array([t.lower().count("unicorn")], dtype=float)
            if isinstance(texts, list):
                return np.array([vec(t) for t in texts])
            return vec(texts)

    monkeypatch.setattr(corpus_memory, "SentenceTransformer", lambda name: DummyModel(name))

    argv_backup = sys.argv.copy()
    sys.argv = ["corpus_memory", "--search", "unicorn", "--top", "1"]
    try:
        corpus_memory.main()
    finally:
        sys.argv = argv_backup

    out = capsys.readouterr().out.lower()
    assert "found.md" in out
