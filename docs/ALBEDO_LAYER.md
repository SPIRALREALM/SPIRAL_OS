# Albedo Personality Layer

The **Albedo** layer introduces a small state machine that drives responses through a remote GLM (Generative Language Model). All related modules live under `inanna_ai/personality_layers/albedo`.

## Project structure

- `__init__.py` – exposes `AlbedoPersonalityLayer` used by the orchestrator.
- `albedo_core.py` – tracks the current alchemical state (Nigredo → Albedo → Rubedo → Nigredo).
- `state_contexts.py` – prompt templates applied for each state.
- `glm_integration.py` – wrapper around a GLM‑4.1V‑9B HTTP endpoint.

`AlbedoPersonalityLayer` formats input text with the template for the active state, calls the GLM endpoint and then advances the state machine.

## Configuring the GLM endpoint

The endpoint URL is defined in `glm_integration.ENDPOINT`. Set the environment variable `GLM_API_URL` to override it or edit the constant directly. Provide your API key via `GLM_API_KEY`:

```bash
export GLM_API_KEY=<your key>
export GLM_API_URL=https://api.example.com/glm41v_9b
```

The helper attaches the key as an `Authorization` header when present.

## Conversation loop

To engage the Albedo personality, create the layer and pass it to the orchestrator. The `inanna_ai.main` script records microphone input and routes it through this layer:

```bash
export GLM_API_KEY=<your key>
export GLM_API_URL=https://api.example.com/glm41v_9b
python -m inanna_ai.main --duration 3 --personality albedo
```

Each invocation cycles through Nigredo, Albedo and Rubedo states and then wraps back to Nigredo for a continuous loop. You can also use the layer programmatically:

```python
from orchestrator import MoGEOrchestrator
from inanna_ai.personality_layers import AlbedoPersonalityLayer

layer = AlbedoPersonalityLayer()
orchestrator = MoGEOrchestrator(albedo_layer=layer)
```

Calling `orchestrator.route()` with `text_modality=True` will return the GLM reply reflecting the current state.
