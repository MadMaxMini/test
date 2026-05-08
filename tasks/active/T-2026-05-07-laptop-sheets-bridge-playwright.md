---
id: T-2026-05-07-laptop-sheets-bridge-playwright
title: Make Sheets bridge testable from Rod's laptop
owner: max
status: open
priority: P2
urgency: convenience
area: automation
waiting_on: None
watchers: [rod]
source: 2026-05-07 sheets bridge troubleshooting
updated: 2026-05-07
---

## Context

The production Google Sheets bridge automation runs on the Mac mini under the
`macBot` account. Rod's laptop is useful as a diagnostic console, but it cannot
currently run local bridge dry-runs because Playwright is not installed in the
local Python environment and the Dakota Dropbox folder is not mounted locally.

This is separate from production testing. Production testing still happens by
dropping PDFs into Dropbox and inspecting the Mac mini's committed logs/output.

## Scope

1. Decide whether Rod's laptop should have a local Playwright venv for bridge
   dry-runs.
2. If yes, create a laptop-local venv with Playwright installed.
3. Document the laptop command separately from the Mac mini command.
4. Confirm whether Dropbox Dakota folders should be mounted locally or whether
   laptop testing should use repo CSV fixtures only.

## Success Criteria

- [ ] Local command can import `playwright.sync_api`.
- [ ] Local bridge dry-run can run against repo CSV fixtures without writing to
      Google Sheets.
- [ ] Docs clearly distinguish laptop diagnostics from Mac mini automation.
