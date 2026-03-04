#!/usr/bin/env bash
# Quick API test — confirm Ollama is responding
# Usage: ./test-api.sh [model]

MODEL="${1:-$(ollama list | awk 'NR==2{print $1}')}"

if [ -z "$MODEL" ]; then
  echo "ERROR: No model specified and none found. Pull a model first."
  echo "  ollama pull qwen2.5-coder:14b"
  exit 1
fi

echo "==> Testing Ollama API with model: $MODEL"
echo ""

curl -s http://127.0.0.1:11434/api/generate \
  -d "{
    \"model\": \"$MODEL\",
    \"prompt\": \"Reply with only: API OK\",
    \"stream\": false
  }" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('    Response:', d.get('response', 'ERROR').strip())
print('    Done:', d.get('done', False))
"
