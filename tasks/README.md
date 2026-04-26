# Tasks

Canonical task records for the mini platform.

## Structure

- **active/** — Open and blocked tasks (T-YYYY-MM-DD-NNNN-slug.md)
- **done/** — Completed tasks, organized by date (YYYY-MM-DD/*.md)
- **views/** — Auto-generated views, do not edit directly

## Task Format

Frontmatter:
```yaml
---
id: T-2026-04-25-NNNN-slug
title: One-liner task description
owner: rod
status: open
priority: P0
urgency: time-sensitive
area: models
waiting_on: HuggingFace model publish
watchers: []
source: bottleMsg
updated: 2026-04-25
---
```

Body: context, next action, rationale.

## Intake

Tasks are created by `intake_router.py` reading drops from `~/Library/CloudStorage/Dropbox/bottleMsg/`. See `automation/intake-router.md` for details.
