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
