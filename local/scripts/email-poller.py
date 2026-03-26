#!/usr/bin/env python3
# email-poller.py — Gmail IMAP poller
#
# Polls Gmail inbox, logs new emails to email-inbox.md, notifies Rod via text.
# Credentials stored in macOS Keychain (never in files).
#
# SETUP (run once when you have the app password):
#   security add-generic-password -a macBot -s email-poller-gmail-user -w "macbotpooterson@gmail.com"
#   security add-generic-password -a macBot -s email-poller-gmail-pass -w "YOUR_APP_PASSWORD"
#
# App password: Google Account → Security → 2-Step Verification → App Passwords
#
# Usage:
#   python3 email-poller.py          # run as daemon (launchd)
#   python3 email-poller.py --once   # single poll (testing)
#   python3 email-poller.py --check  # verify credentials only

import imaplib
import email
import email.header
import subprocess
import sys
import time
import re
import logging
from pathlib import Path
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
HOME          = Path.home()
STATE_FILE    = HOME / "Work/test/local/scripts/email-poller.state"
LOG_FILE      = HOME / "Work/test/local/scripts/email-poller.log"
INBOX_FILE    = HOME / "Work/test/local/scripts/email-inbox.md"
NOTIFY_SCRIPT = HOME / "Work/test/local/scripts/notify.sh"

ROD_EMAILS    = ["roderick.clemente@protonmail.com", "rjclemente"]  # Rod's known addresses

IMAP_HOST     = "imap.gmail.com"
IMAP_PORT     = 993
POLL_INTERVAL = 300   # 5 minutes
MAX_BODY_LEN  = 300   # chars of body to log

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=str(LOG_FILE), level=logging.INFO,
    format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
def log(msg): logging.info(msg)

# ── OpenBao ────────────────────────────────────────────────────────────────────
BAO_ADDR = "http://127.0.0.1:8200"

def bao_token():
    import subprocess
    r = subprocess.run(
        ["security", "find-generic-password", "-a", "macBot", "-s", "openbao-root-token", "-w"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return None
    return r.stdout.strip()

def load_creds():
    import urllib.request, json as _json
    token = bao_token()
    if not token:
        log("[email-poller] ERROR: openbao-root-token not in Keychain")
        sys.exit(1)
    req = urllib.request.Request(
        f"{BAO_ADDR}/v1/secret/data/email/gmail",
        headers={"X-Vault-Token": token}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = _json.loads(resp.read())["data"]["data"]
            return data["username"], data["password"]
    except Exception as e:
        log(f"[email-poller] ERROR: could not read credentials from OpenBao — {e}")
        log("[email-poller] Is OpenBao running and unsealed?")
        sys.exit(1)

# ── State ──────────────────────────────────────────────────────────────────────
def get_last_uid():
    try:    return int(STATE_FILE.read_text().strip())
    except: return 0

def save_last_uid(uid):
    STATE_FILE.write_text(str(uid))

# ── Notify (one text per batch, not per email) ─────────────────────────────────
def notify(msg):
    try:
        subprocess.run([str(NOTIFY_SCRIPT), msg], capture_output=True, timeout=10)
    except Exception as e:
        log(f"[email-poller] notify error: {e}")

# ── Inbox log ──────────────────────────────────────────────────────────────────
def log_to_inbox(uid, sender, subject, snippet):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not INBOX_FILE.exists():
        INBOX_FILE.write_text(
            "# email-inbox — Gmail poller (macbotpooterson@gmail.com)\n"
            "# Reviewed at each /mad-max session start. Delete entries after review.\n\n"
        )
    with open(INBOX_FILE, "a") as f:
        f.write(f"- [{ts}] uid={uid} | {sender} | {subject}\n  {snippet}\n")
    log(f"[email-poller] logged uid={uid} from={sender} subject={subject}")

# ── Header decode ──────────────────────────────────────────────────────────────
def decode_header_val(value):
    if not value:
        return ""
    parts = email.header.decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(str(part))
    return " ".join(decoded).strip()

# ── Body extract ───────────────────────────────────────────────────────────────
def extract_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    break
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
        except Exception:
            pass

    # Strip quoted reply lines (> prefix), collapse whitespace
    lines = [l for l in body.splitlines() if not l.startswith(">")]
    body = " ".join(" ".join(lines).split())
    return body[:MAX_BODY_LEN]

# ── Sanitize ───────────────────────────────────────────────────────────────────
def sanitize(text, maxlen=100):
    text = re.sub(r"[`$;&|]", "", (text or ""))
    return text[:maxlen]

# ── Poll ───────────────────────────────────────────────────────────────────────
def poll_once(user, pw):
    last_uid = get_last_uid()

    try:
        conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        conn.login(user, pw)
        conn.select("INBOX", readonly=True)
    except Exception as e:
        log(f"[email-poller] IMAP connect error: {e}")
        return

    try:
        # Search UIDs > last seen (readonly — never marks as read)
        criterion = f"UID {last_uid + 1}:*" if last_uid > 0 else "ALL"
        status, data = conn.uid("SEARCH", None, criterion)
        if status != "OK" or not data[0]:
            conn.logout()
            return

        raw_uids = data[0].split()
        new_uids = [int(u) for u in raw_uids if int(u) > last_uid]
        if not new_uids:
            conn.logout()
            return

        log(f"[email-poller] {len(new_uids)} new email(s)")
        max_uid = last_uid
        first_sender = ""
        first_subject = ""

        for uid in new_uids:
            try:
                status, data = conn.uid("FETCH", str(uid), "(RFC822)")
                if status != "OK" or not data or not data[0]:
                    continue

                raw = data[0][1]
                msg = email.message_from_bytes(raw)

                sender  = sanitize(decode_header_val(msg.get("From", "unknown")))
                subject = sanitize(decode_header_val(msg.get("Subject", "(no subject)")))
                to_addr = decode_header_val(msg.get("To", ""))
                snippet = sanitize(extract_body(msg), maxlen=MAX_BODY_LEN)

                # Only process emails addressed to @dakotaentllc.com
                if "@dakotaentllc.com" not in to_addr.lower():
                    log(f"[email-poller] skip uid={uid} (not to dakotaentllc.com — to: {to_addr[:60]})")
                    if uid > max_uid:
                        max_uid = uid
                    continue

                log_to_inbox(uid, sender, subject, snippet)

                # If email is from Rod → dispatch as command
                if any(addr in sender.lower() for addr in ROD_EMAILS):
                    import sys as _sys
                    _sys.path.insert(0, str(HOME / "Work/test/local/scripts"))
                    from dispatcher import dispatch
                    msg_body = f"Subject: {subject}\n\n{snippet}"
                    dispatch(msg_body, notify, context="email")

                if not first_sender:
                    first_sender  = sender
                    first_subject = subject

                if uid > max_uid:
                    max_uid = uid

            except Exception as e:
                log(f"[email-poller] error processing uid {uid}: {e}")

        save_last_uid(max_uid)

        # One batch notify (not per-email)
        count = len(new_uids)
        if count == 1:
            notify(f"📧 1 new email — {first_sender[:40]}: {first_subject[:50]}")
        else:
            notify(f"📧 {count} new emails — latest: {first_sender[:30]}: {first_subject[:40]}")

    except Exception as e:
        log(f"[email-poller] poll error: {e}")
    finally:
        try: conn.logout()
        except: pass

# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--check" in sys.argv:
        user, pw = load_creds()
        print(f"Credentials found for: {user}")
        print("Testing IMAP connection...")
        try:
            conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
            conn.login(user, pw)
            conn.select("INBOX", readonly=True)
            status, data = conn.uid("SEARCH", None, "ALL")
            count = len(data[0].split()) if data[0] else 0
            conn.logout()
            print(f"Connected. {count} emails in INBOX.")
        except Exception as e:
            print(f"Connection failed: {e}")
            sys.exit(1)
        sys.exit(0)

    user, pw = load_creds()
    log(f"[email-poller] started — polling every {POLL_INTERVAL}s as {user}")

    if "--once" in sys.argv:
        poll_once(user, pw)
        sys.exit(0)

    while True:
        try:
            poll_once(user, pw)
        except Exception as e:
            log(f"[email-poller] outer error: {e}")
        time.sleep(POLL_INTERVAL)
