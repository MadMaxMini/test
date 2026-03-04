#!/usr/bin/env bash
# OpenBao Init Script
# Run ONCE after first `docker compose up -d`
# Saves unseal keys and root token to ~/.openbao-init (chmod 600)
# After running this, use unseal.sh to unseal the vault

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

echo "==> Checking OpenBao status..."
STATUS=$(curl -s "$BAO_ADDR/v1/sys/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('initialized', False))")

if [ "$STATUS" = "True" ]; then
  echo "OpenBao is already initialized. Run unseal.sh if it's sealed."
  exit 0
fi

echo "==> Initializing OpenBao (1 key share, 1 threshold for simplicity)..."
INIT_RESPONSE=$(curl -s \
  --request POST \
  --data '{"secret_shares": 1, "secret_threshold": 1}' \
  "$BAO_ADDR/v1/sys/init")

UNSEAL_KEY=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['keys'][0])")
ROOT_TOKEN=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['root_token'])")

# Save to file, locked down
cat > "$INIT_FILE" <<EOF
UNSEAL_KEY=$UNSEAL_KEY
ROOT_TOKEN=$ROOT_TOKEN
EOF
chmod 600 "$INIT_FILE"

echo ""
echo "==> OpenBao initialized!"
echo "    Keys saved to: $INIT_FILE (chmod 600)"
echo ""
echo "    IMPORTANT: Back up $INIT_FILE somewhere safe."
echo "    If you lose the unseal key, your vault is unrecoverable."
echo ""
echo "==> Unsealing now..."
bash "$(dirname "$0")/unseal.sh"
