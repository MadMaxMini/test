#!/bin/bash
# poll-inbox.sh — watch bottleMsg for command files, dispatch, notify back
# Command files: any cmd*.txt in bottleMsg/
# Format: first line is the command, rest is ignored

INBOX="$HOME/Library/CloudStorage/Dropbox/bottleMsg"
ARCHIVE="$INBOX/archive"
SCRIPTS="$HOME/Work/test/local/scripts"
LOG="$HOME/Work/test/local/scripts/inbox.log"

mkdir -p "$ARCHIVE"

for cmd_file in "$INBOX"/*.txt; do
  [[ -f "$cmd_file" ]] || continue

  CMD=$(head -1 "$cmd_file" | tr '[:upper:]' '[:lower:]' | xargs)
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

  echo "[$TIMESTAMP] received: $CMD" >> "$LOG"

  case "$CMD" in
    status)
      OLLAMA=$(curl -s http://127.0.0.1:11434/api/tags | python3 -c \
        "import sys,json; d=json.load(sys.stdin); m=[x['name'] for x in d.get('models',[])]; print('models: '+(','.join(m) if m else 'none'))" 2>/dev/null || echo "ollama: down")
      DOCKER=$(docker ps --format "{{.Names}}" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "docker: down")
      BAO=$(curl -s http://127.0.0.1:8200/v1/sys/health 2>/dev/null | python3 -c \
        "import sys,json; d=json.load(sys.stdin); print('vault: '+ ('sealed' if d.get('sealed') else 'open'))" 2>/dev/null || echo "vault: down")
      "$SCRIPTS/notify.sh" "status: $OLLAMA | $BAO | docker: ${DOCKER:-none}"
      ;;

    unseal)
      bash "$HOME/Work/local/openbao/scripts/unseal-keychain.sh" >> "$LOG" 2>&1
      "$SCRIPTS/notify.sh" "unseal attempted — check vault status"
      ;;

    pull\ *)
      MODEL="${CMD#pull }"
      "$SCRIPTS/notify.sh" "pulling $MODEL..."
      ollama pull "$MODEL" >> "$LOG" 2>&1 && \
        "$SCRIPTS/notify.sh" "$MODEL ready" || \
        "$SCRIPTS/notify.sh" "pull failed: $MODEL"
      ;;

    ping)
      "$SCRIPTS/notify.sh" "pong"
      ;;

    *)
      FNAME=$(basename "$cmd_file")
      echo "[$TIMESTAMP] REJECTED: unknown command '$CMD' from $FNAME — ignoring" >> "$LOG"
      "$SCRIPTS/notify.sh" "inbox: unknown command '$CMD' ignored. Use: ping, status, pull <model>, unseal"
      ;;
  esac

  # archive processed file
  mv "$cmd_file" "$ARCHIVE/$(date +%Y%m%d-%H%M%S)-$(basename "$cmd_file")"
done
