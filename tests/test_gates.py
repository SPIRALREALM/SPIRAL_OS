import sys
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import gates


def test_gate_round_trip():
    orchestrator = gates.GateOrchestrator()
    data = np.array([0.5, 0.2, 0.9], dtype=np.float32)
    outbound = orchestrator.process_outward(data)
    inbound = orchestrator.process_inward(outbound)
    assert np.allclose(inbound, data, atol=1e-5)


def test_gate_anomaly_detection():
    orchestrator = gates.GateOrchestrator()
    malformed = np.array([0.1, np.nan], dtype=np.float32)
    with pytest.raises(ValueError):
        orchestrator.process_outward(malformed)
