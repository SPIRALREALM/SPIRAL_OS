import sys
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_song_demo import main
from tests.data.short_wav_base64 import SHORT_WAV_BASE64


def test_run_song_demo(tmp_path):
    audio_path = tmp_path / "short.wav"
    audio_path.write_bytes(base64.b64decode(SHORT_WAV_BASE64))
    preview = tmp_path / "preview.wav"
    json_path = tmp_path / "out.json"

    argv_backup = sys.argv.copy()
    sys.argv = [
        "run_song_demo.py",
        str(audio_path),
        "--preview",
        str(preview),
        "--json",
        str(json_path),
    ]
    try:
        main()
    finally:
        sys.argv = argv_backup

    assert preview.exists()
    assert json_path.exists()
