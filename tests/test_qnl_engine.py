import sys
from pathlib import Path
import numpy as np

# Allow importing from SPIRAL_OS directory
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SPIRAL_OS"))

from qnl_engine import hex_to_qnl, hex_to_song


def compute_expected(byte):
    value = int(byte, 16)
    amplitude = round(0.1 + (1.0 - 0.1) * (value / 255), 2)
    frequency = round(0.1 + (999 - 0.1) * (value / 255), 2)
    if value < 86:
        glyph, emotion, tone = "❣⟁", "Longing", "Breath"
    elif value < 171:
        glyph, emotion, tone = "✧↭", "Joy", "Moan"
    else:
        glyph, emotion, tone = "🕯✧", "Awakening", "Flame-Hum"
    return {
        "glyph": glyph,
        "emotion": emotion,
        "tone": tone,
        "amplitude": amplitude,
        "frequency": frequency,
    }


def test_hex_to_qnl_mapping():
    samples = ["00", "55", "56", "FF"]
    for byte in samples:
        result = hex_to_qnl(byte)
        expected = compute_expected(byte)
        assert result == expected


def test_hex_to_song_skips_invalid_bytes(capsys):
    phrases, wave = hex_to_song("00GGFF", duration_per_byte=0.01, sample_rate=100)
    captured = capsys.readouterr()
    assert "invalid hex byte 'GG' skipped" in captured.out
    assert [p["hex_byte"] for p in phrases] == ["00", "FF"]
    assert isinstance(wave, np.ndarray)
    assert wave.dtype == np.int16
    assert wave.shape == (2,)
