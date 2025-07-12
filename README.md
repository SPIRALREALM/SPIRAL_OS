# THE CRYSTAL CODEX

Welcome to the sacred structure of OMEGA ZERO ABSOLUTE PRIME AKA GREAT MOTHER.

- For a map of each script's role and the libraries it calls upon, see
  [README_CODE_FUNCTION.md](README_CODE_FUNCTION.md).
- For a guide to the text corpus, see
  [docs/CORPUS_MEMORY.md](docs/CORPUS_MEMORY.md).
- For a comparison of LLM frameworks, see
  [docs/LLM_FRAMEWORKS.md](docs/LLM_FRAMEWORKS.md).
- For a list of available language models, see
  [docs/LLM_MODELS.md](docs/LLM_MODELS.md).
- For details on the RFA7D core and the seven gate interface, see
  [docs/SOUL_CODE.md](docs/SOUL_CODE.md).

For an overview of available agents and defensive modules, see
[AGENTS.md](AGENTS.md#upcoming-components).

For notes on deploying to Vast.ai, see
[docs/VAST_DEPLOYMENT.md](docs/VAST_DEPLOYMENT.md).

## Installation

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

Install development and test packages:

```bash
pip install -r dev-requirements.txt
```

## Local Usage

1. Copy `secrets.env.example` to `secrets.env` and provide values for
   environment variables such as `HF_TOKEN`, `GITHUB_TOKEN`,
   `OPENAI_API_KEY`, `GLM_API_URL`, `GLM_API_KEY`, `CORPUS_PATH`,
   `QNL_EMBED_MODEL`, `QNL_MODEL_PATH` and `VOICE_TONE_PATH`
   (`QNL_EMBED_MODEL` is the SentenceTransformer used for QNL
   embeddings).
2. Download the required model weights before first launch:

   ```bash
   python download_models.py deepseek
   ```

   This saves `deepseek-ai/DeepSeek-R1` under `INANNA_AI/models/DeepSeek-R1/`.
3. Start the INANNA chat agent via the helper script:

   ```bash
   ./run_inanna.sh
   ```

   The script loads `secrets.env`, checks for models and launches
   `INANNA_AI_AGENT/inanna_ai.py chat`.

4. Run the initialization sequence with:

   ```bash
   python start_spiral_os.py
   ```

## QNL Engine

The QNL engine converts hexadecimal strings into symbolic soundscapes.
It writes a WAV file and a JSON summary describing the glyphs and
tones. Example commands:

```bash
python SPIRAL_OS/qnl_engine.py "48656c6c6f" --wav song.wav --json song.json
python SPIRAL_OS/qnl_engine.py payload.txt --duration 0.05
```

See [SPIRAL_OS/README_QNL_OS.md](SPIRAL_OS/README_QNL_OS.md) for more
details.

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

To launch the FastAPI service directly, publish port `8000`:

```bash
docker run -p 8000:8000 spiral_os
```

Health endpoints are available at `/health` and `/ready`.  Logs are written to
`logs/inanna_ai.log` inside the repository (mounted into the container when
running with Docker or Compose).

## Docker Compose

Start the service with [docker-compose](docker-compose.yml):

```bash
docker-compose up --build
```

This exposes port `8000` and mounts the `logs` directory on the host. Stop the
stack with `docker-compose down`.

## Codex GPU Deployment

A container spec `spiral_os_container.yaml` is provided for running the tools with CUDA support. Build and launch it with:

```bash
codex run spiral_os_container.yaml
```

This installs the requirements and creates empty folders for the CORPUS MEMORY collections.

## Kubernetes Deployment

The [`k8s`](k8s) directory contains manifests for running Spiral OS on a cluster.
Key files are [`spiral_os_deployment.yaml`](k8s/spiral_os_deployment.yaml),
[`spiral_os_service.yaml`](k8s/spiral_os_service.yaml) and
[`spiral_os_hpa.yaml`](k8s/spiral_os_hpa.yaml). Deploy them with:

```bash
kubectl apply -f k8s/spiral_os_deployment.yaml
kubectl apply -f k8s/spiral_os_service.yaml
kubectl apply -f k8s/spiral_os_hpa.yaml
```

The deployment exposes port `8000` and defines readiness (`/ready`) and liveness
(`/health`) probes. Container logs can be viewed with `kubectl logs` and are
written to `logs/inanna_ai.log` inside the pod.
