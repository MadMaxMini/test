# Session Log

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
