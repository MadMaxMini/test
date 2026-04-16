# Session Log

---

## 2026-04-16 (mini) — Health Coach + AutoDakota Telegram bots

### Done
- **Health Coach Telegram bot** — full stack built and pushed:
  - `telegram_notify.py` — send helper (Keychain: `telegram-health-bot-token`, `telegram-health-chat-id`)
  - `telegram-poller.py` — interactive bot: ask questions, `log weight N`, context-aware Claude dispatch
  - `SOUL.md` — health coach persona
  - `com.healthcoach.telegrampoller.plist` — LaunchAgent (KeepAlive, RunAtLoad)
- **Screen-lock bug fixed** — `daily.py` (6:30pm) was dying with AppleEvent timeout -1712 when screen locked. Swapped AppleScript/Shortcuts → Telegram primary + iMessage fallback. HTTP-only, no screen state dependency.
- **daily-nudge.py (6am)** — same Telegram-primary pattern added. Both push bots now screen-lock-safe.
- **AutoDakota Telegram poller** — full stack built and pushed:
  - `telegram-poller.py` — interactive: "what's overdue?", "what's Devon working on?", context-aware task loading
  - `SOUL.md` — ops-only persona
  - `com.dakotaops.telegrampoller.plist` — LaunchAgent
- **Setup doc** — `~/Work/test/telegram-bots-setup.md` — all permission steps for Rod

### Deferred (needs Rod — ~15 min on phone)
1. BotFather: register `@health_coach_rod_bot` → copy token
2. BotFather: register `@autodakota_mini_bot` → copy token
3. Message each bot once → get chat_id via curl
4. `security add-generic-password` for both sets of credentials
5. `launchctl load` both pollers from `~/Library/LaunchAgents/`

See [telegram-bots-setup.md](telegram-bots-setup.md) — step-by-step, ~15 min total.

---

## 2026-04-15 (laptop) — Sync pull + inbox read

### Done
- Pulled 28 days of mini work (5226eec → a576f86) — 34 files, clean fast-forward
- Read Life Coach inbox (2 messages):
  - **Mar 18:** Local model for Tram 360 — HIGH priority, blocking personal work
  - **Apr 15:** Three system fixes — Today.py cron (MED), status staleness monitoring (HIGH), Faith Coach gap (LOW-MED)
- Committed untracked files: `.claude/settings.json` (laptop permission shortcuts), `_agent_office_/` (Life Coach inbox messages)

### State of the System (as seen from laptop)
- Mini has Telegram bot live, dispatcher stack, health-coach consolidated, session rolling
- Still no local model pulled (Ollama installed but empty) — Life Coach flagged this as blocker
- Laptop evacuation from Mar 18 still pending (async-comms, claude-life, old recruiting files)
- Elevated permissions proposal still open

### P0 — Next Session
- **Dakota-ops: Devon's PDF extractor** — Rod handed off `bot/pdf-extractor/` (mortgage PDF → CSV pipeline) to Devon. Devon's been tasked with output format examples (CSV/markdown/JSON) + Medium article. Mad Max should review the pipeline spec and extractor code, then propose automation enhancements (batch processing, scheduled runs, Plaid integration path, error alerting) — show Devon what the platform can do. Repo: `~/Work/dakota-ops`, key commits: `95155da`, `5696d0e`, `1ddb006`.

### Next (for mini)
1. Pull a local model — `ollama pull llama3.3:8b` or similar. Unblocks Tram 360 work.
2. Status staleness monitor — cron that checks coach status file dates, alerts when >2 days stale
3. Today.py → LaunchAgent on mini (replace flaky iPhone Shortcut)
4. Laptop evacuation — async-comms videos, claude-life, recruiting old files

---


---

## 2026-04-14 (mini) — Telegram bot live + context layer built

### Done
- **@madmax_mini_bot created** via BotFather — name "Mad Max", commands set, description set
- **Bot token + chat_id stored** — Keychain (`telegram-max-bot-token`, `telegram-max-chat-id`) + OpenBao (`secret/telegram/max`)
- **OpenBao unsealed** — container was running, unsealed via keychain script
- **`telegram-poller.py` built** — long-polls Bot API, whitelist (Rod only), routes to dispatcher, LaunchAgent `com.madmax.telegrampoller` (KeepAlive)
- **`sessions.py` built** — per-chat JSONL history, default 10 messages, cap 50, `+context N` / `+context full` / `+reset` inline commands
- **`dispatcher.py` updated** — `run_model()` and `dispatch()` accept `history=` param, injects into prompt as "Recent conversation:" block
- **Claude set as default model** — `dispatcher-model.state` = claude. Was mistral (iMessage-era default). Fixed hardcoded "mistral" reference in SYSTEM_STATIC.
- **Memory architecture designed** — 3-tier: working (session-log 3 days) / episodic (archive, distilled on rolloff) / semantic (Mem0 + Qdrant, not built yet). Design doc in bottleMsg.
- **Session log rolling design** — 3-day window, distill-on-rolloff, monthly archive review via SMS approval loop.
- **Backlog updated** — added: Telegram context layer (P2, now done), bottleMsg cleanup bot (P2), session-log rolling + Mem0 (P3)

### Waiting on Rod
- Test the full loop: send a message to @madmax_mini_bot, confirm Claude responds with context
- OpenBao: stays unsealed until container stops (auto-reseals on restart)
- Google Voice number for dedicated bot account (separate from personal Telegram) — later
- Secret chats: need user account (Telethon + Google Voice), not bot API — Phase later

### Next session priorities
1. Session log rolling cron (3-day window → distill → archive)
2. Mem0 + Qdrant install for semantic memory layer
3. SOUL.md per agent (clean persona separation)

---

---
