import sys
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_main_deepseek_calls_download(monkeypatch):
    module = importlib.import_module("download_models")

    called = {}

    def dummy():
        called["deepseek"] = True

    monkeypatch.setattr(module, "download_deepseek", dummy)
    argv_backup = sys.argv.copy()
    sys.argv = ["download_models.py", "deepseek"]
    try:
        module.main()
    finally:
        sys.argv = argv_backup

    assert called == {"deepseek": True}


def test_main_gemma2_invokes_ollama(monkeypatch):
    module = importlib.import_module("download_models")

    runs = []

    def dummy_run(cmd, *args, **kwargs):
        runs.append((cmd, kwargs))

    monkeypatch.setattr(module.subprocess, "run", dummy_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/ollama")

    argv_backup = sys.argv.copy()
    sys.argv = ["download_models.py", "gemma2"]
    try:
        module.main()
    finally:
        sys.argv = argv_backup

    assert runs
    cmd, kwargs = runs[0]
    assert cmd == ["ollama", "pull", "gemma2"]
    assert kwargs["check"] is True
    assert "env" in kwargs
    assert kwargs["env"]["OLLAMA_MODELS"].endswith("INANNA_AI/models")
