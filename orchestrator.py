# -*- coding: utf-8 -*-
"""Multimodal Generative Expression orchestrator."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any, Dict, Deque, List
from collections import deque
import soundfile as sf

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore

import numpy as np

from task_profiling import classify_task

from inanna_ai import response_manager, tts_coqui, emotion_analysis
from inanna_ai.personality_layers import AlbedoPersonality
from SPIRAL_OS import qnl_engine


class MoGEOrchestrator:
    """Route text and emotion data to the available models."""

    def __init__(self, *, albedo_layer: AlbedoPersonality | None = None) -> None:
        self._responder = response_manager.ResponseManager()
        self._albedo = albedo_layer
        self._context: Deque[Dict[str, Any]] = deque(maxlen=5)
        if SentenceTransformer is not None:
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        else:  # pragma: no cover - fallback when dependency missing
            self._embedder = None

    @staticmethod
    def _select_plane(weight: float, archetype: str) -> str:
        """Return ``ascension`` or ``underworld`` based on ``weight`` and ``archetype``."""
        if weight >= 0.6 or archetype.lower() in {"hero", "sage", "jester"}:
            return "ascension"
        return "underworld"

    @staticmethod
    def _choose_model(task: str, weight: float, history: List[str]) -> str:
        """Return LLM name based on task, ``weight`` and ``history``."""
        emotional_ratio = 0.0
        if history:
            emotional_ratio = history.count("emotional") / len(history)

        if weight > 0.8 or emotional_ratio > 0.5:
            return "mistral"
        if task == "instructional":
            return "deepseek"
        if task == "philosophical":
            return "mistral"
        return "glm"

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

        task = classify_task(text)
        history_tasks = [c["task"] for c in self._context]
        model = self._choose_model(task, weight, history_tasks)

        result: Dict[str, Any] = {
            "plane": plane,
            "archetype": archetype,
            "weight": weight,
            "model": model,
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

        # Update lightweight context memory
        if self._embedder is not None:
            emb = np.asarray(self._embedder.encode([text]))[0]
        else:
            emb = np.array([len(text)], dtype=float)
        self._context.append({"text": text, "task": task, "embedding": emb})

        return result


__all__ = ["MoGEOrchestrator"]
