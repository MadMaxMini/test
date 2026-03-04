#!/usr/bin/env bash
# Ollama status — running models, available models, API health

echo "==> Ollama Status"
echo ""

# Check if running
if ! curl -s --max-time 2 http://127.0.0.1:11434 > /dev/null 2>&1; then
  echo "    Status:  NOT RUNNING"
  echo "    Start:   ollama serve"
  exit 1
fi

echo "    Status:  RUNNING (127.0.0.1:11434)"
echo ""

# Pulled models
echo "==> Available Models"
ollama list
echo ""

# Running models
RUNNING=$(ollama ps 2>/dev/null)
if [ -n "$RUNNING" ]; then
  echo "==> Currently Loaded"
  echo "$RUNNING"
else
  echo "==> Currently Loaded: none"
fi
