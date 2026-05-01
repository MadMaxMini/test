/mad-max quick — Test Google Sheets bridge integration. Use Gemma as grunt worker.

## Pattern: Claude orchestrates, Gemma does the grunt

You are the decision layer. Gemma (via `local-agent`) does the file reading, test running,
and summarizing. You interpret Gemma's output and make decisions. This saves your tokens.

## Step 1 — Have Gemma run the full test suite and report back

```bash
python3 ~/Work/local/scripts/test-sheets-bridge.py 2>&1
```

This script:
- Checks FDA status (are PDF watchers alive?)
- Dry-runs the bridge on known-good 403 CSV
- Checks Playwright can launch
- Validates property_map.json
- Counts stuck PDFs
- Reads activity log
- Sends all output to Gemma for interpretation
- Writes report to `~/Work/test/morning-brief-sheets.md` + `bottleMsg/inbox/`

## Step 2 — Read Gemma's report

```bash
cat ~/Work/test/morning-brief-sheets.md
```

## Step 3 — You decide

Based on Gemma's report:

| Result | Action |
|--------|--------|
| All PASS | Proceed to wire bridge — read `~/Work/dakota-software/bot/pdf-extractor/WIRE-BRIDGE-PROMPT.md` |
| FDA FAIL | Tell Rod he needs to grant FDA in System Settings. Process stuck PDFs manually. |
| Playwright FAIL | Debug — check venv, browser install, network |
| Dry-run FAIL | Read `sheets_bridge.py` yourself to diagnose |

## Step 4 — Update task

```bash
# Have Gemma read the task and draft an update note
local-agent --quiet --file ~/Work/test/tasks/active/T-2026-04-30-sheets-pipeline-wire-bridge.md \
  "Add a status update to the Updates section. Today is $(date +%Y-%m-%d). Test results: [paste summary]. Keep it to 2-3 lines."
```

Review Gemma's draft, edit if needed, write to the task file.

## Key constraint
Do NOT read `sheets_bridge.py`, `property_map.json`, or other large files yourself unless
Gemma flags a problem that requires your judgment. Let Gemma do the reading.
