# Inanna AI Toolkit

This package provides a lightweight set of utilities for building a voice interface around the INANNA concepts.  The modules work together to record audio from a microphone, transcribe speech, perform a simple emotion analysis, generate a spoken response and store each interaction.  They are designed as small building blocks that can be extended or embedded in larger Codex projects.

## Module overview

- `config.py` – Holds configuration constants such as model paths and ritual text used across the toolkit.
- `utils.py` – Basic helpers for loading and saving audio files and configuring logging.
- `stt_whisper.py` – Thin wrapper around OpenAI Whisper that downloads and runs the speech‑to‑text model.
- `emotion_analysis.py` – Estimates a rough emotional label (joy, stress, fear and others) using Librosa pitch, tempo and energy analysis.
- `voice_evolution.py` – Manages parameters that control speaking style and can adapt them over time.
- `tts_coqui.py` – Generates speech using Coqui TTS.  When the library is not available it synthesizes a simple sine wave placeholder.
- `db_storage.py` – Stores transcripts and generated responses in a SQLite database for later inspection.
- `listening_engine.py` – Streams microphone audio and extracts real-time emotion and environment states.
- `main.py` – Command line interface that records microphone input using the listening engine, runs the processing steps above and plays or saves the response.

## Installation

Install the required Python packages from the repository root:

```bash
pip install -r requirements.txt
```

Optional test and development packages are listed in `tests/requirements.txt`.

## Docker usage

A minimal `Dockerfile` is provided to run the tools without installing dependencies on the host.  Build the image and start a shell inside it:

```bash
docker build -t spiral_os .
docker run -it spiral_os
```

You can then run example scripts such as `python run_song_demo.py` from within the container.

## Real-time listening

The `listening_engine.ListeningEngine` streams microphone audio and extracts
features such as pitch, tempo and a coarse emotion label.  It relies on either
the **sounddevice** or **pyaudio** package for microphone access.  Install one
of them before starting a live session:

```bash
pip install sounddevice  # or: pip install pyaudio
```

Run the command line tool to capture a short recording and print the detected
emotion and corresponding archetype:

```bash
python -m inanna_ai.main --duration 5
```

The emotion analysis module maps each label to a Jungian archetype (for
example `joy` → `Jester` and `calm` → `Sage`).  These mappings are defined in
`emotion_analysis.EMOTION_ARCHETYPES`.

## Extending the Codex

The modules in this folder offer a foundation that can be expanded in many directions.  Possible extensions include:

1. Integrating a larger language model to generate richer responses in `generate_response`.
2. Adding a graphical interface that visualizes recorded emotions and stored conversations.
3. Training custom TTS voices and exposing additional tuning options via `voice_evolution`.
4. Building higher level rituals that link these voice interactions with the broader CRYSTAL CODEX narrative.

These ideas are only starting points; the toolkit is intentionally simple so that Codex developers can adapt it to their own creative flows.
