#!/usr/bin/env python3
"""Launch the Spiral OS initialization sequence."""
from __future__ import annotations

import argparse
import logging
import logging.config
import threading
from pathlib import Path
from typing import List, Optional

import yaml

from INANNA_AI_AGENT import inanna_ai
from INANNA_AI import glm_init, glm_analyze
from inanna_ai import defensive_network_utils as dnu
from inanna_ai.personality_layers import REGISTRY, list_personalities
from orchestrator import MoGEOrchestrator
from tools import reflection_loop
import server
import uvicorn
import emotion_registry

logger = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None) -> None:
    config_path = Path(__file__).resolve().parent / "logging_config.yaml"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        Path("logs").mkdir(exist_ok=True)
        logging.config.dictConfig(config)
    else:  # pragma: no cover - default fallback
        logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Start Spiral OS rituals")
    parser.add_argument("--interface", help="Interface to monitor")
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip network monitoring",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Do not start the FastAPI server",
    )
    parser.add_argument(
        "--no-reflection",
        action="store_true",
        help="Disable periodic reflection loop",
    )
    parser.add_argument(
        "--reflection-interval",
        type=float,
        default=60.0,
        help="Seconds between reflection cycles",
    )
    parser.add_argument(
        "--personality",
        metavar="LAYER",
        help=(
            "Activate optional personality layer. "
            f"Available: {', '.join(list_personalities())}"
        ),
    )
    parser.add_argument("--command", help="Initial text command for QNL parsing")
    args = parser.parse_args(argv)

    server_thread = None
    if not args.no_server:
        server_thread = threading.Thread(
            target=uvicorn.run,
            kwargs={"app": server.app, "host": "0.0.0.0", "port": 8000},
            daemon=True,
        )
        server_thread.start()

    stop_reflection = threading.Event()

    def _run_reflection() -> None:
        while not stop_reflection.is_set():
            try:
                reflection_loop.run_reflection_loop()
            except Exception:  # pragma: no cover - safeguard
                logger.exception("reflection loop failed")
            stop_reflection.wait(args.reflection_interval)

    reflection_thread = None
    if not args.no_reflection:
        reflection_thread = threading.Thread(target=_run_reflection, daemon=True)
        reflection_thread.start()

    inanna_ai.display_welcome_message()
    summary = glm_init.summarize_purpose()
    logger.info("Project summary: %s", summary)

    glm_analyze.analyze_code()
    inanna_ai.suggest_enhancement()
    inanna_ai.reflect_existence()


    layer_name = args.personality
    if layer_name and layer_name not in REGISTRY:
        alt = f"{layer_name}_layer"
        if alt in REGISTRY:
            layer_name = alt

    layer_cls = REGISTRY.get(layer_name)
    layer = layer_cls() if layer_cls else None
    if layer_name:
        emotion_registry.set_current_layer(layer_name)
    orch = MoGEOrchestrator(albedo_layer=layer)

    print("Enter commands (blank to exit).")
    next_command = args.command
    try:
        while True:
            if next_command is None:
                next_command = input("> ")
            if not next_command:
                break
            result = orch.handle_input(next_command)
            print(result)
            next_command = None
    except KeyboardInterrupt:
        print()
    finally:
        stop_reflection.set()
        if reflection_thread:
            reflection_thread.join(timeout=0.1)

    log_paths = [
        str(glm_init.PURPOSE_FILE),
        str(glm_analyze.ANALYSIS_FILE),
        str(inanna_ai.SUGGESTIONS_LOG),
    ]

    if args.interface and not args.skip_network:
        dnu.monitor_traffic(args.interface)
        log_paths.append(str(Path("network_logs/defensive.pcap")))

    print("Log files created:")
    for p in log_paths:
        print(f" - {p}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
