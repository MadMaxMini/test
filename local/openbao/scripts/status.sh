#!/usr/bin/env bash
# OpenBao Status Script
# Quick health check — is it running, initialized, sealed?

BAO_ADDR="http://127.0.0.1:8200"

echo "==> OpenBao Status"
echo "    Address: $BAO_ADDR"
echo ""

RESPONSE=$(curl -s --max-time 3 "$BAO_ADDR/v1/sys/health" 2>/dev/null)

if [ -z "$RESPONSE" ]; then
  echo "    Status:  NOT RUNNING (container down?)"
  echo ""
  echo "    To start: cd ~/Work/local/openbao && docker compose up -d"
  exit 1
fi

INITIALIZED=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('initialized', False))")
SEALED=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sealed', True))")
VERSION=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version', 'unknown'))")

echo "    Version:     $VERSION"
echo "    Initialized: $INITIALIZED"
echo "    Sealed:      $SEALED"
echo ""

if [ "$INITIALIZED" = "False" ]; then
  echo "    Next step: run scripts/init.sh"
elif [ "$SEALED" = "True" ]; then
  echo "    Next step: run scripts/unseal.sh"
else
  echo "    Ready! UI: http://127.0.0.1:8200"
fi
