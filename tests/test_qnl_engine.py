import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import SPIRAL_OS.qnl_engine as qe


def test_hex_to_qnl_basic():
    data = qe.hex_to_qnl('ff')
    assert data['glyph'] == '🕯✧'
    assert data['emotion'] == 'Awakening'
    assert data['tone'] == 'Flame-Hum'
    assert data['amplitude'] == 1.0
    assert data['frequency'] == 999.0


def test_hex_to_song_sequence():
    phrases, wave = qe.hex_to_song('0aFF', duration_per_byte=0.1)
    assert [p['hex_byte'] for p in phrases] == ['0a', 'FF']
    # Expect 0.2 seconds of audio at 44100 Hz
    assert len(wave) == 8820
    assert wave.dtype == np.int16
    assert np.max(np.abs(wave)) <= 32767
