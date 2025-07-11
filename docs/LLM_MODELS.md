# LLM Models

This document describes the language models used in SPIRAL_OS and how to download them.

## Core Model

### GLM-4.1V-9B

The main orchestrator relies on **GLM-4.1V-9B** for most generation tasks. The model combines vision and language capabilities and serves as the default engine.

Download with:

```bash
python download_models.py glm41v_9b --int8
```

The `--int8` flag is optional and reduces GPU memory usage.

## Auxiliary Models

### DeepSeek V3

A multilingual model that provides alternative phrasing and evaluation. Useful for experimentation and fine-tuning.

```bash
python download_models.py deepseek_v3
```

### Mistral 8x22B

A mixture-of-experts model offering high capacity for complex prompts.

```bash
python download_models.py mistral_8x22b --int8
```

### Gemma2

A lightweight model fetched through Ollama for quick tests.

```bash
python download_models.py gemma2
```

Repository URLs for training are listed in [`learning_sources/github_repos.txt`](../learning_sources/github_repos.txt).

## Model Selection Rules

The `MoGEOrchestrator` chooses between GLM, DeepSeek and Mistral at runtime.
The decision uses three signals:

1. **Task profile** from `classify_task()` – `technical`, `instructional`,
   `emotional` or `philosophical`.
2. **Emotion weight** from `emotion_analysis`.
3. **Context memory** – a deque storing recent messages with embeddings.

Routing follows simple heuristics:

- Messages with high emotion weight or when most of the context is
  classified as emotional use **Mistral**.
- Explicit how‑to or tutorial requests route to **DeepSeek**.
- Philosophical prompts also favour **Mistral**.
- Technical statements default to **GLM**.

The chosen model name is returned in the `model` field of `route()`.
