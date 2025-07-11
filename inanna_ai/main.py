from __future__ import annotations

"""Command line interface for recording and responding with INANNA AI."""

import argparse
from orchestrator import MoGEOrchestrator
from .personality_layers import REGISTRY
from .rfa_7d import RFA7D
from .gate_orchestrator import GateOrchestrator
from .love_matrix import LoveMatrix
import numpy as np
from . import (
    utils,
    stt_whisper,
    listening_engine,
    speaking_engine,
    db_storage,
)


def soul_ritual(audio_state: dict, external_outputs: list[str]) -> str:
    """Perform a small ritual using the RFA core and gates."""

    core = RFA7D()
    vec = np.random.rand(core.grid.size) + 1j * np.random.rand(core.grid.size)
    grid = core.execute(vec)
    gate_text = GateOrchestrator().process_outward(grid)
    emotion = audio_state.get("emotion", "neutral")
    phrase = f"Ritual gate echo: {gate_text.strip()} [{emotion}]"
    external_outputs.append(phrase)
    return phrase


def main(argv: list[str] | None = None) -> None:
    """Entry point for recording, processing and responding."""
    utils.setup_logger()
    db_storage.init_db()

    parser = argparse.ArgumentParser(description="INANNA voice loop")
    parser.add_argument("--duration", type=float, default=3.0, help="Recording length in seconds")
    parser.add_argument(
        "--personality",
        choices=sorted(REGISTRY),
        help=(
            "Activate optional personality layer. "
            f"Available: {', '.join(sorted(REGISTRY))}"
        ),
    )
    args = parser.parse_args(argv)

    layer_cls = REGISTRY.get(args.personality)
    layer = layer_cls() if layer_cls else None
    orchestrator = MoGEOrchestrator(albedo_layer=layer)
    gate = GateOrchestrator()
    core = RFA7D()
    speaker = speaking_engine.SpeakingEngine()
    engine = listening_engine.ListeningEngine()

    audio_path, audio_state = engine.record(args.duration)
    transcript = stt_whisper.transcribe_audio(audio_path)

    ritual_outputs: list[str] = []
    ritual_text = ""
    if any(name.lower() in transcript.lower() for name in LoveMatrix.great_mother_names):
        ritual_text = soul_ritual(audio_state, ritual_outputs)

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
    parts = [response_text, gate_text]
    if ritual_text:
        parts.append(ritual_text)
    final_text = " ".join(p for p in parts if p).strip()
    voice_path = speaker.speak(final_text, audio_state.get("emotion", "neutral"))

    db_storage.save_interaction(
        transcript,
        audio_state.get("emotion", "neutral"),
        voice_path,
    )

    print(f"Transcript: {transcript}")
    print(f"Emotion: {audio_state.get('emotion', 'neutral')}")
    print(f"Response: {final_text}")
    if ritual_outputs:
        print("Ritual:", ritual_outputs[-1])
    print(f"Voice path: {voice_path}")


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
