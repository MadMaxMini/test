# Google Sheets Automation via Playwright

**Created:** 2026-04-29
**Status:** Working — tested on 401 Kickapoo Ave sheet
**Location:** `~/Work/local/scripts/gsheets_sync.py` (mini)

---

## What This Is

Browser-based Google Sheets read/write using Playwright (headless Chromium). No Google Cloud project, no API keys, no service accounts. Playwright drives a real browser with a saved Google login session — same as a human clicking cells.

## Architecture

```
gsheets_sync.py
    → Playwright (headless Chromium)
        → ~/.playwright-google/  (persistent browser profile w/ Google login)
            → Google Sheets UI
                → Name Box (#t-name-box) for cell navigation
                → Keyboard input for values
                → Auto-saves to Drive
```

## What's Portable vs Machine-Specific

| Component | Portable? | Notes |
|-----------|-----------|-------|
| Script logic | Yes | Read/write/batch/dump pattern works anywhere |
| Name Box approach | Yes | `#t-name-box` is stable Google Sheets DOM |
| SHEET_MAP (slug → ID) | Yes | Same sheet IDs work from any machine |
| Playwright + Chromium | Install per machine | `pipx install playwright && playwright install chromium` |
| Python venv | Install per machine | Playwright needs to be importable |
| Google login session | Per machine | One-time browser login, saved to profile dir |
| Hardcoded paths | Machine-specific | Shebang, PROFILE_DIR — must be updated per machine |

## Setup on a New Machine

### 1. Install Playwright

```bash
# Create a venv (or use an existing one)
python3 -m venv /path/to/venv
/path/to/venv/bin/pip install playwright

# Install Chromium browser
playwright install chromium
# or: /path/to/venv/bin/playwright install chromium
```

### 2. One-Time Google Login

Run the login script (opens a browser window):

```bash
/path/to/venv/bin/python3 gsheets_login.py
```

Log into Google in the window that opens. Close when done. Session persists to `~/.playwright-google/`.

### 3. Configure the Script

Update these in `gsheets_sync.py`:
- **Shebang** — point to your venv's python
- **PROFILE_DIR** — where the browser profile lives (default: `~/.playwright-google/`)
- **SHEET_MAP** — add property slugs → Google Sheet IDs

### 4. Test

```bash
# Read-only test (no browser needed)
gsheets_sync.py dump kickapoo-401

# Write test
gsheets_sync.py write kickapoo-401 C5 "test"
gsheets_sync.py clear kickapoo-401 C5
```

## Usage

```bash
# Read a cell value
gsheets_sync.py read <property> <cell>
gsheets_sync.py read kickapoo-401 C16        # → $1,500.00

# Write a cell
gsheets_sync.py write <property> <cell> <value>
gsheets_sync.py write kickapoo-401 C5 "2"    # NumDoors = 2

# Clear a cell
gsheets_sync.py clear <property> <cell>

# Dump entire sheet as CSV (fast — no browser, uses export URL)
gsheets_sync.py dump <property>

# Batch update from JSON file
gsheets_sync.py batch <property> updates.json
# JSON format: [{"cell": "C5", "value": "2"}, {"cell": "C16", "value": "$1,500"}]

# Target a specific tab
gsheets_sync.py write kickapoo-401 C3 "$1,500" --tab Rent
```

## Property Sheet IDs

| Property | Slug | Google Sheet ID |
|----------|------|-----------------|
| 401 Kickapoo Ave, Gastonia NC | `kickapoo-401` | `1ac7cAq8Drd2eXmOYt16zhRxZvnPxDGA0q-m8qrkyvMk` |
| 403 Kickapoo Ave, Gastonia NC | `kickapoo-403` | `18DflDWq1g6NIQspZzVak6SsJNEvqQ877tV3PzqvfASk` |

## Sheet Structure (Info Tab)

Both Kickapoo sheets share this layout on the Info tab:

| Row | Field A | Field C (Data) |
|-----|---------|----------------|
| 1 | Field Names | Data |
| 3 | Address | (street address) |
| 4 | SFR | (true/false) |
| 5 | NumDoors | (count) |
| 6 | Zillow Link | (URL) |
| 7 | Related Property | (address) |
| 13 | PM URL | (PM company link) |
| 14 | Username | (PM login) |
| 16 | Rent | (monthly $) |
| 17 | Mortgage | (monthly $) |
| 18 | Escrow | (monthly $) |
| 19 | PM Fees | (monthly $) |
| 20 | Lease Fees | (monthly $) |
| 21 | HOA Fee | (monthly $) |
| 23 | FCF | (free cash flow) |

Tabs visible: Info, Mortgage, Maintenance, Rent, Lease Fees, PM Cash Tracking, Insurance, Property Taxes, + more

## Pipeline Integration Points

This script is designed to be called by existing Dakota pipeline stages:

1. **PDF Extractor** (`bot/pdf-extractor/extract_mortgage_data.py`)
   - After extracting mortgage/escrow from a statement PDF
   - Updates: C17 (Mortgage), C18 (Escrow) on Info tab, plus Mortgage tab

2. **Intake Router** (`bot/intake_router.py`)
   - When a property-tagged note contains financial data
   - Updates relevant fields on Info tab

3. **PM Data Extractor** (`bot/pdf-extractor/extract_pm_data.py`)
   - PM company, contact info, fee structure
   - Updates: C13 (PM URL), C14 (Username), C19 (PM Fees)

## Known Behaviors

- **Popup on first load:** Google shows "Use Meet and Docs together" overlay. Script dismisses with Escape.
- **Browser lock files:** If the script crashes, `SingletonLock` persists. Script auto-cleans these on startup.
- **Load time:** ~8 seconds for Sheets to fully render in headless mode. Built into the wait.
- **Headless mode:** No browser window appears. Runs silently.
- **Session expiry:** Google login may expire after weeks/months. Re-run `gsheets_login.py` to refresh.

## Files

| File | Location | Purpose |
|------|----------|---------|
| `gsheets_sync.py` | `~/Work/local/scripts/` | Main read/write/batch script |
| `gsheets_login.py` | `~/Work/local/scripts/` | One-time Google login (opens browser) |
| Browser profile | `~/.playwright-google/` | Persistent Google session |
| Venv | `~/Work/local/scripts/.venv/` | Python env with playwright |

## For Dakota Repo

To add this to `dakota-software/bot/`:
1. Copy `gsheets_sync.py` → `bot/gsheets_sync.py`
2. Update PROFILE_DIR and shebang for the target machine
3. Add property Sheet IDs to SHEET_MAP
4. Wire into `extract-and-commit.sh` post-extraction step
5. The venv and Google login are still per-machine setup

The script is standalone — no dependencies beyond `playwright`.
