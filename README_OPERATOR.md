# Operator Guide

This repository contains several command line utilities for working with the INANNA music tools and Quantum Narrative Language (QNL). Below is a quick summary of the main scripts and example commands for common tasks.

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
