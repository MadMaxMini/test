# Session Log

---


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
- **Shared `ollama_dispatch.py` module** — flexible Ollama fallback for all bots:
  - Dynamic model discovery (queries Ollama API for pulled models)
  - Preference-ordered dispatch: gemma3:27b > mistral-small > devstral > mixtral > llama3.1:8b > llama3.2:3b
  - Compressed per-bot prompts (SOUL.md is 2000-5500 chars, compressed to ~500 for local models)
  - Two tiers: "deep" (450 tokens, 90s timeout) and "fast" (250 tokens, 30s timeout)
  - `/models` command on manager-coach bot shows all local models with strengths and use cases
  - Wired into: manager-coach, elite-hh, health-coach. AutoDakota + Mad Max use different dispatch patterns (skipped).
  - All 3 pollers restarted and verified running
- **3 more repos pushed** — manager-coach, elite-hh-bot, health-coach

### Decisions
- Manager Coach bot follows same pattern as Elite HH: poller + daily nudge + SOUL.md + session logging
- Daily nudge at 8:33am — after 7am Dakota standup and 7:15 pre-session brief, before Rod's workday
- No Sunday nudge per Rod
- Local AI fallback: Option C (flexible, not hardcoded). Shared module, not copy-paste per bot.

### Open on Rod
- .kdbx files in bottleMsg — still awaiting destination decision
- Mem Palace encryption angle — still open

### Next
- Rod wants bots to have knowledge OF local models (can discuss/compare in chat) — `/models` command is a start, needs enrichment
- AutoDakota + Mad Max bot dispatch patterns differ — wire shared module if desired

---

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
