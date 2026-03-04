#!/usr/bin/env bash
# OpenBao Unseal Script
# Run after every Docker restart — vault starts sealed
# Reads unseal key from ~/.openbao-init

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

if [ ! -f "$INIT_FILE" ]; then
  echo "ERROR: $INIT_FILE not found. Run init.sh first."
  exit 1
fi

source "$INIT_FILE"

echo "==> Unsealing OpenBao..."
RESPONSE=$(curl -s \
  --request POST \
  --data "{\"key\": \"$UNSEAL_KEY\"}" \
  "$BAO_ADDR/v1/sys/unseal")

SEALED=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sealed', True))")

if [ "$SEALED" = "False" ]; then
  echo "==> OpenBao unsealed successfully!"
  echo "    Root token is in $INIT_FILE"
  echo "    Export it: export BAO_TOKEN=\$(grep ROOT_TOKEN $INIT_FILE | cut -d= -f2)"
else
  echo "ERROR: Failed to unseal. Response:"
  echo "$RESPONSE"
  exit 1
fi
