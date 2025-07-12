from __future__ import annotations

"""Send shell commands to the Crown GLM endpoint.

Usage:
    python glm_shell.py "<command>"
"""

import argparse

from init_crown_agent import initialize_crown


def send_command(command: str) -> str:
    """Return GLM response for ``command`` sent as a shell instruction."""
    glm = initialize_crown()
    prompt = f"[shell]{command}"
    return glm.complete(prompt)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="glm_shell")
    parser.add_argument("command", help="Shell command to execute")
    args = parser.parse_args(argv)
    print(send_command(args.command))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
