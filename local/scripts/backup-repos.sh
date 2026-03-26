#!/bin/bash
# backup-repos.sh — mirror ~/Work/ to Pi (full git history included)
#
# Recovery: git clone pi@[PI_IP]:~/backup/mini/work/[repo]
#
# SETUP (one-time):
#   1. Get Pi IP: PI_IP=$(cat ~/Work/test/local/scripts/pi-ip.txt)
#   2. Copy SSH key to Pi: ssh-copy-id pi@[PI_IP]
#   3. Store Pi IP: echo "[PI_IP]" > ~/Work/test/local/scripts/pi-ip.txt
#
# Cron (installed by launchd — see com.dakotaops.backup.plist):
#   Runs nightly at 2am

set -euo pipefail

LOGFILE="$HOME/Work/test/local/scripts/backup-repos.log"
PI_IP_FILE="$HOME/Work/test/local/scripts/pi-ip.txt"
BACKUP_DEST="~/backup/mini"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"; }

# ── Load Pi IP ─────────────────────────────────────────────────────────────────
if [[ ! -f "$PI_IP_FILE" ]]; then
  log "ERROR: Pi IP not configured — create $PI_IP_FILE with the Pi's IP address"
  exit 1
fi
PI_IP=$(cat "$PI_IP_FILE" | tr -d '[:space:]')
PI_HOST="pi@${PI_IP}"

# ── Verify Pi reachable ────────────────────────────────────────────────────────
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$PI_HOST" true 2>/dev/null; then
  log "ERROR: Pi unreachable at $PI_IP — skipping backup"
  exit 1
fi

# ── Sync ~/Work/ (includes .git dirs = full history) ──────────────────────────
log "Starting backup to $PI_HOST:$BACKUP_DEST/work/"

rsync -az \
  --delete \
  --exclude='*.log' \
  --exclude='*.err' \
  --exclude='local/openbao/data/' \
  --exclude='local/open-webui/data/' \
  --exclude='local/n8n/data/' \
  --exclude='__pycache__/' \
  --exclude='.DS_Store' \
  -e "ssh -o BatchMode=yes" \
  "$HOME/Work/" \
  "$PI_HOST:$BACKUP_DEST/work/"

log "Backup complete"

# ── Summary ───────────────────────────────────────────────────────────────────
REPOS=$(find "$HOME/Work" -maxdepth 2 -name ".git" -type d | wc -l | tr -d ' ')
log "Repos mirrored: $REPOS"
