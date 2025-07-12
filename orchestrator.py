# -*- coding: utf-8 -*-
"""Multimodal Generative Expression orchestrator."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any, Dict, Deque, List, Callable
from collections import deque
import soundfile as sf
from time import perf_counter
import threading

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore

import numpy as np

from task_profiling import classify_task

from inanna_ai import response_manager, tts_coqui, emotion_analysis, db_storage
from inanna_ai.personality_layers import AlbedoPersonality
from inanna_ai import voice_layer_albedo
from SPIRAL_OS import qnl_engine, symbolic_parser


class MoGEOrchestrator:
    """Route text and emotion data to the available models."""

    def __init__(
        self,
        *,
        albedo_layer: AlbedoPersonality | None = None,
        db_path: Path | None = None,
    ) -> None:
        self._responder = response_manager.ResponseManager()
        self._albedo = albedo_layer
        self._context: Deque[Dict[str, Any]] = deque(maxlen=5)
        if SentenceTransformer is not None:
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        else:  # pragma: no cover - fallback when dependency missing
            self._embedder = None
        self._model_weights = {"glm": 1.0, "deepseek": 1.0, "mistral": 1.0}
        self._alpha = 0.1
        self._db_path = db_path or db_storage.DB_PATH
        db_storage.init_db(self._db_path)
        self._mood_alpha = 0.2
        self.mood_state: Dict[str, float] = {
            e: (1.0 if e == "neutral" else 0.0)
            for e in emotion_analysis.EMOTION_WEIGHT
        }

    @staticmethod
    def _select_plane(weight: float, archetype: str) -> str:
        """Return ``ascension`` or ``underworld`` based on ``weight`` and ``archetype``."""
        if weight >= 0.6 or archetype.lower() in {"hero", "sage", "jester"}:
            return "ascension"
        return "underworld"

    @staticmethod
    def _coherence(text: str) -> float:
        """Return a simple coherence score for ``text``."""
        words = text.split()
        if not words:
            return 0.0
        return len(set(words)) / len(words)

    @staticmethod
    def _relevance(source: str, generated: str) -> float:
        """Return a Jaccard similarity between ``source`` and ``generated``."""
        src = set(source.split())
        gen = set(generated.split())
        if not src or not gen:
            return 0.0
        return len(src & gen) / len(src | gen)

    def _update_weights(self, model: str, rt: float, coh: float, rel: float) -> None:
        reward = coh + rel - 0.1 * rt
        current = self._model_weights.get(model, 1.0)
        self._model_weights[model] = (1 - self._alpha) * current + self._alpha * reward

    def _update_mood(self, emotion: str) -> None:
        """Update ``mood_state`` using an exponential moving average."""
        for key in list(self.mood_state):
            target = 1.0 if key.lower() == emotion.lower() else 0.0
            self.mood_state[key] = (1 - self._mood_alpha) * self.mood_state.get(key, 0.0) + self._mood_alpha * target

    def _benchmark(self, model: str, prompt: str, output: str, elapsed: float) -> None:
        coh = self._coherence(output)
        rel = self._relevance(prompt, output)
        db_storage.log_benchmark(model, elapsed, coh, rel, db_path=self._db_path)
        self._update_weights(model, elapsed, coh, rel)

    def _choose_model(self, task: str, weight: float, history: List[str]) -> str:
        """Return LLM name based on task, ``weight`` and ``history``."""
        emotional_ratio = 0.0
        if history:
            emotional_ratio = history.count("emotional") / len(history)

        base = {"glm": 0.0, "deepseek": 0.0, "mistral": 0.0}

        if weight > 0.8 or emotional_ratio > 0.5 or task == "philosophical":
            base["mistral"] = 1.0
        if task == "instructional":
            base["deepseek"] = 1.0
        if not any(base.values()):
            base["glm"] = 1.0

        scores = {m: base[m] * self._model_weights.get(m, 1.0) for m in base}
        return max(scores, key=scores.get)

    def route(
        self,
        text: str,
        emotion_data: Dict[str, Any],
        *,
        qnl_data: Dict[str, Any] | None = None,
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

        tone = None
        intents = None
        if qnl_data is not None:
            tone = qnl_data.get("tone")
            intents = symbolic_parser.parse_intent(qnl_data)

        task = classify_task(text)
        history_tasks = [c["task"] for c in self._context]
        model = self._choose_model(task, weight, history_tasks)

        start = perf_counter()
        result: Dict[str, Any] = {
            "plane": plane,
            "archetype": archetype,
            "weight": weight,
            "model": model,
        }
        if intents is not None:
            result["qnl_intents"] = intents

        if text_modality:
            if self._albedo is not None:
                result["text"] = self._albedo.generate_response(text)
            else:
                result["text"] = self._responder.generate_reply(text, emotion_data)

        if voice_modality:
            speech_input = result.get("text", text)
            if tone is not None:
                result["voice_path"] = voice_layer_albedo.modulate_voice(
                    speech_input, tone
                )
            else:
                result["voice_path"] = tts_coqui.synthesize_speech(
                    speech_input, emotion
                )

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

        elapsed = perf_counter() - start
        if text_modality and "text" in result:
            self._benchmark(model, text, result["text"], elapsed)

        return result

    def handle_input(self, text: str) -> Dict[str, Any]:
        """Parse ``text`` as QNL, update mood and delegate to :meth:`route`."""
        qnl_data = qnl_engine.parse_input(text)
        symbolic_parser.parse_intent(qnl_data)
        emotion = qnl_data.get("tone", "neutral")
        self._update_mood(emotion)
        dominant = max(self.mood_state, key=self.mood_state.get)
        emotion_data = {
            "emotion": dominant,
            "archetype": emotion_analysis.emotion_to_archetype(dominant),
            "weight": emotion_analysis.emotion_weight(dominant),
        }
        return self.route(text, emotion_data, qnl_data=qnl_data)


def schedule_action(func: Callable[[], Any], delay: float) -> threading.Timer:
    """Execute ``func`` after ``delay`` seconds using a timer."""
    timer = threading.Timer(delay, func)
    timer.start()
    return timer


__all__ = ["MoGEOrchestrator", "schedule_action"]
