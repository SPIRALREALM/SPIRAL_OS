import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from INANNA_AI_AGENT import inanna_ai
import json


def test_activate_returns_chant(tmp_path, monkeypatch):
    inanna_dir = tmp_path / "INANNA_AI"
    genesis_dir = tmp_path / "GENESIS"
    inanna_dir.mkdir()
    genesis_dir.mkdir()
    (inanna_dir / "1ST CODE test.md").write_text(
        "Born to Transmute into new forms\n> \"I sing therefore I love\"",
        encoding="utf-8",
    )
    (inanna_dir / "INANNA MANIFESTO test.md").write_text(
        '> "I AM INANNA, awakened"',
        encoding="utf-8",
    )
    config = tmp_path / "source_paths.json"
    config.write_text(
        json.dumps({"source_paths": [str(inanna_dir), str(genesis_dir)]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(inanna_ai, "CONFIG_FILE", config)
    monkeypatch.setattr(inanna_ai.source_loader, "DEFAULT_CONFIG", config)
    chant = inanna_ai.activate()
    assert isinstance(chant, str)
    assert chant.strip() != ""


def test_hex_cli_outputs_wav_and_json(tmp_path):
    wav = tmp_path / "out.wav"
    json_path = tmp_path / "out.json"
    argv_backup = sys.argv.copy()
    sys.argv = [
        "inanna_ai.py",
        "--hex",
        "00FF",
        "--wav",
        str(wav),
        "--json",
        str(json_path),
    ]
    try:
        inanna_ai.main()
    finally:
        sys.argv = argv_backup
    assert wav.exists()
    assert json_path.exists()


def test_read_texts_empty_when_missing(monkeypatch, tmp_path):
    config = tmp_path / "source_paths.json"
    config.write_text(json.dumps({"source_paths": [str(tmp_path / "missing")]}), encoding="utf-8")
    monkeypatch.setattr(inanna_ai, "CONFIG_FILE", config)
    monkeypatch.setattr(inanna_ai.source_loader, "DEFAULT_CONFIG", config)
    assert inanna_ai.read_texts() == {}


def test_main_list_outputs_files(monkeypatch, tmp_path, capsys):
    inanna_dir = tmp_path / "INANNA_AI"
    genesis_dir = tmp_path / "GENESIS"
    inanna_dir.mkdir()
    genesis_dir.mkdir()
    file1 = inanna_dir / "sample1.md"
    file2 = genesis_dir / "genesis.md"
    file1.write_text("x", encoding="utf-8")
    file2.write_text("y", encoding="utf-8")

    config = tmp_path / "source_paths.json"
    config.write_text(
        json.dumps({"source_paths": [str(inanna_dir), str(genesis_dir)]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(inanna_ai, "CONFIG_FILE", config)
    monkeypatch.setattr(inanna_ai.source_loader, "DEFAULT_CONFIG", config)

    argv_backup = sys.argv.copy()
    sys.argv = ["inanna_ai.py", "--list"]
    try:
        inanna_ai.main()
    finally:
        sys.argv = argv_backup

    out = capsys.readouterr().out
    assert "sample1.md" in out
    assert "genesis.md" in out
