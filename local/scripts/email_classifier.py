#!/usr/bin/env python3
"""
email_classifier.py — standalone email triage module

No dependencies beyond stdlib. Designed to be copy-paste portable
into dakota-software/bot/ when that time comes (Phase 3).

Usage:
    from email_classifier import classify

    result = classify(
        sender="Doc Clemente <doc@example.com>",
        subject="RE: mortgage docs for 1847 Elm",
        to_addr="macbotpooterson@gmail.com",
        body_snippet="Sharon sent the updated statements..."
    )
    # result = {
    #     "tier": "urgent",
    #     "icon": "🔴",
    #     "reason": "Known contact: Doc",
    #     "notify": True,
    #     "batch": False,
    #     "route": "rod",
    # }
"""

import re

# ── Known contacts (🔴 urgent triggers) ──────────────────────────────────────

KNOWN_CONTACTS = [
    # Rod
    "roderick.clemente@protonmail.com",
    "rjclemente",
    # Dakota team
    "faithsv79",           # Sharon
    "devon.clemen",        # Devon
    # Add Doc's email when known
    # Recruiters / job-related
    "linkedin.com",
    "lever.co",
    "greenhouse.io",
    "ashbyhq.com",
    "jobs-noreply@",
]

# ── Noise patterns (auto-silence) ────────────────────────────────────────────

NOISE_SENDERS = [
    "no-reply@em-s.dropbox.com",       # Dropbox marketing
    "no-reply@em.dropbox.com",
    "@insideapple.apple.com",          # Apple promos (TV, Arcade, Creator Studio)
    "no-reply@notify.docker.com",      # Docker marketing
    "noreply@medium.com",
    "noreply@substack.com",
    "marketing@",
    "promo@",
    "newsletter@",
    "offers@",
]

NOISE_SUBJECTS = [
    r"unlock .* features",
    r"free (trial|months?)",
    r"get started",
    r"features you",
    r"you didn.t know",
    r"tips (for|to)",
    r"ready to .* your",
    r"welcome to .* here.s how",
    r"unsubscribe",
]

# ── Important patterns (🟡) ──────────────────────────────────────────────────

IMPORTANT_SENDERS = [
    "@github.com",         # GitHub notifications
    "drive-shares-dm-noreply@google.com",  # Google Docs shares
    "calendar-notification@google.com",     # Calendar invites
    "@dakotaentllc.com",   # Any Dakota domain sender
]

IMPORTANT_SUBJECTS = [
    r"review requested",
    r"assigned to you",
    r"mentioned you",
    r"shared .* with you",
    r"invitation",
    r"calendar",
    r"meeting",
]

# ── Info patterns (🔵) ───────────────────────────────────────────────────────

INFO_SENDERS = [
    "notifications@github.com",   # Generic GitHub (pushes, CI)
    "noreply@google.com",
    "no-reply@accounts.google.com",
    "no-reply@dropbox.com",        # Dropbox transactional (not marketing)
    "noreply@email.apple.com",     # Apple account alerts
]

# ── Classifier ────────────────────────────────────────────────────────────────

def _match_any(value, patterns):
    """Check if value contains any of the patterns (case-insensitive)."""
    val_lower = value.lower()
    for p in patterns:
        if p.lower() in val_lower:
            return p
    return None


def _match_any_re(value, patterns):
    """Check if value matches any regex pattern (case-insensitive)."""
    for p in patterns:
        if re.search(p, value, re.IGNORECASE):
            return p
    return None


def classify(sender, subject, to_addr="", body_snippet=""):
    """
    Classify an email into a triage tier.

    Args:
        sender: From header (e.g., 'Doc Clemente <doc@example.com>')
        subject: Subject line
        to_addr: To header (for +tag routing in Phase 3)
        body_snippet: First ~300 chars of body

    Returns:
        dict with keys: tier, icon, reason, notify, batch, route
    """
    sender = sender or ""
    subject = subject or ""
    to_addr = to_addr or ""
    body_snippet = body_snippet or ""

    # ── Check noise first (reject early) ──────────────────────────────────
    noise_sender = _match_any(sender, NOISE_SENDERS)
    if noise_sender:
        return {
            "tier": "noise",
            "icon": "⚪",
            "reason": f"Noise sender: {noise_sender}",
            "notify": False,
            "batch": False,
            "route": "silent",
        }

    noise_subject = _match_any_re(subject, NOISE_SUBJECTS)
    if noise_subject:
        return {
            "tier": "noise",
            "icon": "⚪",
            "reason": f"Noise subject pattern: {noise_subject}",
            "notify": False,
            "batch": False,
            "route": "silent",
        }

    # ── Known contacts → urgent ───────────────────────────────────────────
    known = _match_any(sender, KNOWN_CONTACTS)
    if known:
        return {
            "tier": "urgent",
            "icon": "🔴",
            "reason": f"Known contact: {known}",
            "notify": True,
            "batch": False,   # break debounce window
            "route": "rod",
        }

    # ── Important patterns ────────────────────────────────────────────────
    imp_sender = _match_any(sender, IMPORTANT_SENDERS)
    if imp_sender:
        return {
            "tier": "important",
            "icon": "🟡",
            "reason": f"Important sender: {imp_sender}",
            "notify": True,
            "batch": True,    # can wait for debounce
            "route": "rod",
        }

    imp_subject = _match_any_re(subject, IMPORTANT_SUBJECTS)
    if imp_subject:
        return {
            "tier": "important",
            "icon": "🟡",
            "reason": f"Important subject: {imp_subject}",
            "notify": True,
            "batch": True,
            "route": "rod",
        }

    # ── Info patterns ─────────────────────────────────────────────────────
    info_sender = _match_any(sender, INFO_SENDERS)
    if info_sender:
        return {
            "tier": "info",
            "icon": "🔵",
            "reason": f"Info sender: {info_sender}",
            "notify": True,
            "batch": True,
            "route": "digest",
        }

    # ── Default: info (unknown sender, not noise) ─────────────────────────
    return {
        "tier": "info",
        "icon": "🔵",
        "reason": "Unclassified — defaulting to info",
        "notify": True,
        "batch": True,
        "route": "digest",
    }


# ── Format helpers (for Telegram messages) ────────────────────────────────────

def format_single(classification, sender, subject, snippet=""):
    """Format a single email alert for Telegram (Markdown)."""
    icon = classification["icon"]
    # Clean sender for display — extract name or email
    sender_display = sender.split("<")[0].strip().strip('"') or sender
    if len(sender_display) > 40:
        sender_display = sender_display[:37] + "..."

    msg = f"{icon} *Email from {sender_display}*\nSubject: {subject}"
    if snippet and classification["tier"] in ("urgent", "important"):
        # Show snippet for urgent/important only
        snippet_clean = snippet[:150].replace("*", "").replace("_", "")
        msg += f'\n"{snippet_clean}..."'
    return msg


def format_batch(items):
    """
    Format a batch of classified emails for Telegram.

    Args:
        items: list of dicts with keys: classification, sender, subject

    Returns:
        str: formatted Telegram message
    """
    if not items:
        return ""

    # Sort: urgent first, then important, then info
    tier_order = {"urgent": 0, "important": 1, "info": 2, "noise": 3}
    items.sort(key=lambda x: tier_order.get(x["classification"]["tier"], 3))

    # Count noise (silenced)
    visible = [i for i in items if i["classification"]["tier"] != "noise"]
    noise_count = len(items) - len(visible)

    if not visible:
        return ""  # all noise, nothing to send

    lines = [f"📧 *{len(visible)} new email(s):*\n"]
    for item in visible:
        c = item["classification"]
        sender_display = item["sender"].split("<")[0].strip().strip('"') or item["sender"]
        if len(sender_display) > 30:
            sender_display = sender_display[:27] + "..."
        lines.append(f"{c['icon']} {sender_display} — {item['subject'][:50]}")

    if noise_count:
        lines.append(f"\n_(⚪ {noise_count} noise email(s) silenced)_")

    return "\n".join(lines)
