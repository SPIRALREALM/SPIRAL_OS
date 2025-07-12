from __future__ import annotations

"""Initialize the Crown agent by loading configuration and memory."""

import logging
import os
from pathlib import Path

import yaml

from inanna_ai.glm_integration import GLMIntegration
import vector_memory
from inanna_ai import corpus_memory

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent / "config" / "INANNA_CORE.yaml"


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(CONFIG_FILE)
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _init_memory(cfg: dict) -> None:
    vec_path = cfg.get("vector_db_path")
    if vec_path:
        os.environ["VECTOR_DB_PATH"] = str(vec_path)
        try:
            vector_memory._get_collection()
            logger.info("Vector memory loaded from %s", vec_path)
        except Exception as exc:  # pragma: no cover - optional deps
            logger.warning("Vector memory unavailable: %s", exc)

    corpus_path = cfg.get("corpus_chroma_path")
    if corpus_path:
        corpus_memory.CHROMA_DIR = Path(corpus_path)
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


def initialize_crown() -> GLMIntegration:
    """Return a :class:`GLMIntegration` instance configured from YAML."""
    cfg = _load_config()
    integration = GLMIntegration(
        endpoint=cfg.get("glm_url"),
        api_key=cfg.get("glm_api_key"),
    )
    _init_memory(cfg)
    _check_glm(integration)
    return integration


__all__ = ["initialize_crown"]
