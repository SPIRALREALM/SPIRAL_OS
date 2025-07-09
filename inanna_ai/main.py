from __future__ import annotations

"""Command line interface for recording and responding with INANNA AI."""

import argparse
from orchestrator import MoGEOrchestrator
from . import (
    utils,
    stt_whisper,
    listening_engine,
    speaking_engine,
    db_storage,
)


def main(argv: list[str] | None = None) -> None:
    """Entry point for recording, processing and responding."""
    utils.setup_logger()
    db_storage.init_db()

    parser = argparse.ArgumentParser(description="INANNA voice loop")
    parser.add_argument("--duration", type=float, default=3.0, help="Recording length in seconds")
    args = parser.parse_args(argv)

    orchestrator = MoGEOrchestrator()
    speaker = speaking_engine.SpeakingEngine()
    engine = listening_engine.ListeningEngine()

    audio_path, audio_state = engine.record(args.duration)
    transcript = stt_whisper.transcribe_audio(audio_path)

    result = orchestrator.route(
        transcript,
        audio_state,
        text_modality=True,
        voice_modality=True,
        music_modality=False,
    )
    response_text = result.get("text", "")
    voice_path = result.get("voice_path")
    if voice_path:
        speaker.play(voice_path)
    else:
        voice_path = speaker.speak(response_text, audio_state.get("emotion", "neutral"))

    db_storage.save_interaction(
        transcript,
        audio_state.get("emotion", "neutral"),
        voice_path,
    )

    print(f"Transcript: {transcript}")
    print(f"Emotion: {audio_state.get('emotion', 'neutral')}")
    print(f"Response: {response_text}")
    print(f"Voice path: {voice_path}")


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
