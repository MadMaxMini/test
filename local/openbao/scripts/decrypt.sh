#!/usr/bin/env bash
# Decrypt a file using OpenBao Transit engine
# Usage: ./decrypt.sh <coach> <file.enc>
# Output: prints plaintext to stdout (pipe or redirect as needed)

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <coach> <file.enc>"
  echo "Example: $0 mad-max workspace/notes.md.enc"
  exit 1
fi

COACH="$1"
FILE="$2"

if [ ! -f "$FILE" ]; then
  echo "ERROR: File not found: $FILE"
  exit 1
fi

if [ -z "${BAO_TOKEN:-}" ]; then
  source "$INIT_FILE"
  export BAO_TOKEN="$ROOT_TOKEN"
fi

CIPHERTEXT=$(cat "$FILE")

curl -s \
  --header "X-Vault-Token: $BAO_TOKEN" \
  --request POST \
  --data "{\"ciphertext\": \"$CIPHERTEXT\"}" \
  "$BAO_ADDR/v1/transit/decrypt/$COACH" | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
if 'data' in d:
    print(base64.b64decode(d['data']['plaintext']).decode('utf-8'), end='')
else:
    print('ERROR:', d, file=sys.stderr)
    sys.exit(1)
"
