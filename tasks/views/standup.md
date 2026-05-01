# Standup View

_Generated from `tasks/active/`. Do not edit directly._

## P0

- **Automation:** Grant FDA to /bin/bash so PDF watchers can access Dropbox
  - Next: macOS Full Disk Access (FDA) must be granted to `/bin/bash` in System Settings > Privacy & Security > Full Disk Access. This cannot be done programmatically.
  - Waiting: Rod (manual System Settings step)
  - [T-2026-04-30-sheets-pipeline-fda-fix](../active/T-2026-04-30-sheets-pipeline-fda-fix.md)
- **Automation:** Wire sheets_bridge.py into mortgage auto-pipeline
  - Next: Phase 1 of the Sheets pipeline: Sharon drops a mortgage PDF → data extracted → Google Sheet updates automatically. The bridge script (`sheets_bridge.py`) is built and tested. It needs to be wired into `extract-and-commit.sh` so it fires automatically.
  - Waiting: FDA permissions (Rod manual step)
  - [T-2026-04-30-sheets-pipeline-wire-bridge](../active/T-2026-04-30-sheets-pipeline-wire-bridge.md)

## P1

- **Skill:** Test intake pipeline end-to-end
  - Next: Verify that bottleMsg → intake_router → task_registry views works.
  - Waiting: None
  - [T-2026-04-25-0001-test-intake-pipeline](../active/T-2026-04-25-0001-test-intake-pipeline.md)
- **Skill:** Verify bottleMsg intake pipeline works end-to-end
  - Next: Testing the new intake system. This drop should:
  - [T-2026-04-25-verify-bottlemsg-intake-pipeline-works-end-to-end](../active/T-2026-04-25-verify-bottlemsg-intake-pipeline-works-end-to-end.md)
