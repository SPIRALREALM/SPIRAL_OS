#!/usr/bin/env python3
"""Launch the Spiral OS initialization sequence."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from INANNA_AI_AGENT import inanna_ai
from INANNA_AI import glm_init, glm_analyze
from inanna_ai import defensive_network_utils as dnu

logger = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Start Spiral OS rituals")
    parser.add_argument("--interface", help="Interface to monitor")
    parser.add_argument("--skip-network", action="store_true", help="Skip network monitoring")
    parser.add_argument(
        "--personality",
        choices=["albedo"],
        help="Activate optional personality layer",
    )
    args = parser.parse_args(argv)

    inanna_ai.display_welcome_message()
    summary = glm_init.summarize_purpose()
    logger.info("Project summary: %s", summary)

    glm_analyze.analyze_code()
    inanna_ai.suggest_enhancement()
    inanna_ai.reflect_existence()

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
