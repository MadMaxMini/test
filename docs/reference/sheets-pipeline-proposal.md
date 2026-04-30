# Sheets Pipeline Proposal — PDF-to-Google-Sheets Automation

**Created:** 2026-04-29
**Status:** Phase 1 built + tested (2026-04-29)
**Depends on:** gsheets_sync.py (working), PDF extractors (working), launchd triggers (working)

---

## Problem

Sharon drops mortgage and PM statement PDFs into Dropbox. The extractors run, CSVs land in the repo, git commits go out. But the Google Sheets that Rod and the team actually *look at* are updated manually. The CSVs are the source of truth nobody reads.

## Goal

When a PDF drops, the extracted data flows all the way through to the Google Sheet — automatically, reliably, with no manual step. The repo CSV remains the source of truth. The Sheet is a live view.

---

## Architecture

```
Sharon drops PDF(s) into Dropbox
        │
        ▼
launchd WatchPaths fires
        │
    ┌───┴───┐
    │ lock  │  lockfile prevents concurrent runs
    │ wait  │  10s debounce for Dropbox sync
    └───┬───┘
        │
        ▼
Classify PDFs (mortgage vs PM)
        │
    ┌───┴────────────┐
    │                │
    ▼                ▼
extract_mortgage  extract_pm
    │                │
    ▼                ▼
CSV (repo)       CSV (repo)
    │                │
    └───┬────────────┘
        │
        ▼
sheets_bridge.py
  - maps property → sheet slug (via property_map.json)
  - builds cell updates per PDF type
  - calls gsheets_sync.py batch
        │
        ▼
Google Sheet updated (Playwright)
        │
        ▼
Single git commit (all CSVs)
        │
        ▼
Notification (iMessage to Dakota group)
        │
        ▼
(Optional) Periodic integrity check
```

---

## Phases

### Phase 1 — Sheets Bridge (the glue)

**What:** After extraction, write key values to Google Sheets via Playwright.

**New files:**
- `bot/pdf-extractor/property_map.json` — maps loan number / property address to sheet slug and cell mappings
- `bot/pdf-extractor/sheets_bridge.py` — reads extractor output, builds updates JSON, calls gsheets_sync.py

**property_map.json structure:**
```json
{
  "properties": [
    {
      "slug": "kickapoo-401",
      "match": {
        "address_contains": "401 KICKAPOO",
        "loan_number": "XXXXXXXXXX"
      },
      "mortgage_cells": {
        "C17": "current_payment",
        "C18": "escrow_balance"
      },
      "pm_cells": {
        "C16": "gross_rent",
        "C19": "mgmt_fee"
      }
    }
  ]
}
```

**How it's called:** From the shell scripts, after extraction, before git commit:
```bash
GSHEETS_PYTHON=~/Work/local/scripts/.venv/bin/python3
"$GSHEETS_PYTHON" bot/pdf-extractor/sheets_bridge.py \
    --type mortgage \
    --data-dir "$OUTPUT" \
    --property-map bot/pdf-extractor/property_map.json \
    >> "$LOG" 2>&1 || true
```

`|| true` — Sheets failure must never block the git commit. CSV is canonical.

**Scope:** Info tab only (C16-C19 summary cells). No tab history rows yet.

**Portable?** Yes. `sheets_bridge.py` calls `gsheets_sync.py` as a subprocess. Each uses its own venv. Only the path to `gsheets_sync.py` is machine-specific (one env var or config line).

---

### Phase 2 — Unified Pipeline Script

**What:** Merge the two shell scripts into one. Right now there are two near-identical launchd pipelines (`extract-and-commit.sh`, `extract-pm-and-commit.sh`) with separate lockfiles, separate debounce, separate git commits, separate notifications.

**Why:** If Sharon drops a mortgage PDF and a PM PDF within 10 seconds, you get two git commits, two iMessage notifications, two Playwright browser launches. Wasteful and noisy.

**Design:**
- Single `extract-pipeline.sh` triggered by WatchPaths on both inbox directories
- Single lockfile, single debounce window
- Classify each PDF (mortgage vs PM) and route to the right extractor
- One `sheets_bridge.py` call with all updates batched
- One git commit
- One notification summarizing everything

**Debounce strategy:**
- First trigger grabs lock
- Wait 10s (Dropbox sync)
- Count PDFs across both inboxes
- If count changed during wait, wait another 5s (Sharon still dropping)
- Process everything in one pass

---

### Phase 3 — Tab History Rows

**What:** Beyond updating summary cells on the Info tab, append statement rows to the appropriate history tabs.

**Tabs and data:**

| PDF Type | Tab | Row data |
|----------|-----|----------|
| Mortgage | Mortgage | Date, principal, escrow, payment, rate |
| PM | Rent | Date, gross rent, vacancy, distribution |
| PM | PM Cash Tracking | Date, mgmt fee, maintenance, other expenses |

**Challenge:** Appending rows via Playwright requires finding the next empty row. Options:
- Read column A downward until empty (slow, one cell at a time)
- Dump tab as CSV, count rows, write to row N+1 (fast but assumes no gaps)
- Use Ctrl+End to find last used cell (browser keyboard shortcut)

Best approach: dump the tab CSV (fast, no browser), count data rows, then write via batch starting at the next row.

**Dedup:** Before appending, check if statement date already exists in the tab. The dump approach makes this a simple string search.

---

### Phase 4 — Integrity Check

**What:** Periodic job that compares CSV data against Google Sheet values. Flags mismatches.

**Design:**
- Cron or scheduled agent (not tied to PDF drops)
- For each property: dump each Sheet tab as CSV, compare against repo CSVs
- Report: which cells are out of sync, which direction (Sheet ahead of CSV or vice versa)
- Notify via Telegram (not iMessage — this is operational, not team-facing)

**Frequency:** Weekly, or on-demand via `/check-sheets` command.

**Why separate:** If the Sheets write in Phase 1 silently fails (browser session expired, DOM changed, Playwright crash), the CSV is still correct. This catch-net tells you before it matters.

---

### Phase 5 — More Properties

**What:** As Rod shares more property Sheet IDs:
- Add to `SHEET_MAP` in `gsheets_sync.py`
- Add to `property_map.json` with cell mappings
- If sheet layout differs, document the layout and adjust cell mappings

No code changes needed if the layout matches the Kickapoo template.

---

## Execution Tiers

Each pipeline run uses a tiered approach — script does the work, agent validates, human decides on exceptions.

```
┌─────────────────────────────────────────────────────┐
│ Tier 1: Python Script (sheets_bridge.py)            │
│   - Dumb. Fast. Portable. No AI.                    │
│   - Maps property → cells → writes to Sheet.        │
│   - Handles the happy path. 95% of runs land here.  │
│   - Works on any machine with Playwright installed.  │
└──────────────────────┬──────────────────────────────┘
                       │ after write
                       ▼
┌─────────────────────────────────────────────────────┐
│ Tier 2: Local Validation Agent (Ollama)             │
│   - Dumps the Sheet, reads the CSV, compares.       │
│   - Flags anomalies: "$0.00 rent", escrow doubled,  │
│     missing data, values outside expected range.     │
│   - Simple prompt to Llama 3.3 or Qwen:             │
│     "Here's the CSV row, here's the Sheet.           │
│      Do these match? Are values reasonable?"         │
│   - No internet, no API keys. Runs locally.          │
│   - Optional — pipeline works without it.            │
└──────────────────────┬──────────────────────────────┘
                       │ if anomaly detected
                       ▼
┌─────────────────────────────────────────────────────┐
│ Tier 3: Escalation (Telegram to Rod)                │
│   - Structured message with context:                 │
│     "kickapoo-401: mortgage changed $1,200 → $0.00  │
│      — looks wrong. Approve / Reject / Ignore"       │
│   - Rod replies in Telegram, bot acts on response.   │
│   - Falls back to logging if Telegram unavailable.   │
└─────────────────────────────────────────────────────┘
```

**Why this layering:**
- Tier 1 alone is fully portable and covers most runs
- Tier 2 adds a safety net without external dependencies (Ollama is already on the mini)
- Tier 3 keeps a human in the loop for genuine anomalies, not routine writes
- Each tier degrades gracefully — if Ollama is down, skip validation. If Telegram is down, log the flag.

---

## Sheet Template Strategy

**Decision: Standardize the template, but support per-property overrides.**

All property sheets should follow the same cell layout (C16=Rent, C17=Mortgage, C18=Escrow, C19=PM Fees, etc.). This makes the bridge script dead simple — same cells every time, one template for new properties.

But `property_map.json` supports per-property cell overrides as an escape hatch. If one sheet is temporarily misaligned, override just that property's cells without touching code.

```json
{
  "properties": [
    {
      "slug": "kickapoo-401",
      "match": { "address_contains": "401 KICKAPOO" },
      "cells": null
    },
    {
      "slug": "some-weird-property",
      "match": { "address_contains": "123 ODD ST" },
      "cells": {
        "mortgage": "D17",
        "escrow": "D18"
      }
    }
  ],
  "defaults": {
    "mortgage_cells": { "C17": "current_payment", "C18": "escrow_balance" },
    "pm_cells": { "C16": "gross_rent", "C19": "mgmt_fee" }
  }
}
```

Convention over configuration. `cells: null` = use defaults. Only specify overrides when a sheet deviates.

**Open question:** Fix existing sheets to match the template now, or map their current layouts first? Recommendation: dump both Kickapoo sheets, compare layouts, fix any differences before Phase 1 build. One-time cost avoids per-property config debt.

---

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| CSV is source of truth | Yes | Sheets can be rebuilt from CSV. Not the other way around. |
| Sheets write is fire-and-forget | `\|\| true` | Never block git commit or notification on Sheets failure |
| Subprocess, not import | gsheets_sync.py called via shell | Different venvs, clean separation, portable |
| Property mapping by loan number | Primary key | Address strings vary by servicer. Loan number is stable. |
| Address substring as fallback | For PM statements | PM statements may not include loan numbers |
| Single browser launch per batch | batch command | 8s load time per launch — batch everything into one |
| Debounce at shell level | sleep + recount | Simple, proven, already in use |

## What I Need From Rod

1. ~~**Loan numbers** for kickapoo-401 and kickapoo-403~~ — DONE (401: 0539476986, 403: 0539476416)
2. ~~**Confirmation** that the Info tab cell layout is the same~~ — DONE (financial rows 16-23 match, Info is a formula rollup from source tabs)
3. ~~**Which phase to start building**~~ — Phase 1 built and tested 2026-04-29
4. **Additional properties** — Rod added sheet IDs for grand-pines-2889, la-estancia-2922, piney-point-8808, cash-tracking. Need loan numbers + verify Mortgage tab structure matches Kickapoo template before onboarding.

## Phase 1 — Revised Scope (2026-04-29)

**What Phase 1 actually does (updated after sheet analysis):**
- Writes to **Mortgage tab historical section** (NOT Info tab — Info is formula rollup)
- Only writes **loan outstanding** (unpaid principal balance) per statement
- **Payment change detection** — alerts Rod via Telegram + iMessage if payment differs from last known (30yr fixed = escrow recalc, Sharon needs to update Chase)
- **Dual dup check** — checks both CSV and Sheet for existing statement date before writing
- **Dupe log** at `~/Library/CloudStorage/Dropbox/bottleMsg/logs/sheets-dupes.log`
- Date normalization handles MM/DD/YY vs MM/DD/YYYY format differences

**What Phase 1 does NOT do:**
- Escrow tracking (Phase 2)
- PM statement updates (Phase 3)
- Rent tab writes
- Tab history row appending for non-balance fields

**Test results (2026-04-29 on kickapoo-403):**
- Live write: balance $53,455.45 written to Mortgage tab row 63
- Payment alert fired: $330.58 → $628.48 (sent via Telegram + iMessage)
- Dup detection: re-run correctly skipped (found date at row 63)
- Log: all actions recorded to Dropbox dupe log

## File Inventory (after Phase 2)

| File | Repo | Purpose |
|------|------|---------|
| `gsheets_sync.py` | local/scripts/ | Playwright Sheets read/write (stays on mini) |
| `gsheets_login.py` | local/scripts/ | One-time Google login |
| `property_map.json` | dakota-software/bot/pdf-extractor/ | Property → sheet slug + cell mappings |
| `sheets_bridge.py` | dakota-software/bot/pdf-extractor/ | Translates extractor output → gsheets_sync calls |
| `extract-pipeline.sh` | dakota-software/bot/pdf-extractor/ | Unified launchd trigger (replaces two scripts) |
| `extract_mortgage_data.py` | dakota-software/bot/pdf-extractor/ | Mortgage PDF extractor (unchanged) |
| `extract_pm_data.py` | dakota-software/bot/pdf-extractor/ | PM PDF extractor (unchanged) |
