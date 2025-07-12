#!/usr/bin/env python3
"""Launch the Spiral OS initialization sequence."""
from __future__ import annotations

import argparse
import logging
import logging.config
from pathlib import Path
from typing import List, Optional

import yaml

from INANNA_AI_AGENT import inanna_ai
from INANNA_AI import glm_init, glm_analyze
from inanna_ai import defensive_network_utils as dnu
from inanna_ai.personality_layers import list_personalities
from SPIRAL_OS import qnl_engine, symbolic_parser

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
        "--personality",
        choices=list_personalities(),
        help="Activate optional personality layer",
    )
    parser.add_argument("--command", help="Text command for QNL parsing")
    args = parser.parse_args(argv)

    inanna_ai.display_welcome_message()
    summary = glm_init.summarize_purpose()
    logger.info("Project summary: %s", summary)

    glm_analyze.analyze_code()
    inanna_ai.suggest_enhancement()
    inanna_ai.reflect_existence()

    intents = None
    if args.command:
        structure = qnl_engine.parse_input(args.command)
        intents = symbolic_parser.parse_intent(structure)
        print("QNL intents:")
        for item in intents:
            print(item)

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
