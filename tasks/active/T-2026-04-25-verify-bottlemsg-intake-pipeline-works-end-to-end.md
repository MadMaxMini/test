---
id: T-2026-04-25-verify-bottlemsg-intake-pipeline-works-end-to-end
title: Verify bottleMsg intake pipeline works end-to-end
owner: rod
status: open
priority: P1
urgency: blocker
area: skill
waiting_on: 
watchers: []
source: intake: bottleMsg/test-intake-from-pipeline.md
updated: 2026-04-25
next_action: Run intake_router.py process --pull --push and check that views update
---

Testing the new intake system. This drop should:
1. Be scanned by intake_router.py
2. Create tasks/active/T-2026-04-25-NNNN-verify-bottlemsg-intake.md
3. Update tasks/views/blockers.md
4. Get archived to bottleMsg/archive/2026-04-25/

If this shows up in blockers.md after processing, the pipeline works.
