# -*- coding: utf-8 -*-
"""Multimodal Generative Expression orchestrator."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any, Dict
import soundfile as sf

from inanna_ai import response_manager, tts_coqui, emotion_analysis
from inanna_ai.personality_layers import AlbedoPersonality
from SPIRAL_OS import qnl_engine


class MoGEOrchestrator:
    """Route text and emotion data to the available models."""

    def __init__(self, *, albedo_layer: AlbedoPersonality | None = None) -> None:
        self._responder = response_manager.ResponseManager()
        self._albedo = albedo_layer

    @staticmethod
    def _select_plane(weight: float, archetype: str) -> str:
        """Return ``ascension`` or ``underworld`` based on ``weight`` and ``archetype``."""
        if weight >= 0.6 or archetype.lower() in {"hero", "sage", "jester"}:
            return "ascension"
        return "underworld"

    def route(
        self,
        text: str,
        emotion_data: Dict[str, Any],
        *,
        text_modality: bool = True,
        voice_modality: bool = False,
        music_modality: bool = False,
    ) -> Dict[str, Any]:
        """Process ``text`` with models based on ``emotion_data`` and flags."""
        emotion = emotion_data.get("emotion", "neutral")
        archetype = emotion_data.get("archetype") or emotion_analysis.emotion_to_archetype(emotion)
        weight = emotion_data.get("weight")
        if weight is None:
            weight = emotion_analysis.emotion_weight(emotion)
        plane = self._select_plane(weight, archetype)

        result: Dict[str, Any] = {
            "plane": plane,
            "archetype": archetype,
            "weight": weight,
        }

        if text_modality:
            if self._albedo is not None:
                result["text"] = self._albedo.generate_response(text)
            else:
                result["text"] = self._responder.generate_reply(text, emotion_data)

        if voice_modality:
            speech_input = result.get("text", text)
            result["voice_path"] = tts_coqui.synthesize_speech(speech_input, emotion)

        if music_modality:
            hex_input = text.encode("utf-8").hex()
            phrases, wave = qnl_engine.hex_to_song(hex_input, duration_per_byte=0.05)
            wav_path = Path(tempfile.gettempdir()) / f"qnl_{abs(hash(hex_input))}.wav"
            sf.write(wav_path, wave, 44100)
            result["music_path"] = str(wav_path)
            result["qnl_phrases"] = phrases

        return result


__all__ = ["MoGEOrchestrator"]
