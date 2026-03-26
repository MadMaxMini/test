#!/bin/bash
# notify.sh — send iMessage to Rod direct
# Uses notify-recipient from Keychain, sends via Messages.app directly.
# Usage: notify.sh "message here"

MESSAGE="${1:-ping from mini}"
RECIPIENT=$(security find-generic-password -a macBot -s "notify-recipient" -w 2>/dev/null)

if [ -z "$RECIPIENT" ]; then
  echo "notify: could not get recipient from Keychain" >&2
  exit 1
fi

MSG_ESCAPED="${MESSAGE//\\/\\\\}"
MSG_ESCAPED="${MSG_ESCAPED//\"/\\\"}"

osascript << APPLESCRIPT
tell application "Messages"
  set s to 1st service whose service type = iMessage
  set b to buddy "${RECIPIENT}" of s
  send "${MSG_ESCAPED}" to b
end tell
APPLESCRIPT
