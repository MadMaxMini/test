#!/usr/bin/env python3
# email-poller.py — Gmail IMAP poller with smart triage + debounce
#
# Polls Gmail inbox, classifies emails (urgent/important/info/noise),
# notifies Rod via Telegram (Max bot) with debounce batching.
# Credentials stored in OpenBao (never in files).
#
# Usage:
#   python3 email-poller.py          # run as daemon (launchd)
#   python3 email-poller.py --once   # single poll (testing)
#   python3 email-poller.py --check  # verify credentials only
#   python3 email-poller.py --test-classify  # test classifier against last 10 emails

import imaplib
import email
import email.header
import subprocess
import sys
import time
import re
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from email_classifier import classify, format_single, format_batch

# ── Config ─────────────────────────────────────────────────────────────────────
HOME          = Path.home()
SCRIPTS_DIR   = HOME / "Work/local/scripts"
STATE_FILE    = SCRIPTS_DIR / "email-poller.state"
LOG_FILE      = SCRIPTS_DIR / "email-poller.log"
INBOX_FILE    = SCRIPTS_DIR / "email-inbox.md"
BATCH_FILE    = SCRIPTS_DIR / "email-batch.json"
NOTIFY_SCRIPT = SCRIPTS_DIR / "notify.sh"

ROD_EMAILS    = ["roderick.clemente@protonmail.com", "rjclemente"]

IMAP_HOST     = "imap.gmail.com"
IMAP_PORT     = 993
POLL_INTERVAL = 300    # 5 minutes
MAX_BODY_LEN  = 300    # chars of body to log
DEBOUNCE_SECS = 900    # 15 minutes — flush batch after this

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=str(LOG_FILE), level=logging.INFO,
    format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
def log(msg): logging.info(msg)

# ── OpenBao ────────────────────────────────────────────────────────────────────
BAO_ADDR = "http://127.0.0.1:8200"

def bao_token():
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

# ── Telegram notify (primary) ─────────────────────────────────────────────────

def keychain_get(service):
    r = subprocess.run(
        ["security", "find-generic-password", "-a", "macBot", "-s", service, "-w"],
        capture_output=True, text=True
    )
    return r.stdout.strip() or None

def tg_send(msg):
    """Send message via Mad Max Telegram bot. Falls back to iMessage on failure."""
    import urllib.request
    token = keychain_get("telegram-max-bot-token")
    chat_id = keychain_get("telegram-max-chat-id")
    if not token or not chat_id:
        log("[email-poller] Telegram creds missing, falling back to iMessage")
        imessage_notify(msg)
        return

    payload = json.dumps({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        log(f"[email-poller] Telegram notify sent ({len(msg)} chars)")
    except Exception as e:
        log(f"[email-poller] Telegram error: {e} — falling back to iMessage")
        # Strip markdown for iMessage fallback
        plain = re.sub(r'[*_`]', '', msg)
        imessage_notify(plain)

def imessage_notify(msg):
    """Fallback: send via notify.sh (iMessage to Rod)."""
    try:
        subprocess.run([str(NOTIFY_SCRIPT), msg], capture_output=True, timeout=10)
    except Exception as e:
        log(f"[email-poller] iMessage fallback error: {e}")

# ── Debounce batch ─────────────────────────────────────────────────────────────

def load_batch():
    """Load pending batch from disk."""
    if BATCH_FILE.exists():
        try:
            data = json.loads(BATCH_FILE.read_text())
            return data.get("items", []), data.get("started", 0)
        except Exception:
            pass
    return [], 0

def save_batch(items, started):
    """Save pending batch to disk."""
    BATCH_FILE.write_text(json.dumps({"items": items, "started": started}))

def clear_batch():
    """Clear the batch file."""
    if BATCH_FILE.exists():
        BATCH_FILE.unlink()

def flush_batch(items):
    """Send the collected batch as one Telegram message."""
    if not items:
        return
    msg = format_batch(items)
    if msg:
        tg_send(msg)
        log(f"[email-poller] flushed batch of {len(items)} email(s)")
    clear_batch()

# ── Inbox log ──────────────────────────────────────────────────────────────────
def log_to_inbox(uid, sender, subject, snippet, classification):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    icon = classification["icon"]
    tier = classification["tier"]
    if not INBOX_FILE.exists():
        INBOX_FILE.write_text(
            "# email-inbox — Gmail poller (macbotpooterson@gmail.com)\n"
            "# Smart triage: 🔴 urgent | 🟡 important | 🔵 info | ⚪ noise\n"
            "# Reviewed at each /mad-max session start. Delete entries after review.\n\n"
        )
    with open(INBOX_FILE, "a") as f:
        f.write(f"- [{ts}] {icon} uid={uid} [{tier}] | {sender} | {subject}\n  {snippet}\n")
    log(f"[email-poller] logged uid={uid} [{tier}] from={sender} subject={subject}")

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
        criterion = f"UID {last_uid + 1}:*" if last_uid > 0 else "ALL"
        status, data = conn.uid("SEARCH", None, criterion)
        if status != "OK" or not data[0]:
            conn.logout()
            # Still check if batch needs flushing (age-based)
            _maybe_flush_aged_batch()
            return

        raw_uids = data[0].split()
        new_uids = [int(u) for u in raw_uids if int(u) > last_uid]
        if not new_uids:
            conn.logout()
            _maybe_flush_aged_batch()
            return

        log(f"[email-poller] {len(new_uids)} new email(s)")
        max_uid = last_uid
        has_urgent = False

        # Load existing batch
        batch_items, batch_started = load_batch()
        if not batch_started:
            batch_started = time.time()

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

                # Classify the email
                classification = classify(sender, subject, to_addr, snippet)
                tier = classification["tier"]

                # Log everything to inbox file (even noise — for audit)
                log_to_inbox(uid, sender, subject, snippet, classification)

                # If email is from Rod → dispatch as command (unchanged)
                if any(addr in sender.lower() for addr in ROD_EMAILS):
                    try:
                        from dispatcher import dispatch
                        msg_body = f"Subject: {subject}\n\n{snippet}"
                        dispatch(msg_body, lambda m: tg_send(m), context="email")
                    except Exception as e:
                        log(f"[email-poller] dispatch error: {e}")

                # Add to batch (if notifiable)
                if classification["notify"]:
                    batch_items.append({
                        "classification": classification,
                        "sender": sender,
                        "subject": subject,
                        "snippet": snippet,
                        "uid": uid,
                    })

                # Urgent emails break the debounce window
                if tier == "urgent":
                    has_urgent = True

                if uid > max_uid:
                    max_uid = uid

            except Exception as e:
                log(f"[email-poller] error processing uid {uid}: {e}")

        save_last_uid(max_uid)

        # ── Debounce logic ────────────────────────────────────────────────
        if has_urgent:
            # Urgent → flush everything immediately
            flush_batch(batch_items)
        elif time.time() - batch_started >= DEBOUNCE_SECS:
            # Batch aged out → flush
            flush_batch(batch_items)
        else:
            # Save batch for later flush
            save_batch(batch_items, batch_started)
            log(f"[email-poller] batch has {len(batch_items)} item(s), waiting for debounce window")

    except Exception as e:
        log(f"[email-poller] poll error: {e}")
    finally:
        try: conn.logout()
        except: pass


def _maybe_flush_aged_batch():
    """Check if an existing batch has aged past the debounce window."""
    batch_items, batch_started = load_batch()
    if batch_items and batch_started and time.time() - batch_started >= DEBOUNCE_SECS:
        flush_batch(batch_items)


# ── Test mode: classify last N emails ─────────────────────────────────────────
def test_classify(user, pw, count=10):
    """Fetch last N emails and show classification (no notifications sent)."""
    conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    conn.login(user, pw)
    conn.select("INBOX", readonly=True)

    status, data = conn.uid("SEARCH", None, "ALL")
    if status != "OK" or not data[0]:
        print("No emails found.")
        conn.logout()
        return

    all_uids = data[0].split()
    test_uids = all_uids[-count:]

    print(f"\nClassifying last {len(test_uids)} emails:\n")
    print(f"{'Icon':<5} {'Tier':<10} {'Notify':<8} {'Batch':<7} {'Sender':<35} {'Subject':<40} {'Reason'}")
    print("-" * 150)

    for uid_bytes in test_uids:
        uid = int(uid_bytes)
        status, data = conn.uid("FETCH", str(uid), "(RFC822)")
        if status != "OK" or not data or not data[0]:
            continue

        raw = data[0][1]
        msg = email.message_from_bytes(raw)

        sender  = decode_header_val(msg.get("From", "unknown"))
        subject = decode_header_val(msg.get("Subject", "(no subject)"))
        to_addr = decode_header_val(msg.get("To", ""))
        snippet = extract_body(msg)

        c = classify(
            sanitize(sender),
            sanitize(subject),
            to_addr,
            sanitize(snippet, maxlen=MAX_BODY_LEN)
        )

        sender_short = sender.split("<")[0].strip().strip('"')[:33]
        subj_short = subject[:38]

        print(f"{c['icon']:<5} {c['tier']:<10} {str(c['notify']):<8} {str(c['batch']):<7} {sender_short:<35} {subj_short:<40} {c['reason']}")

    conn.logout()
    print(f"\nDone. {len(test_uids)} emails classified. No notifications sent.")

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

    if "--test-classify" in sys.argv:
        user, pw = load_creds()
        n = 10
        for arg in sys.argv:
            if arg.isdigit():
                n = int(arg)
        test_classify(user, pw, n)
        sys.exit(0)

    user, pw = load_creds()
    log(f"[email-poller] started (v2 — smart triage + debounce) — polling every {POLL_INTERVAL}s as {user}")

    if "--once" in sys.argv:
        poll_once(user, pw)
        sys.exit(0)

    while True:
        try:
            poll_once(user, pw)
        except Exception as e:
            log(f"[email-poller] outer error: {e}")
        time.sleep(POLL_INTERVAL)
