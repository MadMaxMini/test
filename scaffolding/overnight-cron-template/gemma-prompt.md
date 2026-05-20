You are reviewing a real-estate-finance pipeline that ingests mortgage / Chase checking / Chase credit / PM-owner statements (PDFs and CSVs) and writes them to Google Sheets via Playwright. Your job: brainstorm HARDENING improvements — small AND big — across the WHOLE pipeline, including upcoming DB-migration prep.

Project state in one paragraph: Phase 1 (mortgage → property sheets, 6 properties) shipped 2026-05-12. Phase 3 (Chase checking → PM Cash Tracking tab) shipped 2026-05-18. Phase 2 hardening (Sorting Hat classifier + cleanup) is NEXT — the Sorting Hat classifier itself shipped 2026-05-19 with 100% accuracy on 11 real fixtures, cutover Session 2 is pending. Phase 4 (PM statements, Via Verona quadplex complexity) and Phase 5 (escrow tracking) are queued. Phase 6 is a DB migration to DuckDB with Sheets API replacing Playwright as the render layer; Sharon's validation workflow will move to a Dakota coach chat interface.

A 30-day no-build pact runs through 2026-06-10 (no new agents/services) — but the human will triage, so list EVERYTHING that comes to mind, don't self-censor.

## Output requirements

Produce a Markdown table with these columns:

| # | Title | Category | What (problem) | Why (impact) | How (fix sketch) | Effort | Risk | Phase fit |

Categories: `testing` | `observability` | `security` | `data-integrity` | `refactoring` | `db-prep` | `dx` | `disaster-recovery`
Effort: S (< half day) | M (1-3 days) | L (week+)
Risk: low (touches no prod) | med (new code, prod-adjacent) | high (touches prod files like sheets_bridge.py)
Phase fit: P2 (Phase 2 hardening) | P4 (PM phase) | P5 (escrow/reconciliation) | P6 (DB migration) | now (safe to do anytime) | post-P6 (post-migration only)

Target: **30–50 candidate items**. Better to overshoot. The human will triage.

After the table, add a short "Top 5 I'd push hardest" section with 1-sentence rationale each — your honest pick, ignoring politics or pact.

## Areas to canvass (non-exhaustive — go wider if you see things)

**Phase 2 currently open:**
- Credentials hardening: Playwright OAuth token in `~/.playwright-google/` is unencrypted on disk; spec is to move to OpenBao vault
- Alert noise reduction: pipeline fires too many alerts (Piney Point formula-trap false positives evidenced)
- Playwright batching: per-cell writes are 8-15s each; batching could 10x throughput
- Naming standardization: inconsistent file/script/config naming across `bot/pdf-extractor/`
- Sorting Hat cutover: unified inbox migration, LaunchAgent rewiring, quarantine path
- Repo split audit: should `bot/pdf-extractor/` live in `dakota-software` or `madmax`?

**Phase 1 prod stability (live system):**
- Year-flip ritual: manual annual task to add new year block + repoint "current" formulas; "stale" rejection is the only safety net if forgotten
- Dupe-log surfacing: `~/Library/CloudStorage/Dropbox/bottleMsg/logs/sheets-dupes.log` is append-only, no surfacing UI
- Backup/recovery: no documented sheet-restore procedure if a sheet gets corrupted by bridge bug or human edit
- Idempotency: re-running bridge on same CSV must produce same outcome — needs explicit test
- 2 pre-existing failing mortgage-field tests (mentioned in 5/19 rollup-formulas roadmap doc)
- Known Info-tab errors: kickapoo-401 #REF! on rows 20+23, kickapoo-403 #VALUE! on row 20

**Pending-verification (deferred late P2 or P5):**
- UNVERIFIED markers for pending Chase txns + roll-off handling (full design in docs/cash-tracking/2026-05-19-rollup-formulas-and-verification-roadmap.md section 3)
- Two-phase: write markers (easy) → verify-then-write reconciliation (hard)
- Zero-out vs ghost-sheet treatment is open

**Phase 6 DB-migration prep (DuckDB locked):**
- Schema design: what does the property/statement/transaction model look like in DuckDB
- Sheets API render layer to replace Playwright — proof-of-concept candidate?
- Sharon's validation workflow → Dakota coach chat interface (load-bearing design Q)
- CSV → DB ingestion path (DuckDB reads CSV natively, so the pipeline gets simpler)
- Sheets-as-view vs sheets-as-source-of-truth flip — backwards-compat during migration?

**Edge cases & domain:**
- Via Verona quadplex format (Phase 4 blocker — Doc fact-check open since 05-11)
- Multi-property bridge collisions (concurrent runs on same sheet?)
- PDF parsing failures: corrupt/scanned/non-standard servicer formats
- Ambiguous descriptions in Chase CSV (currently Telegram alerts)
- Day-of-month convention (intentional design per do-not-fix.md — DO NOT propose changing this)

**Observability:**
- Pipeline run telemetry (when did what fire, what was the outcome?)
- Alert tier dispatch (routine vs warning vs error — see alert-tiers-design.md)
- Runtime metrics (cell-write latency, classification confidence distribution)
- Dashboard for Rod's morning brief?

**Disaster recovery:**
- Sheet corruption rollback
- Accidental writes (e.g., bridge bug on wrong sheet)
- LaunchAgent silent failure (last run was 18 days stale before 5/19 fix)
- Dropbox Smart Sync regression (root caused once, watch for repeats)

**Repo / config:**
- `property_map.json` consolidation vs `config/properties.json` rename (per phase-2-inventory.md)
- Config change watcher (any change → Telegram alert to Rod)
- Secrets in repo audit
- LaunchAgent plist locations + version control

Go wider than this list if you see opportunities. Be specific: not "improve testing" but "add idempotency test that re-runs `sheets_bridge.py` on a fixture CSV and asserts zero deltas on 2nd run."

The context bundle attached has the roadmap, all relevant design docs, recent git history, and file inventories. Read it carefully before drafting.
