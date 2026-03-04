#!/usr/bin/env bash
# Quick model switcher — unloads current, loads new
# Usage: ./switch.sh <model>
# Example: ./switch.sh qwen2.5-coder:14b

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <model>"
  echo ""
  echo "Available models:"
  ollama list
  exit 1
fi

MODEL="$1"

echo "==> Switching to $MODEL..."

# Stop any running models
ollama stop --all 2>/dev/null || true

# Warm up the new model
echo "==> Loading $MODEL into memory..."
ollama run "$MODEL" --keepalive 0 <<< "" 2>/dev/null || true

echo "==> Done. $MODEL is loaded."
echo "    Chat: ollama run $MODEL"
echo "    API:  curl http://127.0.0.1:11434/api/generate -d '{\"model\":\"$MODEL\",\"prompt\":\"hello\"}'"
