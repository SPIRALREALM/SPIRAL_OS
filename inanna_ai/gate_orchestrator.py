"""Simple gate orchestrator translating text to/from complex vectors."""
from __future__ import annotations

from typing import Sequence
import numpy as np


class GateOrchestrator:
    """Map between text and complex vectors for the RFA7D core."""

    def process_inward(self, text: str) -> Sequence[complex]:
        """Convert ``text`` to a complex vector of length 128."""
        data = text.encode("utf-8")[:128]
        vec = [complex(b / 255.0, b / 255.0) for b in data]
        if len(vec) < 128:
            vec.extend([0j] * (128 - len(vec)))
        return vec

    def process_outward(self, grid: np.ndarray) -> str:
        """Translate a grid back into a UTF-8 string."""
        flat = np.asarray(grid).ravel()[:128]
        values = [int(max(0, min(255, round(abs(float(z.real)) * 255)))) for z in flat]
        return bytes(values).decode("utf-8", errors="ignore")


__all__ = ["GateOrchestrator"]
