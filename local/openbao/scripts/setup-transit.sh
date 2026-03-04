#!/usr/bin/env bash
# Enable OpenBao Transit engine and create keys + policies for each coach
# Run ONCE after init + unseal

set -euo pipefail

BAO_ADDR="http://127.0.0.1:8200"
INIT_FILE="$HOME/.openbao-init"

if [ -z "${BAO_TOKEN:-}" ]; then
  source "$INIT_FILE"
  export BAO_TOKEN="$ROOT_TOKEN"
fi

echo "==> Enabling Transit secrets engine..."
curl -s --header "X-Vault-Token: $BAO_TOKEN" \
  --request POST \
  --data '{"type":"transit"}' \
  "$BAO_ADDR/v1/sys/mounts/transit" | python3 -c "
import sys, json
r = json.load(sys.stdin)
if r == {} or 'mount_accessor' in str(r):
    print('    Transit engine enabled.')
elif 'already in use' in str(r):
    print('    Transit engine already enabled.')
else:
    print('    Response:', r)
"

echo ""
echo "==> Enabling KV v2 secrets engine..."
curl -s --header "X-Vault-Token: $BAO_TOKEN" \
  --request POST \
  --data '{"type":"kv","options":{"version":"2"}}' \
  "$BAO_ADDR/v1/sys/mounts/secret" > /dev/null 2>&1 || true
echo "    KV v2 ready."

echo ""
echo "==> Creating Transit keys for each coach..."
for KEY in mad-max recruiting life-coach shared; do
  RESP=$(curl -s --header "X-Vault-Token: $BAO_TOKEN" \
    --request POST \
    --data '{"type":"aes256-gcm96"}' \
    "$BAO_ADDR/v1/transit/keys/$KEY")
  echo "    Key: $KEY"
done

echo ""
echo "==> Writing policies..."

# Mad Max policy
curl -s --header "X-Vault-Token: $BAO_TOKEN" \
  --request PUT \
  --data '{
    "policy": "path \"transit/encrypt/mad-max\" { capabilities = [\"update\"] }\npath \"transit/decrypt/mad-max\" { capabilities = [\"update\"] }\npath \"transit/encrypt/shared\" { capabilities = [\"update\"] }\npath \"transit/decrypt/shared\" { capabilities = [\"update\"] }\npath \"secret/data/mad-max/*\" { capabilities = [\"create\",\"read\",\"update\",\"delete\"] }\npath \"secret/data/shared/*\" { capabilities = [\"read\"] }"
  }' \
  "$BAO_ADDR/v1/sys/policies/acl/mad-max" > /dev/null
echo "    Policy: mad-max"

# Recruiting policy
curl -s --header "X-Vault-Token: $BAO_TOKEN" \
  --request PUT \
  --data '{
    "policy": "path \"transit/encrypt/recruiting\" { capabilities = [\"update\"] }\npath \"transit/decrypt/recruiting\" { capabilities = [\"update\"] }\npath \"transit/encrypt/shared\" { capabilities = [\"update\"] }\npath \"transit/decrypt/shared\" { capabilities = [\"update\"] }\npath \"secret/data/recruiting/*\" { capabilities = [\"create\",\"read\",\"update\",\"delete\"] }\npath \"secret/data/shared/*\" { capabilities = [\"read\"] }"
  }' \
  "$BAO_ADDR/v1/sys/policies/acl/recruiting" > /dev/null
echo "    Policy: recruiting"

# Life Coach policy
curl -s --header "X-Vault-Token: $BAO_TOKEN" \
  --request PUT \
  --data '{
    "policy": "path \"transit/encrypt/life-coach\" { capabilities = [\"update\"] }\npath \"transit/decrypt/life-coach\" { capabilities = [\"update\"] }\npath \"transit/encrypt/shared\" { capabilities = [\"update\"] }\npath \"transit/decrypt/shared\" { capabilities = [\"update\"] }\npath \"secret/data/life-coach/*\" { capabilities = [\"create\",\"read\",\"update\",\"delete\"] }\npath \"secret/data/shared/*\" { capabilities = [\"read\"] }"
  }' \
  "$BAO_ADDR/v1/sys/policies/acl/life-coach" > /dev/null
echo "    Policy: life-coach"

echo ""
echo "==> Creating coach tokens..."
for COACH in mad-max recruiting life-coach; do
  TOKEN_RESP=$(curl -s --header "X-Vault-Token: $BAO_TOKEN" \
    --request POST \
    --data "{\"policies\":[\"$COACH\"],\"display_name\":\"$COACH\",\"no_parent\":true}" \
    "$BAO_ADDR/v1/auth/token/create")
  TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['auth']['client_token'])")
  echo "    $COACH token: $TOKEN"
  # Store each coach token back in vault under secret/tokens/
  curl -s --header "X-Vault-Token: $BAO_TOKEN" \
    --request POST \
    --data "{\"data\":{\"token\":\"$TOKEN\"}}" \
    "$BAO_ADDR/v1/secret/data/tokens/$COACH" > /dev/null
  echo "    Stored at: secret/data/tokens/$COACH"
done

echo ""
echo "==> Setup complete!"
echo "    Transit keys: mad-max, recruiting, life-coach, shared"
echo "    Policies: mad-max, recruiting, life-coach"
echo "    Tokens stored in vault at secret/data/tokens/<coach>"
echo ""
echo "    Retrieve a coach token:"
echo "    ./get-secret.sh tokens/mad-max token"
