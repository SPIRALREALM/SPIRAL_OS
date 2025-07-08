from __future__ import annotations

"""Simple dialogue manager blending audio and text context."""

from typing import Dict

from . import corpus_memory


CORE_TEMPLATES = {
    "surface": "[Surface] {snippet} You said: '{text}'",
    "deep": "[Deep] {snippet} Your words carry depth: '{text}'",
    "umbra": "[Umbra] {snippet} Shadows echo: '{text}'",
    "albedo": "[Albedo] {snippet} Reflecting: '{text}'",
}


class ResponseManager:
    """Select replies based on emotional and environmental cues."""

    def choose_core(self, emotion: str, classification: str) -> str:
        """Return core name for the given emotion and environment."""
        emotion = emotion.lower()
        classification = classification.lower()
        if classification == "noise":
            return "umbra"
        if emotion == "excited":
            return "surface"
        if emotion == "calm":
            return "albedo"
        return "deep"

    def generate_reply(self, text: str, info: Dict[str, str]) -> str:
        """Generate a text reply blending ``info`` with ``text``."""
        emotion = info.get("emotion", "neutral")
        classification = info.get("classification", "")
        query = f"{text} {emotion} {classification}".strip()
        snippets = corpus_memory.search_corpus(query, top_k=1)
        snippet = snippets[0][1] if snippets else ""
        core = self.choose_core(emotion, classification)
        template = CORE_TEMPLATES.get(core, CORE_TEMPLATES["surface"])
        return template.format(snippet=snippet, text=text, emotion=emotion)


__all__ = ["ResponseManager", "CORE_TEMPLATES"]
