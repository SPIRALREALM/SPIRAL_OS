"""Command line entry for network utilities."""
from __future__ import annotations

import argparse
import logging

from .capture import capture_packets
from .analysis import analyze_capture


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Network monitoring tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    cap = sub.add_parser("capture", help="Capture packets from an interface")
    cap.add_argument("interface")
    cap.add_argument("--count", type=int, default=20)
    cap.add_argument("--output")

    ana = sub.add_parser("analyze", help="Summarize a pcap file")
    ana.add_argument("pcap")
    ana.add_argument("--log-dir")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if args.cmd == "capture":
        capture_packets(args.interface, count=args.count, output=args.output)
    elif args.cmd == "analyze":
        analyze_capture(args.pcap, log_dir=args.log_dir)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
