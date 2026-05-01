# Mad Max Startup Checklist

**Goal:** Get Rod oriented and into build mode as fast as possible.

---

## Mode Detection

- `/mad-max quick` or `/mad-max` + specific task → **Quick Start**
- `/mad-max full` → **Full Start**
- `/mad-max` with open-ended question ("what's on tap?") → Ask: "Quick or full?"

---

## Quick Start (default)

Read ONE file. Show the summary. Get to work.

```bash
cat ~/Work/test/morning-brief.md
```

- If brief is <24h old → show it, ask Rod what to build
- If brief is stale or placeholder → warn Rod, offer full start
- **Context budget: ~1 read. That's it.**

The morning brief is written nightly at 3:30am by `nightly-triage.py` (Gemma 3 27B).
It covers: Dakota max tasks, bot health, bottleMsg state, blockers.
Brief also lands in `bottleMsg/inbox/` so Rod sees it on his phone.

---

## Full Start

Deep sweep. Burns context but catches everything.

### Phase 1: Context Load

**1. Pull latest**
```bash
git pull
```

**2. Read this repo's structure**
- `tasks/views/blockers.md` — P0/P1 issues on the mini
- `tasks/views/by-area.md` — all open work (models, services, agents, infra, skill, doc)
- `tasks/backlog.md` — canonical roadmap
- `automation/logs/intake-log.md` — what got processed since last session

**3. Check inventory status**
- `inventory/status.md` — what's running (models, services, agent repos)
- `docs/reference/local-ai.md` — current model tiers and roadmap
- `docs/reference/harden.md` — system hardening status

---

### Phase 2: Dakota Hand-in-Glove

**This machine works with Dakota team.** You need to understand their state.

**1. Read Dakota's standup**
```bash
cd /Users/macBot/Work/dakota-software
git pull
cat team-standup/$(date +%Y-%m-%d).md
```
- Rod's top 3 + blockers
- Sharon's queue
- Devon's build lane
- Who's waiting on what

**2. Check Dakota's task registry**
```bash
cat tasks/views/max.md          # Max-owned + watched tasks (THIS IS YOUR INBOX)
cat tasks/views/standup.md      # all P0/P1/P2
cat tasks/views/blockers.md     # P0/P1 only
```

> **Max view is mandatory.** Any task with `owner: max` is work assigned to this machine.
> Surface all open Max tasks to Rod at session start. Don't skip this.

**3. Check if anything is blocked on the mini**
```bash
cd /Users/macBot/Work/test
grep -r "dakota\|coach\|agent" tasks/active/ 2>/dev/null
```
If mini tasks reference Dakota work, flag it in the Dakota coach skill when they session.

---

## Phase 3: Process Work (if any)

**1. Scan bottleMsg**
```bash
python3 automation/intake_router.py scan
```

**2. If drops exist, process them**
```bash
python3 automation/intake_router.py process --pull --push
```

**3. Check what was created**
```bash
cat tasks/views/blockers.md
cat automation/logs/intake-log.md | tail -20
```

---

## Phase 4: Session Context

**What to track:**
- What blockers are P0 (time-sensitive or ops-risk)?
- Who's waiting on what from the mini (models, services, agents)?
- Are any Dakota tasks depending on mini work?
- Any new agent repos to clone or update?

**Example session start (if you're part of a Dakota coach session):**
> "🏃 Rod: Here's the mini state — Mistral 27B is stuck on M4 GPU (P1 blocker), OpenBao is unsealed and running. Three old bottleMsg notes got ingested (Local AI stack, PM pipeline, encryption at rest). Your top 3 on Dakota side — let's see if any of them are waiting on mini work."

---

## Phase 5: Hand-off to Coach Skills

**If working with Dakota team** (Rod, Sharon, Doc, Devon):
- Use their coach skill (`/coach [name]`)
- Reference mini blockers when relevant ("Hey Rod, that encryption-at-rest proposal — do you need the mini to spin up a test container for it?")
- Offer to pull model benchmarks or run local tests if asked

**If working solo on mini**:
- Log to `docs/session-logs/YYYY-MM-DD.md`
- Track decisions in `decisions/` folder
- Update `inventory/status.md` after any service changes

---

## Reference: Dakota Patterns (Hand-in-Glove)

Dakota uses the **intake → normalize → view** pattern. Mad Max uses the same:

| Component | Dakota | Mad Max |
|-----------|--------|---------|
| **Intake** | `people/[name]/inbox/*.md` + LaunchAgent | `bottleMsg/*.md` + LaunchAgent |
| **Normalize** | `intake_router.py` → `tasks/active/` | `intake_router.py` → `tasks/active/` |
| **Generate** | `task_registry.py` → `tasks/views/` | `task_registry.py` → `tasks/views/` |
| **Parse** | Shared frontmatter logic (both hand-code) | `frontmatter.py` shared import |
| **Retry** | Original: silent push failure ⚠️ | Fixed: retry + notify |
| **Schedule** | `com.dakotaops.intakerouter.plist` (15min) | `com.madmax.intakerouter.plist` (nightly) |

**If Dakota merges their feature branch to main:**
- They will have the same intake + views pattern
- If they extract their shared automation to a library, Mini can import it
- For now, consider Mini's code a proof point for the pattern

---

## Quick Commands

```bash
# Check mini blockers
cat tasks/views/blockers.md

# Process bottleMsg work
python3 automation/intake_router.py process --pull --push

# Check Dakota state
cd /Users/macBot/Work/dakota-software && cat team-standup/$(date +%Y-%m-%d).md

# Create a new mini task
cat > tasks/active/T-$(date +%Y-%m-%d)-slug.md << 'EOF'
---
id: T-2026-04-25-NNNN-slug
title: Your task
owner: rod
status: open
priority: P1
urgency: blocker
area: models
waiting_on: None
watchers: []
source: manual/session
updated: 2026-04-25
---

Task body here.
EOF

# Render views after any task changes
python3 automation/task_registry.py render
```

---

## Session Close

1. Update `docs/session-logs/YYYY-MM-DD.md` (rolling log)
2. Check if any tasks changed state → update `tasks/active/` + regenerate views
3. Commit: `git add -A && git commit -m "session: YYYY-MM-DD — [summary]"`
4. Push: `git push origin main`

Done.
