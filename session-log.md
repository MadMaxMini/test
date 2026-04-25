# Session Log

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

