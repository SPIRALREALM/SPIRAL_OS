#!/usr/bin/env python3
"""Demo runner for INANNA Music Composer AI.

This script analyzes a local MP3 or WAV file using
``inanna_music_COMPOSER_ai.py`` and prints the resulting QNL phrases.
"""

import argparse

from MUSIC_FOUNDATION.inanna_music_COMPOSER_ai import (
    InannaMusicInterpreter,
    export_qnl,
)
from MUSIC_FOUNDATION.qnl_utils import generate_qnl_structure


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a local audio file and display QNL output"
    )
    parser.add_argument("audio_file", help="Path to a local MP3 or WAV file")
    parser.add_argument(
        "--preview", default="output/preview.wav", help="Preview WAV file path"
    )
    parser.add_argument(
        "--json", default="output/qnl_7plane.json", help="QNL JSON output path"
    )
    args = parser.parse_args()

    engine = InannaMusicInterpreter(args.audio_file)
    engine.load_audio()
    chroma = engine.analyze()
    planes = engine.analyze_planes()
    engine.export_preview(args.preview)

    qnl_data = generate_qnl_structure(
        chroma,
        engine.tempo,
        metadata={"source": args.audio_file},
        planes=planes,
    )
    export_qnl(qnl_data, args.json)

    print("QNL Output:")
    for phrase in qnl_data["qnl_output"]:
        print(" -", phrase)


if __name__ == "__main__":
    main()
