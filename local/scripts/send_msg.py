#!/usr/bin/env python3
"""
send_msg.py — rate-limited iMessage sender for Mad Max

Usage:
    python3 send_msg.py <recipient> <message>
    python3 send_msg.py --stats          # show recent send history

Rate limits:
    - Max 2 messages per recipient per hour
    - Max 5 messages total (all recipients) per hour
    - Raises on violation — caller must handle

State file: ~/Work/test/local/scripts/outbound-msg-state.jsonl
"""

import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path.home() / "Work/test/local/scripts/outbound-msg-state.jsonl"
LIVE_FLAG   = Path.home() / "Work/test/local/scripts/livechat.flag"

# Default (bot mode)
MAX_PER_RECIPIENT_HOUR = 2
MAX_GLOBAL_HOUR = 5

# Live chat mode
LIVE_PER_RECIPIENT_HOUR = 20
LIVE_GLOBAL_HOUR = 40
LIVE_SESSION_MINUTES = 60  # flag expires after this


def now_ts():
    return datetime.now(timezone.utc).timestamp()


def load_recent(window_seconds=3600):
    if not STATE_FILE.exists():
        return []
    cutoff = now_ts() - window_seconds
    recent = []
    for line in STATE_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if entry["ts"] >= cutoff:
                recent.append(entry)
        except Exception:
            pass
    return recent


def is_live_mode():
    if not LIVE_FLAG.exists():
        return False
    age = now_ts() - LIVE_FLAG.stat().st_mtime
    if age > LIVE_SESSION_MINUTES * 60:
        LIVE_FLAG.unlink()
        return False
    return True


def check_rate(recipient):
    live = is_live_mode()
    per_r = LIVE_PER_RECIPIENT_HOUR if live else MAX_PER_RECIPIENT_HOUR
    global_max = LIVE_GLOBAL_HOUR if live else MAX_GLOBAL_HOUR

    recent = load_recent()
    global_count = len(recent)
    recipient_count = sum(1 for e in recent if e["recipient"] == recipient)

    mode_label = "LIVE" if live else "bot"
    if global_count >= global_max:
        raise RuntimeError(
            f"[{mode_label}] Global rate limit: {global_count}/{global_max} messages in last hour."
        )
    if recipient_count >= per_r:
        raise RuntimeError(
            f"[{mode_label}] Per-recipient limit: {recipient_count}/{per_r} to {recipient} in last hour."
        )


def log_send(recipient, message):
    entry = {
        "ts": now_ts(),
        "recipient": recipient,
        "preview": message[:80],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    STATE_FILE.parent.mkdir(exist_ok=True)
    with STATE_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def send(recipient, message):
    check_rate(recipient)
    escaped = message.replace('\\', '\\\\').replace('"', '\\"')
    script = (
        f'tell application "Messages"\n'
        f'  set targetService to 1st service whose service type = iMessage\n'
        f'  set targetBuddy to buddy "{escaped}" of targetService\n'
        f'  send "{escaped}" to targetBuddy\n'
        f'end tell'
    )
    # Fix: buddy should be recipient, message should be message
    escaped_recipient = recipient.replace('\\', '\\\\').replace('"', '\\"')
    escaped_message = message.replace('\\', '\\\\').replace('"', '\\"')
    script = (
        f'tell application "Messages"\n'
        f'  set targetService to 1st service whose service type = iMessage\n'
        f'  set targetBuddy to buddy "{escaped_recipient}" of targetService\n'
        f'  send "{escaped_message}" to targetBuddy\n'
        f'end tell'
    )
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"osascript failed: {result.stderr.strip()}")
    log_send(recipient, message)
    print(f"[send_msg] sent to {recipient}: {message[:60]}...")


def send_group(chat_id_keychain, message):
    """Send to a group chat via keychain chat ID. Counts as one global send."""
    check_rate(f"group:{chat_id_keychain}")
    result = subprocess.run(
        ['security', 'find-generic-password', '-a', 'macBot', '-s', chat_id_keychain, '-w'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Keychain key not found: {chat_id_keychain}")
    chat_id = result.stdout.strip()
    escaped = message.replace('\\', '\\\\').replace('"', '\\"')
    script = (
        f'tell application "Messages"\n'
        f'  send "{escaped}" to chat id "{chat_id}"\n'
        f'end tell'
    )
    res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"osascript failed: {res.stderr.strip()}")
    log_send(f"group:{chat_id_keychain}", message)
    print(f"[send_msg] sent to group {chat_id_keychain}: {message[:60]}...")


def stats():
    live = is_live_mode()
    global_max = LIVE_GLOBAL_HOUR if live else MAX_GLOBAL_HOUR
    mode = "LIVE" if live else "bot"
    recent = load_recent()
    all_entries = load_recent(window_seconds=86400)
    print(f"Mode: {mode}")
    print(f"Last hour: {len(recent)}/{global_max} global")
    if recent:
        from collections import Counter
        counts = Counter(e["recipient"] for e in recent)
        for r, c in counts.most_common():
            print(f"  {r}: {c}/{MAX_PER_RECIPIENT_HOUR}")
    print(f"\nLast 24h: {len(all_entries)} total")
    for e in all_entries[-10:]:
        print(f"  [{e['time']}] {e['recipient']}: {e['preview']}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--stats":
        stats()
    elif len(sys.argv) == 2 and sys.argv[1] == "--live":
        LIVE_FLAG.touch()
        print(f"[send_msg] LIVE MODE ON — {LIVE_PER_RECIPIENT_HOUR}/recipient, {LIVE_GLOBAL_HOUR}/hr global. Expires in {LIVE_SESSION_MINUTES}min.")
    elif len(sys.argv) == 2 and sys.argv[1] == "--endlive":
        if LIVE_FLAG.exists():
            LIVE_FLAG.unlink()
        print("[send_msg] live mode off — back to bot limits")
    elif len(sys.argv) >= 3:
        recipient = sys.argv[1]
        message = " ".join(sys.argv[2:])
        try:
            send(recipient, message)
        except RuntimeError as e:
            print(f"[send_msg] BLOCKED: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: send_msg.py <recipient> <message>")
        print("       send_msg.py --stats")
        sys.exit(1)
