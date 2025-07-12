from __future__ import annotations

"""Initialize the Crown agent by loading configuration and memory."""

import logging
import os
from pathlib import Path

import yaml

from inanna_ai.glm_integration import GLMIntegration
import vector_memory
from inanna_ai import corpus_memory
import servant_model_manager as smm
try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent / "config" / "INANNA_CORE.yaml"


def _load_config() -> dict:
    """Return configuration merged with environment overrides."""
    cfg: dict = {}
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    env_map = {
        "glm_api_url": "GLM_API_URL",
        "glm_api_key": "GLM_API_KEY",
        "model_path": "MODEL_PATH",
        "memory_dir": "MEMORY_DIR",
    }
    for key, env in env_map.items():
        val = os.getenv(env)
        if val:
            cfg[key] = val

    servant = cfg.get("servant_models", {})
    for name, env in ("deepseek", "DEEPSEEK_URL"), ("mistral", "MISTRAL_URL"):
        val = os.getenv(env)
        if val:
            servant[name] = val
    if servant:
        cfg["servant_models"] = servant

    return cfg


def _init_memory(cfg: dict) -> None:
    mem_dir = cfg.get("memory_dir")
    if mem_dir:
        mem_dir = Path(mem_dir)
        vec_path = mem_dir / "vector_memory"
        os.environ["VECTOR_DB_PATH"] = str(vec_path)
        try:
            vector_memory._get_collection()
            logger.info("Vector memory loaded from %s", vec_path)
        except Exception as exc:  # pragma: no cover - optional deps
            logger.warning("Vector memory unavailable: %s", exc)

        corpus_path = mem_dir / "chroma"
        corpus_memory.CHROMA_DIR = corpus_path
        try:
            corpus_memory.create_collection(dir_path=corpus_memory.CHROMA_DIR)
            logger.info("Corpus memory loaded from %s", corpus_path)
        except Exception as exc:  # pragma: no cover - optional deps
            logger.warning("Corpus memory unavailable: %s", exc)


def _check_glm(integration: GLMIntegration) -> None:
    try:
        resp = integration.complete("ping")
        logger.info("GLM test response: %s", resp)
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Failed to reach GLM endpoint: %s", exc)


def _register_http_servant(name: str, url: str) -> None:
    def _invoke(prompt: str) -> str:
        if requests is None:
            return ""
        try:
            resp = requests.post(url, json={"prompt": prompt}, timeout=10)
            resp.raise_for_status()
            try:
                return resp.json().get("text", "")
            except Exception:
                return resp.text
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Servant %s failed: %s", name, exc)
            return ""

    smm.register_model(name, _invoke)


def _init_servants(cfg: dict) -> None:
    for name, url in (cfg.get("servant_models") or {}).items():
        _register_http_servant(name, url)


def initialize_crown() -> GLMIntegration:
    """Return a :class:`GLMIntegration` instance configured from YAML."""
    cfg = _load_config()
    integration = GLMIntegration(
        endpoint=cfg.get("glm_api_url"),
        api_key=cfg.get("glm_api_key"),
    )
    if cfg.get("model_path"):
        os.environ.setdefault("MODEL_PATH", str(cfg["model_path"]))
    _init_memory(cfg)
    _init_servants(cfg)
    _check_glm(integration)
    return integration


__all__ = ["initialize_crown"]
