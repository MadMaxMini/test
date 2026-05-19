# Session Log

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

**Repos touched:** `dakota-software` (branch `phase-2-sorting-hat`, PR #3, pushed). No `madmax` code changes this session — only session log.

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
