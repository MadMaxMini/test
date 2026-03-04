#!/usr/bin/env bash
# Retrieve a secret from OpenBao
# Usage: ./get-secret.sh <path> <key>
# Example: ./get-secret.sh ai/huggingface token

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <path> <key>"
  echo "Example: $0 ai/huggingface token"
  exit 1
fi

PATH_NAME="$1"
KEY="$2"

if [ -z "${BAO_TOKEN:-}" ]; then
  if [ -f "$INIT_FILE" ]; then
    export BAO_TOKEN=$(grep ROOT_TOKEN "$INIT_FILE" | cut -d= -f2)
  else
    echo "ERROR: BAO_TOKEN not set and $INIT_FILE not found."
    exit 1
  fi
fi

curl -s \
  --header "X-Vault-Token: $BAO_TOKEN" \
  "$BAO_ADDR/v1/secret/data/$PATH_NAME" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'data' in d and 'data' in d['data']:
    val = d['data']['data'].get('$KEY')
    if val:
        print(val)
    else:
        print('ERROR: key \"$KEY\" not found', file=sys.stderr)
        sys.exit(1)
else:
    print('ERROR:', d, file=sys.stderr)
    sys.exit(1)
"
