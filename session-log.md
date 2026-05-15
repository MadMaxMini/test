# Session Log

## 2026-05-13 — Phase 3 Chase bridge PROD cutover + Phase 2 scope correction

**Completed:**
- Phase 3 Chase → Cash Tracking bridge: design, classify/collapse logic, live writes to PROD
  - March 2026 statement: 41 txns → 34 rows, reconciliation $14,629.85 (exact match to Chase)
  - 3 rows landed in PROD (r15, r16, r17), idempotent re-run no-op, dedup working
  - commit 048417f, pushed to phase-3-chase-cash-tracking
- Phase 2 scope reframed: asset inventory + detailed flowchart + refactoring audit (not alerting/long-polling)
  - Rewrote roadmap.md lines 28-72, drafted fresh-agent prompts for Phase 2 + Phase 3 work
  - Rod working on phase-2-inventory.md (887L) + alert-system-design.md (324L) — uncommitted

**Decisions:**
- Phase 3 authorized under no-build pact (core Dakota automation, not new agents)
- Phase 4 bundles PM statements + alerting hardening
- Phase 2 uses fresh agent (clean context for design)
- Bridge: balance-only scope, dedup by (year-month, amount, prefix), drift thresholds (mortgage $500, dist $2000, CC $200)

**Blockers/Open:**
- Sharon: Via Verona May statement pending ServiceMac issuance (P0)
- Phase 3 v1.6 checklist: CSV dedup test, folder rename, auto-watcher integration, partial-mortgage completion, drift refinement, answer Sharon's 7 questions
- dakota-software: roadmap.md, phase-2-inventory.md, alert-system-design.md uncommitted (Rod will commit)

**What's next:** Rod spins up fresh agent for Phase 2 inventory. Monitor June statements for Phase 1 validation.

---

## 2026-05-12 — Phase 1 shipped (formula guard + scope-down landed)

**Completed:**
- Reviewed 6 properties' May 12 statements. 5 worked, 1 dedup'd (Via Verona real duplicate). Found Piney Point formula trap (C20 =C19+C4 → false alerts).
- Patched sheets_bridge.py: MORTGAGE_FIELD_SPECS 4→1 (balance-only), added formula-as-payment guard (skip alerts if prev_payment.startswith("="))
- Rod manually verified + cleaned all 6 sheets (401K, 403K, Grand Pines, Piney, La Estancia, Via Verona)
- Phase 1 marked ✅ COMPLETE in roadmap
- commits f020bd1, 37d6027, 2af58c0

**Decisions:**
- Bridge scope: only C21 (Balance) + D21 (date), read C20 for change-detect only, never write
- Sheets API re-wire deferred to Phase 2 (Playwright works fine)
- Phase 1 untested live — first real test early June

**Blockers:** Bridge changes untested live, await June statements.

**What's next:** Sharon drops real May Via Verona (pending), June statements validate new code.

---

## 2026-05-12 — Model switching: TTL + flipped defaults

**Completed:**
- Added temporary TTL mode (1-2h expiration) to dispatcher. Three modes: one-off > TTL > persistent > default.
- Flipped defaults: bare `/model X` = temporary 2h (auto-revert), `/model X perm` = persistent (explicit)
- `/model?` query now shows TTL remaining, `/help` rewritten
- commits 8be6d52, ac76a1f, 8517c5c

**Decisions:** Temp 2h default right — most switches revert, permanent is exception.

---

## 2026-05-12 — Big-picture audit + 30-day no-build pact + OpenBao unsealed

**Completed:**
- Full start sweep, verified FDA fix working (pdfwatch + pmwatch firing), verified Piney Point dedup correct
- OpenBao discovery: already initialized (KV + Transit engines, real secrets stored), was sealed. Unsealed via unseal-keychain.sh, R/W test passed.
- 30-day no-build pact written + saved to memory (active through 2026-06-10)
- needs-rod.md updated

**Decisions:**
- **30-day no-build pact ACTIVE 2026-06-10.** Override clause: Rod must explicitly say "I'm overriding pact for X because Y."
- Dakota mortgage pipeline = franchise, coaches = overhead
- Coaches not dead — outbound nudges work, inbound Telegram pollers broken (DNS errors)

**Bugs surfaced (not fixed):**
- OpenBao helper scripts hunt for token at ~/.openbao-init (plaintext), not Keychain — unusable from CLI
- No auto-unseal LaunchAgent — Docker restart silently breaks coaches with secrets
- Elite HH + Health Telegram pollers: DNS error since 2026-05-08 (daily nudges fine, inbound chat broken)
- Watcher dedup leaves dupes in inbox instead of processed/ (cosmetic)

**What's next (pact-aware priority):** auto-unseal LaunchAgent, coach roster triage (keep/simplify/archive), time audit, DNS poller fix, Phase 2 Dakota.

---

## 2026-05-10 — Max Bot in Dakota Automation Team group

**Completed:**
- Wired @madmax_mini_bot into Dakota Automation Team Telegram group (was unmonitored)
- Group commands: `/ping`, `/status`, `/models`, `/tasks [name]`, `/standup`, `@madmax_mini_bot [question]`
- tg_send upgraded for explicit chat_id, added tg_send_chunked (para boundaries, cap 3 msgs × 4000 chars)
- Fixed `/tasks` reading legacy people/{p}/tasks.md → switched to canonical tasks/views/{p}.md
- Group session history via sessions_mod.Session(GROUP_CHAT_ID)

**Decisions:** Max handles group, AutoDakota handles 1-on-1.

---

## 2026-05-08 — Via Verona 8302 sheet onboarded

**Completed:**
- Identified good vs stale Via Verona sheets via Playwright, added label_column config (Via Verona=G, Kickapoo=J)
- Caught escrow mismatch: was writing account balance to monthly-payment row. Added new "Escrow Balance" row 24, wired config.
- Wired Via Verona into property_map.json + SHEET_MAP, live run: 6 cells written (balance, escrow, dates)
- All 6 properties online

**Decisions:** Escrow account balance ≠ monthly payment (separate rows).

---

## 2026-05-06 — Local model audit + Telegram bot intelligence bump

**Completed:**
- Full HuggingFace/Ollama audit: 6 models (74GB total), reviewed March benchmarks
- Created ~/Work/local/scripts/reference-models.md (speed charts, scorecards, failure modes, verdicts)
- Wired `models` + `models detail` into dispatcher (on-demand pull)
- Bumped Telegram bot depth 10→20, Ollama output cap 200→500 tokens

**Decisions:** Mixtral = dead weight (26GB, timeouts), candidate for removal. Mistral Small = dispatcher default.

---

## 2026-04-30 — Phase 1 review + handoff plans + FDA blocker found

**Completed:**
- Walked Rod through sheet architecture, revised phase roadmap (P1=balance, P2=cleanup, P3=escrow, P4=PM, P5=hardening)
- Date format aligned (extractors normalize to MM/DD/YYYY)
- 4 more property IDs added (grand-pines, la-estancia, piney-point, cash-tracking)
- Notification routing decided: routine→Telegram to Rod, alerts→Telegram+iMessage, urgent→Dakota group
- Investigated missing PDFs: 4 PM Owner Statements stuck in inbox. Root cause: **FDA not granted to launchd /bin/bash** — both pdfwatch + pmwatch dead.
- Wrote 3 handoff prompts (wire-bridge, FDA fix, Phase 2 plan)

**Blockers:** FDA permissions — Rod must grant in System Settings manually.

**What's next:** FDA fix, wire bridge into pipeline, process stuck PDFs.

---

## 2026-04-29 — Sheets pipeline Phase 1 built + tested

**Completed:**
- Analyzed Kickapoo sheets (401K + 403K) via Playwright, mapped tab structure + formulas
- Built sheets_bridge.py: single Playwright session, dual dup check (CSV + Sheet), date normalization, payment-change alerting
- Built property_map.json for Kickapoo properties
- Live test kickapoo-403: balance $53,455.45 written, payment alert fired ($330.58→$628.48), dup check worked
- RFC dropped to Dakota team inboxes
- Saved sheet architecture to madmax + dakota memory

**Decisions:** Phase 1 = balance + payment alerts (escrow=Phase2, PM=Phase3). Bridge uses Playwright direct (single session).

---

## 2026-04-28 — GTD sweep via Telegram

**Completed:**
- Built gtd-sweep.py (bottleMsg inventory → classified table → Telegram)
- Wired GTD reply commands: `gtd go`, `gtd go 1,3`, `gtd hold 2`, `gtd move 4 archive`, `gtd skip`
- LaunchAgent com.madmax.gtdsweep: WatchPaths on bottleMsg + 11:55am daily (5-min debounce)
- KeePass auto-stay, cheat-sheet-failure auto-archive (laptop-only)
- Processed bottleMsg inbox

**Decisions:** GTD sweep async via Telegram. Cheat-sheet failures laptop-only (saved to memory).

---

## 2026-04-25 — Calendar Bot live + context fix

**Completed:**
- Calendar Bot end-to-end: 13,616 events→SQLite FTS5, search engine, Claude+Ollama layer, Telegram poller
- Registered @cala_tele_bot (token + chat_id in Keychain)
- Fixes: emails now in LLM context, conversation history passed to search+LLM, triple-response bug killed
- PROJECT.md created

**Decisions:** No git repo (personal data, encrypt later). Data in ~/Work/coaches/calendar-bot/data/.

---

## 2026-04-24 — PM pipeline stood up + PDF dup detection

**Completed:**
- Reviewed Devon's PM extractor + wrappers (pre-built)
- Updated shell scripts + launchd plists for Dropbox folder renames (statements → account-statements-inbox, new pm-statements-inbox)
- Installed + loaded com.dakotaops.pmwatch — PM pipeline live
- Test extracted Georgia Owner Statement (HomeRiver, 2889 Grand Pines Ct, Dec 2025) clean
- Added canonical PDF rename on move: YYYY-MM_property-slug_bank.pdf
- Dual dup detection: filename check + CSV date check
- Both pipelines handle move+rename in Python
- Symlinked operations/mortgage-data + operations/pm-data into Dropbox processed/
- Test results to bottleMsg

**Decisions:** Flat pm-statements-inbox/ (no subfolders). Owner Statement PDFs = extraction target.

---
