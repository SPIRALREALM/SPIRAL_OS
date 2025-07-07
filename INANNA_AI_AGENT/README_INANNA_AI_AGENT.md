# INANNA AI Agent

This directory contains a small command line tool for activating the INANNA chant and for generating a QNL song from a hex string.

## Installation

Use `pip` to install the required dependencies:

```bash
pip install -r Requirements_INANNA_AI_AGENT.txt
```

Create `OPENAI_API_KEY.env` containing your OpenAI API key:

```bash
echo "OPENAI_API_KEY=<your key>" > OPENAI_API_KEY.env
```

The examples below assume [`python-dotenv`](https://pypi.org/project/python-dotenv/) is installed so the script
loads the key from this file automatically.

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
