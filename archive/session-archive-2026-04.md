# Session Archive — 2026-04

## 2026-04-02 (distilled)
- **notify-group.sh re-enabled** — was deliberately disabled, Rod approved turning back on
- **scan.py group text fixed** — was sending old digest format; now sends agreed format: top 1 per person + wins + GH link
- **Wins dedup fixed** — one win per person, 55-char truncation, no duplicates
- **Standup manually sent** to Dakota group with `FORCE_NOTIFY=1`
- **standup-system-deets.md** dropped in bottleMsg — full architecture writeup, Rod texted
- **bottleMsg inbox processed** — 9 items, GTD loop: routed model intel → local-ai.md, model-lab → backlog P2 + folder created, screenshots archived
- **GTD inbox loop built into mad-max skill** — collect→clarify→organize→table→archive. Runs every session start.
- **Weekly review cron** — Friday 4pm, texts Rod backlog counts + bottleMsg status + HH pipeline + GitHub links. `com.madmax.weeklyreview` loaded.
- **Qwen3.5-35B-A3B added to local-ai.md** — strong agentic candidate, 3B active params, fits 32GB, HF CTO-endorsed
- **LLMFit + GGUF tooling section added to local-ai.md**
- **model-lab/ folder created** at `~/Work/model-lab/` per Rod's kickoff doc
- **Decision log updated** in mad-max SKILL.md — 3 new entries
- **elite-hh-bot repo live** — migrated `~/Work/coaches/job/` into skill/office structure, pushed to `git@github.com:Roderick-Clemente/elite-hh-bot.git`, local at `~/Work/coaches/elite-hh-bot`
- **health-coach repo live** — skeleton scaffolded and pushed to `git@github.com:Roderick-Clemente/health-coach.git`, local at `~/Work/coaches/health-coach`. Content to port from Rod's laptop.
- **Daily crons wired (launchd)**:
- **Dakota standup format updated** — text message now shows top task per person + quick wins + GitHub link instead of digest+top3
- **Inventory updated** — both new repos added, local paths corrected
- elite-hh-bot uses skill/office split (matches recruiting-coach pattern)
- health-coach daily bot is "port reminder" until content arrives — auto-upgrades to real check-in after GOALS.md populated
- Full autonomy by default in both new repos — ask only on deletes
- Port health coach content from laptop to `~/Work/coaches/health-coach/office/`
- Scale AI job URL for pipeline.md

## 2026-04-13 (distilled)
- Telegram context architecture designed: Channel = identity + context + session, JSONL history per channel, 3-msg default / 20-msg cap, inline `+context N` / `+model X` / `+reset` controls
- Researched OpenClaw/MoltBot lineage; decided to reference patterns (sessions dir, SOUL.md, litellm) without deploying their code
- Audited current system — dispatcher, msggateway, model routing already exist; only missing piece is conversation history buffer
- bottleMsg cleanup bot designed: daily scan → SMS to Rod → go/skip → archive, human-in-the-loop same pattern as night-planner
- mad-max skill updated with permanent bottleMsg output rule
- Telegram context layer + bottleMsg cleanup bot added to backlog as P2
- Plan doc dropped: `2026-04-11-telegram-context-architecture.md`
- Blocked on: webhook exposure decision (ngrok/Cloudflare/static IP), iMessage deprecation timeline, model defaults per bot channel

## 2026-04-13 (distilled)
- Discovered `~/Work/coaches/health/` had real untracked content from Apr 8; git repo `health-coach/` was still an empty scaffold
- Merged all content from `health/` into `health-coach/office/` (CLAUDE.md, GOALS.md, log.md, roadmap.md, session-log.md, daily-nudge.py)
- Deleted orphaned `~/Work/coaches/health/` directory
- Updated and reloaded `com.dakotaops.healthnudge` launchd plist to point to new path
- Added `git pull` to `daily-nudge.py` so 6am script picks up latest GOALS.md from any device push
- Pushed all changes to `Roderick-Clemente/health-coach` on GitHub
- Open: `office/GOALS.md` needs weight target, workout routine, diet protocol, and sleep goals — nudges are generic until filled in

## 2026-04-15 (distilled)
- Pulled 28 days of mini work (5226eec → a576f86), 34 files fast-forward; committed `.claude/settings.json` and `_agent_office_/` inbox
- Read 2 Life Coach messages: Mar 18 local-model blocker for Tram 360 (HIGH); Apr 15 three fixes (Today.py cron MED, status staleness HIGH, Faith Coach LOW-MED)
- Mini state: Telegram bot live, dispatcher stack, health-coach consolidated, session rolling; Ollama installed but no model pulled
- Dakota-ops handoff: Devon owns `bot/pdf-extractor/` (mortgage PDF→CSV) with output-format examples + Medium article; Mad Max to review pipeline and propose batch/scheduled/Plaid/alerting enhancements
- Key dakota-ops commits: 95155da, 5696d0e, 1ddb006 in `~/Work/dakota-ops`
- Open: laptop evacuation from Mar 18 (async-comms, claude-life, recruiting) still pending
- Open: elevated permissions proposal still unresolved
- Next P0 for mini: `ollama pull llama3.3:8b` to unblock Tram 360
- Next for mini: status staleness cron (>2 days alert), Today.py → LaunchAgent replacing iPhone Shortcut, laptop evacuation

## 2026-04-16 (distilled)
- All 3 Telegram bots registered and live: @madmax_mini_bot, @healthcoach_rod_bot, @autodakota_mini_bot
- Health Coach bot: 6am + 6:30pm push notifications, AppleScript screen-lock send bug fixed
- AutoDakota bot: interactive queries for tasks, overdue items, team info
- 7:15am morning brief LaunchAgent fires daily with P0/P1 tasks + last session summary
- Telegram ops documented in `telegram-ops.md` skill; BotFather workflow self-sufficient going forward
- OpenBao token storage for Health Coach + AutoDakota pending (vault needs unsealing)

## 2026-04-16 (distilled)
- Built Health Coach Telegram bot stack: send helper, interactive poller, SOUL.md persona, LaunchAgent plist
- Built AutoDakota Telegram bot stack: same pattern, ops-only persona, separate LaunchAgent
- Fixed screen-lock AppleEvent timeout bug in daily.py (6:30pm) — swapped AppleScript/Shortcuts for Telegram primary + iMessage fallback
- Applied same Telegram-primary pattern to daily-nudge.py (6am) — both push bots now screen-lock-safe
- Credentials stored in Keychain; LaunchAgents configured with KeepAlive + RunAtLoad
- Created telegram-bots-setup.md with full setup walkthrough (~15 min)
- Open: Rod needs to register both bots via BotFather, capture tokens, get chat_ids, add Keychain entries, and load both LaunchAgents

## 2026-04-16 (distilled)
- Diagnosed 6:30pm send failures: root cause is AppleEvent timeouts when screen locked/idle, affecting Messages.app and Shortcuts Events
- Earlier switch to Shortcuts on Apr 14 (d0d7966) hit same wall
- Created `telegram_notify.py` — reads bot token + chat id from Keychain, pure HTTP, no AppleScript
- Wired both `daily.py` (6:30pm) and `daily-nudge.py` (6am) to use Telegram as primary, iMessage as fallback
- Blocker: Keychain creds `telegram-health-bot-token` and `telegram-health-chat-id` not yet set
- Open decision for Rod: reuse Mad Max bot creds (zero setup) vs. new dedicated health bot via BotFather (~5min, cleaner separation)
- Until creds set, bots fall back to flaky iMessage path
- Next: Rod picks option, stores creds in Keychain, then test

## 2026-04-17 (distilled)
- Refactored ArchiveLD.py from full-year to quarter-based archiving; accepts YEAR and QUARTER args, defaults to Q1 2020
- Auto-calculates date range for any quarter (Q1–Q4); runs in Pythonista or CLI (`python3 ArchiveLD.py 2020 1`)
- Pulled latest from dakota-software and pushed updated script
- Motivation: Rod left LD but wants calendar history for personal CRM; prior full-year 2020 run timed out on Dropbox write via Pythonista
- Smaller quarterly chunks expected to avoid timeout
- Open: Rod to test Q1 2020 via Pythonista shortcut → Dropbox
- Open: if Q1 works, archive Q2–Q4 2020 and later years (possibly batched)

## 2026-04-18 (distilled)
- Built `telegram-chat-review.sh` unified viewer for all 4 bots with claims/interleaved modes
- Extracted shared `claim_detector.py` to `~/Work/local/scripts/`; Health Coach + Mad Max pollers migrated and restarted
- Shipped Elite HH Coach bot (`@elitehh_rod_bot`): token in Keychain+OpenBao, poller live, SOUL.md with CAN/CANNOT
- Elite HH features: auto daily session summaries to `office/sessions/YYYY-MM-DD.md`, `/note` command, `[TASK:rod]` detection to task-inbox, 9pm digest via `com.elitehh.sessionsummary`
- Updated Mad Max skill with Telegram Chat Review section and capability boundaries
- Wrote `proposals/two-tier-telegram-dispatch.md` for big-ask vs quick-question routing — awaiting Rod review
- Processed and archived bottleMsg `2026-04-18-mad-max-telegram-audit.md`
- Decided: AutoDakota keeps inline claim detection (working, low priority); pipeline.md stays manual (table format too fragile for LLM)
- Open: Rod to confirm keyword triggers + confirmation gate in two-tier dispatch proposal
- Open: real job-hunting session test on `@elitehh_rod_bot` to verify 9pm summary fires; AutoDakota migration to shared module (backlog)

## 2026-04-19 (distilled)
- Built and shipped Manager Coach Telegram bot (@manager_coach_bot): poller with Claude/Ollama fallback, SOUL.md (Manager Tools + Sharon profile), daily 8:33am Mon-Sat nudge, LaunchAgents installed, creds in Keychain/OpenBao
- Created shared `ollama_dispatch.py` module with dynamic model discovery, preference-ordered dispatch, deep/fast tiers, compressed per-bot prompts
- Wired shared Ollama module into manager-coach, elite-hh, and health-coach bots; AutoDakota and Mad Max skipped (different dispatch patterns)
- Added `/models` command to manager-coach showing local models with strengths and use cases
- Pushed 3 repos: manager-coach (08864b2), madmax (9d7f681), elite-hh-bot, health-coach
- Rod feedback: GTD inbox sweeps must be processed together, not just filed/routed ("too filing clerk")
- Decisions: daily nudge at 8:33am (post-Dakota standup, pre-workday), no Sunday nudge, flexible shared Ollama module over hardcoded copy-paste
- Open on Rod: .kdbx files in bottleMsg destination, Mem Palace encryption angle
- Next: enrich bots' knowledge of local models for in-chat discussion; optionally wire shared dispatch into AutoDakota + Mad Max

## 2026-04-19 (distilled)
- GTD inbox swept: bottleMsg watcher TODO filed as P3 backlog; two .kdbx files surfaced to needs-rod.md pending destination
- Memory architecture audit across 5 layers of all agent repos — found duplication (team identities in 3 places, arm injury only in Mad Max SOUL.md, routing buried in 6 skill files)
- Designed Mem Palace at ~/Work/palace/ — shared read layer with rooms (rod/, team/, platform/, decisions/); agents get 1-line CLAUDE.md pointer
- Sent 3-part Telegram write-up of Mem Palace proposal to Rod
- Mem Palace added to backlog as P3; needs-rod.md created
- Blocker: awaiting Rod on .kdbx destination
- Blocker: Rod to pick encryption angle (FileVault check / encrypt palace dir / platform/security.md)
- Next: Phase 1 Mem Palace build (~2hrs) once encryption angle chosen
