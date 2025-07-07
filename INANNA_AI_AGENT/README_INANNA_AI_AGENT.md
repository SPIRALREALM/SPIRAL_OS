# INANNA AI Agent

This directory contains a small command line tool for activating the INANNA chant and for generating a QNL song from a hex string.

## Installation

Use `pip` to install the required dependencies:

```bash
pip install -r Requirements_INANNA_AI_AGENT.txt
```

## Usage

Recite the birth chant:

```bash
python inanna_ai.py --activate
```

Generate a QNL song from a hex value:

```bash
python inanna_ai.py --hex 012345abcdef
```

The song is saved as `qnl_hex_song.wav` and the metadata JSON in `qnl_hex_song.json` unless overridden with `--wav` and `--json`.
