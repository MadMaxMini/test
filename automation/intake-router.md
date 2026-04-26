# Intake Router

Mad Max's intake system. Scans `~/Library/CloudStorage/Dropbox/bottleMsg/` for work drops and routes them into the task registry.

## How It Works

1. **Rod drops a file** to bottleMsg/ (from phone, laptop, or CLI)
2. **intake_router.py** (runs nightly via LaunchAgent) scans the folder
3. **Parses frontmatter** and infers task vs. note
4. **Creates canonical task** in `tasks/active/T-YYYY-MM-DD-NNNN-slug.md`
5. **Appends to notes** log
6. **Re-renders views** (blockers.md, by-area.md, standup.md)
7. **Archives drop** to `bottleMsg/archive/YYYY-MM-DD/`
8. **On failure**: Retries push once, then calls `notify.sh` alert + error exit

## Drop Format

### Minimal Note

No frontmatter required. Just drop a .md file:

```markdown
# Ollama models stuck on M4 GPU

Mistral pulls are hanging after 2GB. Suspect memory pressure.
```

This gets appended to `inbox/notes.md` with metadata (timestamp, source).

### Task Drop

Use frontmatter when the drop should become a canonical task:

```markdown
---
title: Test Mistral 27B on metal
owner: rod
priority: P1
urgency: context-sync
area: models
waiting_on: M4 GPU availability
next_action: Run benchmark on native metal vs Docker isolation
---

Rod gave the go-ahead to test both Tier 1 (native) and Tier 2 (Docker) paths.
Baseline is Claude token spend. Need 30 min uninterrupted on the mini.
```

Router will:
- Create `tasks/active/T-2026-04-25-NNNN-test-mistral-27b-on-metal.md`
- Append to `inbox/notes.md`
- Re-render `tasks/views/` files
- Move drop to `bottleMsg/archive/2026-04-25/`

### Field Reference

| Field | Required? | Values |
|-------|-----------|--------|
| `title` | Yes | One-liner |
| `owner` | No (defaults to rod) | rod |
| `priority` | No (defaults to P2) | P0, P1, P2 |
| `urgency` | No (defaults to waiting) | time-sensitive, blocker, ops-risk, context-sync, waiting |
| `area` | No (inferred from context) | models, services, agents, infra, skill, doc |
| `waiting_on` | No | person, system, approval, or description |
| `watchers` | No | [] (empty) or [names] |
| `next_action` | No | explicit next step |

## Commands

Scan inboxes (dry run):
```bash
python3 automation/intake_router.py scan
```

Process locally (no push):
```bash
python3 automation/intake_router.py process
```

Process, commit, and push:
```bash
python3 automation/intake_router.py process --pull --push
```

## Scheduling

LaunchAgent runs nightly:
```bash
launchctl load ~/Library/LaunchAgents/com.madmax.intakerouter.plist
```

Or trigger manually via `/loop`:
```bash
/loop /mad-max intake
```

## Reliability

- **Push failure**: Retries once (`git pull --rebase` → `git push`). If both fail, calls `notify.sh` and exits with error.
- **No silent drops**: All errors are logged to `automation/logs/intake-router.stderr.log` and alerted.
- **Idempotent**: Drops are archived after processing; next run won't re-process them.

## Troubleshooting

Check the logs:
```bash
tail -f automation/logs/intake-router.stdout.log
tail -f automation/logs/intake-router.stderr.log
```

If a drop is stuck (not archived), check:
1. Is the .md file still in bottleMsg/? (If so, why didn't it parse?)
2. Is `tasks/active/` writable? (permissions issue?)
3. Did the git push fail? (check stderr.log for "rejected" or "conflict")

Manually process one drop:
```bash
python3 automation/intake_router.py process --person rod --dry-run
```
