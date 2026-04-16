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
