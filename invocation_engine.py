from __future__ import annotations

"""Pattern-based invocation engine."""

from typing import Callable, Dict, Tuple, Any, List
import re

import vector_memory
from orchestrator import MoGEOrchestrator


# Map of (symbols, emotion) -> callback
_CALLBACKS: Dict[Tuple[str, str | None], Callable[[str, str | None, MoGEOrchestrator | None], Any]] = {}
# Map of (symbols, emotion) -> orchestrator hook name
_HOOKS: Dict[Tuple[str, str | None], str] = {}

_SYMBOL_RE = re.compile(r"[^\w\s\[\]#]+")
_EMO_RE = re.compile(r"\[(\w+)\]|#(\w+)")


def register_invocation(
    symbols: str,
    emotion: str | None = None,
    callback: Callable[[str, str | None, MoGEOrchestrator | None], Any] | None = None,
    *,
    hook: str | None = None,
) -> None:
    """Register an invocation pattern with ``callback`` or orchestrator ``hook``."""
    if callback is None and hook is None:
        raise ValueError("callback or hook required")
    key = (symbols, emotion)
    if callback:
        _CALLBACKS[key] = callback
    if hook:
        _HOOKS[key] = hook
    try:
        vector_memory.add_vector(symbols, {"symbols": symbols, "emotion": emotion or ""})
    except Exception:
        pass


def clear_registry() -> None:
    """Remove all registered invocation patterns."""
    _CALLBACKS.clear()
    _HOOKS.clear()


def _extract_symbols(text: str) -> str:
    parts = _SYMBOL_RE.findall(text)
    return "".join(parts)


def _extract_emotion(text: str) -> str | None:
    m = _EMO_RE.search(text)
    if m:
        return (m.group(1) or m.group(2)).lower()
    return None


def invoke(text: str, orchestrator: MoGEOrchestrator | None = None) -> List[Any]:
    """Process ``text`` and trigger callbacks for matching invocations."""
    symbols = _extract_symbols(text)
    emotion = _extract_emotion(text)
    key = (symbols, emotion)
    results: List[Any] = []

    cb = _CALLBACKS.get(key)
    hk = _HOOKS.get(key)

    if cb is None and hk is None:
        try:
            search_res = vector_memory.search(symbols or text, filter={"emotion": emotion} if emotion else None, k=1)
        except Exception:
            search_res = []
        if search_res:
            meta = search_res[0]
            key = (str(meta.get("symbols", meta.get("text", ""))), meta.get("emotion") or None)
            cb = _CALLBACKS.get(key)
            hk = _HOOKS.get(key)

    if cb:
        results.append(cb(symbols, emotion, orchestrator))
    if hk and orchestrator is not None:
        method = getattr(orchestrator, hk, None)
        if callable(method):
            results.append(method(symbols, emotion))
    return results


__all__ = ["register_invocation", "invoke", "clear_registry"]

