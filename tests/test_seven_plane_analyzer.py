import sys
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SPIRAL_OS"))

from MUSIC_FOUNDATION.inanna_music_COMPOSER_ai import InannaMusicInterpreter


def test_seven_plane_analyzer_keys(tmp_path):
    sample_rate = 22050
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)
    wav_path = tmp_path / "tone.wav"
    sf.write(wav_path, tone, sample_rate)

    engine = InannaMusicInterpreter(str(wav_path))
    engine.load_audio()
    engine.analyze()
    planes = engine.analyze_planes()

    expected = {
        "physical",
        "emotional",
        "mental",
        "astral",
        "etheric",
        "celestial",
        "divine",
    }
    assert set(planes.keys()) == expected
