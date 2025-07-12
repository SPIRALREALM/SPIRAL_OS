import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import connector


def _dummy_settings(backend: str) -> dict:
    return {
        "backend": backend,
        "webrtc_server": "x",
        "discord_token": "y",
        "telegram_token": "z",
        "latency": 0.0,
    }


def test_start_call_webrtc(monkeypatch):
    calls = {}

    class Dummy:
        def __init__(self, server: str, latency: float = 0.0):
            calls["args"] = (server, latency)

        def start(self, audio, video):
            calls["started"] = True

    monkeypatch.setattr(connector, "WebRTCConnector", Dummy)
    monkeypatch.setattr(connector, "load_settings", lambda: _dummy_settings("webrtc"))

    audio = iter([b"a"])
    video = iter([b"v"])
    obj = connector.start_call(audio, video)

    assert calls["args"] == ("x", 0.0)
    assert calls["started"] is True
    assert isinstance(obj, Dummy)


def test_start_call_discord(monkeypatch):
    calls = {}

    class Dummy:
        def __init__(self, token: str, latency: float = 0.0):
            calls["args"] = (token, latency)

        def start(self, audio, video):
            calls["started"] = True

    monkeypatch.setattr(connector, "DiscordConnector", Dummy)
    monkeypatch.setattr(connector, "load_settings", lambda: _dummy_settings("discord"))

    obj = connector.start_call(iter([]), iter([]))

    assert calls["args"] == ("y", 0.0)
    assert calls["started"] is True
    assert isinstance(obj, Dummy)


def test_start_call_telegram(monkeypatch):
    calls = {}

    class Dummy:
        def __init__(self, token: str, latency: float = 0.0):
            calls["args"] = (token, latency)

        def start(self, audio, video):
            calls["started"] = True

    monkeypatch.setattr(connector, "TelegramConnector", Dummy)
    monkeypatch.setattr(connector, "load_settings", lambda: _dummy_settings("telegram"))

    obj = connector.start_call(iter([]), iter([]))

    assert calls["args"] == ("z", 0.0)
    assert calls["started"] is True
    assert isinstance(obj, Dummy)
