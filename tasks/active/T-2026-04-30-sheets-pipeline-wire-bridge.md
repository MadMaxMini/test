---
id: T-2026-04-30-sheets-pipeline-wire-bridge
title: Wire sheets_bridge.py into mortgage auto-pipeline
owner: max
status: blocked
priority: P0
urgency: time-sensitive
area: automation
waiting_on: FDA permissions (Rod manual step)
watchers: [rod, devon]
source: 2026-04-30 session
updated: 2026-05-01
---

## Context

Phase 1 of the Sheets pipeline: Sharon drops a mortgage PDF → data extracted → Google Sheet updates automatically. The bridge script (`sheets_bridge.py`) is built and tested. It needs to be wired into `extract-and-commit.sh` so it fires automatically.

## Blocker

**FDA (Full Disk Access)** not granted to `/bin/bash` in System Settings. Both PDF watcher LaunchAgents (`com.dakotaops.pdfwatch`, `com.dakotaops.pmwatch`) fail with "Operation not permitted." Rod must grant this manually in System Settings > Privacy & Security > Full Disk Access.

Fix prompt: `~/Work/dakota-software/bot/pdf-extractor/FIX-FDA-PROMPT.md`

## Next Action (after FDA is fixed)

Follow the wire-bridge prompt exactly:
`~/Work/dakota-software/bot/pdf-extractor/WIRE-BRIDGE-PROMPT.md`

1. Edit `extract-and-commit.sh` — add bridge call after extractor, before git add
2. Update notification routing (iMessage group → Telegram to Rod)
3. Same notification fix in `extract-pm-and-commit.sh`
4. Test with `--dry-run` on existing 403 CSV
5. Commit and push

## Also

4 stuck PM PDFs in `pm-statements-inbox/` (Apr 25-29). Can process manually.

## Key Files

- Bridge: `~/Work/dakota-software/bot/pdf-extractor/sheets_bridge.py`
- Plan: `~/Work/dakota-software/bot/pdf-extractor/WIRE-BRIDGE-PLAN.md`
- Shell pipeline: `~/Work/dakota-software/bot/pdf-extractor/extract-and-commit.sh`
- Status digest: `bottleMsg/inbox/2026-04-30-sheets-pipeline-status.md`
