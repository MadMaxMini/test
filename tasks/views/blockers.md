# Blockers

_Generated from `tasks/active/`. Do not edit directly._

- [P0] **Grant FDA to /bin/bash so PDF watchers can access Dropbox** (time-sensitive) - macOS Full Disk Access (FDA) must be granted to `/bin/bash` in System Settings > Privacy & Security > Full Disk Access. This cannot be done programmatically. [T-2026-04-30-sheets-pipeline-fda-fix](../active/T-2026-04-30-sheets-pipeline-fda-fix.md)
- [P0] **Wire sheets_bridge.py into mortgage auto-pipeline** (time-sensitive) - Phase 1 of the Sheets pipeline: Sharon drops a mortgage PDF → data extracted → Google Sheet updates automatically. The bridge script (`sheets_bridge.py`) is built and tested. It needs to be wired into `extract-and-commit.sh` so it fires automatically. [T-2026-04-30-sheets-pipeline-wire-bridge](../active/T-2026-04-30-sheets-pipeline-wire-bridge.md)
- [P1] **Test intake pipeline end-to-end** (blocker) - Verify that bottleMsg → intake_router → task_registry views works. [T-2026-04-25-0001-test-intake-pipeline](../active/T-2026-04-25-0001-test-intake-pipeline.md)
- [P1] **Verify bottleMsg intake pipeline works end-to-end** (blocker) - Testing the new intake system. This drop should: [T-2026-04-25-verify-bottlemsg-intake-pipeline-works-end-to-end](../active/T-2026-04-25-verify-bottlemsg-intake-pipeline-works-end-to-end.md)
