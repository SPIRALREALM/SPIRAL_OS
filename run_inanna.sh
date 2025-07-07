#!/bin/bash

# Load environment variables if secrets file exists
if [ -f "INANNA_AI/secrets.env" ]; then
    set -a
    source "INANNA_AI/secrets.env"
    set +a
fi

python INANNA_AI_AGENT/inanna_ai.py chat
