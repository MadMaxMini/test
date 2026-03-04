#!/usr/bin/env bash
# Create the coach workspace and mailbox folder structure
# Run once after setup-transit.sh

set -euo pipefail

BASE="$HOME/Work/madmax"

# If still named 'test', use that
if [ ! -d "$BASE" ] && [ -d "$HOME/Work/test" ]; then
  BASE="$HOME/Work/test"
fi

echo "==> Creating coach workspace and mailbox structure..."
echo "    Base: $BASE"
echo ""

COACHES=("mad-max" "recruiting" "life-coach")

for COACH in "${COACHES[@]}"; do
  mkdir -p "$BASE/coaches/$COACH/workspace"
  mkdir -p "$BASE/coaches/$COACH/inbox"
  mkdir -p "$BASE/coaches/$COACH/outbox"
  echo "    coaches/$COACH/ — workspace, inbox, outbox"
done

# Shared assets
mkdir -p "$BASE/shared/assets"
mkdir -p "$BASE/shared/inbox"
echo "    shared/ — assets, inbox"

# Add gitignore for workspace contents (encrypted files only, no plaintext)
cat > "$BASE/coaches/.gitignore" << 'EOF'
# Never commit plaintext workspace contents
*/workspace/*.plaintext
*/workspace/*.tmp
EOF

echo ""
echo "==> Mailbox structure ready!"
echo ""
echo "    To send mail to a coach:"
echo "    echo 'message' > $BASE/coaches/recruiting/inbox/\$(date +%Y-%m-%dT%H:%M)-from-mad-max-re-topic.md"
