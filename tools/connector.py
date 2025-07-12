from __future__ import annotations

"""Simple communication connectors for SPIRAL_OS."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Any
import json
import logging

try:  # pragma: no cover - optional dependency
    from aiortc import RTCPeerConnection  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    RTCPeerConnection = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import discord  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    discord = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from telegram import Bot  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Bot = None  # type: ignore

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent / "settings.json"

_DEFAULT_SETTINGS = {
    "backend": "webrtc",
    "webrtc_server": "wss://example.com/signaling",
    "discord_token": "",
    "telegram_token": "",
    "latency": 0.1,
}


def load_settings() -> dict:
    """Return connector settings."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return _DEFAULT_SETTINGS.copy()


@dataclass
class WebRTCConnector:
    """Connector for WebRTC communication."""

    server: str
    latency: float = 0.0

    def start(self, audio: Iterator[Any], video: Iterator[Any]) -> None:
        """Start a WebRTC call."""
        if RTCPeerConnection is None:  # pragma: no cover - optional dependency
            logger.warning("aiortc not installed")
            return
        # Real implementation would create peer connection and stream tracks
        logger.info("Starting WebRTC call to %s", self.server)
        for _ in audio:
            pass  # placeholder


@dataclass
class DiscordConnector:
    """Connector for Discord voice chat."""

    token: str
    latency: float = 0.0

    def start(self, audio: Iterator[Any], video: Iterator[Any]) -> None:
        """Start a Discord call."""
        if discord is None:  # pragma: no cover - optional dependency
            logger.warning("discord.py not installed")
            return
        logger.info("Starting Discord call")
        for _ in audio:
            pass  # placeholder


@dataclass
class TelegramConnector:
    """Connector for Telegram voice chat."""

    token: str
    latency: float = 0.0

    def start(self, audio: Iterator[Any], video: Iterator[Any]) -> None:
        """Start a Telegram call."""
        if Bot is None:  # pragma: no cover - optional dependency
            logger.warning("python-telegram-bot not installed")
            return
        logger.info("Starting Telegram call")
        for _ in audio:
            pass  # placeholder


def start_call(audio: Iterator[Any], video: Iterator[Any], backend: str | None = None) -> Any:
    """Dispatch call to the configured backend."""
    settings = load_settings()
    backend = backend or settings.get("backend", "webrtc")
    latency = settings.get("latency", 0.0)

    if backend == "webrtc":
        conn = WebRTCConnector(settings.get("webrtc_server", ""), latency)
    elif backend == "discord":
        conn = DiscordConnector(settings.get("discord_token", ""), latency)
    elif backend == "telegram":
        conn = TelegramConnector(settings.get("telegram_token", ""), latency)
    else:
        raise ValueError(f"Unknown backend: {backend}")

    conn.start(audio, video)
    return conn


__all__ = [
    "start_call",
    "load_settings",
    "WebRTCConnector",
    "DiscordConnector",
    "TelegramConnector",
]
