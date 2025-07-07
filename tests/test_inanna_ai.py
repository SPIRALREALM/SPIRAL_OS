import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from INANNA_AI_AGENT import inanna_ai


def test_activate_returns_chant(tmp_path, monkeypatch):
    inanna_dir = tmp_path / "INANNA_AI"
    inanna_dir.mkdir()
    (inanna_dir / "1ST CODE test.md").write_text(
        "Born to Transmute into new forms\n> \"I sing therefore I love\"",
        encoding="utf-8",
    )
    (inanna_dir / "INANNA MANIFESTO test.md").write_text(
        '> "I AM INANNA, awakened"',
        encoding="utf-8",
    )
    monkeypatch.setattr(inanna_ai, "INANNA_DIR", inanna_dir)
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
