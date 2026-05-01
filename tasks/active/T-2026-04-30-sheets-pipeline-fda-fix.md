---
id: T-2026-04-30-sheets-pipeline-fda-fix
title: Grant FDA to /bin/bash so PDF watchers can access Dropbox
owner: rod
status: open
priority: P0
urgency: time-sensitive
area: automation
waiting_on: Rod (manual System Settings step)
watchers: [max, devon]
source: 2026-04-30 session
updated: 2026-05-01
---

## What

macOS Full Disk Access (FDA) must be granted to `/bin/bash` in System Settings > Privacy & Security > Full Disk Access. This cannot be done programmatically.

## Why

Both PDF watcher LaunchAgents (`com.dakotaops.pdfwatch`, `com.dakotaops.pmwatch`) fail with "Operation not permitted" when trying to `find` in the Dropbox folder. No PDFs are processing automatically.

## Impact

- 4 PM Owner Statements stuck since Apr 25-29
- Mortgage pipeline would also fail on next drop
- Sheets bridge can't fire because nothing upstream works

## How

Fix prompt with full steps: `~/Work/dakota-software/bot/pdf-extractor/FIX-FDA-PROMPT.md`

## Unblocks

- T-2026-04-30-sheets-pipeline-wire-bridge (Max, P0)
