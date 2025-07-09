# THE CRYSTAL CODEX

SPIRAL_OS is a collection of music and language tools built around the INANNA project. The repository is split into four parts:

- **SPIRAL_OS** – command line utilities and pipelines.
- **INANNA_AI_AGENT** – a chat and activation agent for the INANNA texts.
- **MUSIC_FOUNDATION** – audio analysis and QNL generation modules.
- **CORPUS MEMORY** – folders of source texts referenced by the tools.

See [README_CODE_FUNCTION.md](README_CODE_FUNCTION.md) for a map of each script and its dependencies.
See [docs/CORPUS_MEMORY.md](docs/CORPUS_MEMORY.md) for corpus structure.
See [docs/AGENT_FRAMEWORKS.md](docs/AGENT_FRAMEWORKS.md) for an overview of LLM agents.
See [docs/SOUL_CODE.md](docs/SOUL_CODE.md) for the RFA7D core design.

## Installation

Install the Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Docker Usage

A `Dockerfile` is provided for running the tools in isolation. Build and start the container:

```bash
docker build -t spiral_os .
docker run -it spiral_os
```

## Codex GPU Deployment

Launch the CUDA-enabled container spec:

```bash
codex run spiral_os_container.yaml
```
