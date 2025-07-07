import sys
import os
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from SPIRAL_OS.seven_dimensional_music import main


def test_cli_creates_final_track(tmp_path):
    sr = 44100
    t = np.linspace(0, 0.25, sr // 4, endpoint=False)
    tone = np.sin(2 * np.pi * 220 * t)
    wav_path = tmp_path / "tone.wav"
    sf.write(wav_path, tone, sr)

    out = tmp_path / "final.wav"
    argv_backup = sys.argv.copy()
    sys.argv = [
        "seven_dimensional_music.py",
        str(wav_path),
        "--output",
        str(out),
    ]
    try:
        main()
    finally:
        sys.argv = argv_backup

    assert out.exists()

def test_cli_secret_message(tmp_path):
    sr = 44100
    t = np.linspace(0, 0.25, sr // 4, endpoint=False)
    tone = np.sin(2 * np.pi * 220 * t)
    wav_path = tmp_path / "tone.wav"
    sf.write(wav_path, tone, sr)

    out = tmp_path / "final.wav"
    secret = "hello"
    argv_backup = sys.argv.copy()
    cwd = os.getcwd()
    sys.argv = [
        "seven_dimensional_music.py",
        str(wav_path),
        "--output",
        str(out),
        "--secret",
        secret,
    ]
    try:
        os.chdir(tmp_path)
        main()
    finally:
        os.chdir(cwd)
        sys.argv = argv_backup

    from MUSIC_FOUNDATION.synthetic_stego import extract_data
    hidden = extract_data(tmp_path / "human_layer.wav")
    assert hidden == secret
