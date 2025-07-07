from __future__ import annotations

import os
from typing import Optional

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
except Exception:  # transformers not installed
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    torch = None  # type: ignore


class EchoModel:
    """Fallback model that echoes the prompt."""

    def generate(self, prompt: str, **_: object) -> str:
        return f"{prompt}"


class HFModel:
    """Lightweight wrapper around a HuggingFace causal LM."""

    def __init__(self, model_name: str) -> None:
        if AutoModelForCausalLM is None or AutoTokenizer is None:
            raise RuntimeError("transformers library not available")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        device = "cuda" if torch and torch.cuda.is_available() else "cpu"
        if torch is not None:
            self.model.to(device)
        self.device = device

    def generate(self, prompt: str, max_new_tokens: int = 50) -> str:
        if AutoTokenizer is None or AutoModelForCausalLM is None:
            return prompt
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch is not None:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


def load_model(model_name: Optional[str] = None):
    """Load and return a language model.

    If transformers is unavailable or the model fails to load, an echo
    model is returned instead.
    """

    model_name = model_name or os.getenv("INANNA_MODEL", "sshleifer/tiny-gpt2")
    if AutoModelForCausalLM is None:
        return EchoModel()
    try:
        return HFModel(model_name)
    except Exception:
        return EchoModel()
