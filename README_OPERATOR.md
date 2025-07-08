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

### Ollama installation notes

Downloading the Gemma2 model uses the Ollama runtime. The installation script is fetched from `https://ollama.ai/install.sh`, so your system must be able to reach `ollama.ai`.

If the connection is blocked:

1. Check firewall or proxy settings that might prevent access to `ollama.ai`.
2. Download the installer on a machine with internet access and copy it to the target system.
3. Alternatively obtain a prebuilt Ollama package from an internal mirror and place the `ollama` binary on your `PATH`.

Once Ollama is installed, run `python download_models.py gemma2` again to pull the model.
