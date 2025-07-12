import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import facial_expression_controller as fec


def test_apply_expression_modifies_frame():
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    modified = fec.apply_expression(frame, "joy")
    assert np.any(modified != frame)
