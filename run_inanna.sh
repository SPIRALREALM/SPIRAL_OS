#!/bin/bash

# Load environment variables if secrets file exists
if [ -f "secrets.env" ]; then
    set -a
    source "secrets.env"
    set +a
fi

# Check for required models before starting chat
MODELS_DIR="INANNA_AI/models"
if [ ! -d "$MODELS_DIR/DeepSeek-R1" ] && [ ! -d "$MODELS_DIR/gemma2" ]; then
    echo "Required model files not found in $MODELS_DIR." >&2
    echo "Run 'python download_models.py deepseek' or 'python download_models.py gemma2' before launching." >&2
    exit 1
fi

python INANNA_AI_AGENT/inanna_ai.py chat "$@"
