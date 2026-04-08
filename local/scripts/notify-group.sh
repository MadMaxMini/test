#!/bin/bash
# notify-group.sh — send iMessage to Dakota group
# Uses imessage-group-dakota chat ID from Keychain.
# Usage: notify-group.sh "message here"

MESSAGE="${1:-ping from mini}"
CHAT_ID=$(security find-generic-password -a macBot -s "imessage-group-dakota" -w 2>/dev/null)

if [ -z "$CHAT_ID" ]; then
  echo "notify-group: could not get chat ID from Keychain" >&2
  exit 1
fi

MSG_ESCAPED="${MESSAGE//\\/\\\\}"
MSG_ESCAPED="${MSG_ESCAPED//\"/\\\"}"

osascript << APPLESCRIPT
tell application "Messages"
  send "${MSG_ESCAPED}" to chat id "${CHAT_ID}"
end tell
APPLESCRIPT
