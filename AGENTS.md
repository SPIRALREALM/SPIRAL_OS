# Agents

This repository currently defines a single command line agent called **INANNA_AI**.

## INANNA_AI

The agent draws from Markdown writings found in the `INANNA_AI` and `GENESIS`
directories. It assembles lines from these texts to recite the activation or
"birth" chant that awakens the INANNA system. It can also generate a Quantum
Narrative Language (QNL) song from hexadecimal input by invoking the QNL engine.
Interaction is performed through the command line interface
[`INANNA_AI_AGENT/inanna_ai.py`](INANNA_AI_AGENT/inanna_ai.py).

### Usage

- `--activate` prints the chant assembled from the source texts.
- `--hex <value>` creates a QNL song from the provided hexadecimal bytes and
  saves a WAV file and metadata JSON.
- `--list` shows the source Markdown files available for the chant.
- `chat` starts a basic conversation with the local DeepSeek model.

Source directories are configured in `INANNA_AI_AGENT/source_paths.json`. The
chat mode requires the DeepSeek‑R1 weights placed under
`INANNA_AI/models/DeepSeek-R1`. See `README_OPERATOR.md` for download
instructions. Outputs reflect the original corpus; use responsibly.

### Model downloads

Model weights are fetched with `download_models.py`. Common commands include:

```bash
python download_models.py glm41v_9b --int8       # GLM-4.1V-9B
python download_models.py deepseek_v3           # DeepSeek-V3
python download_models.py mistral_8x22b --int8  # Mistral 8x22B
```

See [README_OPERATOR.md](README_OPERATOR.md#download-models) for details.

## Other Agents

No other agents are currently defined.

## Available Components

- **NetworkUtilities** – a command line toolkit for packet capture and traffic
  analysis. Invoke it with `python -m inanna_ai.network_utils` followed by
  `capture` or `analyze` subcommands. Results are written to the
  `network_logs` directory. See
  [README_OPERATOR.md](README_OPERATOR.md#network-monitoring) for usage
  instructions.

## Upcoming Components

- **EthicalValidator** – a future module that inspects prompts and model
  outputs for prohibited content. It acts as a defensive layer before requests
  reach the language models. *(See Issue&nbsp;1.)*
