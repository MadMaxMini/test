#!/usr/bin/env bash
# Encrypt a file using OpenBao Transit engine
# Usage: ./encrypt.sh <coach> <file>
# Output: <file>.enc (base64 encoded ciphertext)

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <coach> <file>"
  echo "Example: $0 mad-max workspace/notes.md"
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

# Base64 encode the file contents
PLAINTEXT_B64=$(base64 < "$FILE")

# Encrypt via Transit
RESPONSE=$(curl -s \
  --header "X-Vault-Token: $BAO_TOKEN" \
  --request POST \
  --data "{\"plaintext\": \"$PLAINTEXT_B64\"}" \
  "$BAO_ADDR/v1/transit/encrypt/$COACH")

CIPHERTEXT=$(echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'data' in d:
    print(d['data']['ciphertext'])
else:
    print('ERROR:', d, file=sys.stderr)
    sys.exit(1)
")

echo "$CIPHERTEXT" > "${FILE}.enc"
echo "==> Encrypted: ${FILE}.enc"
