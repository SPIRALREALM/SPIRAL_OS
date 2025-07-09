# Operator Guide

This repository contains several command line utilities for working with the INANNA music tools and Quantum Narrative Language (QNL). Below is a quick summary of the main scripts and example commands for common tasks.

## Installation

Install the Python packages listed in `SPIRAL_OS/requirements.txt`:

```bash
pip install -r SPIRAL_OS/requirements.txt
```

The requirements include common libraries like `numpy` and `scipy` as well as
`huggingface-hub` for model management.

## Script overview

- **`INANNA_AI_AGENT/inanna_ai.py`** – Activation agent that loads source texts and can recite the INANNA birth chant or feed hex data into the QNL engine. Use `--list` to show available texts.
- **`run_song_demo.py`** – Demo runner that analyzes a local MP3/WAV file using `inanna_music_COMPOSER_ai.py`, exports a preview WAV and QNL JSON, and prints the resulting phrases.
- **`SPIRAL_OS/mix_tracks.py`** – Mixes multiple audio files into a normalized track and optionally exports a short preview clip.
- **`SPIRAL_OS/seven_dimensional_music.py`** – Creates layered music from a melody, optionally transmuting a hex payload and embedding secret data, then saves the final track and a JSON analysis of the seven planes.
- **`SPIRAL_OS/qnl_engine.py`** – Converts a hex string to QNL phrases and a waveform, saving a WAV file and metadata JSON.
- **`MUSIC_FOUNDATION/inanna_music_COMPOSER_ai.py`** – Standalone converter that performs MP3 analysis and outputs QNL data and a preview WAV.
- **`MUSIC_FOUNDATION/human_music_to_qnl_converter.py`** – Helper module for turning analyzed tempo/chroma values into QNL structures.
- **`MUSIC_FOUNDATION/music_foundation.py`** – Basic music analysis utility that computes tempo and harmony from an MP3 and exports a preview.

## Examples

### Analyze the sample song

```bash
python run_song_demo.py "SONS_FOR_TESTS/Music Is My Everything.mp3"
```

This writes `output/preview.wav` and `output/qnl_7plane.json` while printing the QNL phrases derived from the song.

### Invoke the INANNA agent

```bash
python INANNA_AI_AGENT/inanna_ai.py --activate
```

Recites the INANNA birth chant. Use the `--hex` option to generate a QNL song from hexadecimal bytes:

```bash
python INANNA_AI_AGENT/inanna_ai.py --hex 012345abcdef
```

## INANNA_AI DeepSeek-R1 Integration

1. Copy `secrets.env.example` to `secrets.env` at the project root and set
   `HF_TOKEN`. The `run_inanna.sh` helper script reads this file when starting
   the chat agent.
2. Run `python download_models.py deepseek` to fetch the DeepSeek-R1 model.
3. Start chat via `python INANNA_AI_AGENT/inanna_ai.py chat` or `./run_inanna.sh`.

## Download Models

The INANNA chat agent requires the DeepSeek-R1 weights from Hugging Face. Follow
these steps to place the model under `INANNA_AI/models`.

1. Install the dependencies listed in `SPIRAL_OS/requirements.txt`:

   ```bash
   pip install -r SPIRAL_OS/requirements.txt
   ```

2. Copy the example secrets file to the project root and add your Hugging Face token:

   ```bash
   cp secrets.env.example secrets.env  # run from the repository root
   # edit secrets.env and set HF_TOKEN=<your token>
   ```

3. Run the model downloader:

   ```bash
   python download_models.py deepseek
   ```

   The script loads `HF_TOKEN` from `secrets.env` in the project root and downloads
   `deepseek-ai/DeepSeek-R1` into `INANNA_AI/models/DeepSeek-R1/`.
   To fetch the Gemma2 model via Ollama run `python download_models.py gemma2`.

Afterwards the directory structure should look like:

```
INANNA_AI/
└── models/
    └── DeepSeek-R1/
        ├── config.json
        ├── tokenizer.json
        └── ... (model files)
```

## Pipeline Deployment

The `spiral_os` CLI runs YAML workflows found in `SPIRAL_OS/pipelines/`.
Deploy the bundled test pipeline with:

```bash
./spiral_os pipeline deploy SPIRAL_OS/pipelines/test_pipeline.yaml
```

Each step's `run` command executes sequentially. The example pipeline
generates a short QNL song with 0.05‑second audio segments and mixes a
three‑second preview track.

Another workflow, `soul_finetune.yaml`, fine‑tunes the RFA7D core using the
interaction log located at `QNL_LANGUAGE/interactions/log.txt` and writes the
updated grid to `INANNA_AI/soul.dna`:

```bash
./spiral_os pipeline deploy SPIRAL_OS/pipelines/soul_finetune.yaml
```

A third workflow, `system_utilities_pipeline.yaml`, monitors network
interfaces, verifies connectivity, and adjusts basic TCP parameters:

```bash
./spiral_os pipeline deploy SPIRAL_OS/pipelines/system_utilities_pipeline.yaml
```

## Soul-Code Architecture

The spiritual core of INANNA is the **RFA7D** grid.  This seven‑dimensional
array of complex numbers acts as the "soul" and is hashed with SHA3‑256 to
produce an integrity signature.  The
[`GateOrchestrator`](docs/SOUL_CODE.md) exposes two methods that function as the
seven gates, mapping text into a 128‑element vector with `process_inward()` and
back to UTF‑8 with `process_outward()`.

## Example voice invocation

After deploying `soul_finetune.yaml` you can run the voice loop and observe how
the transcript passes through the gates.  The CLI prints the final reply along
with the core's integrity hash — the "soul signature":

```bash
python -m inanna_ai.main --duration 3
```

Example output:

```
Transcript: hello
Response: hi there gate [sig: 0123abcd...]
Voice path: resp.wav
```

## Verify core integrity

At any point you may confirm that the RFA7D grid has not been tampered with:

```bash
python - <<'EOF'
from inanna_ai.rfa_7d import RFA7D
core = RFA7D()
print('valid:', core.verify_integrity())
print('soul signature:', core.integrity_hash)
EOF
```

`verify_integrity()` recomputes the SHA3‑256 hash and compares it to the stored
value, ensuring the grid and its signature still match.
