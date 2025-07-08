from __future__ import annotations

"""Command line interface for recording and responding with INANNA AI."""

from pathlib import Path
import argparse
import tempfile
import logging

from . import utils, stt_whisper, emotion_analysis, tts_coqui, db_storage

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - optional dependency
    sd = None


def record_audio(duration: float = 3.0, sr: int = 44100) -> str:
    """Record microphone input and return path to a temporary WAV file."""
    if sd is None:
        raise RuntimeError("sounddevice library not installed")
    logging.info("Recording %.1f seconds of audio", duration)
    wave = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    wave = wave[:, 0]
    path = Path(tempfile.gettempdir()) / "inanna_recording.wav"
    utils.save_wav(wave, str(path), sr=sr)
    return str(path)


def generate_response(transcript: str, emotion: str) -> str:
    """Return placeholder text response for ``transcript`` and ``emotion``."""
    return f"I heard you say: '{transcript}'."


def main(argv: list[str] | None = None) -> None:
    """Entry point for recording, processing and responding."""
    utils.setup_logger()
    db_storage.init_db()

    parser = argparse.ArgumentParser(description="INANNA voice loop")
    parser.add_argument("--duration", type=float, default=3.0, help="Recording length in seconds")
    args = parser.parse_args(argv)

    audio_path = record_audio(args.duration)
    transcript = stt_whisper.transcribe_audio(audio_path)
    emotion_info = emotion_analysis.analyze_audio_emotion(audio_path)
    emotion = emotion_info["emotion"]

    response_text = generate_response(transcript, emotion)
    response_path = tts_coqui.synthesize_speech(response_text, emotion)

    db_storage.save_interaction(transcript, emotion, response_path)

    print(f"Transcript: {transcript}")
    print(f"Emotion: {emotion}")
    print(f"Response audio saved to: {response_path}")


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
