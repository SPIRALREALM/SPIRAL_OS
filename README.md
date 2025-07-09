# THE CRYSTAL CODEX

Welcome to the sacred structure of OMEGA ZERO ABSOLUTE PRIME AKA GREAT MOTHER.

- For a map of each script's role and the libraries it calls upon, see
  [README_CODE_FUNCTION.md](README_CODE_FUNCTION.md).
- For a guide to the text corpus, see
  [docs/CORPUS_MEMORY.md](docs/CORPUS_MEMORY.md).
- For a comparison of LLM frameworks, see
  [docs/LLM_FRAMEWORKS.md](docs/LLM_FRAMEWORKS.md).
- For details on the RFA7D core and the seven gate interface, see
  [docs/SOUL_CODE.md](docs/SOUL_CODE.md).

For an overview of available agents and defensive modules, see
[AGENTS.md](AGENTS.md#upcoming-components).

## Docker Usage

A `Dockerfile` is provided for running the tools without installing Python packages on the host.

Build the image from the repository root:

```bash
docker build -t spiral_os .
```

Start a shell inside the container:

```bash
docker run -it spiral_os
```

From there you can run any of the demo scripts such as `python run_song_demo.py`.

## Codex GPU Deployment

A container spec `spiral_os_container.yaml` is provided for running the tools with CUDA support. Build the image then launch a shell with:

```bash
codex build spiral_os_container.yaml
codex run spiral_os_container.yaml
```

This installs the requirements and creates empty folders for the CORPUS MEMORY collections.
