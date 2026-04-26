# Mad Max Autonomous Decision Architecture

**Last updated:** 2026-04-26  
**Status:** Design (ready for Rod review before build)

---

## Problem Statement

Mad Max needs to operate autonomously when Rod is not in the room — running the bot, night planner (10pm), and daily standup (7am) — while knowing when to escalate. The task registry (`tasks/views/`) is the source of truth. This document defines the decision tree, what each component reads/writes/triggers, and what goes to Rod via Telegram.

---

## Mental Model

Think of Mad Max as having **three autonomous agents** that don't sleep:

1. **Task Executor** — runs continuously, decides what to do next based on task state
2. **Night Planner** — runs at 10pm, proposes tomorrow's work and surfaces blockers
3. **Standup Surfacer** — runs at 7am, feeds the Dakota standup with mini + Dakota blockers

Each agent follows the **same decision framework:**
- Read the task views (`tasks/views/blockers.md`, `by-area.md`, `standup.md`)
- Apply the autonomy rules (see Decision Tree below)
- Take action or escalate
- Write what happened to a decision log
- Optionally notify Rod via Telegram (if material)

---

## Autonomy Rules: The Decision Tree

### Tier 1: Can Mad Max Do This Alone?

**YES (autonomous) — do it without asking:**

| Case | Rule | Why | Example |
|------|------|-----|---------|
| **P2, waiting** | Execute if work is setup/config (not decision) | Rod owns it but it's low-urgency; Mad Max can prep the table | "Install latest Ollama" is automatable; "choose between two model arches" is not |
| **P1, context-sync** | Execute if Rod owns the task and blockers are clear | Rod asked for it; the path is unambiguous | "Benchmark Mistral 27B on metal" — Rod owns it, method is known |
| **Admin / tooling** | Execute — this is Mad Max's domain | Intake, views, LaunchAgent setup, etc. | Re-render views after intake, update Telegram polling script |
| **Locked (waiting_on: person/system)** | Check status quietly, don't escalate unless overdue | Some blocker is external; Mad Max monitors without noise | Waiting on HuggingFace model publish — check once daily, don't bug Rod |

**ESCALATE TO ROD (Telegram alert, flag task, wait for input):**

| Case | Rule | Why | Example |
|------|------|-----|---------|
| **P0 or urgency: blocker/ops-risk** | Always escalate, even if unambiguous | These kill the system; Rod must decide priority | "OpenBao unsealing broken" — escalate now |
| **P0/P1 + no owner** | Escalate with "who owns this?" | Ownership ambiguity is a blocker | Task exists but owner field is empty |
| **P1/P0 + ambiguous next action** | Escalate with proposal | Need Rod's judgment on direction | "Optimize token spend" — propose 3 approaches, ask which |
| **Waiting on Rod's decision** | Don't pretend; escalate the blocker itself | Rod needs to unblock it | "Choose: Tier 1 native Ollama or Tier 2 Docker-isolated for DeepSeek?" |
| **Cross-repo blocker (Dakota context)** | Surface in standup; mention in night planner | Dakota context requires Dakota stakeholder input | "elite-hh-bot deploy blocked on manager-coach DB schema" |
| **Unknown urgency / area / priority** | Escalate with request for clarification | Can't decide without taxonomy | Task has no priority, area unclear |

---

## The Three Agents

### Agent 1: Task Executor (Continuous)

**Runs:** On startup, then hourly (or on-demand via `/loop`)  
**Reads:** `tasks/active/`, task metadata (status, priority, urgency, owner, waiting_on)  
**Writes:** Task status updates (open → in-progress → done), decision log  
**Triggers:** None directly; acts based on task state

#### Logic

1. **Filter to executable tasks:**
   - Status = `open` (not blocked, done, archived)
   - Priority = P1 or P2
   - Owner = rod
   - Waiting_on = None or status = "ready" (blocker lifted)

2. **For each executable task:**
   - Read task body, next_action field
   - Is the next action a decision or a runnable operation?
     - **Decision:** Escalate to Rod (see Decision Tree above)
     - **Operation:** Check autonomy rules
       - If in "YES" tier → mark as `in-progress`, do the work, mark as `done`, update views
       - If in "ESCALATE" tier → flag task with `[ESCALATE: reason]` comment, send Telegram alert

3. **Update and re-render:**
   - Commit status changes to git
   - Run `intake_router.py views` to regenerate `tasks/views/`
   - Push if no conflicts (if conflict, flag to Rod)

4. **Write decision log:**
   - Log each action taken (started task, skipped due to blocker, escalated, completed)
   - Include: task ID, action, reasoning, timestamp
   - File: `automation/logs/executor.log` (append-only, rotate daily)

#### Example

```
Task: T-2026-04-26-0005-test-ollama-models
Owner: rod
Status: open
Priority: P1
Urgency: context-sync
Next: Run benchmark on Mistral 27B native vs Docker

→ Executor reads this
→ Is it a decision? No, it's a runnable operation
→ Does Rod own it? Yes
→ Is it P1 + context-sync? Yes → in "YES" tier
→ Executor: marks as in-progress, runs the benchmark, marks done, pushes changes
→ Executor logs: "2026-04-26 09:15 COMPLETED T-2026-04-26-0005 (took 23 min)"
```

---

### Agent 2: Night Planner (Daily, 10pm)

**Runs:** Every night at 22:00 (cron job)  
**Reads:** `tasks/views/blockers.md`, `tasks/views/by-area.md`, executor's decision log  
**Writes:** Night planner proposal (sent to Rod via Telegram, also saved to bottleMsg)  
**Triggers:** Telegram message to Rod

#### Logic

1. **Harvest what's ready to do tomorrow:**
   - Read `by-area.md`, filter to: P1 + owner=rod + waiting_on=None
   - Rank by area and urgency (models > services > agents > infra > skill > doc)
   - Pick top 3–5 unblocked tasks

2. **Surface blockers that need Rod:**
   - Read `blockers.md` (P0 and P1 urgency:blocker tasks)
   - Filter out tasks Rod is already working on (status: in-progress)
   - If any blockers are overdue (created >2 days ago and still open) → flag as "ancient blocker"

3. **Compose the night planner message:**
   ```
   🌙 Tomorrow's Work — [3-5 tasks]
   
   Top Tasks:
   1. [Highest priority] T-2026-04-26-NNNN — one-liner
      • Owner: rod
      • Est. time: based on task body
   2. [Next highest] T-2026-04-26-NNNN — one-liner
   ...
   
   ⚠️ Blockers (needs your input):
   - [ANCIENT - 3 days] T-2026-04-25-NNNN — P0 blocker description
   - [NEW] T-2026-04-26-NNNN — P0 blocker description
   
   → If no blockers: (none today)
   → If no top tasks: (all waiting on dependencies)
   ```

4. **Send to Rod:**
   - Telegram bot message (not intrusive — async, no notification sound)
   - Subject line: `Mad Max: Tomorrow's Work — [task count] tasks`
   - Format: 1-liner per task + effort estimate (inferred from task body word count: <100 words = <30min, 100–300 = 30min–1hr, >300 = 1–2hr)

5. **Don't duplicate Rod's view:**
   - Night planner proposes, doesn't force
   - If Rod checks `blockers.md` in the morning, he sees the same P0/P1 items
   - Night planner is the "here's what I think you should do" voice, not the law

6. **Write proposal to bottleMsg:**
   - Save proposal as `bottleMsg/planner-proposals/2026-04-26-night-proposal.md`
   - If Rod doesn't like the proposal, he can edit it or ignore it
   - Proposals archive after 3 days (non-blocking)

7. **Write decision log:**
   - File: `automation/logs/night-planner.log`
   - Include: proposals made, blockers surfaced, reasoning per task

---

### Agent 3: Standup Surfacer (Daily, 7am)

**Runs:** Every morning at 07:00 (cron job)  
**Reads:** `tasks/views/standup.md` (mini blockers), cross-repo blockers (Dakota bots)  
**Writes:** Standup message to Dakota group  
**Triggers:** AutoDakota_Notify_Group (iMessage)

#### Logic

1. **Harvest mini blockers:**
   - Read `tasks/views/standup.md` (generated by intake router)
   - Extract P1 tasks with next action (keep format: area + title + next action + wait list)

2. **Harvest Dakota blockers (cross-repo):**
   - Read status from each Dakota bot repo:
     - `~/Work/dakota-software/bot/tasks/views/standup.md` (if exists)
     - `~/Work/coaches/elite-hh-bot/office/bot/tasks/views/standup.md` (if exists)
     - `~/Work/coaches/health-coach/office/bot/tasks/views/standup.md` (if exists)
   - For each repo, pick P1 tasks only
   - Merge by priority (P0 first, then P1) + repo (ops > coaches)

3. **Format for Dakota standup:**
   ```
   | Person | Task | Status | Blocker | Link |
   |--------|------|--------|---------|------|
   | Rod (mini) | Test intake pipeline | in-progress | None | T-2026-04-25-0001 |
   | Rod (Dakota) | Model approval gates | blocked | Waiting on engineering → [link] |
   | Devon (elite-hh) | Job lead scoring | open | None | [link] |
   ```

4. **Send to Dakota group:**
   - Telegram: No (standup is iMessage only)
   - iMessage: Send via `AutoDakota_Notify_Group` shortcut
   - Format: table (scannable, shows blockers at a glance)
   - Include: person + task + status + blocker + link to task

5. **Handle missing repos:**
   - If a Dakota bot repo doesn't have `tasks/views/standup.md`, skip it silently (no error)
   - Log: `"standup.md not found in [repo], skipping"` to executor.log

6. **Write decision log:**
   - File: `automation/logs/standup-surfacer.log`
   - Include: repos scanned, tasks merged, message sent timestamp

---

## Data Flow: What Reads What

```
┌─────────────────────────────────────────────────────────────────┐
│ Input                                                             │
└─────────────────────────────────────────────────────────────────┘
    ↓
    • bottleMsg/          ← Rod drops work
    • Manual task edits   ← Rod or Mad Max edit active/*.md
    • External systems   ← HuggingFace API, Docker, etc.

┌─────────────────────────────────────────────────────────────────┐
│ intake_router.py (runs nightly, on-demand)                      │
│ • Scans bottleMsg/                                               │
│ • Creates tasks/active/T-YYYY-MM-DD-NNNN-slug.md               │
│ • Renders: views/blockers.md, views/by-area.md, views/standup.md│
└─────────────────────────────────────────────────────────────────┘
    ↓
    • tasks/active/*.md          (source of truth)
    • tasks/views/*.md           (auto-generated, don't edit)

┌─────────────────────────────────────────────────────────────────┐
│ Three Autonomous Agents (read task views)                        │
└─────────────────────────────────────────────────────────────────┘
    ↓
    • Task Executor                → reads active/*, writes status changes
    • Night Planner (10pm)          → reads by-area.md, blockers.md
    • Standup Surfacer (7am)        → reads standup.md, cross-repo views

┌─────────────────────────────────────────────────────────────────┐
│ Output                                                            │
└─────────────────────────────────────────────────────────────────┘
    ↓
    • Telegram: Executor escalations, Night Planner proposals
    • iMessage: Standup via AutoDakota_Notify_Group
    • Git: Task status updates, view regenerations, logs
    • bottleMsg: Night planner proposals (saved for Rod's review)
```

---

## Telegram Bot Digest: Smart Alerting

**Problem:** Telegram bot runs hourly, pulls task views. Don't spam Rod with the full views; only show what changed.

**Solution:** Maintain a changes.log file (delta tracking).

### Changes.log Format

```yaml
---
timestamp: 2026-04-26T08:34:00Z
agent: executor
---

task_created:
  - T-2026-04-26-0010: Setup OpenBao secrets vault (P1, blocker)

task_status_changed:
  - T-2026-04-25-0001: open → in-progress (Test intake pipeline)

task_urgency_changed:
  - T-2026-04-25-0003: waiting → time-sensitive (Ollama model pulls)

blocker_overdue:
  - T-2026-04-25-0002: created 2026-04-24, still blocked on "HuggingFace token"
```

### Telegram Digest Logic

**On each hourly run (or more frequent if needed):**

1. Read `changes.log` (or diff task views against last-known state)
2. Filter to significant changes (ignore P3, ignore status:done)
3. Compose a message:
   ```
   📋 Mad Max Changes (last hour)
   
   ✅ Started: T-2026-04-26-0005 — Test Ollama models
   
   🆕 New Tasks:
   • T-2026-04-26-0010 — Setup OpenBao vault (P1, blocker)
   
   ⚠️ Urgency Bumped:
   • T-2026-04-25-0003 — Ollama model pulls (time-sensitive now)
   
   🔴 Ancient Blockers (>2 days):
   • T-2026-04-25-0002 — Waiting on HuggingFace token (created 2026-04-24)
   
   → No new escalations
   → 3 tasks in progress
   ```

4. Send to Rod if there are changes; skip if nothing changed (don't spam empty updates)

5. Append to changes.log, then rotate (archive when log > 100 lines)

---

## Escalation Channels: What Goes Where

| Event | Channel | Format | Trigger |
|-------|---------|--------|---------|
| **P0 blocker** | Telegram (immediate) | "🔴 BLOCKER: [task] — Rod input needed" | Executor finds P0 urgency:blocker |
| **Ambiguous task** | Telegram (immediate) | "❓ Need clarification: [task] — proposal in bottleMsg" | Executor can't decide |
| **Night planner** | Telegram (async) | "🌙 Tomorrow: 3 tasks + blockers" | Nightly 22:00 |
| **Morning standup** | iMessage (Dakota group) | Table: person + task + status + blocker | Daily 07:00 |
| **Ancient blocker** | Telegram (daily in night planner) | "⚠️ [ANCIENT - X days] [task]" | Nightly 22:00 if age >2 days |
| **Executor decision log** | File only (bottleMsg-archived) | `automation/logs/executor.log` | Every action (no Telegram) |

---

## Example Walkthrough: One Day in the Life

**Scenario:** Rod has 3 tasks in the queue: intake pipeline test (P1), Ollama benchmark (P1), and OpenBao setup (P2).

### 7:00 AM — Standup Surfacer Runs

```
1. Reads tasks/views/standup.md (mini P1 tasks)
   - Test intake pipeline (in-progress)
   - Verify bottleMsg intake (open, blocked on intake test)
   
2. Reads Dakota bot standup.md files
   - elite-hh-bot: Job score model (open)
   - health-coach: Exercise intake (blocked)
   
3. Merges and sends iMessage to Dakota group:
   
   | Person | Task | Status | Blocker |
   |--------|------|--------|---------|
   | Rod | Test intake pipeline | in-progress | None |
   | Rod | Verify bottleMsg | open | Waiting on intake test |
   | Devon | Job score model | open | None |
   | Ashley | Exercise intake | blocked | Db schema change pending |
   
4. Logs to standup-surfacer.log: "2026-04-26 07:01 Standup sent (4 tasks, 1 blocker)"
```

### 9:00 AM — Task Executor Hourly Run

```
1. Reads tasks/active/
   - T-2026-04-25-0001: Test intake pipeline (P1, in-progress, owner: rod, waiting: None)
   - T-2026-04-25-0003: Verify bottleMsg (P1, open, owner: rod, waiting: "intake test done")
   - T-2026-04-26-0005: Benchmark Mistral (P1, open, owner: rod, waiting: None)
   
2. Applies autonomy rules:
   
   T-2026-04-25-0001 (intake test, in-progress):
   → Already started by Rod. Executor checks if unblocked and ready.
   → Status: in-progress, no blockers → Skip (Rod is working on it)
   → Log: "SKIPPED (in-progress by rod)"
   
   T-2026-04-25-0003 (verify bottleMsg, open):
   → Waiting on: "intake test done"
   → Current status of T-2026-04-25-0001: in-progress (not done yet)
   → Blocked. Log: "BLOCKED (waiting: T-2026-04-25-0001 not done)"
   → Do NOT escalate (Rod knows it's blocked)
   
   T-2026-04-26-0005 (benchmark Mistral, open):
   → P1, context-sync, owner: rod, waiting: None
   → Autonomy rule: YES (P1 + context-sync + unblocked)
   → But: Benchmark = computational work that takes 30+ min
   → Executor's logic: Does this need Rod's judgment? No, method is clear.
   → Action: Mark as in-progress, start benchmark, update task with interim results
   → Log: "STARTED T-2026-04-26-0005 (Mistral benchmark in progress)"
   
3. Renders views (changes detected: T-2026-04-26-0005 now in-progress)
   → changes.log: task_status_changed T-2026-04-26-0005: open → in-progress
   
4. Sends Telegram digest (changes):
   "✅ Started: T-2026-04-26-0005 — Benchmark Mistral 27B (est. 45 min)"
```

### 10:00 PM — Night Planner Runs

```
1. Reads tasks/views/by-area.md, blockers.md
   - Intake test: in-progress (skip)
   - Verify bottleMsg: blocked (skip)
   - Benchmark Mistral: in-progress (skip)
   
   → No unblocked, open P1 tasks for tomorrow
   → All current work is in-progress
   
2. Checks blockers.md:
   - No P0 urgency:blocker tasks
   - All P1 tasks are accounted for in by-area.md
   
3. Composes proposal:
   "🌙 Tomorrow's Work
   
   ✅ Continuing Today:
   • T-2026-04-26-0005 — Benchmark Mistral (in-progress, ~45 min remaining)
   
   ⏳ Waiting to Unblock:
   • T-2026-04-25-0003 — Verify bottleMsg intake (blocked on intake test)
   
   → No new tasks ready for tomorrow. All hands on current batch."
   
4. Sends Telegram: "🌙 Mad Max: Tomorrow — all hands on current batch"
5. Saves proposal to bottleMsg/planner-proposals/2026-04-26-night-proposal.md
6. Logs: "PROPOSAL (no new tasks ready; 1 in-progress; 1 blocked)"
```

### 10:30 PM — Executor Hourly Run (Finishing)

```
1. Benchmark finishes. Executor detects:
   T-2026-04-26-0005 status: in-progress → done
   Writes results to task body.
   
2. Updates status to: done
3. Renders views (T-2026-04-26-0005 removed from by-area.md / moved to done archive)
4. Commits and pushes
5. Sends Telegram: "✅ Completed: T-2026-04-26-0005 — Benchmark Mistral (results in task)"
6. Logs: "COMPLETED T-2026-04-26-0005 (results: Mistral 27B 18s/call, 4.2/5 rating)"
```

---

## Files Created / Modified

| File | Created? | Who | When | Purpose |
|------|----------|-----|------|---------|
| `tasks/active/T-*.md` | Y | intake_router | on drop | Canonical task record |
| `tasks/views/blockers.md` | N (auto-gen) | intake_router | after intake | P0/P1 view |
| `tasks/views/by-area.md` | N (auto-gen) | intake_router | after intake | Area-grouped view |
| `tasks/views/standup.md` | N (auto-gen) | intake_router | after intake | Standup-format view |
| `automation/logs/executor.log` | Y | executor | continuous | Decision log (append) |
| `automation/logs/night-planner.log` | Y | night-planner | nightly | Proposals + blocker log |
| `automation/logs/standup-surfacer.log` | Y | standup-surfacer | daily 7am | Standup generation log |
| `automation/logs/changes.log` | Y | executor/intake | on change | Delta log for Telegram |
| `bottleMsg/planner-proposals/YYYY-MM-DD-*.md` | Y | night-planner | nightly | Proposal for Rod review |

---

## Configuration & Triggers

### LaunchAgents / Cron

| Agent | Schedule | Plist / Cron | Command |
|-------|----------|-------------|---------|
| **Executor** | Hourly (on :00) | `com.madmax.executor.plist` | `python3 automation/executor.py run` |
| **Night Planner** | Daily 22:00 | `com.madmax.night-planner.plist` | `python3 automation/night_planner.py run` |
| **Standup Surfacer** | Daily 07:00 | `com.madmax.standup.plist` | `python3 automation/standup_surfacer.py run` |
| **Intake Router** | Nightly 01:00 | `com.madmax.intakerouter.plist` | `python3 automation/intake_router.py process --pull --push` |

**Status:** Plist files live in `~/Library/LaunchAgents/`. Intake router already exists; executor, night-planner, standup need to be created.

---

## Safety & Rollback

### If Something Goes Wrong

1. **Executor gets stuck on a task:** Remove `status: in-progress` from the task file, mark as `open` instead. Next run will skip it.
2. **Changes.log explodes:** Rotate it manually: `mv automation/logs/changes.log automation/logs/changes.log.$(date +%s)`, recreate.
3. **Night planner sends wrong message:** Read `night-planner.log` to see what it proposed, then edit the Telegram message or ask Rod to clarify tomorrow.
4. **Standup includes wrong repos:** Edit the list of repos to scan in `automation/standup_surfacer.py` (env var or config file).

### Monitoring

All three agents log to `automation/logs/`. Rod can check logs anytime:

```bash
tail -f automation/logs/executor.log           # What executor is doing
tail -f automation/logs/night-planner.log      # What planner proposed
tail -f automation/logs/standup-surfacer.log   # Standup merges
```

### Disable Mode (If Needed)

Temporarily disable any agent:

```bash
launchctl unload ~/Library/LaunchAgents/com.madmax.AGENT.plist
```

Re-enable:

```bash
launchctl load ~/Library/LaunchAgents/com.madmax.AGENT.plist
```

---

## Next: Implementation Checklist

- [ ] Build `automation/executor.py` (Task Executor)
- [ ] Build `automation/night_planner.py` (Night Planner)
- [ ] Build `automation/standup_surfacer.py` (Standup Surfacer)
- [ ] Create plist files for all three in `~/Library/LaunchAgents/`
- [ ] Test on mini: verify task views render, executor runs, Telegram sends
- [ ] Rod reviews and approves before running live
- [ ] Set cron triggers live

---

## Open Questions for Rod

1. **Effort estimates in night planner:** Should I infer time from task body word count, or does Rod want to manually tag each task with `est_time: 30m`?
2. **Cross-repo blockers:** Which Dakota repos should standup surfacer scan? (Currently: dakota-software, elite-hh-bot, health-coach)
3. **Telegram digest frequency:** Hourly is noisy; should I batch to "once per 3 hours" or "only send if something changed"?
4. **Night planner timing:** 10pm every day, or only weekdays? Should it skip Sunday night?
5. **Executor autonomy ceiling:** Are there any task areas (e.g., "models") where I should never auto-execute, even if unblocked?

---

**Ready for Rod to review, ask questions, and guide the build.**
