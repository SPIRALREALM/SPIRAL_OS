from __future__ import annotations

"""Command line interface for recording and responding with INANNA AI."""

import argparse
from orchestrator import MoGEOrchestrator
from .rfa_7d import RFA7D
from .gate_orchestrator import GateOrchestrator
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
    gate = GateOrchestrator()
    core = RFA7D()
    speaker = speaking_engine.SpeakingEngine()
    engine = listening_engine.ListeningEngine()

    audio_path, audio_state = engine.record(args.duration)
    transcript = stt_whisper.transcribe_audio(audio_path)

    encoded = gate.process_inward(transcript)
    core_grid = core.execute(encoded)
    gate_text = gate.process_outward(core_grid)

    result = orchestrator.route(
        transcript,
        audio_state,
        text_modality=True,
        voice_modality=False,
        music_modality=False,
    )

    response_text = result.get("text", "")
    final_text = f"{response_text} {gate_text}".strip()
    voice_path = speaker.speak(final_text, audio_state.get("emotion", "neutral"))

    db_storage.save_interaction(
        transcript,
        audio_state.get("emotion", "neutral"),
        voice_path,
    )

    print(f"Transcript: {transcript}")
    print(f"Emotion: {audio_state.get('emotion', 'neutral')}")
    print(f"Response: {final_text}")
    print(f"Voice path: {voice_path}")


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
