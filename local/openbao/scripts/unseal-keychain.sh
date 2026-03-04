#!/usr/bin/env bash
# OpenBao Unseal — reads unseal key from macOS Keychain
# Run after every Docker restart

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
KEYCHAIN_SERVICE="openbao"

echo "==> Reading unseal key from Keychain..."
UNSEAL_KEY=$(security find-generic-password -a "$USER" -s "${KEYCHAIN_SERVICE}-unseal-key" -w 2>/dev/null)

if [ -z "$UNSEAL_KEY" ]; then
  echo "ERROR: Unseal key not found in Keychain."
  echo "       Run init-keychain.sh first, or check Keychain Access app."
  exit 1
fi

echo "==> Unsealing OpenBao..."
RESPONSE=$(curl -s \
  --request POST \
  --data "{\"key\": \"$UNSEAL_KEY\"}" \
  "$BAO_ADDR/v1/sys/unseal")

SEALED=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sealed', True))")

if [ "$SEALED" = "False" ]; then
  echo "==> Unsealed successfully!"
else
  echo "ERROR: Failed to unseal."
  echo "$RESPONSE"
  exit 1
fi
