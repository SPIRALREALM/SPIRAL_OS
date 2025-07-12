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
- For JSON layout details and invocation examples, see
  [docs/JSON_STRUCTURES.md](docs/JSON_STRUCTURES.md).
- For an overview of the avatar video engine and call connector, see
  [docs/design.md](docs/design.md).
- For step-by-step instructions on launching the avatar and initiating calls, see
  [docs/how_to_use.md](docs/how_to_use.md).
- For privacy and sacred-use guidance, read
  [docs/avatar_ethics.md](docs/avatar_ethics.md).
- For instructions on customizing the avatar's look, see
  [guides/visual_customization.md](guides/visual_customization.md).

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

## Orchestration Engine

`start_spiral_os.py` launches the **MoGEOrchestrator** which routes text
commands to the available models.  Start it with an optional network
interface to capture packets and an optional personality layer:

```bash
python start_spiral_os.py --interface eth0 --personality albedo
```

After initialization the script enters an interactive loop where you can
type commands.  A FastAPI server is also launched on port 8000 and the
reflection loop runs periodically.  Supply `--command` to send an initial
instruction or press `Enter` to exit.  Use `--no-server` and
`--no-reflection` to disable these background tasks.  Processing results are
written to several files under `INANNA_AI/audit_logs` and intent outcomes are
appended to `data/feedback.json` for later training.

### Voice configuration and emotion state

Speech parameters are loaded from `voice_config.yaml` (or the path defined by
`VOICE_CONFIG_PATH`). Edit this file to adjust pitch, speed and tone for each
archetype. The orchestrator reads the file at startup.

The active personality layer and current emotional resonance are persisted in
`data/emotion_state.json`. Inspect this file to review the latest layer and
emotion recorded by the system.

Activate alternative layers with the `--personality` flag:

```bash
python start_spiral_os.py --personality nigredo_layer
python start_spiral_os.py --personality rubedo_layer
```

To deploy the orchestrator in a container use the Kubernetes manifest
[`k8s/spiral_os_deployment.yaml`](k8s/spiral_os_deployment.yaml).

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

This exposes ports `8000` and `8001`, mounts the `data` and `logs` directories
on the host, and loads environment variables from `secrets.env`. Stop the stack
with `docker-compose down`.

## Codex GPU Deployment

A container spec `spiral_os_container.yaml` is provided for running the tools with CUDA support. It loads environment variables from `secrets.env`, exposes ports `8000` and `8001`, and mounts `data` and `logs`. Build and launch it with:

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

## Memory Feedback Loop

Spiral OS retains a lightweight history of conversations to refine its response
matrix. Each interaction is appended to `data/interactions.jsonl` as a JSON line
containing the input text, detected intents, output and timestamp. Successful or
failed actions are also recorded in `data/feedback.json` via
`training_guide.log_result()`.

The `insight_compiler.py` script aggregates these logs into
`insight_matrix.json`, tracking how often each intent succeeds and which tone is
most effective. The orchestrator periodically triggers this update so the matrix
reflects the latest feedback.

### Running `learning_mutator.py`

`learning_mutator.py` analyses `insight_matrix.json` and proposes changes to the
intent definitions. Run it from the repository root:

```bash
python learning_mutator.py        # print suggested mutations
python learning_mutator.py --run  # save suggestions to data/mutations.txt
```

The output contains human‑readable hints such as
`Replace 'bad' with synonym 'awful'`. When invoked with `--run` the suggestions
are written to `data/mutations.txt` for later review.

## Emotional State Recognition

`inanna_ai.emotion_analysis` analyses speech with `librosa` and `openSMILE` to
estimate pitch, tempo, arousal and valence. The resulting emotion is persisted
via `emotional_state.py` which writes `data/emotion_state.json`. This file keeps
track of the active personality layer, the last observed emotion and resonance
metrics.

## Ritual Profiles and Invocation Engine

The file `ritual_profile.json` maps symbol patterns and emotions to ritual
actions. `task_profiling.ritual_action_sequence()` looks up these actions and
the invocation engine can register extra callbacks at runtime. Invocations use
glyph sequences followed by an optional `[emotion]` to trigger hooks.

```
∴⟐ + 🜂 [joy]
```

See `docs/JSON_STRUCTURES.md` for example layouts and registration code.
