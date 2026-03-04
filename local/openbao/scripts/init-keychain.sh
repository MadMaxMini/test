#!/usr/bin/env bash
# OpenBao Init — Keychain variant (Option B)
# Stores unseal key and root token in macOS Keychain instead of plaintext file
# Run ONCE after first `docker compose up -d`

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
KEYCHAIN_SERVICE="openbao"

echo "==> Checking OpenBao status..."
STATUS=$(curl -s "$BAO_ADDR/v1/sys/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('initialized', False))")

if [ "$STATUS" = "True" ]; then
  echo "OpenBao is already initialized. Run unseal-keychain.sh if it's sealed."
  exit 0
fi

echo "==> Initializing OpenBao..."
INIT_RESPONSE=$(curl -s \
  --request POST \
  --data '{"secret_shares": 1, "secret_threshold": 1}' \
  "$BAO_ADDR/v1/sys/init")

UNSEAL_KEY=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['keys'][0])")
ROOT_TOKEN=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['root_token'])")

echo "==> Storing in macOS Keychain (you may be prompted)..."

security add-generic-password \
  -a "$USER" \
  -s "${KEYCHAIN_SERVICE}-unseal-key" \
  -w "$UNSEAL_KEY" \
  -T "" \
  -U 2>/dev/null || \
security add-generic-password \
  -a "$USER" \
  -s "${KEYCHAIN_SERVICE}-unseal-key" \
  -w "$UNSEAL_KEY"

security add-generic-password \
  -a "$USER" \
  -s "${KEYCHAIN_SERVICE}-root-token" \
  -w "$ROOT_TOKEN" \
  -T "" \
  -U 2>/dev/null || \
security add-generic-password \
  -a "$USER" \
  -s "${KEYCHAIN_SERVICE}-root-token" \
  -w "$ROOT_TOKEN"

echo ""
echo "==> OpenBao initialized!"
echo "    Unseal key + root token stored in Keychain under service: $KEYCHAIN_SERVICE"
echo "    No plaintext file written."
echo ""
echo "    To retrieve manually:"
echo "    security find-generic-password -a \$USER -s openbao-unseal-key -w"
echo ""
echo "==> Unsealing now..."
bash "$(dirname "$0")/unseal-keychain.sh"
