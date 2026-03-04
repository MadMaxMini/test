#!/usr/bin/env bash
# Run a Tier 2 model interactively
# Usage: ./run.sh <model>

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <model>"
  docker exec ollama-tier2 ollama list 2>/dev/null || echo "Container not running. Start with: docker compose up -d"
  exit 1
fi

MODEL="$1"

echo "==> Starting Tier 2 isolated session: $MODEL"
echo "    Network: NONE — model cannot reach internet"
echo "    Type /bye to exit"
echo ""
docker exec -it ollama-tier2 ollama run "$MODEL"
