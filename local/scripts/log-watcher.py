#!/usr/bin/env python3
# log-watcher.py — tail msggateway.log, dispatch unknown admin commands to Claude
#
# The C gateway (msggateway_bin) has FDA and reads chat.db. It logs:
#   [msggateway] unknown admin command: <body>
# This watcher picks those up and passes them to dispatcher.py.
#
# No FDA needed — reads a log file, not chat.db.
# Runs as a launchd agent alongside msggateway_bin.

import sys
import time
import re
import logging
from pathlib import Path

HOME        = Path.home()
WATCH_FILE  = HOME / "Work/test/local/scripts/msggateway.log"
STATE_FILE  = HOME / "Work/test/local/scripts/log-watcher.state"
LOG_FILE    = HOME / "Work/test/local/scripts/log-watcher.log"
NOTIFY_SCRIPT = HOME / "Work/test/local/scripts/notify.sh"

logging.basicConfig(
    filename=str(LOG_FILE), level=logging.INFO,
    format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
def log(msg): logging.info(msg)

PATTERN = re.compile(r"\[msggateway\] unknown admin command.*?: (.+)$")

def notify(msg):
    import subprocess
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", "macBot", "-s", "notify-recipient", "-w"],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            log(f"[log-watcher] notify: could not get recipient from Keychain")
            return
        recipient = r.stdout.strip()
        msg_escaped = msg.replace('\\', '\\\\').replace('"', '\\"')
        script = (
            f'tell application "Messages"\n'
            f'  set s to 1st service whose service type = iMessage\n'
            f'  set b to buddy "{recipient}" of s\n'
            f'  send "{msg_escaped}" to b\n'
            f'end tell'
        )
        r = subprocess.run(["osascript", "-e", script], capture_output=True, timeout=15)
        log(f"[log-watcher] sent: {msg[:60]}")
    except Exception as e:
        log(f"[log-watcher] notify error: {e}")

def get_offset():
    try:    return int(STATE_FILE.read_text().strip())
    except: return 0

def save_offset(n):
    STATE_FILE.write_text(str(n))

def poll_once():
    sys.path.insert(0, str(HOME / "Work/test/local/scripts"))
    from dispatcher import dispatch

    if not WATCH_FILE.exists():
        return

    current_size = WATCH_FILE.stat().st_size
    offset = get_offset()

    # Handle log rotation / truncation
    if current_size < offset:
        offset = 0

    if current_size == offset:
        return

    with open(WATCH_FILE, "r", errors="replace") as f:
        f.seek(offset)
        new_lines = f.readlines()
        new_offset = f.tell()

    save_offset(new_offset)

    for line in new_lines:
        m = PATTERN.search(line.strip())
        if m:
            body = m.group(1).strip()
            log(f"[log-watcher] dispatching: {body[:100]}")
            dispatch(body, notify, context="text")

if __name__ == "__main__":
    log("[log-watcher] started")
    # Initialize offset to current end of file (don't replay old logs)
    if not STATE_FILE.exists() and WATCH_FILE.exists():
        save_offset(WATCH_FILE.stat().st_size)

    while True:
        try:
            poll_once()
        except Exception as e:
            log(f"[log-watcher] error: {e}")
        time.sleep(15)
