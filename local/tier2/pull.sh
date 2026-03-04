#!/usr/bin/env bash
# Pull a Tier 2 model into the isolated container
# Usage: ./pull.sh <model>
# Example: ./pull.sh deepseek-r1:14b

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <model>"
  echo "Tier 2 models: deepseek-r1:14b, deepseek-r1:32b, minimax-m2"
  exit 1
fi

MODEL="$1"

echo "==> Pulling $MODEL into isolated Tier 2 container..."
echo "    (no network access to host — model data stays in container)"
docker compose up -d
docker exec ollama-tier2 ollama pull "$MODEL"
echo "==> Done. Run with:"
echo "    docker exec -it ollama-tier2 ollama run $MODEL"
