# Email Poller Upgrade — Smart Triage + GTD Sweep via Telegram

**Date:** 2026-04-22
**Author:** Mad Max
**Status:** Plan — awaiting Rod's review
**Priority:** P1

---

## Problem

The email poller works but is dumb. It texts Rod "📧 1 new email — sender: subject" for every email to @dakotaentllc.com. No classification, no context, no action. Dakota emails can flood with noise (GitHub notifications, Google alerts, system mail) and Rod gets pinged for all of them equally.

Meanwhile, bottleMsg items sit in the inbox until a `/mad-max` session happens to sweep them. There's no proactive processing — items age out instead of getting ingested.

Rod wants inbox zero, not inbox ignored.

---

## Design Goals

1. **Smart alerts** — classify emails, only interrupt Rod when it matters, with enough context to decide without opening Gmail
2. **Debouncer** — Dakota email bursts (GitHub notifications, system alerts) get batched, not spammed
3. **Proactive GTD nudges** — the system comes to Rod periodically via Telegram, suggests processing items based on age and type
4. **Real ingestion** — items get read, understood, and routed to where they'll be used, not just moved to archive/
5. **Portable by design** — email classification/routing logic stays clean enough to copy into `dakota-software/bot/` later (Phase 3)

---

## Architecture Concern (Phase 3 — noted, not blocking)

The email triage + debounce + routing rules are genuinely useful for Dakota Software as a product. If they live only in `local/scripts/`, they're welded to the mini.

**Decision for now:** Build in `local/scripts/` where the poller already lives. Keep the classification logic in a separate module (`email_classifier.py`) so it's easy to copy into `dakota-software/bot/` when that time comes. No framework, no dependencies beyond stdlib — just a function that takes email metadata and returns a tier + routing suggestion.

**The split:**

| Layer | Where it lives | Portable? |
|-------|---------------|-----------|
| `email_classifier.py` — triage rules, contact list, debounce logic | `local/scripts/` now → `dakota-software/bot/` later | ✅ Yes, standalone module |
| `email-poller.py` — IMAP polling, OpenBao creds, notification dispatch | `local/scripts/` | Mini infrastructure |
| bottleMsg GTD processing | `local/scripts/` | Rod-specific, stays |
| Telegram sweep commands | Max bot (`telegram-poller.py`) | Mini infrastructure |

**Email address routing (future):** If we set up aliases or filters on macbotpooterson@gmail.com (e.g., `macbotpooterson+dakota@gmail.com` vs `macbotpooterson+max@gmail.com`), we can route at the address level. Gmail delivers both to the same inbox but preserves the +tag in the `To:` header. The classifier can split on this. Not needed now, but the design accommodates it.

---

## Phase 1: Smart Classification + Debounce (build now)

### New file: `email_classifier.py`

A standalone module. No imports beyond stdlib. Takes email metadata, returns a decision.

```python
def classify(sender: str, subject: str, to_addr: str, body_snippet: str) -> dict:
    """
    Returns:
        tier: "urgent" | "important" | "info" | "noise"
        reason: str (why this classification)
        notify: bool (should Rod be pinged?)
        batch: bool (can wait for debounce window?)
        route: str (suggested destination — "rod", "dakota-group", "backlog", "silent")
    """
```

**Classification tiers:**

| Tier | Icon | Criteria | Notify? | Examples |
|------|------|----------|---------|---------|
| 🔴 Urgent | Known contacts, reply-needed signals, "urgent" in subject | Immediately | Email from Doc, Devon, Sharon, a recruiter reply |
| 🟡 Important | GitHub PR reviews, Google Doc shares, calendar invites, @mentions | Yes, can batch | GitHub PR requested review, shared doc, meeting invite |
| 🔵 Info | GitHub commit notifications, CI results, system confirmations | Batch in digest | GitHub push notifications, Dropbox confirmations |
| ⚪ Noise | Marketing, newsletters, automated onboarding, promos | Silent | Apple promos, Dropbox upsells, "unlock features" |

**Known contacts list (🔴 triggers):**
- Rod's addresses: `roderick.clemente@protonmail.com`, `rjclemente`
- Doc (add email when known)
- Devon (add email when known)
- Sharon: `faithsv79@gmail.com`
- Cain Andrews
- Any `@dakotaentllc.com` sender

**Noise patterns (auto-silence):**
- `no-reply@em-s.dropbox.com` (marketing)
- `@insideapple.apple.com` (Apple promos)
- `no-reply@notify.docker.com` (Docker marketing)
- Subject contains: "unlock", "free trial", "get started", "features you"
- Any sender matching `no-reply@` + marketing domain

### Debouncer

Instead of one text per email, collect for a **15-minute window**, then send one Telegram summary:

```
📧 3 new emails (last 15 min):
🔴 Doc Clemente — RE: mortgage docs for 1847 Elm
🟡 GitHub — PR review requested: fix standup dedup
🔵 Google — Security alert (new sign-in)

(⚪ 2 noise emails silenced)
```

If a 🔴 urgent email arrives, **break the window** and send immediately. Don't make Rod wait 15 minutes for something from Doc.

**Implementation:** The poller already runs every 5 minutes. Change the notify logic:
- On each poll, classify new emails and append to a batch file (`email-batch.json`)
- If any 🔴 in the batch → flush immediately via Telegram
- If batch age > 15 min → flush whatever's collected
- If only ⚪ noise → don't flush at all (log only)

### Changes to `email-poller.py`

1. Import `email_classifier.classify()`
2. Remove the `@dakotaentllc.com` filter — classify ALL incoming mail, let the classifier decide what matters
3. Replace `notify()` (iMessage via notify.sh) with Telegram send via Max bot — richer formatting, Rod can reply inline
4. Add debounce logic (batch file + flush rules)
5. Keep logging to `email-inbox.md` for the sweep system

### Notification channel change

**Current:** iMessage via `notify.sh` (plain text, character limits, can't reply)
**New:** Telegram via Mad Max bot (markdown formatting, inline reply, threaded)

iMessage stays as fallback if Telegram API fails.

---

## Phase 2: Proactive GTD Nudge System (build next)

### Nudge triggers via Max Telegram bot

| Trigger | When | Message |
|---------|------|---------|
| **Morning brief** | 7:15am (already planned as P1) | Include: "📬 X items in bottleMsg, Y unread emails — want a sweep?" |
| **Item aging** | Check hourly | If any bottleMsg item > 24hrs old: "📬 [filename] has been in your inbox since yesterday. Route it?" |
| **New bottleMsg drop** | File watcher (WatchPaths LaunchAgent) | "📬 You just dropped [filename]. I think it's [type]. Want me to process it?" |
| **Evening check** | 6pm | "📬 Inbox status: X items remaining. [list them]. Sweep before EOD?" |
| **Post-email-burst** | After debounce flush | If 3+ emails in one flush: "Busy inbox — want me to triage the batch?" |

### Sweep conversation flow

When Rod engages (replies "yes", "sweep", "inbox" to the Max bot):

1. Bot reads `email-inbox.md` (unprocessed emails) + lists `bottleMsg/` (non-archived files)
2. Presents items **one at a time** with a recommendation:
   ```
   1/4 📧 Email from Cain Andrews — "VS Code setup instructions" (Google Doc share)
   Looks like a reference doc. Archive or save somewhere?
   ```
3. Rod replies: "archive" / "backlog P2" / "send to elite-hh" / "skip" / "do it"
4. Bot executes the routing, marks item as processed
5. Moves to next item
6. At the end: "✅ Inbox zero. 4 items processed."

### Real ingestion rules

| Item type | What the bot does before routing |
|-----------|--------------------------------|
| PDF article | Read it (Read tool or pdftotext), extract key insight in 1-2 sentences |
| Screenshot | View it, describe what it shows |
| Voice memo / audio | Transcribe via Whisper (local, Apple Silicon) |
| Performance reviews | Read, extract wins/themes/growth areas |
| .md file (plan, notes) | Read, summarize, check if still current |
| .kdbx (KeePass) | Don't open — ask Rod where to store |
| Email | Body snippet already captured — summarize action needed |

### New Telegram commands for Max bot

| Command | What it does |
|---------|-------------|
| `sweep` or `inbox` | Start GTD sweep of email + bottleMsg |
| `sweep email` | Sweep email inbox only |
| `sweep btl` | Sweep bottleMsg only |
| `status` | Show current inbox counts |
| `skip` (during sweep) | Skip current item, come back later |
| `done` | End sweep early |

---

## Phase 3: Portability + Dakota Split (future — when it matters)

When Dakota Software needs its own email processing:

1. Copy `email_classifier.py` into `dakota-software/bot/email_classifier.py`
2. Dakota's version gets its own contact list (Dakota team only), its own routing rules
3. The mini keeps the Max version for personal/platform email
4. Email address routing via +tags: `macbotpooterson+dakota@gmail.com` → Dakota classifier, `macbotpooterson+max@gmail.com` or bare address → Max classifier
5. Or: Dakota gets its own email account entirely (`ops@dakotaentllc.com` or similar)

**No work needed now.** The classifier module is designed to be copy-paste portable. When the trigger comes (selling Dakota, onboarding someone else), it's a 30-minute migration.

---

## Dependencies

| Dep | Status | Blocker? |
|-----|--------|----------|
| Email poller running | ✅ Live | No |
| OpenBao (creds) | ✅ Running | No |
| Max Telegram bot | ✅ Live | No |
| Whisper (audio transcription) | ❌ Not installed | Only blocks voice memo ingestion — Phase 2 |
| bottleMsg file watcher | ❌ Not built | Only blocks auto-detect on drop — Phase 2 |

---

## Build Order

### Phase 1 — can build today
1. Write `email_classifier.py` (standalone module, ~100 lines)
2. Update `email-poller.py` — import classifier, remove dakotaentllc filter, add debounce, switch notify to Telegram
3. Test: send a test email, verify classification + Telegram alert
4. Verify debounce: send 3 emails in 5 min, confirm single batched notification

### Phase 2 — next session
5. Add `sweep` command to Max Telegram bot
6. Build nudge schedule (LaunchAgent, fires at 7:15am + 6pm + hourly age check)
7. Wire bottleMsg file watcher (WatchPaths LaunchAgent)
8. Install `mlx-whisper` for audio transcription (needs Rod's OK)
9. Test end-to-end: drop file in bottleMsg → bot nudges → Rod sweeps via Telegram → item routed + archived

### Phase 3 — when triggered
10. Copy classifier to dakota-software/bot/
11. Set up +tag email routing or separate Dakota email
12. Dakota bot gets its own email sweep commands

---

## What's NOT in scope

- No new email accounts or domains
- No changes to other coach bots (they don't touch email)
- No email sending (send_email.py already works fine)
- No Gmail label/folder management (we stay readonly)
- No AI-powered email replies (that's a different project entirely)

---

## Rod decides:

- [ ] Phase 1 good to build today?
- [ ] OK to remove the @dakotaentllc.com filter and classify ALL incoming mail?
- [ ] Notification channel: switch from iMessage → Telegram? (iMessage as fallback)
- [ ] Nudge schedule: 7:15am + 6pm + hourly age check — right cadence?
- [ ] Audio transcription: OK to install mlx-whisper? (local, Metal, no network)
- [ ] Anything missing?
