import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import video_engine


def test_generate_one_frame():
    stream = video_engine.start_stream()
    frame = next(stream)
    assert isinstance(frame, np.ndarray)
    assert frame.ndim == 3 and frame.shape[2] == 3
