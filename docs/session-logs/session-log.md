# Session Log

## 2026-04-29 — Sheets Pipeline Phase 1 Built + Tested

**What got done:**
- Analyzed both Kickapoo Google Sheets (401 + 403) via Playwright — mapped full tab structure, formula chains, historical data blocks
- Key insight: Info tab is a pure formula rollup — bridge writes to Mortgage tab historical section, not Info
- Built `sheets_bridge.py` — single Playwright session, reads all historical rows in one pass, dual dup check (CSV + Sheet), date normalization (MM/DD/YY ↔ MM/DD/YYYY), payment change alerting
- Built `property_map.json` — both Kickapoo properties mapped with loan numbers and tab structure
- Created dupe log at `~/Library/CloudStorage/Dropbox/bottleMsg/logs/sheets-dupes.log`
- Live test on kickapoo-403: balance $53,455.45 written to row 63, payment alert fired ($330.58→$628.48), dup detection verified on re-run
- Rod added 4 more property sheet IDs (grand-pines, la-estancia, piney-point, cash-tracking)
- Dropped RFC in all Dakota team inboxes
- Saved sheet architecture to madmax + dakota memory (cross-repo reference with sync cadence)

**Decisions:**
- Phase 1 = balance only + payment change alerts. Escrow = Phase 2. PM statements = Phase 3.
- Payment change on 30yr fixed = escrow recalc → alert Rod, Sharon updates Chase
- Bridge uses Playwright directly (not shelling out per cell) — single browser session for all reads + writes
- Dupe log in Dropbox (not repo) so Rod can check from phone
- Scripts home in `dakota-software/bot/pdf-extractor/` for now, review in Phase 2

**What's next:**
- Wire bridge into shell pipeline (extract-and-commit.sh calls sheets_bridge.py after extraction)
- Onboard additional properties (need loan numbers + verify Mortgage tab matches template)
- Phase 2: escrow tracking
- Phase 3: PM statement updates (multi-unit, vacancy alerts, rent change detection)

---

## 2026-04-28 — GTD Sweep via Telegram

**What got done:**
- Built `gtd-sweep.py` — scans bottleMsg inbox, classifies items, sends numbered GTD table to Rod via Telegram
- Wired GTD reply commands into `dispatcher.py`: `gtd go`, `gtd go 1,3`, `gtd hold 2`, `gtd move 4 archive`, `gtd skip`
- Created LaunchAgent `com.madmax.gtdsweep` — dual trigger: WatchPaths on bottleMsg (on file drop) + 11:55am daily
- 5-min debounce so rapid Dropbox syncs don't spam
- KeePass files auto-classified as "stays" (Rod wants them in bottleMsg)
- Cheat-sheet failure alerts auto-routed to archive (laptop-only)
- Fixed VS Code permissions: added Glob + Grep to settings.json allow list
- Processed bottleMsg inbox: routed phase1/phase2 confirmations, autonomous layer design doc, screenshots (job leads, productivity, smol-audio), Devon PM pipeline text

**Decisions:**
- GTD sweep is async via Telegram, not session-only — Rod approves from phone
- Cheat-sheet failures are laptop-only, ignore on mini (saved to memory)
- KeePass files stay in bottleMsg root per Rod's preference

**What's next:**
- Monitor GTD sweep in the wild — first 11:55am fire tomorrow
- Rod still needs to reply `gtd go` to the test sweep sent today
- P0: Job search docs (GOALS.md + career-doc.md) still empty
- P1: 7:15am pre-session brief, night agent first real run, local/scripts → GitHub

---

## 2026-04-25 — Calendar Bot Live + Context Fix

**What got done:**
- Calendar Bot built end-to-end: parser (13,616 events → SQLite FTS5), search engine, Claude+Ollama query layer, Telegram poller
- Bot registered: @cala_tele_bot, token + chat_id in Keychain
- Fixed: emails now included in LLM context (were being stripped to names-only)
- Fixed: conversation history now passed to search + LLM (follow-ups like "all emails please" work)
- Fixed: triple-response bug — multiple poller instances killed, single instance running
- Created PROJECT.md in calendar-bot repo

**Decisions:**
- No git repo for calendar bot — personal data, encrypt later
- Data lives at ~/Work/coaches/calendar-bot/data/ (not Dropbox)
- LLM mode: auto (Claude primary, Ollama fallback)

**What's next:**
- P1: Fuzzy search (alias/synonym layer for company name variations)
- LaunchAgent so poller survives reboots
- Local LLM benchmark (Claude vs Ollama quality on calendar queries)
- Data encryption

---

## 2026-04-24 — PM Pipeline Stood Up + PDF Rename/Dup Detection

**What got done:**
- Pulled dakota repo, reviewed Devon's PM extractor + shell wrapper + plist (all pre-built)
- Detected Rod's Dropbox folder renames: `statements` → `account-statements-inbox`, new `pm-statements-inbox`
- Updated both shell scripts and both launchd plists to match renamed paths
- Installed and loaded `com.dakotaops.pmwatch` — PM pipeline is live
- Test-extracted Georgia Owner Statement (HomeRiver, 2889 Grand Pines Ct, Dec 2025) — clean extraction, all fields populated
- P&L Summary and Income Statement PDFs are different report types — not what the extractor targets, Owner Statements are the right doc
- Added canonical PDF rename on move to processed: `YYYY-MM_property-slug_bank.pdf`
- Added two-layer dup detection: filename check in processed/ (cheap) + CSV date check (fallback)
- Both pipelines now handle move+rename in Python (removed mv from shell scripts)
- Added bank name to mortgage CSV filenames
- Symlinked `operations/mortgage-data` and `operations/pm-data` into Dropbox processed/ folders so Rod/Sharon can see CSVs
- Wrote full test results to bottleMsg: `2026-04-24-pm-pipeline-test-results.md`

**Decisions:**
- Flat `pm-statements-inbox/` folder (no subfolders per property) — simpler for Sharon
- Owner Statement PDFs are the extraction target; P&L summaries are reference-only
- Dup PDFs get deleted from inbox (not left sitting); canonical name in processed/ is the gate

**Open items:**
- NC Owner Statement sample needed to verify regex patterns across states
- Sharon needs to learn: drop Owner Statements flat into `pm-statements-inbox/`, not in subfolders
- Georgia/NC `(test)` folders in account-statements-inbox need cleanup once Sharon understands layout

---


---


---

