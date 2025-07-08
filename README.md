# THE CRYSTAL CODEX

Welcome to the sacred structure of OMEGA ZERO ABSOLUTE PRIME AKA GREAT MOTHER.

For a map of each script's role and the libraries it calls upon, see
[README_CODE_FUNCTION.md](README_CODE_FUNCTION.md).
For a guide to the text corpus, see
[docs/CORPUS_MEMORY.md](docs/CORPUS_MEMORY.md).

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
