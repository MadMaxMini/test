#!/bin/bash
# auto-unseal.sh — unseal OpenBao after login if sealed
# Runs via launchd on login. Safe to run repeatedly.

BAO_ADDR="http://127.0.0.1:8200"

# Wait for Docker to be ready (up to 30s)
for i in $(seq 1 15); do
  docker info &>/dev/null && break
  sleep 2
done

# Start OpenBao container if not running
cd ~/Work/local/openbao && docker compose up -d &>/dev/null

# Wait for OpenBao to be reachable (up to 30s)
for i in $(seq 1 15); do
  curl -sf "$BAO_ADDR/v1/sys/health" &>/dev/null && break
  sleep 2
done

# Check if sealed
SEALED=$(curl -sf "$BAO_ADDR/v1/sys/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sealed','true'))" 2>/dev/null)

if [ "$SEALED" = "True" ] || [ "$SEALED" = "true" ]; then
  bash ~/Work/test/local/openbao/scripts/unseal-keychain.sh
else
  echo "[auto-unseal] already unsealed, nothing to do"
fi
