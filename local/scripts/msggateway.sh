#!/bin/bash
# msggateway.sh — iMessage receive gateway (Phase 3.5)
#
# REQUIRES: Full Disk Access for Terminal
#   System Settings → Privacy & Security → Full Disk Access → add Terminal
#
# Two modes per sender:
#   Admin  (Keychain: msggateway-admin)   → execute commands, get replies
#   Monitor (Keychain: msggateway-monitor) → logged to inbox for Rod review, no reply
#   Unknown → silently ignored
#
# Run via launchd (see com.dakotaops.msggateway.plist).
# Never run as root. Read-only access to chat.db.
#
# Usage: ./msggateway.sh [--once]   (--once for testing a single poll)
#
# Keychain setup:
#   security add-generic-password -a macBot -s "msggateway-admin"   -w "+17373288018"
#   security add-generic-password -a macBot -s "msggateway-monitor" -w "+15551111111,+15552222222"

set -euo pipefail

CHAT_DB="$HOME/Library/Messages/chat.db"
STATE_FILE="$HOME/Work/test/local/scripts/msggateway.state"
LOG_FILE="$HOME/Work/test/local/scripts/msggateway.log"
INBOX_FILE="$HOME/Work/test/local/scripts/msggateway-inbox.md"
NOTIFY_SCRIPT="$HOME/Work/test/local/scripts/notify.sh"
MAX_MSG_LEN=500
MAX_PER_HOUR=20
POLL_INTERVAL=30

# ── Keychain loaders ──────────────────────────────────────────────────────────
load_admin() {
    security find-generic-password -a macBot -s "msggateway-admin" -w 2>/dev/null \
        | tr ',' '\n' | sed 's/[[:space:]]//g'
}

load_monitor() {
    security find-generic-password -a macBot -s "msggateway-monitor" -w 2>/dev/null \
        | tr ',' '\n' | sed 's/[[:space:]]//g'
}

is_admin() {
    local sender="$1"
    load_admin | grep -qx "$sender"
}

is_monitor() {
    local sender="$1"
    load_monitor | grep -qx "$sender"
}

# ── FDA check ─────────────────────────────────────────────────────────────────
check_fda() {
    if ! sqlite3 "$CHAT_DB" "SELECT count(*) FROM message LIMIT 1;" >/dev/null 2>&1; then
        echo "[msggateway] ERROR: No Full Disk Access. System Settings → Privacy & Security → Full Disk Access → add Terminal." | tee -a "$LOG_FILE"
        exit 1
    fi
}

# ── State ─────────────────────────────────────────────────────────────────────
get_last_rowid() { cat "$STATE_FILE" 2>/dev/null || echo "0"; }
save_last_rowid() { echo "$1" > "$STATE_FILE"; }

# ── Rate limiting ─────────────────────────────────────────────────────────────
rate_ok() {
    local sender="$1"
    local safe_sender
    safe_sender=$(echo "$sender" | tr -dc '[:alnum:]')
    local rate_file="/tmp/msggateway_rate_${safe_sender}"
    local now
    now=$(date +%s)
    local count=0

    if [[ -f "$rate_file" ]]; then
        local cutoff=$((now - 3600))
        local fresh
        fresh=$(awk -v cutoff="$cutoff" '$1 > cutoff' "$rate_file" 2>/dev/null || true)
        echo "$fresh" > "$rate_file"
        count=$(wc -l < "$rate_file" | tr -d ' ')
    fi

    if [[ "$count" -ge "$MAX_PER_HOUR" ]]; then
        echo "[msggateway] rate limit hit for $sender ($count/$MAX_PER_HOUR/hr)" >> "$LOG_FILE"
        return 1
    fi

    echo "$now" >> "$rate_file"
    return 0
}

# ── Sanitize ──────────────────────────────────────────────────────────────────
sanitize() {
    local raw="${1:0:$MAX_MSG_LEN}"
    echo "$raw" | sed -e 's/[`$]//g' -e 's/[;&|]//g' -e 's/\.\.\///g'
}

# ── Monitor inbox ─────────────────────────────────────────────────────────────
log_to_inbox() {
    local sender="$1"
    local body="$2"
    local ts
    ts=$(date "+%Y-%m-%d %H:%M")

    # Create file with header if missing
    if [[ ! -f "$INBOX_FILE" ]]; then
        echo "# msggateway inbox — texts from monitored contacts" > "$INBOX_FILE"
        echo "# Reviewed at each /mad-max session start. Delete entries after review." >> "$INBOX_FILE"
        echo "" >> "$INBOX_FILE"
    fi

    echo "- [$ts] $sender: $body" >> "$INBOX_FILE"
    echo "[msggateway] monitor logged: $sender: $body" >> "$LOG_FILE"
}

# ── Admin dispatch ────────────────────────────────────────────────────────────
dispatch_admin() {
    local body="$1"
    local lower
    lower=$(echo "$body" | tr '[:upper:]' '[:lower:]')

    case "$lower" in
        ping)
            "$NOTIFY_SCRIPT" "pong — mini is alive" ;;
        status)
            local ollama_count docker_status
            ollama_count=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
            docker_status=$(docker ps --format "{{.Names}}" 2>/dev/null | tr '\n' ' ' || echo "docker not running")
            "$NOTIFY_SCRIPT" "mini status: ${ollama_count} ollama models. docker: ${docker_status}" ;;
        help | commands)
            "$NOTIFY_SCRIPT" "commands: ping, status, help, robot shutdown. More coming." ;;
        *robot*shutdown*)
            touch /tmp/msggateway_shutdown
            "$NOTIFY_SCRIPT" "Gateway silenced. Texts still logged. Delete /tmp/msggateway_shutdown to resume."
            echo "[msggateway] SHUTDOWN — silenced until flag removed" >> "$LOG_FILE" ;;
        *)
            echo "[msggateway] unknown admin command: $body" >> "$LOG_FILE" ;;
    esac
}

# ── Poll ──────────────────────────────────────────────────────────────────────
poll_once() {
    [[ -f /tmp/msggateway_shutdown ]] && return  # silenced until flag removed
    local last_rowid
    last_rowid=$(get_last_rowid)

    local new_messages
    new_messages=$(sqlite3 "$CHAT_DB" \
        "SELECT m.ROWID, h.id, m.text
         FROM message m
         JOIN handle h ON m.handle_id = h.ROWID
         WHERE m.ROWID > $last_rowid
           AND m.is_from_me = 0
           AND m.cache_roomnames IS NULL
           AND m.text IS NOT NULL
           AND m.text != ''
         ORDER BY m.ROWID ASC;" 2>/dev/null || true)

    [[ -z "$new_messages" ]] && return

    local max_seen="$last_rowid"

    while IFS='|' read -r rowid sender body; do
        # Skip lines that aren't proper records (e.g. newlines embedded in message body)
        [[ "$rowid" =~ ^[0-9]+$ ]] || continue
        [[ "$rowid" -gt "$max_seen" ]] && max_seen="$rowid"

        local clean
        clean=$(sanitize "$body")

        if is_admin "$sender"; then
            rate_ok "$sender" || continue
            echo "[msggateway] admin command from $sender: $clean" >> "$LOG_FILE"
            dispatch_admin "$clean"
        elif is_monitor "$sender"; then
            log_to_inbox "$sender" "$clean"
        else
            # Unknown sender — flag as suspicious, notify Rod immediately
        local ts
        ts=$(date "+%Y-%m-%d %H:%M")
        echo "[msggateway] SUSPICIOUS: unknown sender $sender — $clean" >> "$LOG_FILE"
        echo "- [SUSPICIOUS $ts] $sender: $clean" >> "$INBOX_FILE"
        "$NOTIFY_SCRIPT" "⚠️ UNKNOWN contact on mini: $sender said: \"$clean\" — not in any tier. Add to monitor or ignore."
        fi

    done <<< "$new_messages"

    save_last_rowid "$max_seen"
}

# ── Entry ─────────────────────────────────────────────────────────────────────
check_fda

if [[ "${1:-}" == "--once" ]]; then
    poll_once
    exit 0
fi

echo "[msggateway] started — polling every ${POLL_INTERVAL}s" >> "$LOG_FILE"
while true; do
    poll_once
    sleep "$POLL_INTERVAL"
done
