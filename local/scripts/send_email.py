#!/usr/bin/env python3
"""
send_email.py — send email or calendar invites from macbotpooterson@gmail.com

Usage:
    # Plain email
    python3 send_email.py --to "someone@example.com" --subject "Hello" --body "Message here"

    # Calendar invite
    python3 send_email.py --invite \
        --to "rod@proton.com,devon@gmail.com" \
        --subject "Team check-in" \
        --body "Agenda: Q2 review" \
        --start "2026-03-26 10:00" \
        --end "2026-03-26 11:00" \
        --location "Zoom / TBD"

Contacts shorthand (--to accepts names):
    rod       → roderick.clemente@protonmail.com
    devon     → (add to CONTACTS below)
    doc       → (add to CONTACTS below)
    sharon    → (add to CONTACTS below)
    dakota    → all four
"""

import smtplib
import urllib.request
import json
import subprocess
import argparse
import uuid
import sys
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ── Contacts shorthand ─────────────────────────────────────────────────────────
CONTACTS = {
    "rod":    "roderick.clemente@protonmail.com",
    "devon":  "",   # fill in when known
    "doc":    "",   # fill in when known
    "sharon": "",   # fill in when known
}
CONTACTS["dakota"] = ",".join(v for v in [
    CONTACTS["rod"], CONTACTS["devon"], CONTACTS["doc"], CONTACTS["sharon"]
] if v)

# ── OpenBao creds ──────────────────────────────────────────────────────────────
def load_creds():
    token = subprocess.run(
        ["security", "find-generic-password", "-a", "macBot", "-s", "openbao-root-token", "-w"],
        capture_output=True, text=True
    ).stdout.strip()
    if not token:
        print("ERROR: openbao-root-token not in Keychain")
        sys.exit(1)
    req = urllib.request.Request(
        "http://127.0.0.1:8200/v1/secret/data/email/gmail",
        headers={"X-Vault-Token": token}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())["data"]["data"]
            return data["username"], data["password"]
    except Exception as e:
        print(f"ERROR: could not read credentials from OpenBao — {e}")
        sys.exit(1)

# ── Resolve recipients ─────────────────────────────────────────────────────────
def resolve_recipients(to_str):
    addrs = []
    for part in to_str.split(","):
        part = part.strip()
        if part in CONTACTS:
            resolved = CONTACTS[part]
            if not resolved:
                print(f"WARNING: no email on file for '{part}' — skipping")
                continue
            addrs += [a.strip() for a in resolved.split(",") if a.strip()]
        elif "@" in part:
            addrs.append(part)
        else:
            print(f"WARNING: unknown contact '{part}' — skipping")
    return list(dict.fromkeys(addrs))  # dedup, preserve order

# ── Build ICS calendar invite ──────────────────────────────────────────────────
def build_ics(summary, description, start_str, end_str, location, organizer, attendees):
    def fmt_dt(dt_str):
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y%m%dT%H%M%S")

    uid = f"{uuid.uuid4()}@dakotaentllc.com"
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    attendee_lines = "\n".join(
        f"ATTENDEE;CN={a.split('@')[0].title()};RSVP=TRUE:mailto:{a}"
        for a in attendees
    )

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Max Mini//Dakota//EN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now}
DTSTART:{fmt_dt(start_str)}
DTEND:{fmt_dt(end_str)}
SUMMARY:{summary}
DESCRIPTION:{description.replace(chr(10), '\\n')}
LOCATION:{location}
ORGANIZER;CN=Max (Dakota):mailto:{organizer}
{attendee_lines}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""

# ── Send ───────────────────────────────────────────────────────────────────────
def send(user, pw, recipients, subject, body, ics=None):
    msg = MIMEMultipart("mixed" if ics else "alternative")
    msg["From"] = f"Max (Dakota) <{user}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if ics:
        part = MIMEBase("text", "calendar", method="REQUEST", name="invite.ics")
        part.set_payload(ics.encode())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="invite.ics")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pw)
        s.sendmail(user, recipients, msg.as_string())

    print(f"Sent to: {', '.join(recipients)}")

# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True, help="Recipient(s) — email or shorthand: rod, devon, dakota")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--invite", action="store_true", help="Send as calendar invite")
    parser.add_argument("--start", help="Start time: '2026-03-26 10:00'")
    parser.add_argument("--end",   help="End time:   '2026-03-26 11:00'")
    parser.add_argument("--location", default="TBD")
    args = parser.parse_args()

    if args.invite and (not args.start or not args.end):
        print("ERROR: --invite requires --start and --end")
        sys.exit(1)

    user, pw = load_creds()
    recipients = resolve_recipients(args.to)
    if not recipients:
        print("ERROR: no valid recipients")
        sys.exit(1)

    ics = None
    if args.invite:
        ics = build_ics(
            summary=args.subject,
            description=args.body,
            start_str=args.start,
            end_str=args.end,
            location=args.location,
            organizer=user,
            attendees=recipients,
        )

    send(user, pw, recipients, args.subject, args.body, ics)

if __name__ == "__main__":
    main()
