#!/usr/bin/env bash
# Store a secret in OpenBao
# Usage: ./store-secret.sh <path> <key> <value>
# Example: ./store-secret.sh ai/huggingface token hf_xxxxxxxxxxxx

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <path> <key> <value>"
  echo "Example: $0 ai/huggingface token hf_xxxxxxxxxxxx"
  exit 1
fi

PATH_NAME="$1"
KEY="$2"
VALUE="$3"

if [ -z "${BAO_TOKEN:-}" ]; then
  if [ -f "$INIT_FILE" ]; then
    export BAO_TOKEN=$(grep ROOT_TOKEN "$INIT_FILE" | cut -d= -f2)
  else
    echo "ERROR: BAO_TOKEN not set and $INIT_FILE not found."
    exit 1
  fi
fi

echo "==> Storing secret at secret/$PATH_NAME..."
curl -s \
  --header "X-Vault-Token: $BAO_TOKEN" \
  --request POST \
  --data "{\"data\": {\"$KEY\": \"$VALUE\"}}" \
  "$BAO_ADDR/v1/secret/data/$PATH_NAME" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'data' in d:
    print('    Stored! Version:', d['data'].get('version', '?'))
else:
    print('ERROR:', d)
    sys.exit(1)
"
