from __future__ import annotations

"""Interactive REPL for the Crown agent."""

import logging
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout

from init_crown_agent import initialize_crown

try:
    from crown_prompt_orchestrator import crown_prompt_orchestrator
except Exception:  # pragma: no cover - orchestrator may be added later
    crown_prompt_orchestrator = None  # type: ignore

logger = logging.getLogger(__name__)

HISTORY_FILE = Path("data/console_history.txt")


def run_repl() -> None:
    """Start the interactive console."""
    glm = initialize_crown()
    session = PromptSession(history=FileHistory(str(HISTORY_FILE)))
    print("Crown console started. Type /exit to quit.")

    while True:
        try:
            with patch_stdout():
                text = session.prompt("crown> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text:
            continue
        command = text.strip()
        if command.startswith("/"):
            if command == "/exit":
                break
            if command == "/reload":
                glm = initialize_crown()
                print("Agent reloaded.")
                continue
            if command == "/memory":
                _show_memory()
                continue
            print(f"Unknown command: {command}")
            continue

        if crown_prompt_orchestrator is None:
            print("Orchestrator unavailable")
            continue
        try:
            reply = crown_prompt_orchestrator(command, glm)
        except Exception as exc:  # pragma: no cover - runtime errors
            logger.error("orchestrator failed: %s", exc)
            print("Error: could not process input")
            continue
        print(reply)


def _show_memory() -> None:
    """Display recent interaction logs."""
    try:
        from corpus_memory_logging import load_interactions

        entries = load_interactions(limit=5)
        if not entries:
            print("No memory entries found.")
            return
        for e in entries:
            ts = e.get("timestamp", "")
            text = e.get("input", "")
            print(f"{ts}: {text}")
    except Exception as exc:  # pragma: no cover - optional deps
        logger.error("Failed to load memory: %s", exc)
        print("Memory unavailable")


__all__ = ["run_repl"]
