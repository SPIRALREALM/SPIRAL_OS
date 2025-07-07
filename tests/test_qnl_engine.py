import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import SPIRAL_OS.qnl_engine as qe


def test_hex_to_qnl_uses_qnl_map():
    data = qe.hex_to_qnl("ff")
    assert data["glyph"] == "🕯✧"
    assert data["frequency"] == qe.QNL_MAP["🕯✧"]["freq"]
    assert data["tone"] == qe.QNL_MAP["🕯✧"]["tone"]
