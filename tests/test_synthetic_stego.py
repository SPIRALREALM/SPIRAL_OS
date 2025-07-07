import sys
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from MUSIC_FOUNDATION.synthetic_stego import embed_data, extract_data


def test_embed_extract(tmp_path):
    sr = 44100
    data = np.zeros(sr, dtype=np.float32)
    wav = tmp_path / "base.wav"
    sf.write(wav, data, sr)

    stego = tmp_path / "stego.wav"
    embed_data(str(wav), str(stego), "hi")
    assert extract_data(str(stego)) == "hi"
