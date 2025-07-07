import numpy as np
from MUSIC_FOUNDATION.qnl_utils import chroma_to_qnl, generate_qnl_structure


def test_generate_qnl_structure():
    chroma = np.zeros(12)
    chroma[0] = 1.0
    chroma[4] = 0.5
    tempo = 120.0

    data = generate_qnl_structure(chroma, tempo, metadata={"title": "x"})

    assert data["tempo"] == tempo
    assert data["metadata"]["title"] == "x"
    assert len(data["structure"]) == 4
    assert data["structure"][0]["glyph"] == '❣⟁'
    assert data["qnl_output"][0].startswith('❣⟁')
