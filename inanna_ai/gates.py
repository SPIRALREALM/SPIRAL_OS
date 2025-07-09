"""Gating system for communication with the RFA core."""

from __future__ import annotations

import base64
import os
from typing import Any, List

import numpy as np
from cryptography.fernet import Fernet
from OpenSSL import rand as openssl_rand

try:  # optional quantum library
    import qutip
except Exception:  # pragma: no cover - optional dependency
    qutip = None  # type: ignore


class Gate:
    """Base gate class."""

    def inward(self, data: Any) -> Any:
        """Process data coming into the core."""
        return data

    def outward(self, data: Any) -> Any:
        """Process data leaving the core."""
        return data


class Gate1(Gate):
    """Add and remove random noise."""

    def __init__(self, scale: float = 0.01) -> None:
        self.scale = scale
        self._noise: np.ndarray | None = None

    def outward(self, data: Any) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        self._noise = np.random.normal(0, self.scale, size=arr.shape).astype(np.float32)
        return arr + self._noise

    def inward(self, data: Any) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        if self._noise is not None:
            arr = arr - self._noise
            self._noise = None
        return arr


class Gate2(Gate):
    """Encrypt and decrypt data using a Fernet key seeded with pyOpenSSL."""

    def __init__(self, key: bytes | None = None) -> None:
        if key is None:
            openssl_rand.add(os.urandom(32), 32)
            key = Fernet.generate_key()
        self.key = key
        self._fernet = Fernet(self.key)

    def outward(self, data: Any) -> bytes:
        if qutip is not None and isinstance(data, qutip.Qobj):
            arr = np.array(data.full()).astype(np.float32)
        else:
            arr = np.asarray(data, dtype=np.float32)
        return self._fernet.encrypt(arr.tobytes())

    def inward(self, data: bytes) -> np.ndarray:
        decrypted = self._fernet.decrypt(data)
        return np.frombuffer(decrypted, dtype=np.float32)


class Gate3(Gate):
    """Apply a simple reversible embedding transformation."""

    def __init__(self) -> None:
        self._matrix: np.ndarray | None = None

    def outward(self, data: Any) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        if self._matrix is None:
            n = arr.size
            self._matrix = np.eye(n, dtype=np.float32)[::-1]
        return self._matrix @ arr

    def inward(self, data: Any) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        if self._matrix is not None:
            arr = self._matrix @ arr
        return arr


class Gate4(Gate):
    """Detect NaN or infinite values."""

    def outward(self, data: Any) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        if not np.all(np.isfinite(arr)):
            raise ValueError("anomaly detected")
        return arr

    inward = outward


class Gate5(Gate):
    """Optionally convert to a quantum representation."""

    def outward(self, data: Any) -> Any:
        if qutip is not None:
            arr = np.asarray(data, dtype=np.complex128)
            return qutip.Qobj(arr)
        return data

    def inward(self, data: Any) -> Any:
        if qutip is not None and isinstance(data, qutip.Qobj):
            return np.array(data.full()).ravel()
        return data


class Gate6(Gate):
    """Filter arrays below a fitness threshold."""

    def __init__(self, threshold: float = 0.1) -> None:
        self.threshold = threshold

    def _score(self, arr: np.ndarray) -> float:
        return float(np.linalg.norm(arr))

    def outward(self, data: Any) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        if self._score(arr) < self.threshold:
            raise ValueError("fitness below threshold")
        return arr

    inward = outward


class Gate7(Gate):
    """Adapt data for external APIs using base64 encoding."""

    def outward(self, data: Any) -> str | List[float]:
        if isinstance(data, bytes):
            return base64.b64encode(data).decode("ascii")
        if qutip is not None and isinstance(data, qutip.Qobj):
            return np.array(data.full()).ravel().tolist()
        if isinstance(data, np.ndarray):
            return data.tolist()
        return data

    def inward(self, data: Any) -> Any:
        if isinstance(data, str):
            try:
                return base64.b64decode(data.encode("ascii"))
            except Exception:
                return data
        if isinstance(data, list):
            return np.asarray(data, dtype=np.float32)
        return data


class GateOrchestrator:
    """Chain all gates for in/out processing."""

    def __init__(self) -> None:
        self.gates = [
            Gate1(),
            Gate3(),
            Gate4(),
            Gate6(),
            Gate5(),
            Gate2(),
            Gate7(),
        ]

    def process_outward(self, data: Any) -> Any:
        """Send data from the core outward through all gates."""
        for gate in self.gates:
            data = gate.outward(data)
        return data

    def process_inward(self, data: Any) -> Any:
        """Receive data from outside and pass through gates inward."""
        for gate in reversed(self.gates):
            data = gate.inward(data)
        return data


__all__ = [
    "Gate",
    "Gate1",
    "Gate2",
    "Gate3",
    "Gate4",
    "Gate5",
    "Gate6",
    "Gate7",
    "GateOrchestrator",
]
