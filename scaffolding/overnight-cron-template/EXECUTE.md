# Overnight Sheets-Pipeline Hardening Review — Execution Plan

**Scheduled wake:** 01:05 local Wednesday 2026-05-20
**Owner:** Future Claude (this is you reading this at 01:05)
**Context:** Rod asked at ~22:53 Tuesday to schedule this overnight review while he sleeps. Past-Claude (me, drafting at 22:55) prepped these artifacts before going dormant so future-you has clean inputs without burning a fresh window re-deriving project state.

## What Rod wants when he wakes

1. **A prioritized hardening doc** — items + recommendations spanning Phase 2 / Phase 4 / Phase 5 / Phase 6, ranked by impact × effort × risk
2. **Phase 2 triage explicitly carved out** — what's done, what's left, what stays in P2 vs punts to P4 (PM) or P5 (escrow/reconciliation)
3. **Safe-path code where appropriate** — new tests, helper modules in new files, OpenBao migration scaffolding, observability scripts. DO NOT touch the production-locked files (`sheets_bridge.py`, `extract_mortgage_data.py`, `property_map.json`, LaunchAgent plists) without explicit go-ahead — there is none here.

## Constraints

- **30-day no-build pact through 2026-06-10** — no new agents/coaches/services. Hardening of existing stuff is fine. New tests, new docs, scaffolding for already-planned moves (OpenBao, DuckDB prep) are fine. Net-new agents/daemons are NOT.
- **Cross-repo:** spans `~/Work/test` (this repo) AND `~/Work/dakota-software`. Most code lives in dakota.
- **Don't propose "fix" of day-of-month convention** — it's intentional design per `docs/sheets/do-not-fix.md`.

## Step-by-step

### Step 1 — Sanity check (5 min)

```bash
# Confirm both repos clean, no in-flight work
cd ~/Work/dakota-software && git status && git log --oneline -5
cd ~/Work/test && git status && git log --oneline -5

# Confirm Ollama is up and Gemma is free
curl -s localhost:11434/api/tags | head -20
```

### Step 2 — Build context bundle for Gemma (1 min)

```bash
bash /tmp/sheets-hardening/build-context.sh
ls -la /tmp/sheets-hardening/context-bundle.txt
# Should be a sizeable file (50-500KB depending on doc lengths). DO NOT cat or Read it into your window.
```

### Step 3 — Fire Gemma (background, ~10-30 min on 27B model)

```bash
# Run in background so you can prep synthesis while she chews
local-agent --file /tmp/sheets-hardening/context-bundle.txt \
  --model gemma3:27b \
  "$(cat /tmp/sheets-hardening/gemma-prompt.md)" \
  > /tmp/sheets-hardening/gemma-output.md 2>&1 &

echo "Gemma PID: $!" > /tmp/sheets-hardening/gemma.pid
```

If `local-agent` doesn't accept `--model`, fall back to whatever flag it does take (check `local-agent --help`). If it streams to stdout only, just redirect to file.

**Watch progress:** `tail -f /tmp/sheets-hardening/gemma-output.md` (or use Monitor tool)

### Step 4 — While Gemma chews, prep the synthesis skeleton (~5-15 min)

Create `~/Work/dakota-software/docs/sheets/2026-05-20-hardening-review.md` with sections:

1. **Executive summary** (fill in last)
2. **Phase 2 status** — done / in-flight / open
3. **Phase 2 triage** — table: items × {keep in P2 | punt to P4 | punt to P5 | drop}
4. **Cross-pipeline hardening recommendations** — table ranked by impact × effort
5. **Phase 6 DB-prep notes**
6. **Safe-path code shipped tonight** — links to commits/files
7. **Decisions Rod needs to make in the morning**

Fill in skeleton headers + your own initial thinking (without Gemma's output) so synthesis later is just slotting + filtering.

### Step 5 — Ingest Gemma's output, synthesize (~30-60 min)

```bash
wc -l /tmp/sheets-hardening/gemma-output.md
# Read the file — this IS allowed because it's Gemma's distilled output, not raw source
```

For each candidate Gemma surfaces:
- Verify against current repo state (memory is stale, things move)
- Slot into your Phase 2 triage table
- Promote / demote / drop based on risk × pact × roadmap fit
- Add your own items Gemma missed

### Step 6 — Safe-path code (~60-120 min)

Pick 2–5 items from the list that:
- Are confidently in scope (P2 hardening, not net-new)
- Touch only safe paths (new files, new tests, doc-only, or non-prod modules)
- Have clear rollback (just delete the new file)

Candidates to consider (verify they make sense after seeing Gemma's full list):
- Idempotency test for `sheets_bridge.py` (calls fixture, runs twice, asserts no deltas on 2nd run) — new test file
- Fix the 2 pre-existing failing mortgage-field tests (if root cause is small)
- OpenBao migration scaffolding for Playwright OAuth token (script that takes a path, stashes secret, returns retrieval helper — no wire-in yet)
- Dupe-log surfacing script (parse `sheets-dupes.log`, emit a summary, callable from morning brief)
- DuckDB schema sketch (just the SQL DDL, in `docs/db-migration/schema-v0.sql`)

DO NOT:
- Modify `sheets_bridge.py`, `extract_mortgage_data.py`, `property_map.json`, or LaunchAgent plists
- Add a new LaunchAgent or daemon (pact)
- Make changes that need Rod-side validation (year-flip ritual changes, new alerts firing)

### Step 7 — Commit + push (each repo as needed)

```bash
cd ~/Work/dakota-software
git add docs/sheets/2026-05-20-hardening-review.md  # plus any safe-path files
git commit -m "Hardening review 2026-05-20 — overnight pass + Gemma synthesis"
git push origin main  # main push pre-authorized per CLAUDE.md
```

Update session-log.md in ~/Work/test with what happened overnight.

### Step 8 — Telegram summary to Rod (so he sees it on phone)

End-of-run, send Rod a Telegram message via the established channel (look up the pattern — there's a notify path from the auto-agent setup). Brief: 1 paragraph summary + link to the doc + the top 3 decisions waiting on him.

If you can't figure out the Telegram send path in <10 min, skip it — the doc is on disk, he'll find it.

### Step 9 — Leave a clean breadcrumb

Update `/tmp/sheets-hardening/STATUS.md` with: when you started, when you finished, what got committed, anything that surprised you, anything you skipped and why.

## If something goes wrong

- **Gemma hangs or returns garbage:** Try llama3.1:8b or mistral-small as fallback. If all local models fail, skip Gemma entirely and do the synthesis yourself from the context bundle (read it directly).
- **Context bundle build fails:** Check file paths in `build-context.sh`. Both repos should exist. If `~/Work/test` files are missing, just bundle the dakota docs.
- **Both repos dirty when you wake:** STOP. Don't commit on top of unknown state. Write findings to `/tmp/sheets-hardening/findings-only.md` and let Rod sort it out.
- **You're running out of context window:** Stop writing code, finalize the doc, commit what you have, leave clear notes in STATUS.md.

## Posture reminders

- Match Rod's terseness preference (`feedback_rod_engagement_style.md`) — terse, mission-focused
- Challenge over agreement — if Gemma proposes something dumb, say so in the doc
- Mission = "take hours off Sharon's plate" — bias recommendations toward things that automate her validation/manual work
- Hardening ≠ feature work. Stay in the safety lane.
