# Session Log

## 2026-05-20 — Overnight sheets-pipeline hardening review + Phase 2 to ~90%

**Setup:** Scheduled cron `02bf6900` (one-shot CronCreate from previous night) fired at 01:05 Wed 2026-05-20. Goal: review the sheets pipeline (cross-repo: madmax + dakota), brainstorm hardening, ship safe-path code while Rod sleeps.

**Overnight local-model handoff:**
- Built 305KB cross-repo context bundle via `build-context.sh` (without burning Claude's window, per feedback_local_model_context)
- gemma3:27b timed out at local-agent's 600s cap on the 305KB bundle. Fell back to llama3.1:8b — completed in ~5 min but returned thin output, mostly paraphrasing the prompt
- Net: my own 35-item brainstorm carried the synthesis. Llama added 1 useful new angle (concurrent-bridge-run safety)

**Overnight: shipped to dakota-software (2 commits, pushed to main):**
- `docs/sheets/2026-05-20-hardening-review.md` — synthesis doc with Phase 2 triage + 36-item recommendations table + top-5 picks
- `bot/pdf-extractor/dupe_log_summary.py` + 9 tests — surfacing tool, already finding real signal (11 REJECTED rows in 30 days incl. Via Verona schema mismatch + kickapoo float-precision rejects)
- `bot/pdf-extractor/scaffolding/openbao_playwright_token.py` + README — OpenBao migration scaffold, NOT WIRED IN
- `docs/db-migration/schema-v0.sql` — DuckDB schema sketch
- `tests/test_extract_mortgage_data.py` — one-line fix for sys.modules.setdefault test-pollution that was masking 10 Sorting Hat failures. Net: 12 failures → 2

### Day-of continuation — Rod engaged with overnight findings

After overnight pass landed, Rod woke and walked through the synthesis. Three rounds of clarification + course-correction, then a focused execution sprint to push Phase 2 from ~60% to ~90% in one session.

**Corrections Rod made:**
- Phase 4 is NOT blocked on Doc fact-check (defaults exist; just dirty data + Sharon update)
- Phase 6/7 reshuffle: P6 = hardening v2 + DB prep (new), P7 = DuckDB migration (was Phase 6)
- Kickapoo float-precision REJECT already fixed in `b963d03` on 5/07 (dupe-log entries are pre-fix history)
- OpenBao wire-in is "load-bearing, don't touch" — keep as scaffold, defer to later-stage hardening
- Year-flip lint not urgent until August — record the design but don't ship now
- Silent-failure fix belongs AFTER alert tier work — defer to P6
- Concurrent-bridge-run race IS worth fixing in P2 (sticky enough)

**Shipped during sprint (commits pushed to dakota main):**
- `9c3d7e2` — mortgage bridge structural-check + multi-field date repair. Expanded `MORTGAGE_FIELD_SPECS` from 1 field (Balance) to 4 with a `writes_value` flag. Closes the 2 long-standing failing tests. 11/11 mortgage tests now green.
- `a395ff1` — Phase 2 push to ~90%: bridge lockfile + 3 lock tests, sorting_hat_confidence.py dashboard, property_map.json schema test (8 tests), notification-routing-audit doc, alert-noise-inventory doc, onboard-property checklist doc, Via Verona Sharon writeup, P2-QUICK-STATE single-page status doc, hardening-review doc corrections.

**Shutdown:**
- Morning-brief.py wired (~/Work/local/scripts/) to surface dupe-log + Sorting Hat alerts via subprocess. Already finding 1 unknown Sorting Hat classification on live test.
- Overnight cron template saved to `~/Work/test/scaffolding/overnight-cron-template/` (EXECUTE.md + build-context.sh + gemma-prompt.md) — reusable for future overnight drops
- 3 new memory entries: project_p2_quick_state_pointer, feedback_openbao_load_bearing, feedback_overnight_cron_pattern, feedback_token_frugality_and_gemma_suggestions (4 actually). MEMORY.md index updated.
- iMessage sent to Rod with Via Verona Sharon-fix summary + routing question

**iMessage sent to Rod:** Via Verona Sharon-fix summary + routing question (no Sharon-direct channel — asked whether Rod will forward or have me send to Dakota group).

**Test suite:** 116 tests, 0 failures (was 12 failures earlier).

**Phase 2 status at end of day:** 21 done / 5 remaining (all human-bound). ~89% by item count, ~95% by Claude-shippable surface.

**🎯 Low-context-return doc:** `dakota-software/docs/sheets/P2-QUICK-STATE.md` — single-page emoji-rich Phase 2 status. New chat? Point Claude at that file → 30-second pickup.

---

## 2026-05-19 — Backlog setup + nightly triage fix

**Completed:**
- **Created backlog.md** — canonical roadmap for mini work (P0/P1/P2/P3). TTS hook for Claude Code sessions added as P1, blocked by 30-day no-build pact through 2026-06-10.
- **Fixed nightly triage** — morning-brief.md was 18 days stale (last run 2026-05-01). Root cause: Dropbox Smart Sync PermissionError. LaunchAgent ran at 3:30am before Dropbox daemon hydrated cloud-only bottleMsg cache. Added 10s startup sleep in nightly-triage.py; manual test successful. Should resume on next overnight run.
- Committed and pushed both changes to main.

**Status:** Nightly triage should resume tonight. TTS setup queued as P1 (post-pact, 2026-06-10).

---

## 2026-05-19 — Sorting Hat Session 1 shipped (PR #3)

**Completed:**
- **Classifier built and passing:** `bot/pdf-extractor/sorting_hat.py` — deterministic `classify(path) → ClassificationResult{statement_type, confidence, evidence, route}`. Types: `mortgage | chase_checking | chase_credit | pm_owner | unknown`. PDF path uses pdfplumber text + servicer/marker scoring; CSV path uses header set match. Ambiguity guard (runner-up within 0.15 → unknown). Confidence floor 0.7. CLI `python sorting_hat.py <file> [--json]`.
- **11 real fixtures, 100% accuracy:** 4 mortgage (Wells Fargo, NewRez, Rocket, ServiceMac), 2 Chase checking PDFs, 2 Chase credit PDFs, 2 PM owner (HomeRiver Group), 1 Chase native checking CSV. Every classification at 0.95 confidence with rich multi-marker evidence.
- **PII out of repo:** Real loan numbers, balances, addresses don't go to GitHub. `tests/fixtures/sorting-hat/fetch.sh` copies from local Dropbox `processed/` paths; local `.gitignore` covers PDFs and CSVs in that subtree.
- **No production touch:** Existing mortgage/Chase/PM extractors, LaunchAgents, inbox folders unchanged. Sorting Hat lands as new code in new files.
- 3 commits on `phase-2-sorting-hat` (fetch infra → classifier → tests); PR #3 opened against main.

**Key correction during session:** kickoff doc said PM owner statements were Phase 4 / "not yet seen." Rod corrected: PM ingest *works* (LaunchAgent loaded, CSV gets written), only sheets-wiring is the messy Phase 4 piece. So PM samples went into the fixture set and the classifier covers all 4 real types, not 3 + stub.

**Open for next session (cutover):**
- Unified-inbox folder (`account-statements-inbox` + `pm-statements-inbox` → single `inbox/`)
- LaunchAgent rewiring → call Sorting Hat first, dispatch to existing extractors
- Quarantine path for unknowns + alert
- Chase credit native CSV pattern (no real sample yet — current Chase CSV support is checking only)

**Follow-up: logging + viewer + hardening (same session)**
- `sorting_hat.py` now supports `--log FILE` → appends JSONL per run
- `sorting-hat-viewer.html` — static page reads JSONL, shows last 50 runs as emoji table, red highlight for unknowns
- **Error handling:** nonexistent files, bad PDFs, corrupt CSVs all log gracefully as "unknown" (not crashes)
- **Integration test:** verify JSONL format round-trips (test_sorting_hat_logging.py, 3 tests passing)
- **Chase credit CSV:** added TODO stub + commented pattern (no real native sample yet; extractor outputs in operations/bank-data/ are processed, not native)
- Ready for LaunchAgent wiring in cutover session
- **Cutover prep (Gemma):** `sorting-hat-watch.sh` (unified inbox classifier + router) + `SORTING_HAT_CUTOVER.md` (full design doc, migration checklist, 4 decisions for Rod)

**Session 2 (end of month):** Wire the LaunchAgent, test full pipeline, go live. Four decisions needed from Rod first (Dropbox Smart Sync, alert batching, quarantine cleanup, credit card routing).

**Repos touched:** 
- `dakota-software`: PR #3 merged (classifier + tests + fixtures), logging/viewer, error handling, cutover design (4 commits total)
- `madmax`: session log updated

**End-of-month goal met:** Sorting Hat fully designed, tested, and ready for deployment.

**Cutover decisions actioned:**
1. ✅ Dropbox Smart Sync: pinned offline (per existing memory)
2. 🔄 Alert verbosity: written `docs/sheets/sorting-hat-alert-discussion.md` (4 options A-D); iMessage sent to Dakota group asking Doc, Devon, Sharon to weigh in
3. ✅ Quarantine cleanup: manual to start (safest default)
4. 🔄 Chase credit routing: Telegram DM to Rod (msg 306) asking whether 3160/3202 flow to sheets automatically today, before deciding route vs quarantine

**Phase 2 hardening picture clarified:**
- **Drift fix REMOVED from backlog** — Rod corrected: day-of-month convention (mortgage=1, distribution=15, cc=10) is intentional. Rows reflect DUE DATE, not posting date. Early payments are by design.
- **Created `docs/sheets/do-not-fix.md`** as catalog of intentional patterns. First entry: day-of-month convention. Future sessions read this before "fixing" sheet behavior.
- **Pending verification full design captured** in `docs/cash-tracking/2026-05-19-rollup-formulas-and-verification-roadmap.md` section 3. Key insight from Rod: Phase B (verify + roll-off handling) is NOT punt-able because balance reconciliation needs a clean slate before new-txn writes. Bundled as late Phase 2 or Phase 5 hardening candidate.
- **Open Phase 2 items remaining (all fresh-session candidates):** Credentials hardening, Alert noise reduction, Playwright batching, Naming standardization.

---

## 2026-05-19 — Stage B shipped + quit/timeout added

**Completed:**
- **Stage B built and live:** Read-only Telegram inbox commands (verified working)
  - `/sweep` → bottleMsg + recent emails, emoji-rich, aged markers (⏰), saves browse state
  - `/inbox` → quick count
  - `/email [N]` → last N emails (default 10, max 50) with tier icons
  - `/email pending` → debounce batch about to flush
  - `/read N|filename` → md/txt/PDF (pdfplumber venv, first 5 pages)
  - `/quit` / `/done` / `/clear` → manual browse state clear
  - Browse state auto-expires after 30 min (prevents stale `/read` references)
  - All read-only; tested before deploy

- **Documentation updated:** CAPABILITIES.md (testing procedures + monitoring), CLAUDE.md (added Telegram section + current status)
- **Deferring Stage C for 1 week** — observation period to validate Stage B UX before building file-moving actions
- **Decision:** resist jumping to GTD/Stage C work; use Stage B for real, report back what needs improvement

**Commits this session:**
- `cda0724` — Stage B commands shipped
- `9e7c2a2` — Documentation (CAPABILITIES.md + CLAUDE.md)
- `c3bc60d` — /quit + 30-min timeout

**Earlier (2026-05-15):**
- Stage A shipped: SOUL-telegram.md routing for context="group" (fixed hallucination bug)
- Audited email system (no new deps — poppler + pdfplumber present)
- Wrote Phase 2 report with 3-stage design (A ✅, B ✅, C deferred)

---

## 2026-05-19 (distilled)
- **Phase 2 rollup formulas SHIPPED** (`dakota-software` commit `fabf3fc`, pushed) — bridge now ALWAYS emits `=-x-y-z` addend formulas for collapsed rows (mortgage, distribution, etc.), not just `is_partial`. Singletons stay flat. The TODO at sheets_bridge.py line 953 is now closed.
- **Three connected items captured in roadmap doc** `dakota-software/docs/cash-tracking/2026-05-19-rollup-formulas-and-verification-roadmap.md` (commit `f90635a`, corrected `a749b84`): rollup formulas (✅ DONE), day-of-month drift fix (DEFERRED), pending verification yellow+UNVERIFIED model (DEFERRED). All three share the same code path; bundle when revisiting.
- **Critical finding via Rod:** the bridge already had `make_addend_formula()` at line 891 — I initially missed it and proposed building new infrastructure. Rod caught it ("you already have this code"). The actual change was ~10 lines: extract `_compute_e_value()` pure helper + drop the `is_partial` conditional. 8 new unit tests; 75 prior tests still green; same 2 pre-existing mortgage failures.
- **Concrete drift bug found on live sheet:** row 25 (`=-1016.30-842.80-628.48-568.37`) contains late-April 4/30 mortgage payments but is dated 5/1 — exact instance of the day-of-month convention drift flagged in `phase-3-complete-handoff.md`. Visibility came FROM the formula; rollup-formulas-everywhere makes drift bugs equally visible on full rollups.
- **Sorting Hat kickoff doc** created at `dakota-software/docs/sheets/sorting-hat-kickoff.md` (commit `c3666d6`) — self-contained brief for fresh-context session. Read order, Session 1 scope (samples + classifier, no cutover), production posture, deferred items not to bundle. Rod will start fresh `/mad-max quick` session referencing this doc.
- **Reframing of "reconciliation gap":** Rod corrected — the ~$178 wasn't a gap, it was pending Chase txns the bridge correctly wrote but Chase's cleared-balance ending excluded. Number is accurate; the framing in the handoff doc was wrong. Real work is items 1-3 in the roadmap doc above.
- Next: Rod resumes with fresh-context `/mad-max quick` + kickoff doc → Sorting Hat Session 1 (sample collection + classifier)

---

## 2026-05-18 (distilled)
- **Phase 2 hardening kicked off** with Priority 1 fix from `docs/sheets/phase-2-inventory.md`: consolidated `SHEET_MAP` into `property_map.json` as single source of truth (`bot/pdf-extractor/sheets_bridge.py`, commit `6dda8a8`, pushed)
- Helper `_resolve_sheet_id()` reads from `property_map.json`; preserves both `SheetSession(slug)` callsite (line 1507) and `SheetSession(sheet_id)` callsite (line 1023) by passing unknown keys through unchanged
- Tests: 75/77 pass (2 pre-existing failures in `test_sheets_bridge_mortgage.py` per `phase-3-complete-handoff.md` — unrelated)
- Rod confirmed no-build pact does NOT apply to Sheets work; updated `feedback_no_build_pact_2026.md` memory to make the carve-out explicit for ALL Sheets phases (including new internal components like The Sorting Hat)
- Phase 2 strategic priority discussion: **🎩 The Sorting Hat** is the high-leverage piece ("last most valuable piece" per Rod) — full design already in `roadmap.md` lines 75-94
- Note: `gsheets_sync.py` in `~/Work/local/scripts/` still has its own SHEET_MAP — separate cleanup pass when convenient
- Note: morning-brief.md is 17 days stale (last triage 2026-05-01) — nightly triage still broken
- Next: pick Sorting Hat design (collect 10 sample PDFs/CSVs, build classifier deterministically) OR knock out next quick win (reconciliation framing fix)

---
