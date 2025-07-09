"""Network monitoring utilities."""
from __future__ import annotations

from pathlib import Path
import json

CONFIG_FILE = Path(__file__).resolve().parents[2] / "INANNA_AI_AGENT" / "network_utils_config.json"

_DEFAULT_CONFIG = {"log_dir": "network_logs", "capture_file": "network_logs/capture.pcap"}


def load_config() -> dict:
    """Return configuration for network utilities."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return _DEFAULT_CONFIG.copy()


from .capture import capture_packets
from .analysis import analyze_capture

__all__ = ["capture_packets", "analyze_capture", "load_config", "CONFIG_FILE"]
