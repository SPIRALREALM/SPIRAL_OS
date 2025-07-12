from __future__ import annotations

"""Lightweight orchestrator for the Crown console."""

from typing import Any, Dict
import asyncio

from state_transition_engine import StateTransitionEngine

from inanna_ai.glm_integration import GLMIntegration
from inanna_ai import emotion_analysis
from corpus_memory_logging import load_interactions
import servant_model_manager as smm


_EMOTION_KEYS = list(emotion_analysis.EMOTION_ARCHETYPES.keys())
_INSTRUCTION_TRIGGERS = {"how", "explain", "tutorial"}
_PHILOSOPHY_TRIGGERS = {"why", "meaning", "purpose"}


_STATE_ENGINE = StateTransitionEngine()


def _detect_emotion(text: str) -> str:
    lowered = text.lower()
    for key in _EMOTION_KEYS:
        if key in lowered:
            return key
    return "neutral"


def _build_context(limit: int = 3) -> str:
    entries = load_interactions(limit=limit)
    parts = [e.get("input", "") for e in entries if e.get("input")]
    return "\n".join(parts)


async def _delegate(prompt: str, glm: GLMIntegration) -> str:
    return glm.complete(prompt)


async def _maybe_servant(text: str) -> tuple[str, str]:
    if any(t in text.lower() for t in _INSTRUCTION_TRIGGERS) and smm.has_model("deepseek"):
        return await smm.invoke("deepseek", text), "deepseek"
    if any(t in text.lower() for t in _PHILOSOPHY_TRIGGERS) and smm.has_model("mistral"):
        return await smm.invoke("mistral", text), "mistral"
    raise LookupError


def crown_prompt_orchestrator(message: str, glm: GLMIntegration) -> Dict[str, Any]:
    """Return GLM or servant model reply with metadata."""
    emotion = _detect_emotion(message)
    archetype = emotion_analysis.emotion_to_archetype(emotion)
    weight = emotion_analysis.emotion_weight(emotion)
    state = _STATE_ENGINE.update_state(message)
    context = _build_context()
    prompt_body = f"{context}\n{message}" if context else message
    prompt = f"[{state}]\n{prompt_body}"

    async def _process() -> tuple[str, str]:
        try:
            return await _maybe_servant(message)
        except Exception:
            text = await _delegate(prompt, glm)
            return text, "glm"

    text, model = asyncio.run(_process())

    return {
        "text": text,
        "model": model,
        "emotion": emotion,
        "archetype": archetype,
        "weight": weight,
        "state": state,
        "context_used": context,
    }


__all__ = ["crown_prompt_orchestrator"]
