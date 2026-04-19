# Session Log

---

## 2026-04-19b (mini) — Manager Coach bot live on Telegram

### Done
- **GTD inbox sweep** — `from-manager-coach-2026-04-19-sharon-plan.md` processed WITH Rod (not just filed). Content already captured in Sharon's profile. Archived.
- **Inbox feedback** — Rod flagged that GTD sweep was too "filing clerk" — need to actually process items together, not just route and archive. Noted.
- **Manager Coach Telegram bot** — `@manager_coach_bot` registered (Rod did BotFather), full build:
  - `telegram-poller.py` — Claude primary, Ollama fallback, Rod-only whitelist, session history (10-deep), claim detection via shared module
  - `SOUL.md` — Manager Tools methodology (feedback model, 1:1s, delegation, difficult conversations) + Sharon's full profile + phrasing guide ("Sharon said X, how do I respond?")
  - `daily.py` — 8:33am Mon-Sat nudge: the 5 Things, open items, day-specific prompts (Mon=warm text, Wed=mid-week call check, Fri=did you do both?)
  - LaunchAgents installed: `com.manager.telegrampoller` (KeepAlive) + `com.manager.dailynudge` (Mon-Sat 8:33am)
  - Creds in Keychain + OpenBao (`telegram-manager-bot-token`, `telegram-manager-chat-id`)
  - Daily nudge test fired successfully
- **Inventory + Mad Max skill updated** — chat log paths, execution log paths, telegram-ops bot registry, claim detection status
- **Both repos pushed** — manager-coach (08864b2) + madmax (9d7f681)

### Decisions
- Manager Coach bot follows same pattern as Elite HH: poller + daily nudge + SOUL.md + session logging
- Daily nudge at 8:33am — after 7am Dakota standup and 7:15 pre-session brief, before Rod's workday
- No Sunday nudge per Rod

### Open on Rod
- .kdbx files in bottleMsg — still awaiting destination decision
- Mem Palace encryption angle — still open
- **Local AI fallback quality** — Rod tested the bot via Telegram and it knew nothing. Need to discuss Ollama model context injection and whether the fallback path is viable for coaching bots

### Next
- Discuss local AI fallback strategy — are Ollama models getting enough context? Is the fallback path worth keeping for coaching use cases?

---

## 2026-04-19 (mini) — Mem Palace design + GTD sweep

### Done
- **GTD inbox sweep** — bottleMsg processed: TODO-bottlemsg-watcher.md → backlog P3, two .kdbx files surfaced to needs-rod.md (awaiting Rod's instruction on destination)
- **Memory architecture audit** — surveyed all 5 memory layers across every agent repo. Identified duplication: team identities in 3 places, arm injury only in Mad Max SOUL.md, routing buried in 6 skill files
- **Mem Palace designed** — `~/Work/palace/` proposal: shared read layer with rooms rod/, team/, platform/, decisions/. All agents get 1-line pointer in CLAUDE.md. Sent 3-part Telegram write-up to Rod
- **Backlog updated** — bottleMsg watcher + Mem Palace both added as P3; needs-rod.md created

### Open on Rod
- .kdbx files in bottleMsg — what's the destination?
- Mem Palace encryption angle: laptop FileVault check / encrypt palace dir / platform/security.md — pick one

### Next
- Rod picks encryption angle → Phase 1 build (~2hrs)

---

## 2026-04-16 (mini) — health-coach Telegram wiring

### Done
- **Diagnosed 6:30pm send failures** — root cause: AppleEvent timeouts when screen locked/idle. Affects both Messages.app and Shortcuts Events. Switched daily.py to Shortcuts on Apr 14 (d0d7966) but hit same wall.
- **Both bots updated to use `telegram_notify.py`** — `daily.py` (6:30pm) and `daily-nudge.py` (6am) both load it as primary send channel, iMessage as fallback
- **`telegram_notify.py` created** — reads `telegram-health-bot-token` + `telegram-health-chat-id` from Keychain, pure HTTP (no AppleScript)

### Open on Rod
- **Keychain credentials missing** — `telegram-health-bot-token` and `telegram-health-chat-id` not set. Two options:
  1. Reuse Mad Max bot (`telegram-max-*` creds already in Keychain) — zero setup, works now
  2. New dedicated health bot via BotFather — cleaner separation, ~5min setup
- Until one of these is done, bots fall back to iMessage (still flaky at 6:30pm)

### Next
- Rod picks: reuse max bot or new health bot → store creds in Keychain → test

---

## 2026-04-18 (mini) — Telegram awareness + Elite HH Coach bot

### Done
- **`telegram-chat-review.sh`** — unified viewer for all 4 bots (autodakota/health/max/elitehh), claims mode, interleaved mode
- **`claim_detector.py`** — shared module at `~/Work/local/scripts/`; Health Coach + Mad Max pollers updated to import it; both restarted
- **Mad Max skill** — added Telegram Chat Review section (verified paths), CAN/CANNOT capability section
- **`proposals/two-tier-telegram-dispatch.md`** — design doc for big-ask vs quick-question routing (needs Rod review)
- **Elite HH Coach bot** — `@elitehh_rod_bot` registered, token in Keychain + OpenBao, poller live (pid confirmed)
  - SOUL.md with CAN/CANNOT
  - Auto daily session summary to `office/sessions/YYYY-MM-DD.md` (every turn, both sides)
  - `/note [text]` → appends to session-log.md
  - `[TASK:rod]` tag detection → writes to task-inbox.md
  - 9pm daily digest: condensed bullets + file pointer via Telegram (`com.elitehh.sessionsummary`)
- **bottleMsg** — `2026-04-18-mad-max-telegram-audit.md` processed and archived

### Decisions
- Claim detection shared via module, not copy-paste per bot
- AutoDakota keeps its inline copy for now (working, low priority to migrate)
- Pipeline.md edits left as manual — table format too fragile for LLM writes

### Next
- Rod reviews `proposals/two-tier-telegram-dispatch.md` — confirm keyword triggers + confirmation gate design
- Test `@elitehh_rod_bot` with a real job hunting session; verify summary fires at 9pm
- AutoDakota: migrate inline claim detection to shared module (backlog)

---

## 2026-04-17 (mini) — ArchiveLD quarter-based testing setup

### Done
- **ArchiveLD.py refactor** — converted from full-year to quarter-based archiving
  - Accepts `YEAR` and `QUARTER` as command-line args (defaults to Q1 2020)
  - Auto-calculates date range for any quarter (Q1–Q4)
  - Works in Pythonista (tap Run) or CLI: `python3 ArchiveLD.py 2020 1`
  - Pulled latest from dakota-software, pushed updated script
  - Ready for Rod's Pythonista → Dropbox shortcut testing

### Why
- Rod left LD but wants to archive old calendar (who he spoke with, when) for personal CRM history
- Previous approach (full year 2020) timed out on Dropbox write via Pythonista shortcut
- Smaller chunks (Q1, Q2, Q3, Q4 one at a time) should succeed without timeout
- If Q1 2020 works, can scale up or batch quarters together

### Next
- Rod tests Q1 2020 through Pythonista shortcut → Dropbox
- If successful, archive subsequent quarters (Q2, Q3, Q4 2020) and following years

---

---
