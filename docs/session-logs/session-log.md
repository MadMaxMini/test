# Session Log

## 2026-05-12 (late evening) — Sheets pipeline Phase 1 shipped + Phase 2 code landed (UNTESTED LIVE)

**Context:** Rod ran today's morning test plan with Sharon dropping May statements on all 6 properties. Came in this evening to review logs + outputs.

**What got done:**
- Reviewed `pdf-extractor.log` for all 6 properties' May 12 runs. 5 worked (with anomalies), 1 dedup'd (Via Verona — turned out to be a real duplicate, not a bug)
- Found scope drift: bridge was writing 5 fields (Balance, Escrow, Total Payment, Servicer, Escrow Shortfall) + dates per statement. Rod's product intent was only Balance + date, with payment-change alert
- Found Piney Point formula trap: cell C20 held `=C19+C4`, bridge read it as a string, fired false PAYMENT CHANGE alerts to Sharon via Telegram + iMessage twice (May 7 and May 12)
- Patched `sheets_bridge.py` (commit `f020bd1`):
  - Shrank `MORTGAGE_FIELD_SPECS` from 4 entries to 1 (Balance only)
  - Added formula-as-previous-payment guard: if `prev_payment.startswith("=")`, suppress alert
- Rod manually verified all 6 sheets in sequence (401 K, 403 K, Grand Pines, Piney, La Estancia, Via Verona) — sheet-by-sheet cleanup of wrongly-written cells
- Logged decision: defer escrow-balance sheet tracking; CSV still captures it
- Logged Phase 2 hardening items in `dakota-software/docs/sheets/roadmap.md`: scope-down, formula-guard, re-wire Sheets API (was wired up earlier this spring, never recorded, lost), per-servicer extractor refactor consideration
- Opened P0 task for Sharon: drop the real May Via Verona statement when ServiceMac issues it + report back. Task lives at `dakota-software/tasks/active/T-2026-05-12-sharon-via-verona-may-statement.md`
- Wrote Phase 1 shipped celebration to bottleMsg + mirrored into `dakota-software/docs/sheets/2026-05-12-phase-1-shipped.md`

**Decisions:**
- Bridge writes scope down to KISS: only `C21` (Balance) + `D21` (date), always together. Read `C20` for change-detection only, never write
- Sheets API re-wire is a Phase 2 hardening item, not urgent — Playwright works
- Per-servicer extractor refactor: wait for trigger (new servicer being onboarded), not urgent
- Phase 1 marked ✅ COMPLETE in roadmap (with Via Verona May validation called out as pending Sharon)
- Bridge changes are LANDED IN CODE but UNTESTED LIVE — first real test is early June statement cycle

**Commits (dakota-software):**
- `f020bd1` — sheets bridge: scope down to balance-only + payment-change alert (UNTESTED LIVE)
- `37d6027` — sheets pipeline: mark Phase 1 complete + open P0 task for Sharon
- `2af58c0` — docs(sheets): add Phase 1 shipped writeup alongside project files

**What's next:**
- Sharon: drop real May Via Verona statement when ServiceMac issues it + report back (P0)
- Rod is starting Phase 3 (Chase → PM Cash Tracking) wiring in parallel
- Mad Max long-poll on Phase 2 verification (per Rod's ask) — monitor `pdf-extractor.log` + bridge writes when June statements drop (~early June 2026), confirm scope-down + formula-guard worked, report on first real run of new code
- Pact note: scope-down + formula-guard count as bug-fix maintenance inside Phase 1 closeout. Phase 3 wiring is genuinely new build — Rod aware of the no-build pact (active through 2026-06-10), driving the decision himself

---

## 2026-05-12 (evening) — Model switching: temporary TTL + flipped defaults

**What got done:**
- Added third model-switch mode to dispatcher: temporary with TTL (1-2 hour expiration), alongside existing permanent and one-off modes
- New state file `dispatcher-model-ttl.state` (JSON: `{label, expires_at}`) with auto-expire on read
- Priority chain in `run_model()`: one-off ("use claude" in msg) > TTL > persistent > default
- Command parser supports `/model X Nm` and `/model X Nh` for explicit durations
- **Flipped defaults per Rod's preference:** bare `/model X` is now temporary (2h default), `/model X perm` is the explicit permanent switch (also accepts `permanent`, `forever`, `sticky`)
- "perm" switch clears any active TTL so persistent takes effect immediately
- `/model?` query now reports TTL with remaining minutes vs. permanent
- `/help` rewritten with dedicated 🔧 Model Switching (3 modes) section — temporary listed first as the default path
- Cleaned up misleading `use mistral:` colon-prefix entry from inline-overrides section (was duplicate + implied syntax that didn't exist)

**Decisions:**
- Temporary 2h is the right default — most switches should auto-revert; permanent is the explicit exception
- Default TTL = 120 minutes (2 hours). Reasoning: long enough for a focused session, short enough that you won't accidentally leave gemma running for days
- Kept "default", "mistral", "local" all aliased to mistral-small (Rod's mental model varies)

**Commits:**
- `8be6d52` — initial TTL implementation + help expansion
- `ac76a1f` — flipped defaults to temp-first
- `8517c5c` — removed misleading colon-prefix line from /help

**Known cruft (not fixed tonight):**
- `~/Work/test/local/scripts/dispatcher.py` is the test-repo tracked copy; canonical lives at `~/Work/local/scripts/dispatcher.py`. I sync by `cp` before commit. Should consolidate — flagged previously, still flagged.

**What's next:**
- Pact still active (no new builds) — this session was polish on an existing surface, allowed under "closing loops"
- No follow-up needed on model switching — three modes cover the use space

## 2026-05-12 — Big-picture audit + 30-day no-build pact + OpenBao unsealed

**What got done:**
- Full-start sweep — session log, inventory, Dakota tasks, bot health, bottleMsg state
- Big-picture honest assessment delivered: Dakota mortgage pipeline is the franchise (only thing with measurable $ impact), 2-3 coaches are zombies, OpenBao was sitting idle (turned out NOT idle — see below), platform layer is necessary overhead not the prize
- Verified FDA fix: unloaded + reloaded pdfwatch/pmwatch, did real file-move test on Piney Point PDF. Stderr clean, watcher fired, extractor ran, dedup correctly skipped the duplicate. **FDA is working.** Morning brief's "FDA blocker" was stale (May 1).
- **OpenBao discovery:** Not half-built — already initialized, KV + Transit engines live, real secrets stored (dmg/, email/, hf, telegram/, tokens/). Was just sealed. Unsealed via `unseal-keychain.sh`. Functional R/W test passed via API.
- Wrote 30-day no-build pact to `bottleMsg/2026-05-11-30-day-no-build-pact.md`
- Saved pact as persistent feedback memory: `feedback_no_build_pact_2026.md` + MEMORY.md index entry (loads into every future session)
- needs-rod.md updated with 4 new items from this session

**Decisions:**
- **30-day no-build pact ACTIVE through 2026-06-10.** No new agents/coaches/services. Closing existing loops only. Override clause: Rod must explicitly say "I'm overriding the pact for X because Y." Full rules in pact file + memory.
- Cash tracking deferred to week 2 minimum (was Rod's instinct to start now — pact blocked it)
- Coaches died ≠ true — outbound nudges fire fine for Elite HH/Health/Manager. INBOUND Telegram pollers are broken (DNS errors). Distinct bug, lower severity unless Rod actually chats back.

**Discoveries / bugs surfaced (not fixed tonight):**
- OpenBao helper scripts (`store-secret.sh`, `get-secret.sh`) look for token at `~/.openbao-init` plaintext path, not Keychain. Scripts unusable from CLI until fixed (one-line edit). Backlogged.
- No auto-unseal LaunchAgent for OpenBao — every Docker restart silently breaks every coach that depends on a secret. Decision pending (see needs-rod.md).
- Elite HH + Health Coach Telegram pollers throwing `getUpdates error: [Errno 8] nodename nor servname provided` since 2026-05-08. Daily nudges fine, inbound chat broken. Severity depends on whether Rod ever replies to nudges.
- Watcher dedup logic leaves duplicate PDFs in inbox instead of moving to processed/ — cosmetic, not functional.

**What's next (priority order within the pact):**
1. Auto-unseal LaunchAgent for OpenBao (~5 min, closes a reliability loop)
2. Coach roster triage — Elite HH, Manager, Health, Faith, Recruiting: keep/simplify/archive decision per coach
3. Time audit setup — log builder vs doer hours starting Monday
4. DNS poller fix for Elite HH / Health (if Rod confirms he chats back to them)
5. Helper script Keychain bug fix
6. Phase 2 Dakota — properties config, change watcher, PM end-to-end hardening

## 2026-05-10 — Max Bot in Dakota Automation Team Group

**What got done:**
- Wired @madmax_mini_bot into the Dakota Automation Team Telegram group (was unmonitored)
- Architecture decision: Max handles the group (better dispatcher), AutoDakota stays as Rod's 1-on-1 task bot
- Group commands live: `/ping`, `/status`, `/models`, `/tasks [name]`, `/standup`, plus `@madmax_mini_bot [question]` for full AI dispatch
- AutoDakota poller upgraded: `tg_send` accepts explicit chat_id so it can push outbound notifications to the group when needed
- Fix pass after first deploy: `/tasks` was reading the legacy `people/{p}/tasks.md` redirect — switched to canonical `tasks/views/{p}.md`
- Added `tg_send_chunked` — splits long replies at paragraph boundaries, capped at 3 messages, each under 4000 chars
- Group session history wired via `sessions_mod.Session(GROUP_CHAT_ID)`, sender first-name prefixed so the AI knows who said what

**Decisions:**
- Group monitoring: Max bot only (not both bots — keeps responsibility clean)
- `/tasks` group output: P0/P1 first, max 5 per person, strip verbose descriptions to keep replies tight

**What's next:**
- iMessage path has no session history (msggateway → dispatcher); fixable by adding sessions to that path. Rod hasn't asked yet — leave for now.

## 2026-05-08 — Via Verona 8302 Sheet Onboarding

**What got done:**
- Reviewed two competing Google Sheets for Via Verona via Playwright — identified "good" (real Via Verona data) vs "bad" (stale Jacksonville/Gilmore St copy, safe to delete)
- Verified sheet structure after Rod's row fix — now matches Kickapoo template (row 17 = Historical Data)
- Caught label column difference: Via Verona uses column G for field labels, Kickapoo uses J. Made `label_column` configurable in property_map.json (defaults to J)
- Caught escrow field mismatch: bridge was writing escrow account balance ($10,701) to a row meant for monthly escrow payment ($1,783). Added new "Escrow Balance" row 24 + "Current Escrow Balance" row 14 in the sheet. Changed config to target the new row
- Wired Via Verona into `property_map.json` and `SHEET_MAP` in `sheets_bridge.py`
- Live bridge run: 6 cells written successfully (balance, escrow balance, as-of dates)
- All 6 properties now online in the mortgage pipeline

**Decisions:**
- Escrow account balance tracked separately from monthly escrow payment (new row, not overwrite)
- Label column is per-property config, not hardcoded to J

**What's next:**
- Sharon to delete the "bad" Via Verona sheet (Jacksonville copy)
- Loan number in sheet still truncated to "3595" — Max 1 may have fixed (commit mentions it)
- Phase 2 rent tab for quadplex (4 units) still ahead

## 2026-05-06 — Local Model Audit + Telegram Bot Intelligence Upgrade

**What got done:**
- Full HuggingFace / local model audit — inventoried all 6 Ollama models (74 GB total), reviewed March benchmark results across Dakota ops + Faith coach workloads
- Created `~/Work/local/scripts/reference-models.md` — detailed reference doc with installed models, speed charts, scorecards, sample outputs, failure modes, and verdicts
- Wired `models` and `models detail` commands into dispatcher — on-demand pull (not auto-loaded), accessible from Telegram
- Diagnosed why Telegram bot feels dopey: 10-message history + 200-token output cap
- Bumped conversation depth 10 → 20 in sessions.py
- Bumped Ollama output cap 200 → 500 tokens in dispatcher.py

**Decisions:**
- Mixtral 8x7B confirmed dead weight — 26 GB, times out on every task. Candidate for removal to free space for Qwen3.5-35B-A3B
- Mistral Small remains dispatcher default (Fallback 1), Devstral as Fallback 2
- Gemma 3 disqualified from ops pipelines (hallucination risk), chat-only
- Reference docs should be pull-not-push — don't burn tokens loading into every message context

**What's next:**
- Remove Mixtral, pull Qwen3.5-35B-A3B and benchmark it
- Consider further Telegram bot improvements (richer SOUL, more reference commands)

---

## 2026-04-30 — Phase 1 Review + Handoff Plans + FDA Blocker Found

**What got done:**
- Walked Rod through full sheet architecture (tab hierarchy, formula chains, historical data blocks)
- Revised phase roadmap: P1=mortgage balance, P2=cleanup+hardening, P3=escrow, P4=PM statements, P5=harden
- Date format alignment: both extractors now normalize to MM/DD/YYYY at extraction boundary
- Rod added 4 more property sheet IDs to SHEET_MAP (grand-pines, la-estancia, piney-point, cash-tracking)
- Properties config file scoped for Phase 2 with change watcher (alert on config drift in multi-hand repo)
- Notification routing decided: routine processing → Telegram to Rod only, payment alerts → Telegram + iMessage to Rod, Dakota group only for urgent/actionable
- CSV-in-repo question raised for Phase 2 (duplicate data — Sheet vs CSV, worth rethinking)
- Investigated Sharon's missing PDFs: 4 PM Owner Statements stuck in inbox since Apr 25-29
- Root cause: FDA (Full Disk Access) not granted to launchd `/bin/bash` — both pdfwatch and pmwatch are dead
- Wrote 3 handoff prompts for fresh agents: wire-bridge, FDA fix, and Phase 2 plan in memory

**Decisions:**
- Phase 1 isn't complete until PDF drop → Sheet update is hands-free (wire-up is P1 completion, not P2)
- Extractor should pass data directly to bridge via CLI args, not re-read from CSV (cleaner, faster)
- Escrow bumped to Phase 3, PM statements to Phase 4, hardening to Phase 5
- Folder rename (account-statements → mortgage/loan-statements) — Rod to decide, Sharon uses it

**Blockers:**
- FDA permissions — both launchd watchers dead. Rod must grant in System Settings manually.
- 4 PM PDFs stuck unprocessed (can run manually from terminal as workaround)

**Handoff prompts written:**
- `dakota-software/bot/pdf-extractor/WIRE-BRIDGE-PROMPT.md` — wire bridge into shell pipeline
- `dakota-software/bot/pdf-extractor/FIX-FDA-PROMPT.md` — fix FDA + process stuck PDFs
- Phase 2 scope saved in `project_sheets_architecture.md` memory

**What's next:**
- Fix FDA (Rod manual step)
- Wire bridge into pipeline (agent prompt ready)
- Process 4 stuck PM PDFs
- Phase 2: properties config, change watcher, CSV question, onboard more properties

---

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

