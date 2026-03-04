#!/usr/bin/env bash
# Pull all Tier 1 models (trusted, native Ollama)
# These run natively with full Apple Silicon Metal GPU

set -euo pipefail

MODELS=(
  "llama3.3:70b"
  "devstral:24b"
  "qwen2.5-coder:14b"
  "gemma3:12b"
)

echo "==> Pulling Tier 1 models (native Ollama)"
echo "    This will take a while — models are large."
echo ""

for MODEL in "${MODELS[@]}"; do
  echo "--- Pulling $MODEL ---"
  ollama pull "$MODEL"
  echo ""
done

echo "==> All Tier 1 models pulled!"
ollama list
