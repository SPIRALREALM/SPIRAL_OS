import json
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from INANNA_AI_AGENT import preprocess, source_loader


def test_preprocess_creates_cache(tmp_path):
    text_dir = tmp_path / "INANNA_AI"
    text_dir.mkdir()
    (text_dir / "sample.md").write_text("## Header\n\nThis is **bold** text.", encoding="utf-8")

    config = tmp_path / "source_paths.json"
    config.write_text(json.dumps({"source_paths": [str(text_dir)]}), encoding="utf-8")

    texts = source_loader.load_sources(config)
    cache_dir = tmp_path / "cache"
    tokens = preprocess.preprocess_texts(texts, cache_dir)

    assert tokens == {"sample.md": ["header", "this", "is", "bold", "text"]}
    cache_file = cache_dir / "sample.md.tokens.json"
    assert cache_file.exists()

    # Call again to ensure cache is loaded
    tokens2 = preprocess.preprocess_texts(texts, cache_dir)
    assert tokens2 == tokens
