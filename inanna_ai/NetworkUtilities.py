"""Network utilities for monitoring and secure communication."""
from __future__ import annotations

import logging
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

# Optional dependencies
try:
    import pyshark  # type: ignore
except Exception:  # pragma: no cover - optional
    pyshark = None

try:
    from scapy.all import sniff  # type: ignore
except Exception:  # pragma: no cover - optional
    sniff = None

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional
    psutil = None

logger = logging.getLogger(__name__)


############################
# Audit logging utilities  #
############################

def audit_log(message: str, log_file: str | Path = "network_audit.log") -> None:
    """Append ``message`` with timestamp to ``log_file``."""
    line = f"{datetime.utcnow().isoformat()} {message}\n"
    Path(log_file).open("a", encoding="utf-8").write(line)
    logger.info(message)


########################
# Packet capture       #
########################

def capture_packets(
    interface: str,
    *,
    count: int | None = 10,
    timeout: int | None = 10,
) -> List[str]:
    """Capture packets on ``interface`` using pyshark or scapy.

    Returns a list of textual summaries for each packet.
    """
    summaries: List[str] = []
    if pyshark is not None:
        cap = pyshark.LiveCapture(interface=interface)
        try:
            for pkt in cap.sniff_continuously(packet_count=count, timeout=timeout):
                summaries.append(str(pkt))
        finally:
            cap.close()
    elif sniff is not None:  # pragma: no cover - requires root
        pkts = sniff(iface=interface, count=count, timeout=timeout)
        summaries = [p.summary() for p in pkts]
    else:
        raise RuntimeError("Neither pyshark nor scapy is available")

    audit_log(f"Captured {len(summaries)} packets on {interface}")
    return summaries


####################################
# NetFlow-style connection monitor #
####################################

def monitor_flows(
    *,
    duration: float = 10.0,
    interval: float = 1.0,
) -> List[Dict[str, Any]]:
    """Collect basic NetFlow-style stats for ``duration`` seconds."""
    if psutil is None:  # pragma: no cover - optional
        raise RuntimeError("psutil library not installed")

    records: List[Dict[str, Any]] = []
    start = time.time()
    prev = psutil.net_io_counters()
    while time.time() - start < duration:
        time.sleep(interval)
        now = psutil.net_io_counters()
        record = {
            "timestamp": time.time(),
            "bytes_sent": now.bytes_sent - prev.bytes_sent,
            "bytes_recv": now.bytes_recv - prev.bytes_recv,
        }
        records.append(record)
        prev = now
    audit_log(f"Recorded {len(records)} flow records")
    return records


#############################
# WireGuard communication   #
#############################

def wg_command(args: Iterable[str]) -> str:
    """Run a ``wg`` command and return its output."""
    cmd = ["wg", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    audit_log(f"Executed: {' '.join(cmd)} (rc={proc.returncode})")
    return proc.stdout.strip()


def send_wireguard_message(
    peer_ip: str,
    peer_port: int,
    message: bytes,
    *,
    interface: str = "wg0",
    timeout: float = 5.0,
) -> None:
    """Send ``message`` to a WireGuard peer via UDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.bind(("0.0.0.0", 0))  # use ephemeral port
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface.encode())  # type: ignore[attr-defined]
        sock.sendto(message, (peer_ip, peer_port))
    audit_log(f"Sent {len(message)} bytes to {peer_ip}:{peer_port} via {interface}")


__all__ = [
    "capture_packets",
    "monitor_flows",
    "send_wireguard_message",
    "wg_command",
    "audit_log",
]
