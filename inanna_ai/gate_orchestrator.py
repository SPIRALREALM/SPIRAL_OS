"""Simple gate orchestrator translating text to/from complex vectors."""
from __future__ import annotations

from typing import Sequence
import numpy as np
from pathlib import Path
from time import perf_counter

from . import db_storage


class GateOrchestrator:
    """Map between text and complex vectors for the RFA7D core."""

    def __init__(self, *, db_path: Path | None = None) -> None:
        self._db_path = db_path or db_storage.DB_PATH

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

    @staticmethod
    def _coherence(text: str) -> float:
        words = text.split()
        if not words:
            return 0.0
        return len(set(words)) / len(words)

    @staticmethod
    def _relevance(source: str, generated: str) -> float:
        src = set(source.split())
        gen = set(generated.split())
        if not src or not gen:
            return 0.0
        return len(src & gen) / len(src | gen)

    def benchmark(self, text: str) -> dict:
        start = perf_counter()
        vec = self.process_inward(text)
        out = self.process_outward(np.asarray(vec))
        elapsed = perf_counter() - start
        coh = self._coherence(out)
        rel = self._relevance(text, out)
        db_storage.log_benchmark("gate", elapsed, coh, rel, db_path=self._db_path)
        return {
            "vector": vec,
            "out_text": out,
            "response_time": elapsed,
            "coherence": coh,
            "relevance": rel,
        }


__all__ = ["GateOrchestrator"]
