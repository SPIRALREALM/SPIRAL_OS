from __future__ import annotations

"""Command line interface for recording and responding with INANNA AI."""

import argparse
import logging

from . import (
    utils,
    stt_whisper,
    emotion_analysis,
    tts_coqui,
    db_storage,
    listening_engine,
    response_manager,
)


def generate_response(transcript: str, info: dict) -> str:
    """Return a reply using :class:`ResponseManager`."""
    mgr = response_manager.ResponseManager()
    return mgr.generate_reply(transcript, info)


def main(argv: list[str] | None = None) -> None:
    """Entry point for recording, processing and responding."""
    utils.setup_logger()
    db_storage.init_db()

    parser = argparse.ArgumentParser(description="INANNA voice loop")
    parser.add_argument("--duration", type=float, default=3.0, help="Recording length in seconds")
    args = parser.parse_args(argv)

    engine = listening_engine.ListeningEngine()
    audio_path, emotion_info = engine.record(args.duration)
    transcript = stt_whisper.transcribe_audio(audio_path)
    if not emotion_info:
        emotion_info = emotion_analysis.analyze_audio_emotion(audio_path)
    emotion = emotion_info.get("emotion", "neutral")

    response_text = generate_response(transcript, emotion_info)
    response_path = tts_coqui.synthesize_speech(response_text, emotion)

    db_storage.save_interaction(transcript, emotion, response_path)

    print(f"Transcript: {transcript}")
    print(f"Emotion: {emotion}")
    print(f"Response audio saved to: {response_path}")


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
