#!/usr/bin/env python3
# msggateway.py — iMessage receive gateway (Phase 3.5)
#
# Python port of msggateway.sh — runs as the launchd process directly
# so FDA is attributed to python3, not to bash or Terminal.
#
# REQUIRES: Full Disk Access for /opt/homebrew/bin/python3
#   System Settings → Privacy & Security → Full Disk Access → add python3
#
# Usage: python3 msggateway.py [--once]

import sqlite3 as sq
import subprocess
import os
import sys
import time
import re
import logging
from pathlib import Path
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
HOME         = Path.home()
CHAT_DB      = HOME / "Library/Messages/chat.db"
STATE_FILE   = HOME / "Work/test/local/scripts/msggateway.state"
LOG_FILE     = HOME / "Work/test/local/scripts/msggateway.log"
INBOX_FILE   = HOME / "Work/test/local/scripts/msggateway-inbox.md"
NOTIFY_SCRIPT = HOME / "Work/test/local/scripts/notify.sh"
MAX_MSG_LEN  = 500
MAX_PER_HOUR = 20
POLL_INTERVAL = 30

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(filename=str(LOG_FILE), level=logging.INFO, format="%(message)s")
def log(msg): logging.info(msg)

# ── FDA check ──────────────────────────────────────────────────────────────────
def check_fda():
    try:
        conn = sq.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
        conn.execute("SELECT count(*) FROM message LIMIT 1").fetchone()
        conn.close()
    except Exception as e:
        log(f"[msggateway] ERROR: No Full Disk Access — {e}")
        log("[msggateway] Fix: System Settings → Privacy & Security → Full Disk Access → add python3")
        sys.exit(1)

# ── Keychain ───────────────────────────────────────────────────────────────────
def load_keychain(service):
    r = subprocess.run(
        ["security", "find-generic-password", "-a", "macBot", "-s", service, "-w"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return []
    return [x.strip() for x in r.stdout.strip().split(",") if x.strip()]

def is_admin(sender):  return sender in load_keychain("msggateway-admin")
def is_monitor(sender): return sender in load_keychain("msggateway-monitor")

# ── State ──────────────────────────────────────────────────────────────────────
def get_last_rowid():
    try:    return int(STATE_FILE.read_text().strip())
    except: return 0

def save_last_rowid(rowid):
    STATE_FILE.write_text(str(rowid))

# ── Rate limiting ──────────────────────────────────────────────────────────────
def rate_ok(sender):
    safe = re.sub(r"[^a-zA-Z0-9]", "", sender)
    rate_file = Path(f"/tmp/msggateway_rate_{safe}")
    now = int(time.time())
    cutoff = now - 3600

    timestamps = []
    if rate_file.exists():
        for line in rate_file.read_text().splitlines():
            try:
                ts = int(line.strip())
                if ts > cutoff:
                    timestamps.append(ts)
            except: pass

    if len(timestamps) >= MAX_PER_HOUR:
        log(f"[msggateway] rate limit hit for {sender} ({len(timestamps)}/{MAX_PER_HOUR}/hr)")
        return False

    timestamps.append(now)
    rate_file.write_text("\n".join(str(t) for t in timestamps))
    return True

# ── Attributed body decoder ────────────────────────────────────────────────────
def decode_attributed_body(data):
    """Extract plain text from iMessage typedstream attributed body."""
    if not data:
        return ""
    try:
        raw = data.decode("utf-8", errors="replace")
        chunks = re.findall(r"[\x20-\x7e]{4,}", raw)
        skip = {"streamtyped", "NSAttributedString", "NSMutableString",
                "NSObject", "NSDictionary", "__kIMMessagePartAttributeName",
                "NSColor", "NSFont", "NSParagraphStyle"}
        parts = [c for c in chunks if c not in skip and not c.startswith("$") and len(c) > 3]
        return " ".join(parts) if parts else ""
    except Exception:
        return ""

def get_body(text, attributed_body):
    if text and text.strip():
        return text.strip()
    return decode_attributed_body(attributed_body)

# ── Sanitize ───────────────────────────────────────────────────────────────────
def sanitize(text):
    text = (text or "")[:MAX_MSG_LEN]
    text = re.sub(r"[`$;&|]", "", text)
    text = text.replace("../", "")
    return text

# ── Notify (Rod direct via notify.sh → AutoDakota_Notify_Rod) ─────────────────
def notify(msg):
    try:
        subprocess.run([str(NOTIFY_SCRIPT), msg], capture_output=True, timeout=10)
    except Exception as e:
        log(f"[msggateway] notify error: {e}")

# ── Monitor inbox ──────────────────────────────────────────────────────────────
def log_to_inbox(sender, body, prefix=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not INBOX_FILE.exists():
        INBOX_FILE.write_text(
            "# msggateway inbox — texts from monitored contacts\n"
            "# Reviewed at each /mad-max session start. Delete entries after review.\n\n"
        )
    label = f"{prefix} {ts}" if prefix else ts
    with open(INBOX_FILE, "a") as f:
        f.write(f"- [{label}] {sender}: {body}\n")
    log(f"[msggateway] inbox: {sender}: {body}")

# ── Admin dispatch ─────────────────────────────────────────────────────────────
def dispatch_admin(sender, body):
    sys.path.insert(0, str(Path(__file__).parent))
    from dispatcher import dispatch
    dispatch(body, notify, context="text")

# ── Poll ───────────────────────────────────────────────────────────────────────
SHUTDOWN_FLAG = Path("/tmp/msggateway_shutdown")

def poll_once():
    if SHUTDOWN_FLAG.exists():
        return  # silenced until flag removed
    last_rowid = get_last_rowid()

    try:
        conn = sq.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
        rows = conn.execute("""
            SELECT m.ROWID, h.id, m.text, m.attributedBody
            FROM message m
            JOIN handle h ON m.handle_id = h.ROWID
            WHERE m.ROWID > ?
              AND m.is_from_me = 0
              AND m.cache_roomnames IS NULL
              AND (m.text IS NOT NULL AND m.text != '' OR m.attributedBody IS NOT NULL)
            ORDER BY m.ROWID ASC
        """, (last_rowid,)).fetchall()
        conn.close()
    except Exception as e:
        log(f"[msggateway] db error: {e}")
        return

    if not rows:
        return

    max_seen = last_rowid
    for rowid, sender, raw_text, attributed_body in rows:
        if rowid > max_seen:
            max_seen = rowid

        body = get_body(raw_text, attributed_body)
        if not body:
            save_last_rowid(rowid)
            continue
        clean = sanitize(body)

        if is_admin(sender):
            if rate_ok(sender):
                log(f"[msggateway] admin command from {sender}: {clean}")
                dispatch_admin(sender, clean)
        elif is_monitor(sender):
            log_to_inbox(sender, clean)
        else:
            log(f"[msggateway] SUSPICIOUS: unknown sender {sender} — {clean}")
            log_to_inbox(sender, clean, prefix="SUSPICIOUS")
            notify(f"⚠️ UNKNOWN contact on mini: {sender} said: \"{clean[:100]}\" — not in any tier.")

    save_last_rowid(max_seen)

# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    check_fda()

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        poll_once()
        sys.exit(0)

    log(f"[msggateway] python gateway started — polling every {POLL_INTERVAL}s")
    while True:
        try:
            poll_once()
        except Exception as e:
            log(f"[msggateway] poll error: {e}")
        time.sleep(POLL_INTERVAL)
