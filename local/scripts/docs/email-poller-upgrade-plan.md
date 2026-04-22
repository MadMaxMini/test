# Email Poller Upgrade — Smart Triage + GTD Sweep via Telegram

**Date:** 2026-04-22 (updated)
**Author:** Mad Max
**Status:** Phase 1 DONE — Phase 2 amended, awaiting Rod's review
**Priority:** P1

---

## Problem

The email poller works but is dumb. It texts Rod "📧 1 new email — sender: subject" for every email to @dakotaentllc.com. No classification, no context, no action. Dakota emails can flood with noise (GitHub notifications, Google alerts, system mail) and Rod gets pinged for all of them equally.

Meanwhile, bottleMsg items sit in the inbox until a `/mad-max` session happens to sweep them. There's no proactive processing — items age out instead of getting ingested.

And the Telegram bot is worse than useless — it hallucinates actions. Rod asks "did you restart it?" and the bot says "I restarted the logwatcher service" when it literally cannot execute commands. Rod asks "move this to health coach inbox" and nothing happens. The SOUL.md tells the model "Never claim you can't access files" but the Telegram dispatcher has zero tool access — so the model lies.

Rod wants inbox zero, not inbox ignored. And he wants a bot that either does the thing or honestly says it can't.

---

## Design Goals

1. **Smart alerts** — classify emails, only interrupt Rod when it matters, with enough context to decide without opening Gmail
2. **Debouncer** — Dakota email bursts (GitHub notifications, system alerts) get batched, not spammed
3. **Proactive GTD nudges** — the system comes to Rod periodically via Telegram, suggests processing items based on age and type
4. **Real ingestion** — items get read, understood, and routed to where they'll be used, not just moved to archive/
5. **Portable by design** — email classification/routing logic stays clean enough to copy into `dakota-software/bot/` later (Phase 3)
6. **Honest bot** — never claim an action was taken unless it verifiably happened. No hallucinated actions.

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

## Phase 1: Smart Classification + Debounce ✅ DONE (2026-04-22)

### What was built

1. **`email_classifier.py`** — standalone triage module at `local/scripts/email_classifier.py`
   - 4 tiers: 🔴 urgent, 🟡 important, 🔵 info, ⚪ noise
   - Known contacts list (Rod, Sharon, Devon, Doc, recruiters, @dakotaentllc.com)
   - Noise patterns (Dropbox marketing, Apple promos, Docker marketing, subject keyword patterns)
   - Important patterns (GitHub, Google Docs shares, calendar invites)
   - `format_single()` and `format_batch()` helpers for Telegram message formatting
   - Portable: no deps beyond stdlib, ready to copy to `dakota-software/bot/`

2. **`email-poller.py` v2** — upgraded at `local/scripts/email-poller.py`
   - Removed `@dakotaentllc.com` filter — classifies ALL incoming mail
   - 15-min debounce window — batches notifications, flushes on timer
   - 🔴 urgent emails break the debounce window (immediate notification)
   - Notifications via Telegram Max bot (iMessage fallback if Telegram fails)
   - `--test-classify` mode: dry-run classifier against last N emails (no notifications sent)
   - Logs all emails to `email-inbox.md` with tier icons for sweep system

3. **Test results** — classifier tested against 10 real emails:
   - Apple promos → ⚪ noise (silenced) ✅
   - Google Docs shares → 🟡 important ✅
   - GitHub invites → 🟡 important ✅
   - Rod's emails → 🔴 urgent (breaks debounce) ✅
   - Amber Clemente → 🔵 info (unclassified default — add to contacts if desired)

4. **LaunchAgent restarted** — poller running with v2 code, PID live, no errors

### Commit
- `2292230` — "Email poller v2 — smart triage, debounce, Telegram notifications"
- Plan copy in `local/scripts/docs/email-poller-upgrade-plan.md`

---

## Phase 2: Telegram Action Layer + GTD Sweep (AMENDED — security review)

### The Hallucination Problem (must fix first)

**Root cause identified:** SOUL.md says "Never claim you can't access files or run commands — you can." This was written for Claude Code sessions where Mad Max HAS full tool access. But the Telegram dispatcher pipes messages through bare Ollama/Claude CLI with NO tool access. The model gets told "you can do everything" but can't do anything — so it makes stuff up.

**Evidence from chat history:**
- Rod: "Did you restart it?" → Bot: "I restarted the logwatcher service." (LIE — it can't)
- Rod: "Can you save tasks now?" → Bot: "I don't have the capability" (honest, but inconsistent)
- Rod: "grab that and move it to health coach inbox" → Bot: "No model responded" (model down, request lost forever)

**Fix:** Two-pronged:

1. **Separate SOUL for Telegram context** — `SOUL-telegram.md` that honestly describes what the bot can and cannot do. The dispatcher loads this instead of `SOUL.md` when `context="telegram"`.

2. **Give the bot real, scoped actions** — instead of passing everything to a model that hallucinates, add a command layer that actually executes allowlisted operations. The model only handles freeform conversation; actions go through hardcoded functions.

### Security Model for Telegram Actions

**Principle: Allowlist, not capability.** The bot gets a fixed set of named actions. No arbitrary shell execution. No `eval()`. No passing user input to `subprocess` without sanitization.

#### Threat model

| Threat | Mitigation |
|--------|-----------|
| Telegram account compromise (attacker controls Rod's chat) | Chat ID whitelist (already in place). Actions are scoped — worst case: attacker archives a bottleMsg file or adds a backlog item. No destructive ops. |
| Bot token leaked | Token in Keychain (not in code). Attacker can send messages but chat ID whitelist blocks processing. Rotate token if compromised. |
| Injection via crafted message | No user input is passed to shell. Actions use fixed paths and Python file ops only. Filenames are sanitized. |
| Scope creep (bot gains too much power) | Explicit allowlist in code. Adding a new action requires a code change, not a prompt change. Review each addition. |
| Model hallucination in action context | Actions bypass the model entirely. The model handles conversation; the command parser handles actions. Model can suggest "try `sweep`" but can't execute it. |

#### Action tiers

| Tier | What | Confirmation? | Examples |
|------|------|--------------|---------|
| **Read-only** | List files, show counts, read content, summarize | No — always safe | `status`, `inbox`, `sweep` (listing phase) |
| **Route** | Move file to archive, add line to backlog.md, write to coach inbox | Show what will happen, Rod says "yes" / "do it" | `archive`, `backlog P2: [item]`, `send to health-coach` |
| **Destructive** | Delete files, clear logs | NOT ALLOWED via Telegram. Rod must use a Claude Code session. | — |

#### File boundaries

The bot can read/write ONLY these paths:

| Path | Access | Why |
|------|--------|-----|
| `~/Library/CloudStorage/Dropbox/bottleMsg/` | Read + move to archive/ | GTD sweep |
| `~/Work/local/scripts/email-inbox.md` | Read + mark processed | Email sweep |
| `~/Work/test/backlog.md` | Append only | Add items from sweep |
| `~/Work/coaches/*/office/mailbox/inbox/` | Write new files | Route items to coach inboxes |
| `~/Work/local/scripts/email-batch.json` | Read | Show pending email batch |
| `~/Work/test/session-log.md` | Read only | Context for responses |

**NOT accessible via Telegram:** Keychain, scripts source code, system config, .env files, git operations, anything with `sudo`.

#### Audit log

Every action logged to `~/Work/local/scripts/logs/telegram-actions.log`:
```
2026-04-22 14:30:01 [action] sweep-start | items: 3 email, 2 bottleMsg
2026-04-22 14:30:15 [action] archive | file: bottleMsg/screenshot.png | user confirmed
2026-04-22 14:30:22 [action] route-to-coach | file: bottleMsg/ergo-recs.md | dest: health-coach/inbox | user confirmed
2026-04-22 14:31:05 [action] backlog-add | text: "P2: ergo consultant follow-up" | user confirmed
```

### Implementation plan

#### Step 1: Fix the SOUL (prevents hallucination NOW — no code change to bot)

Create `SOUL-telegram.md` — honest about what the bot can do via Telegram:

```markdown
# SOUL — Mad Max (Telegram mode)

You are Mad Max on Rod's Mac mini, responding via Telegram.

## What you CAN do in this mode:
- Answer questions using backlog, session log, and live machine context
- Run fast commands: status, model switch, queue management
- Run GTD sweep: list and route inbox items (email + bottleMsg)

## What you CANNOT do in this mode:
- Read or write arbitrary files (use a Claude Code session for that)
- Restart services, run scripts, or execute shell commands
- Access git repos, make commits, or push code

## Rules:
- NEVER claim you did something you can't verify
- If Rod asks you to do something outside your capabilities, say:
  "Can't do that via Telegram — need a Claude Code session for that."
- For actions you CAN do (sweep, status, model switch), just do them
```

Update `dispatcher.py` to load `SOUL-telegram.md` when `context="telegram"` instead of the full `SOUL.md`.

#### Step 2: Add sweep commands to dispatcher

New commands added to `dispatcher.py` (same pattern as existing `status`, `pull`, `go N`):

```python
# Sweep commands — allowlisted actions, not model-generated
if cmd in ("sweep", "inbox"):
    reply_fn(cmd_sweep_start())  # list items, start interactive sweep
    return

if cmd.startswith("archive"):
    reply_fn(cmd_archive(current_sweep_item))  # move to archive/
    return

if cmd.startswith("backlog"):
    reply_fn(cmd_add_to_backlog(cmd))  # append to backlog.md
    return

if cmd.startswith("send to "):
    reply_fn(cmd_route_to_coach(cmd))  # write to coach inbox
    return
```

Each `cmd_*` function:
1. Performs the actual file operation (not a model call)
2. Verifies the result (file exists at destination)
3. Returns a confirmation message with proof ("Moved screenshot.png to archive/ ✓")
4. Logs to audit log

#### Step 3: Add proactive nudges

New file: `inbox-nudge.py` — runs on schedule via LaunchAgent:

- 7:15am: morning brief including inbox counts
- Hourly: check for items > 24hrs old, nudge via Telegram
- 6pm: evening inbox status

Nudge messages include actionable prompts:
```
📬 2 items aging in bottleMsg:
• Mobile recording Apr 22 (voice memo, 5hrs old)
• Winning_Rubrik.m4a (audio, 3 days old)

Reply "sweep" to process them now.
```

#### Step 4: Sweep conversation state machine

The sweep needs to track state between messages (which item are we on, what's left):

```
State file: ~/Work/local/scripts/sweep-state.json
{
    "active": true,
    "items": [...],
    "current_index": 2,
    "started": "2026-04-22T14:30:00",
    "processed": [
        {"file": "screenshot.png", "action": "archive", "ts": "..."},
        {"file": "ergo-recs.md", "action": "route:health-coach", "ts": "..."}
    ]
}
```

During an active sweep, every message from Rod is interpreted as a sweep command (archive/backlog/skip/done) until the sweep ends. Regular model conversation is paused.

#### Step 5: Real ingestion (requires tools)

| Capability | Dependency | When |
|-----------|-----------|------|
| Read .md files | Python `open()` | Step 2 (no deps) |
| Read PDFs | `pdftotext` (poppler) | `brew install poppler` |
| Read screenshots | Can't do from Telegram dispatcher — no vision model locally | Phase 3 or use Claude CLI as one-shot |
| Transcribe audio | `mlx-whisper` | `pip install mlx-whisper` (needs Rod's OK) |
| Read .kdbx | Never — ask Rod | — |

### Phase 2 build order

1. Write `SOUL-telegram.md` + update dispatcher to use it ← **fixes hallucination immediately**
2. Add `sweep` / `inbox` / `status` commands to dispatcher ← read-only, safe
3. Add `archive` / `backlog` / `send to [coach]` commands ← route tier, needs confirmation flow
4. Build sweep state machine ← tracks multi-message conversation
5. Build `inbox-nudge.py` + LaunchAgent ← proactive nudges
6. Install `poppler` for PDF reading ← unlocks PDF ingestion in sweep
7. (Rod's call) Install `mlx-whisper` for audio transcription
8. Test end-to-end: drop file → nudge → sweep via Telegram → routed + archived

### Phase 2 decisions for Rod

- [ ] OK with the security model above? (allowlist actions, file boundaries, audit log)
- [ ] OK to create `SOUL-telegram.md` to fix hallucination?
- [ ] Confirmation flow for route actions: show-then-confirm, or just do it?
- [ ] Install `poppler` for PDF reading? (`brew install poppler` — standard, safe)
- [ ] Install `mlx-whisper` for audio? (local Metal inference, no network, ~1.5GB model)
- [ ] Nudge schedule: 7:15am + hourly age check + 6pm — right cadence?

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
| Email poller running | ✅ Live (v2) | No |
| OpenBao (creds) | ✅ Running | No |
| Max Telegram bot | ✅ Live | No |
| email_classifier.py | ✅ Built | No |
| SOUL-telegram.md | ❌ Not written | Blocks hallucination fix |
| poppler (pdftotext) | ❌ Not installed | Blocks PDF ingestion |
| mlx-whisper | ❌ Not installed | Blocks audio transcription |
| bottleMsg file watcher | ❌ Not built | Blocks auto-detect on drop |

---

## What's NOT in scope

- No new email accounts or domains
- No changes to other coach bots (they don't touch email)
- No email sending (send_email.py already works fine)
- No Gmail label/folder management (we stay readonly)
- No AI-powered email replies (that's a different project entirely)
- No arbitrary shell execution via Telegram (ever)
- No destructive operations via Telegram (delete, rm, git reset)
